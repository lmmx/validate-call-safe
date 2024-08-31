# validate-call-safe

`validate_call_safe` is a safe, non-error-raising alternative to Pydantic's `validate_call` decorator.
It allows you to validate function arguments while gracefully handling validation errors through an error model,
inspired by effects handlers, returning them as structured data models instead of raising exceptions.

This therefore means that side effects ('erroring') are transformed into return types.
The return type annotation of a decorated function is modified accordingly as the `Union` of the
existing return type with the provided error model type.

## Features

- Validates function arguments using Pydantic's existing `validate_call` decorator
- Returns a custom error model instead of raising exceptions when validation fails
- Configurable error information, including tracebacks
- Compatible with Pydantic v2, tested back to version 2.0.1
- Optional model config and return value validation, as in the original Pydantic `@validate_call` decorator
- Option to validate function body execution (`validate_body`)
- Option to specify additional exceptions to capture when validating body execution (`extra_exceptions`)

## Installation

```bash
pip install validate-call-safe
```

## Usage

### Basic Usage

The simplest possible usage is as a direct alternative to `@validate_call`:

```py
from validate_call_safe import validate_call_safe

def foo(a: int) -> None:
    return a

value = foo(a="bar")  # ErrorModel(error_type='ValidationError', ...)
```

Instead of raising the `ValidationError`, it's captured in a Pydantic model,
specifically an instance of [`ErrorModel`][EM]. Its fields are:

- `error_type`
- `error_details`
- `error_str`
- `error_repr`
- `error_tb`

[EM]: https://github.com/lmmx/validate-call-safe/blob/master/src/validate_call_safe/errors/model.py

### Decorator Forms

`validate_call_safe` offers flexibility in specifying the error model:

1. No brackets:
   ```python
   @validate_call_safe
   def int_noop(a: int) -> int:
       return a
   ```

2. Empty brackets:
   ```python
   @validate_call_safe()
   def int_noop(a: int) -> int:
       return a
   ```

3. Custom error model:
   ```python
   @validate_call_safe(CustomErrorModel)
   def int_noop(a: int) -> int:
       return a
   ```

4. With validation parameters:
   ```python
   @validate_call_safe(validate_return=True)
   def int_noop(a: int) -> int:
       return a
   ```

### Custom Error Models

To get more concise error model objects, you might want to override the default `ErrorModel` class
with your own, and just include the fields you want.

For example:

```python
from pydantic import BaseModel
from validate_call_safe import validate_call_safe, ErrorDetails

class MyErrorModel(BaseModel):
    error_type: str
    error_details: list[ErrorDetails]

@validate_call_safe(MyErrorModel)
def int_noop(a: int) -> int:
    return a

success = int_noop(a=1)  # 1
failure = int_noop(a="A")  # MyErrorModel(error_type='ValidationError', ...)
```

### Return Value Validation

You can enable return value validation using the `validate_return` parameter,
which is passed along to the original Pydantic `@validate_call` decorator flag of the same name:

```python
@validate_call_safe(validate_return=True)
def int_noop(a: int) -> int:
    return "foo"  # This will cause a validation error

result = int_noop(a=1)  # ErrorModel(error_type='ValidationError', ...)
```

### Function Body Validation

To capture exceptions that occur within the function body, use the `validate_body` parameter:

```python
@validate_call_safe(validate_body=True)
def failing_function(name: str):
    raise ValueError(f"Invalid name: {name}")

result = failing_function("John")  # ErrorModel(error_type='ValueError', ...)
```

### Capturing Additional Exceptions

You can specify additional exceptions to capture using the `extra_exceptions` parameter:

```python
@validate_call_safe(validate_body=True, extra_exceptions=(NameError, TypeError))
def risky_function(a: int):
    if a == 1:
        raise NameError("Name not found")
    elif a == 2:
        raise TypeError("Type mismatch")
    return a

result1 = risky_function(1)  # ErrorModel(error_type='NameError', ...)
result2 = risky_function(2)  # ErrorModel(error_type='TypeError', ...)
result3 = risky_function(3)  # 3
```

The `extra_exception` default is `Exception` (enough for most user-level exceptions,
but will not stop `sys.exit` calls for which you'd need to capture `BaseException`).

Specifying it is useful to narrow the handled exception types, as is good practice
with regular `try`/`except` exception handling.

## Comparison with `validate_call`

With `validate_call_safe` you don't have to catch the expected `ValidationError` from Pydantic's `validate_call`:

```python
from pydantic import validate_call

@validate_call
def unsafe_int_noop(a: int) -> int:
    return a

try:
    unsafe_int_noop(a="A")
except ValidationError as e:
    print(f"Error: {e}")
else:
    ...  # Regular business logic here
```

Using `validate_call_safe`:

```py
from validate_call_safe import validate_call_safe, ErrorModel

@validate_call_safe:
def safe_int_noop(a: int) -> int:
    return a

result = safe_int_noop(a="A")
match result:
    case ErrorModel():
        print(f"Error: {result.error_repr}")
    case int():
        ...  # Regular business logic here
```

- These both do the same thing and have the same number of lines
- In the safe form, you get structured error objects to work with (including tracebacks)
- You can trivially extend the safety level to more exception types with `validate_body`
- The side effects of the safe form may be easier to reason about for you (I think they are)

## Extensions/ideas

- Multiple model types for different error types with tagged union on the `error_type` field name?
