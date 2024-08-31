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

Here's a basic example using a custom error model:

```python
from pydantic import BaseModel
from validate_call_safe import validate_call_safe, ErrorDetails

class CustomErrorModel(BaseModel):
    error_type: str
    error_details: list[ErrorDetails]
    error_repr: str
    error_tb: str

@validate_call_safe(CustomErrorModel)
def int_noop(a: int) -> int:
    return a

success = int_noop(a=1)  # 1
failure = int_noop(a="A")  # CustomErrorModel(error_type='ValidationError', ...)
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

### Error Model Configuration

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

## Comparison with `validate_call`

With `validate_call_safe` you don't have to catch the expected `ValidationError` from Pydantic's `validate_call`:

```python
# Using validate_call
from pydantic import validate_call

@validate_call
def unsafe_int_noop(a: int) -> int:
    return a

try:
    unsafe_int_noop(a="A")
except ValidationError as e:
    print(f"Error: {e}")

# Using validate_call_safe
from validate_call_safe import validate_call_safe

@validate_call_safe(CustomErrorModel)
def safe_int_noop(a: int) -> int:
    return a

result = safe_int_noop(a="A")
match result:
    case CustomErrorModel():
        print(f"Error: {result.error_type}")
    case int():
        ...  # Regular business logic here
```
