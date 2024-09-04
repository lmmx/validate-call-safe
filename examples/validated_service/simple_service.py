from __future__ import annotations

from typing import Annotated

from pydantic import AfterValidator, BaseModel
from validate_call_safe import validate_call_safe, ErrorModel


class Event(BaseModel):
    user: Person


class Person(BaseModel):
    name: str
    "Name of the user."
    pet: Pet
    "The user's pet."


class Pet(BaseModel):
    animal: str
    "Type of animal."
    age: int
    "Age of animal in years."


# An alternative to a lambda with `include` would be a custom error model with only the
# desired fields, which could then just use `AfterValidator(YourError.model_dump_json)`
ErrorModelJson = Annotated[
    ErrorModel,
    AfterValidator(
        lambda m: ErrorModel.model_dump_json(
            m,
            include=["error_type", "error_details"],
            indent=2,
        ),
    ),
]
StrReturn = Annotated[int, AfterValidator(str)]


# The decorator here implicitly changes the return type to `StrReturn | ErrorModelJson`
# i.e. always a `str` (since both types' Annotated AfterValidator produce string values)
@validate_call_safe(ErrorModelJson, validate_body=True, validate_return=True)
def check(event: Event, context: None = None) -> StrReturn:
    """The Pet Age Check service behaviour has three main paths:

    - Invalid input/return value: return `ErrorModelJson` don't throw `ValidationError`
    - Body error: if some error occurs (unlikely!), also return as an `ErrorModelJson`
    - Happy path: if the user has 1+ pets, return the first pet's age as a string
    """
    pet_age: int = event.user.pet.age
    return pet_age


pet_turtle = check({"user": {"name": "A", "pet": {"animal": "turtle", "age": 100}}})
assert type(pet_turtle) is str
print(pet_turtle)
# 100

no_pet_err = check({"user": {"name": "B"}})
assert type(no_pet_err) is str
print(no_pet_err)
# {
#   "error_type": "ValidationError",
#   "error_details": [
#     {
#       "type": "missing",
#       "loc": [
#         0,
#         "user",
#         "pet"
#       ],
#       "msg": "Field required",
#       "input": {
#         "name": "B"
#       }
#     }
#   ]
# }
