from __future__ import annotations

from functools import wraps
from traceback import format_exc
import types
from typing import Annotated, Any, TypeVar, overload, get_origin, get_args, Type, Union, _GenericAlias
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError, validate_call

from .errors import ErrorModel

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")
X = TypeVar("X", bound=BaseException)
GenericType = Union[Type, _GenericAlias]

__all__ = ("validate_call_safe",)

def is_union(cls: GenericType) -> bool:
    """Check if a class is a Union."""
    # UnionType added in py3.10
    if not hasattr(types, "UnionType"):
        return get_origin(cls) is Union
    return get_origin(cls) in [Union, types.UnionType]

# Decorator with brackets
@overload
def validate_call_safe(
    error_model: type[T] = ErrorModel,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
    validate_body: bool = False,
    extra_exceptions: type[X] | tuple[type[X]] = Exception,
    report: bool = False,
    reporter: Callable[[str], None] = print,
) -> Callable[[Callable[..., R]], Callable[..., R | T]]: ...


# Decorator without brackets
@overload
def validate_call_safe(
    func: Callable[..., R],
    /,
) -> Callable[..., R | T]: ...


def validate_call_safe(
    error_model_or_func: type[T] | Callable[..., R] = ErrorModel,
    /,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
    validate_body: bool = False,
    extra_exceptions: type[X] | tuple[type[X]] = Exception,
    report: bool = False,
    reporter: Callable = print,
):
    """Decorator for validating function calls and handling errors safely.

    This decorator wraps the Pydantic validate_call decorator and captures any validation
    or other errors, passing them into a provided error model instead of allowing them to raise.

    Usage must be as a decorator with arguments `@validate_call_safe(ErrorModel, config=...)`.

    Args:
        error_model: A Pydantic model class to use for error reporting.
        func: The function to be decorated (optional, can be passed in decorator form).
        config: Configuration for the Pydantic model (optional).
        validate_return: Whether to validate the return value.
        validate_body: Whether to handle exceptions besides signature validation.
        extra_exceptions: Additional exception types to handle in the function body execution
                          (requires `validate_body = True`).
        report: Whether to report in/outputs via `reporter`.
        reporter: The function used to report in/outputs if `report = True`.

    Returns:
        The decorated function that returns either the original return type or the error model.

    Example:
        ```python
        from pydantic import BaseModel

        class CustomErrorModel(BaseModel):
            error_type: str
            error_str: str

        @validate_call_safe(CustomErrorModel)
        def int_func(a: int) -> int:
            return a

        result = int_func("not an int")  # Returns CustomErrorModel instance
        ```
    """

    def is_annotated_basemodel_subclass(cls):
        if get_origin(cls) is Annotated:
            base_cls = get_args(cls)[0]
            return isinstance(base_cls, type) and issubclass(base_cls, BaseModel)
        return False

    def is_union_basemodel_subclasses(cls):
        if is_union(cls):
            all_models = all(
                isinstance(base_cls, type) and issubclass(base_cls, BaseModel)
                for base_cls in get_args(cls)
            )
            if all_models:
                return True
            else:
                raise TypeError(f"Union argument to decorator must only contain models")
        return False

    empty_brackets = error_model_or_func is ErrorModel
    is_annotated_model_cls = is_annotated_basemodel_subclass(error_model_or_func)
    is_model_cls_union = is_union_basemodel_subclasses(error_model_or_func)
    # For Union, we'll use the default ErrorModel then dump into a TypeAdapter to decide
    is_wrapped_model_cls = is_annotated_model_cls or is_model_cls_union
    pos_arg_is_cls = isinstance(error_model_or_func, type) or is_wrapped_model_cls

    # Annotated classes behave as the class (`__call__` method falls thru to model cls)
    provided_err_model = pos_arg_is_cls and (
        is_wrapped_model_cls or issubclass(error_model_or_func, BaseModel)
    )
    if empty_brackets or provided_err_model:
        # Either validate_call used with empty brackets, and the first positional arg
        # defaulted to the ErrorModel or used with brackets and an error_model was set
        error_model = error_model_or_func
        func = None
    else:
        # validate_call is used without brackets, and defaults to the ErrorModel
        func = error_model_or_func
        error_model = ErrorModel

    # TODO: cache these TypeAdapters at module level to avoid recomputation latency
    # (would affect programs with multiple decorated classes with custom error models?)
    if is_annotated_model_cls:
        # TypeAdapter triggers functional validators in Annotated metadata if present.
        # Pre-provision it here (upon # decorator creation, if I understand correctly?)
        # rather than delaying TypeAdapter creation until the wrapper function is run.
        error_model_validate = TypeAdapter(error_model).validate_python
    elif is_model_cls_union:
        # First parse into the default `ErrorModel`, then use a `TypeAdapter` on the
        # dumped model output to re-parse as one of the `Union` model classes
        error_model_validate = ErrorModel.model_validate
    else:
        # There is no `Annotated` metadata (so no potential functional validators),
        # so no need to use `TypeAdapter` just a regular `.model_validate()` method
        error_model_validate = error_model.model_validate

    def validate(f: Callable[..., R]) -> Callable[..., R | T]:
        validated_func = validate_call(
            f,
            config=config,
            validate_return=validate_return,
        )

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> R | T:
            _signature_only = not validate_body  # Alias for internal clarity
            func_name = f.__name__
            try:
                if report:
                    msg = f"{func_name} received *{args}, **{kwargs}"
                    reporter(msg)
                ret = validated_func(*args, **kwargs)
            except ValidationError as e:
                # Good enough heuristic to tell if the error came from the func schema
                is_signature_ve = validated_func.__name__ == e.title
                if _signature_only and not is_signature_ve:
                    raise
                else:
                    error_t_name = "ValidationError"
                    ret = error_model_validate(
                        dict(
                            error_type=error_t_name,
                            error_details=e.errors(),
                            error_str=str(e),
                            error_repr=repr(e),
                            error_tb=format_exc(),
                        ),
                    )
                    # TODO: move this TypeAdapter construction up to a higher level:
                    if is_model_cls_union:
                        # We just validated into a temporary ErrorModel
                        # Now validate using a TypeAdapter on the Union of models
                        ret = TypeAdapter(error_model).validate_python(ret.model_dump())
                    if report and validate_return:
                        reporter(f"{func_name} -> {ret!r}")
            except extra_exceptions as e:
                if _signature_only:
                    raise
                else:
                    error_t_name = type(e).__name__
                    ret = error_model_validate(
                        dict(
                            error_type=error_t_name,
                            error_details=[],
                            error_str=str(e),
                            error_repr=repr(e),
                            error_tb=format_exc(),
                        ),
                    )
                    # TODO: move this TypeAdapter construction up to a higher level:
                    if is_model_cls_union:
                        # We just validated into a temporary ErrorModel
                        # Now validate using a TypeAdapter on the Union of models
                        ret = TypeAdapter(error_model).validate_python(ret.model_dump())
                    if report and validate_return:
                        reporter(f"{func_name} -> {ret!r}")
            else:
                if report and validate_return:
                    f_name = f.__name__
                    ret_t_name = type(ret).__name__
                    msg = f"{f_name} -> {ret_t_name}: {ret!r}"
                    reporter(msg)
            return ret

        return wrapper

    if func:
        return validate(func)
    else:
        return validate
