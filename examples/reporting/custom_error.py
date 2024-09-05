from pydantic import BaseModel
from inline_snapshot import snapshot
from validate_call_safe import validate_call_safe

reports = []


class CustomErrorModel(BaseModel):
    error_type: str
    error_details: list


@validate_call_safe(
    CustomErrorModel,
    report=True,
    reporter=reports.append,
    validate_return=True,
)
def int_noop(a: int) -> int:
    return a


success = int_noop(a=1)  # 1

assert success == 1
assert reports == snapshot(["int_noop received *(), **{'a': 1}", "int_noop -> int: 1"])

reports.clear()

failure = int_noop(a="A")  # CustomErrorModel(error_type='ValidationError', ...)

assert isinstance(failure, CustomErrorModel)
assert reports == snapshot(
    [
        "int_noop received *(), **{'a': 'A'}",
        "int_noop -> CustomErrorModel(error_type='ValidationError', error_details=[{'type': 'int_parsing', 'loc': ('a',), 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'A', 'url': 'https://errors.pydantic.dev/2.8/v/int_parsing'}])",
    ],
)
