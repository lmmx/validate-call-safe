from pydantic import BaseModel
from validate_call_safe import validate_call_safe
from inline_snapshot import snapshot


class CustomErrorModel(BaseModel):
    error_type: str
    error_details: list


@validate_call_safe(CustomErrorModel)
def int_noop(a: int) -> int:
    return a


success = int_noop(a=1)  # 1
failure = int_noop(a="A")  # CustomErrorModel(error_type='ValidationError', ...)

assert success == 1

assert isinstance(failure, CustomErrorModel)
assert failure.model_dump() == snapshot(
    {
        "error_type": "ValidationError",
        "error_details": [
            {
                "type": "int_parsing",
                "loc": ("a",),
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "A",
                "url": "https://errors.pydantic.dev/2.8/v/int_parsing",
            },
        ],
    },
)
