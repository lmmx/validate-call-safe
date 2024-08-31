from __future__ import annotations

from functools import wraps
from traceback import format_exc
from typing import Any, TypeVar, overload
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, ValidationError, validate_call

from .errors import ErrorModel

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")
X = TypeVar("X", bound=BaseException)

__all__ = ("validate_call_safe",)


# Decorator with brackets
@overload
def validate_call_safe(
    error_model: type[T] = ErrorModel,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
    validate_body: bool = False,
    extra_exceptions: type[X] | tuple[type[X]] = Exception,
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
    empty_brackets = error_model_or_func is ErrorModel
    pos_arg_is_cls = isinstance(error_model_or_func, type)
    provided_err_model = pos_arg_is_cls and issubclass(error_model_or_func, BaseModel)
    if empty_brackets or provided_err_model:
        # Either validate_call used with empty brackets, and the first positional arg
        # defaulted to the ErrorModel or used with brackets and an error_model was set
        error_model = error_model_or_func
        func = None
    else:
        # validate_call is used without brackets, and defaults to the ErrorModel
        func = error_model_or_func
        error_model = ErrorModel

    def validate(f: Callable[..., R]) -> Callable[..., R | T]:
        validated_func = validate_call(
            f,
            config=config,
            validate_return=validate_return,
        )

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> R | T:
            _signature_only = not validate_body  # Alias for internal clarity (lol)
            try:
                return validated_func(*args, **kwargs)
            except ValidationError as e:
                # Good enough heuristic to tell if the error came from the func schema
                is_signature_ve = validated_func.__name__ == e.title
                if _signature_only and not is_signature_ve:
                    raise
                else:
                    return error_model(
                        error_type="ValidationError",
                        error_details=e.errors(),
                        error_str=str(e),
                        error_repr=repr(e),
                        error_tb=format_exc(),
                    )
            except extra_exceptions as e:
                if _signature_only:
                    raise
                else:
                    return error_model(
                        error_type=type(e).__name__,
                        error_details=[],
                        error_str=str(e),
                        error_repr=repr(e),
                        error_tb=format_exc(),
                    )

        return wrapper

    if func:
        return validate(func)
    else:
        return validate
