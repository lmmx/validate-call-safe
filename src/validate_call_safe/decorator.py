from functools import wraps
from typing import Type, TypeVar, Callable, Any, Union, overload
from pydantic import BaseModel, ValidationError, validate_call

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")


@overload
def validate_call_safe(
    error_model: Type[T],
) -> Callable[[Callable[..., R]], Callable[..., Union[R, T]]]: ...


@overload
def validate_call_safe(
    error_model: Type[T], func: Callable[..., R]
) -> Callable[..., Union[R, T]]: ...


def validate_call_safe(error_model: Type[T], func: Callable[..., R] = None):
    """Decorator for validating function calls and handling errors safely.

    This decorator wraps the Pydantic validate_call decorator and captures any validation
    or other errors, passing them into a provided error model instead of allowing them to raise.

    Usage may be either as a decorator with arguments `@validate_call_safe(ErrorModel)`
    or as a plain decorator `@validate_call_safe(ErrorModel)(func)`.

    Args:
        error_model: A Pydantic model class to use for error reporting.
        func: The function to be decorated (optional, can be passed in decorator form).

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

    def validate(f: Callable[..., R]) -> Callable[..., Union[R, T]]:
        validated_func = validate_call(f)

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
