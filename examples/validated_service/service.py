import argparse
import json
from ast import literal_eval
from pprint import pprint
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Json, model_validator
from validate_call_safe import validate_call_safe, ErrorModel

class Pet(BaseModel):
    name: str
    "Name of the pet."
    species: Literal["cat", "dog"]
    "Type of animal."
    age: int
    "Age of animal in years."


class Person(BaseModel):
    name: str
    "Name of the user."
    age: int
    "Age of the user in years."
    pets: list[Pet] = []
    "The user's pets."


class Event(BaseModel):
    user: Person

class StrError(ErrorModel):
    @model_validator(mode="after")
    @classmethod
    def stringify(cls, value):
        return str(value)

# StrError = Annotated[ErrorModel, AfterValidator(str)]
StrReturn = Annotated[int, AfterValidator(str)]

@validate_call_safe(StrError, validate_body=True, validate_return=True)
def service(event: Event, context: None = None) -> StrReturn:
    """The service behaviour has three main paths:

    - Validation error: if the event is invalid, return ErrorModel from ValidationError
    - Traced error: if the user has 0 pets, return ErrorModel from AttributeError
    - Happy path: if the user has 1+ pets, return the first pet's age as a string
    """
    first_pet_age: int = event.user.pets[0].age
    return first_pet_age


class KVAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for value in values:
            if '=' in value:
                key, val = value.split('=', 1)
                setattr(namespace, key, val)
            else:
                setattr(namespace, key, None)


def main():
    parser = argparse.ArgumentParser(description="Accepts arbitrary key=value pairs.")
    # Use nargs='+' to capture multiple key=value pairs
    parser.add_argument('params', nargs='+', action=KVAction, help="key=value pairs")
    args = parser.parse_args()
    var_p = vars(args)["params"]
    params = args.params
    ev = {k: v if v is None else literal_eval(v) for k,v in vars(args).items()}
    breakpoint()
    result = service(event=ev)
    try:
        print(result.error_str)
    except:
        pprint(result)
    return result

if __name__ == "__main__":
    """Usage:

    python service.py 'user={"age":1, "name":"A", "pets": [{"species":"cat", "name": "foo", "age": 100}]}'
    """
    result = main()
