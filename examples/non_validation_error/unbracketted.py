from validate_call_safe import validate_call_safe, ErrorModel


@validate_call_safe(validate_body=True, extra_exceptions=Exception)
def int_noop(a: int) -> int:
    raise ValueError("L")


invalid = int_noop(a="A")  # ErrorModel(error_type='ValidationError', ...)
failure = int_noop(a=1)  # ErrorModel(error_type='ValueError', ...)

assert isinstance(invalid, ErrorModel)
assert invalid.error_type == "ValidationError"
assert isinstance(failure, ErrorModel)
assert failure.error_type == "ValueError"
