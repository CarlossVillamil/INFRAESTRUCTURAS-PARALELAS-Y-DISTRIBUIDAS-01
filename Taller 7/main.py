import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@postgres-service.taller7-app.svc.cluster.local:2392/demo"
)

class Student(BaseModel):
    name: str
    lastName: str
    age: int
    state: bool

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.on_event("startup")
def startup():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                last_name VARCHAR(50),
                age INT,
                state BOOLEAN
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creando tabla: {e}")

@app.get("/init-db")
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                last_name VARCHAR(50),
                age INT,
                state BOOLEAN
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Tabla student creada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/student/save")
def create_student(student: Student):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO student (name, last_name, age, state) VALUES (%s, %s, %s, %s) RETURNING id, name, last_name AS \"lastName\", age, state;",
            (student.name, student.lastName, student.age, student.state)
        )
        new_student = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return new_student
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo/student")
def get_student_by_id(id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, name, last_name AS \"lastName\", age, state FROM student WHERE id = %s;", (id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/readiness")
@app.get("/health/liveness")
def health_check():
    return {"status": "UP"}