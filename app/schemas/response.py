from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    source: Optional[str] = None

    @classmethod
    def success_response(cls, data: T) -> "ApiResponse[T]":
        return cls(success=True, data=data, error=None, source=None)

    @classmethod
    def error_response(cls, error: str) -> "ApiResponse[T]":
        return cls(success=False, data=None, error=error, source="ERROR")