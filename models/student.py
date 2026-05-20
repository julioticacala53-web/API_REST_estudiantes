from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StudentCreate(BaseModel):
    dni: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0)
    grade: float
    is_approved: bool

    @field_validator("dni")
    @classmethod
    def dni_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El DNI no puede estar vacío")
        return v

    @field_validator("name")
    @classmethod
    def name_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v


class StudentUpdate(BaseModel):
    dni: str | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1)
    age: int | None = Field(default=None, gt=0)
    grade: float | None = None
    is_approved: bool | None = None

    @field_validator("dni")
    @classmethod
    def dni_no_vacio(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El DNI no puede estar vacío")
        return v

    @field_validator("name")
    @classmethod
    def name_no_vacio(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v


class StudentResponse(BaseModel):
    id: int
    dni: str
    name: str
    age: int
    grade: float
    is_approved: bool
    created_at: datetime
    updated_at: datetime
