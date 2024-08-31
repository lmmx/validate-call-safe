"""Ported from pydantic_core

https://github.com/pydantic/pydantic-core/blob/d93e6b15419bcefaf0e952591c3d9e1901171181/python/pydantic_core/__init__.py
"""

import sys
from typing import Any

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired
else:
    from typing import NotRequired

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

__all__ = ("ErrorDetails",)


class ErrorDetails(TypedDict):
    type: str
    loc: tuple[str | int, ...]
    msg: str
    input: Any
    ctx: NotRequired[dict[str, Any]]
