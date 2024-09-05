from typing import Literal
from pydantic import BaseModel, ValidationError
from validate_call_safe import validate_call_safe, ErrorModel


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
    assert model.x != "foo"
    return model.x


try:
    fail_fallthru = x_access(dict(x="foo"))  # ! Resolves to B, assert fails
except ValidationError:
    print("The AssertionError was not modelled by the error model union and raised!")
    fail_fallthru = "You lose"
else:
    print("This was not supposed to work!")
    fail_fallthru = "This was not supposed to work!"


# We do the same again but now add the ErrorModel to the Union: it cannot fail this time
@validate_call_safe(ValidnFail | AttribFail | ErrorModel, validate_body=True)
def x_access_safe(model: A | B | C) -> int:
    """Input is again assumed to have field `x: int`."""
    assert model.x != "foo"
    return model.x


rescued = x_access_safe(
    dict(x="foo"),
)  # ! Assert fails again, but ErrorModel catches it
print(f"Phew: {type(rescued).__name__} rescued the {rescued.error_type}")
