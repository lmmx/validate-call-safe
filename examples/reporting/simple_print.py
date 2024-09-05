from validate_call_safe import validate_call_safe


@validate_call_safe(report=True)
def foo(a: int) -> int:
    return a


assert foo(1) == 1
# prints "foo -> int: 1"


@validate_call_safe(report=True, validate_return=True)
def bar(a: int) -> int:
    return 1


assert bar(1) == 1
# prints "bar -> int: 1"
