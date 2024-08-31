from validate_call_safe import ErrorModel, validate_call_safe

@validate_call_safe(validate_body=True, extra_exceptions=NameError)
def failing(name: str):
    raise NameError(name)

failure = failing(name="foo")
assert isinstance(failure, ErrorModel)
assert failure.error_type == "NameError"
