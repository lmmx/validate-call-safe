from pydantic import BaseModel, Json
from validate_call_safe import validate_call_safe, ErrorModel


@validate_call_safe(validate_return=True)
def int_noop(a: int) -> int:
    return "foo"


bad_return = int_noop(a=1)  # ErrorModel(error_type='ValidationError', ...)
bad_input = int_noop(a="A")  # ErrorModel(error_type='ValidationError', ...)

assert isinstance(bad_return, ErrorModel)
assert bad_return.error_json[0]["input"] == 'foo'
assert bad_return.error_json[0]["loc"] == []

assert isinstance(bad_input, ErrorModel)
assert bad_input.error_json[0]["input"] == 'A'
assert bad_input.error_json[0]["loc"] == ['a']
