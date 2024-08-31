from __future__ import annotations

from functools import wraps
from typing import TypeVar, Callable, Any, Union, overload
from pydantic import BaseModel, ValidationError, validate_call, Json

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")

class ErrorModel(BaseModel):
    error_type: str
    error_json: Json
    error_str: str
    error_repr: str


# Decorator with brackets
@overload
def validate_call_safe(
    error_model: type[T] = ErrorModel,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
) -> Callable[[Callable[..., R]], Callable[..., Union[R, T]]]: ...


# Decorator without brackets
@overload
def validate_call_safe(
    func: Callable[..., R],
    /,
) -> Callable[..., Union[R, T]]: ...


def validate_call_safe(
    error_model_or_func: type[T] | Callable[..., R] = ErrorModel,
    /,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
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
    if error_model_or_func is ErrorModel:
        # validate_call is used with empty brackets, and defaults to the ErrorModel
        error_model = error_model_or_func
        func = None
    elif isinstance(error_model_or_func, type) and issubclass(error_model_or_func, BaseModel):
        # validate_call is used with brackets, and a positional error_model was set
        error_model = error_model_or_func
        func = None
        # TODO: of this logic is sound, this can be merged with previous condition
    else:
        # validate_call is used without brackets, and defaults to the ErrorModel
        func = error_model_or_func
        error_model = ErrorModel

    def validate(f: Callable[..., R]) -> Callable[..., Union[R, T]]:
        validated_func = validate_call(f, config=config, validate_return=validate_return)

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Union[R, T]:
            try:
                return validated_func(*args, **kwargs)
            except ValidationError as e:
                return error_model(
                    error_type="ValidationError",
                    error_json=e.json(),
                    error_str=str(e),
                    error_repr=repr(e),
                )
            except Exception as e:
                return error_model(
                    error_type=type(e).__name__,
                    error_json="{}",
                    error_str=str(e),
                    error_repr=repr(e),
                )

        return wrapper

    if func:
        return validate(func)
    else:
        return validate
