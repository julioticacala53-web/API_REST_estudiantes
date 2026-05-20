# API REST de Estudiantes

API para gestión de estudiantes con **FastAPI**, **MongoDB** y fragmento HTML con **htmx**.

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- MongoDB en ejecución local (`mongodb://localhost:27017`)

## Instalación

```bash
uv sync
cp .env.example .env
```

## Ejecución

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000/docs
- Página con tabla htmx: http://localhost:8000/

## Variables de entorno

| Variable       | Descripción              | Por defecto                    |
|----------------|--------------------------|--------------------------------|
| `MONGODB_URI`  | URI de conexión MongoDB  | `mongodb://localhost:27017`    |
| `MONGODB_DB`   | Nombre de la base de datos | `estudiantes_db`             |

## Endpoints

| Método | Ruta                 | Descripción                          |
|--------|----------------------|--------------------------------------|
| POST   | `/students`          | Crear estudiante                     |
| GET    | `/students`          | Listar todos                           |
| GET    | `/students/{id}`     | Obtener por ID                         |
| PUT    | `/students/{id}`     | Actualizar (solo campos enviados)    |
| DELETE | `/students/{id}`     | Eliminar (200 + JSON)                  |
| POST   | `/students/bulk`     | Creación masiva (todo o nada)          |
| GET    | `/students/average`  | Promedio de notas `{"promedio": ...}`  |
| GET    | `/students/table`    | Fragmento HTML de la tabla             |
| GET    | `/`                  | `index.html` con carga htmx            |

## Ejemplo de creación

```bash
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{
    "dni": "12345678",
    "name": "Juan Pérez",
    "age": 20,
    "grade": 15.5,
    "is_approved": true
  }'
```

## Estructura del proyecto

```
├── main.py
├── pyproject.toml
├── database/
├── models/
├── routes/
├── services/
└── templates/
    ├── index.html
    └── partials/
        └── students_table.html
```
