from validate_call_safe import validate_call_safe, ErrorModel
from inline_snapshot import snapshot

reports = []


@validate_call_safe(
    report=True,
    reporter=reports.append,
    validate_return=True,
)
def botched_ret(a: int) -> int:
    return "foo"


bad_input = botched_ret(a="A")  # ErrorModel(error_type='ValidationError', ...)

assert isinstance(bad_input, ErrorModel)
assert bad_input.error_details[0]["input"] == "A"
assert bad_input.error_details[0]["loc"] == ("a",)

assert reports == snapshot(
    [
        "botched_ret received *(), **{'a': 'A'}",
        "botched_ret -> ErrorModel(error_type='ValidationError', error_details=[{'type': 'int_parsing', 'loc': ('a',), 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'A'}], error_str=\"1 validation error for botched_ret\\na\\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='A', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\", error_repr=\"1 validation error for botched_ret\\na\\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='A', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\", error_tb='Traceback (most recent call last):\\n  File \"/home/louis/lab/validate-call-safe/src/validate_call_safe/decorator.py\", line 140, in wrapper\\n    ret = validated_func(*args, **kwargs)\\n  File \"/home/louis/miniconda3/envs/validate-call-safe/lib/python3.10/site-packages/pydantic/validate_call_decorator.py\", line 60, in wrapper_function\\n    return validate_call_wrapper(*args, **kwargs)\\n  File \"/home/louis/miniconda3/envs/validate-call-safe/lib/python3.10/site-packages/pydantic/_internal/_validate_call.py\", line 96, in __call__\\n    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))\\npydantic_core._pydantic_core.ValidationError: 1 validation error for botched_ret\\na\\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value=\\'A\\', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\\n')",
    ],
)

reports.clear()

bad_return = botched_ret(a=1)  # ErrorModel(error_type='ValidationError', ...)

assert isinstance(bad_return, ErrorModel)
assert bad_return.error_details[0]["input"] == "foo"
assert bad_return.error_details[0]["loc"] == tuple()
assert reports == snapshot(
    [
        "botched_ret received *(), **{'a': 1}",
        "botched_ret -> ErrorModel(error_type='ValidationError', error_details=[{'type': 'int_parsing', 'loc': (), 'msg': 'Input should be a valid integer, unable to parse string as an integer', 'input': 'foo'}], error_str=\"1 validation error for botched_ret\\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='foo', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\", error_repr=\"1 validation error for botched_ret\\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='foo', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\", error_tb='Traceback (most recent call last):\\n  File \"/home/louis/lab/validate-call-safe/src/validate_call_safe/decorator.py\", line 140, in wrapper\\n    ret = validated_func(*args, **kwargs)\\n  File \"/home/louis/miniconda3/envs/validate-call-safe/lib/python3.10/site-packages/pydantic/validate_call_decorator.py\", line 60, in wrapper_function\\n    return validate_call_wrapper(*args, **kwargs)\\n  File \"/home/louis/miniconda3/envs/validate-call-safe/lib/python3.10/site-packages/pydantic/_internal/_validate_call.py\", line 98, in __call__\\n    return self.__return_pydantic_validator__(res)\\npydantic_core._pydantic_core.ValidationError: 1 validation error for botched_ret\\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value=\\'foo\\', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/int_parsing\\n')",
    ],
)
