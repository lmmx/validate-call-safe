from pydantic import BaseModel, Json
from validate_call_safe import validate_call_safe, ErrorModel


@validate_call_safe(extra_exceptions=NameError, validate_body=True)
def int_noop(a: int) -> int:
    if a == 1:
        raise ValueError("Thrown")
    elif a == 2:
        raise NameError("Captured")
    else:
        return a


invalid = int_noop(a="A")  # ErrorModel(error_type='ValidationError', ...)

try:
    failure = int_noop(a=1)  # ErrorModel(error_type='ValueError', ...)
except ValueError:
    pass
else:
    assert False, "Should have thrown ValueError"

captured = int_noop(2)

success = int_noop(3)

assert isinstance(invalid, ErrorModel)
assert invalid.error_type == "ValidationError"

assert isinstance(captured, ErrorModel)
assert captured.error_type == "NameError"

assert success == 3
