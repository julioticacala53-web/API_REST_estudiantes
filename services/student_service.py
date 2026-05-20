from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from models.student import StudentCreate, StudentUpdate, utc_now

COLLECTION = "students"
COUNTERS = "counters"


def _doc_to_response(doc: dict) -> dict:
    return {
        "id": doc["id"],
        "dni": doc["dni"],
        "name": doc["name"],
        "age": doc["age"],
        "grade": doc["grade"],
        "is_approved": doc["is_approved"],
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
    }


async def _next_id(db: AsyncIOMotorDatabase) -> int:
    result = await db[COUNTERS].find_one_and_update(
        {"_id": COLLECTION},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return result["seq"]


async def _dni_exists(db: AsyncIOMotorDatabase, dni: str, exclude_id: int | None = None) -> bool:
    query: dict = {"dni": dni}
    if exclude_id is not None:
        query["id"] = {"$ne": exclude_id}
    doc = await db[COLLECTION].find_one(query)
    return doc is not None


async def create_student(db: AsyncIOMotorDatabase, data: StudentCreate) -> dict:
    if await _dni_exists(db, data.dni):
        raise HTTPException(status_code=400, detail=f"Ya existe un estudiante con el DNI {data.dni}")

    now = utc_now()
    student_id = await _next_id(db)
    doc = {
        "id": student_id,
        "dni": data.dni,
        "name": data.name,
        "age": data.age,
        "grade": data.grade,
        "is_approved": data.is_approved,
        "created_at": now,
        "updated_at": now,
    }
    await db[COLLECTION].insert_one(doc)
    return _doc_to_response(doc)


async def get_all_students(db: AsyncIOMotorDatabase) -> list[dict]:
    cursor = db[COLLECTION].find().sort("id", 1)
    return [_doc_to_response(doc) async for doc in cursor]


async def get_student_by_id(db: AsyncIOMotorDatabase, student_id: int) -> dict:
    doc = await db[COLLECTION].find_one({"id": student_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return _doc_to_response(doc)


async def update_student(db: AsyncIOMotorDatabase, student_id: int, data: StudentUpdate) -> dict:
    doc = await db[COLLECTION].find_one({"id": student_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    if "dni" in updates and await _dni_exists(db, updates["dni"], exclude_id=student_id):
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un estudiante con el DNI {updates['dni']}",
        )

    updates["updated_at"] = utc_now()
    await db[COLLECTION].update_one({"id": student_id}, {"$set": updates})
    updated = await db[COLLECTION].find_one({"id": student_id})
    return _doc_to_response(updated)


async def delete_student(db: AsyncIOMotorDatabase, student_id: int) -> dict:
    result = await db[COLLECTION].delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"mensaje": "Estudiante eliminado correctamente", "id": student_id}


async def bulk_create_students(db: AsyncIOMotorDatabase, students: list[StudentCreate]) -> list[dict]:
    if not students:
        raise HTTPException(status_code=400, detail="La lista de estudiantes no puede estar vacía")

    dnis = [s.dni for s in students]
    if len(dnis) != len(set(dnis)):
        raise HTTPException(status_code=400, detail="Hay DNIs duplicados en la solicitud")

    for dni in dnis:
        if await _dni_exists(db, dni):
            raise HTTPException(status_code=400, detail=f"Ya existe un estudiante con el DNI {dni}")

    now = utc_now()
    docs: list[dict] = []
    for data in students:
        student_id = await _next_id(db)
        docs.append(
            {
                "id": student_id,
                "dni": data.dni,
                "name": data.name,
                "age": data.age,
                "grade": data.grade,
                "is_approved": data.is_approved,
                "created_at": now,
                "updated_at": now,
            }
        )

    try:
        await db[COLLECTION].insert_many(docs)
    except Exception:
        for doc in docs:
            await db[COLLECTION].delete_one({"id": doc["id"]})
        raise HTTPException(status_code=500, detail="Error al crear estudiantes en lote")

    return [_doc_to_response(doc) for doc in docs]


async def get_grade_average(db: AsyncIOMotorDatabase) -> float:
    pipeline = [{"$group": {"_id": None, "promedio": {"$avg": "$grade"}}}]
    result = await db[COLLECTION].aggregate(pipeline).to_list(1)
    if not result:
        return 0.0
    return round(result[0]["promedio"], 2)
