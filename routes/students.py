from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import get_database
from models.student import StudentCreate, StudentResponse, StudentUpdate
from services import student_service

router = APIRouter(prefix="/students", tags=["estudiantes"])
templates = Jinja2Templates(directory="templates")


def get_db() -> AsyncIOMotorDatabase:
    return get_database()


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(
    data: StudentCreate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    return await student_service.create_student(db, data)


@router.get("", response_model=list[StudentResponse])
async def list_students(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    return await student_service.get_all_students(db)


@router.post("/bulk", response_model=list[StudentResponse], status_code=201)
async def bulk_create_students(
    students: list[StudentCreate],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    return await student_service.bulk_create_students(db, students)


@router.get("/average")
async def grade_average(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]):
    promedio = await student_service.get_grade_average(db)
    return {"promedio": promedio}


@router.get("/table", response_class=HTMLResponse)
async def students_table(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    students = await student_service.get_all_students(db)
    return templates.TemplateResponse(
        request=request,
        name="partials/students_table.html",
        context={"students": students},
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    return await student_service.get_student_by_id(db, student_id)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    return await student_service.update_student(db, student_id, data)


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
):
    return await student_service.delete_student(db, student_id)
