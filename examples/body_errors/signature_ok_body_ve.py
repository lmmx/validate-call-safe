from pydantic import BaseModel, ValidationError
from validate_call_safe import validate_call_safe

class A(BaseModel):
    a: int

@validate_call_safe
def failing(a: int):
    value = A(a="x")
    return value

try:
    failing(a=1)
except ValidationError:
    pass # Due to body error
else:
    raise ValueError("Body error should throw")
