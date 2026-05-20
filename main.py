from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from database import close_database, get_database
from routes import students_router

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    await db["students"].create_index("id", unique=True)
    await db["students"].create_index("dni", unique=True)
    yield
    await close_database()


app = FastAPI(
    title="API REST de Estudiantes",
    description="Gestión de estudiantes con FastAPI y MongoDB",
    lifespan=lifespan,
)

app.include_router(students_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        msg = err.get("msg", "Valor inválido")
        if "greater than 0" in msg:
            msg = "La edad debe ser mayor que cero"
        elif "Field required" in msg or err["type"] == "missing":
            msg = "Campo obligatorio"
        elif "Value error" in msg:
            msg = msg.split(", ", 1)[-1] if ", " in msg else msg
        errors.append({"campo": field, "mensaje": msg})
    return JSONResponse(
        status_code=422,
        content={"detail": {"mensaje": "Error de validación", "errores": errors}},
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})
