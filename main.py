import jwt
import psycopg2
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from config import SECRET_KEY,DB_HOST, DB_PASS, DB_USER, DB_NAME, DB_PORT
from pydantic import BaseModel


class InputCode(BaseModel):
    code: str


app = FastAPI()
security = HTTPBearer()


connection = psycopg2.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=DB_PORT,
)
connection.autocommit = True


@app.on_event("startup")
async def startup_event():
    print("Сервер запущен")


@app.on_event("shutdown")
async def shutdown_event():
    connection.close()
    print("Сервер остановлен")


@app.post("/login")
async def auth_user(item: InputCode):
    code = item.code

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM users WHERE code = %s;""",
                (code,)
            )
            data = cursor.fetchone()

            if data:
                user_data = data
                payload = {"id": user_data[0], "username": user_data[1], "tg_id": user_data[2]}
                secret_key = SECRET_KEY
                token = jwt.encode(payload, secret_key, algorithm="HS256")
                return {"token": token}
            else:
                return {"error": "Пользователь не найден"}
    except Exception as ex:
        print("[INFO] Ошибка при работе с PostgreSQL:", ex)

