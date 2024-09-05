from typing import Literal
from pydantic import BaseModel
from validate_call_safe import validate_call_safe, ErrorModel
from inline_snapshot import snapshot


class A(BaseModel):
    x: int
    y: int

class B(BaseModel):
    x: str


class C(BaseModel):
    z: int


class ValidnFail(BaseModel):
    error_type: Literal["ValidationError"]

class AttribFail(BaseModel):
    error_type: Literal["AttributeError"]

@validate_call_safe(ValidnFail | AttribFail, validate_body=True)
def x_access(model: A | B | C) -> int:
    """Input is assumed to have field `x: int`."""
    assert model.x != 4
    return model.x


A_xy_x = x_access(dict(x=1, y=2))  # Resolves to A(x: int, y: str)
# -> ErrorModel(error_type='ValidationError', ...)

B_fail = x_access(dict(x=1))  # No ! Resolves to B(x: str) not x: int
# -> ErrorModel(error_type='ValidationError'

C_fail = x_access(dict(z=3))  # No ! Resolves to C(z: int) not x: int

other_fail = x_access(dict(x=4))  # ! Resolves to B, assert fails
