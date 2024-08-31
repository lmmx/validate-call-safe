from pydantic import BaseModel, Json
from validate_call_safe import validate_call_safe

class CustomErrorModel(BaseModel):
    error_type: str
    error_json: Json = {}
    error_str: str | None = None
    error_repr: str | None = None

@validate_call_safe(CustomErrorModel)
def int_noop(a: int) -> int:
    return a

success = int_noop(a=1)
failure = int_noop(a="A")
