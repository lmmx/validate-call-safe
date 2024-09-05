from validate_call_safe import validate_call_safe, ErrorModel
from inline_snapshot import snapshot


@validate_call_safe()
def int_noop(a: int) -> int:
    return a


success = int_noop(a=1)  # 1

assert success == 1

failure = int_noop(a="A")  # ErrorModel(error_type='ValidationError', ...)
assert isinstance(failure, ErrorModel)
assert failure.model_dump() == snapshot(
    {
        "error_type": "ValidationError",
        "error_details": [
            {
                "type": "int_parsing",
                "loc": ("a",),
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "A",
            },
        ],
        "error_str": """\
1 validation error for int_noop
a
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='A', input_type=str]
    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\
""",
        "error_repr": """\
1 validation error for int_noop
a
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='A', input_type=str]
    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\
""",
        "error_tb": """\
Traceback (most recent call last):
  File "/home/louis/lab/validate-call-safe/src/validate_call_safe/decorator.py", line 140, in wrapper
    ret = validated_func(*args, **kwargs)
  File "/home/louis/miniconda3/envs/validate-call-safe/lib/python3.10/site-packages/pydantic/validate_call_decorator.py", line 60, in wrapper_function
    return validate_call_wrapper(*args, **kwargs)
  File "/home/louis/miniconda3/envs/validate-call-safe/lib/python3.10/site-packages/pydantic/_internal/_validate_call.py", line 96, in __call__
    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))
pydantic_core._pydantic_core.ValidationError: 1 validation error for int_noop
a
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='A', input_type=str]
    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing
""",
    },
)
