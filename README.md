# validate-call-safe

`validate_call_safe` is a Python package that provides a safe, non-error-raising alternative to Pydantic's `validate_call` decorator.
It allows you to validate function arguments while gracefully handling validation errors through an error model,
inspired by effects handlers, returning them as structured data models instead of raising exceptions.

This therefore means that side effects ('erroring') are transformed into return types. This is
reflected in the type annotation of the decorator.

## Features

- Validates function arguments using Pydantic's existing `validate_call` decorator
- Returns a custom error model instead of raising exceptions when validation fails
- Configurable error information, including JSON representation and string representation of errors
- Written for Pydantic v2 (more specifically at version 2.8.2)

## Installation

```bash
pip install validate-call-safe
```

## Usage

### Basic Usage

Here we use an example model with **all** error fields: you may only want one of `error_json`,
`error_str` and `error_repr`.

```python
from pydantic import BaseModel, Json
from validate_call_safe import validate_call_safe

class CustomErrorModel(BaseModel):
    error_type: str
    error_json: Json | None = {}
    error_repr: str
    error_str: str

@validate_call_safe(CustomErrorModel)
def int_noop(a: int) -> int:
    return a

# Successful call
result = int_noop(a=1)
print(result)  # Output: 1

# Failed call
result = int_noop(a="A")
print(result)  # Output: CustomErrorModel instance
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
if isinstance(result, CustomErrorModel):
    print(f"Error: {result.error_type}")
```

## Ideas

- Restrict to ValidationError
- Specify non-ValidationError exceptions to capture
