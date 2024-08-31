from validate_call_safe import validate_call_safe


@validate_call_safe
def failing(name: str):
    raise NameError(name)


try:
    failing(name="foo")
except NameError:
    pass  # Due to body error
else:
    raise ValueError("Body error should throw")
