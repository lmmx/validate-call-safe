from pydantic import BaseModel, validate_call


class CustomErrorModel(BaseModel):
    error_type: str
    error_json: str | None = None
    error_str: str | None = None


@validate_call
def int_noop(a: int) -> int:
    return a


def success():
    return int_noop(a=1)


def failure():
    return int_noop(a=None)
