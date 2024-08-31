from pydantic import BaseModel
from validate_call_safe import validate_call_safe


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
