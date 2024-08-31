from pydantic import BaseModel, Json
from validate_call_safe import validate_call_safe, ErrorModel


@validate_call_safe()
def int_noop(a: int) -> int:
    return a


success = int_noop(a=1)  # 1
failure = int_noop(a="A")  # ErrorModel(error_type='ValidationError', ...)

assert success == 1
assert isinstance(failure, ErrorModel)
