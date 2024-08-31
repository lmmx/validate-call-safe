from pydantic import BaseModel

from .details import ErrorDetails


class ErrorModel(BaseModel):
    error_type: str
    error_details: list[ErrorDetails]
    error_str: str
    error_repr: str
    error_tb: str
