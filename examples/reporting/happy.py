from validate_call_safe import validate_call_safe
from inline_snapshot import snapshot

in_reports = []
in_out_reports = []


@validate_call_safe(report=True, reporter=in_reports.append)
def int_noop_in_validated(a: int) -> int:
    return 1


@validate_call_safe(report=True, reporter=in_out_reports.append, validate_return=True)
def int_noop_in_out_validated(a: int) -> int:
    return 1


ok_return = int_noop_in_validated(a=1)  # 1

assert ok_return == 1
assert in_reports == snapshot(["int_noop_in_validated received *(), **{'a': 1}"])

ok_return = int_noop_in_out_validated(a=1)  # 1

assert ok_return == 1
assert in_out_reports == snapshot(
    [
        "int_noop_in_out_validated received *(), **{'a': 1}",
        "int_noop_in_out_validated -> int: 1",
    ],
)
