from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar, Union, overload

from pydantic import BaseModel, ValidationError
from pydantic.config import ConfigDict
from pydantic._internal import _validate_call, _generate_schema, _typing_extra
from pydantic._internal._config import ConfigWrapper

T = TypeVar('T')
ErrorModel = TypeVar('ErrorModel', bound=BaseModel)

class ValidateCallSafeWrapper:
    def __init__(
        self,
        function: Callable[..., Any],
        error_model: type[ErrorModel],
        config: ConfigDict | None,
        include_json: bool,
        include_str: bool,
    ):
        self.function = function
        self.error_model = error_model
        self.include_json = include_json
        self.include_str = include_str

        config_wrapper = ConfigWrapper(config)
        gen_schema = _generate_schema.GenerateSchema(config_wrapper, _typing_extra.get_cls_types_namespace(function))
        schema = gen_schema.generate_schema(function)
        core_config = config_wrapper.core_config(function)

        self.validator = _validate_call.ValidateCallWrapper(
            function,
            config,
            validate_return=False,
            namespace=_typing_extra.get_cls_types_namespace(function),
        )

        functools.update_wrapper(self, function)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return self.validator(*args, **kwargs)
        except Exception as e:
            error_data = {"error_type": type(e).__name__}
            if self.include_json:
                if isinstance(e, ValidationError):
                    error_data["error_json"] = e.json()
                else:
                    error_data["error_json"] = "{}"
            if self.include_str:
                error_data["error_str"] = str(e)
                error_data["error_repr"] = repr(e)
            return self.error_model.model_validate(error_data)

def validate_call_safe(
    error_model: type[ErrorModel],
    *,
    config: ConfigDict | None = None,
    include_json: bool = True,
    include_str: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., Union[T, ErrorModel]]]:
    def decorator(function: Callable[..., T]) -> Callable[..., Union[T, ErrorModel]]:
        return functools.wraps(function)(
            ValidateCallSafeWrapper(
                function,
                error_model,
                config,
                include_json,
                include_str,
            )
        )
    return decorator
