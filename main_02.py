import logging
import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date

logging.basicConfig(filename='log_main/main_02_log.log',
                    level=logging.INFO,
                    encoding='utf-8',
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///task2_database.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("surname", sqlalchemy.String(32)),
    sqlalchemy.Column("date", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("address", sqlalchemy.String(128)),
)
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
app = FastAPI()


# для создания
class UserIn(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    surname: str = Field(min_length=2, max_length=32)
    date: Optional[date]
    email: EmailStr
    address: str = Field(max_length=128)
    logger.info(f'Отработала модель UserIn')


# для вызова
class User(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=32)
    surname: str = Field(min_length=2, max_length=32)
    date: Optional[date]
    email: EmailStr
    address: str = Field(max_length=128)
    logger.info(f'Отработала модель User')


# Добавление пользователя в базу данных
@app.post("/users/", response_model=UserIn)
async def create_user(user: UserIn):
    query = users.insert().values(**user.dict())
    last_record_id = await database.execute(query)
    logger.info(f"Отработал post запрос (Добавление {user.name} в базу данных)")
    return {**user.dict(), "id": last_record_id}


# Получение списка всех пользователей в базе данных
@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    logger.info(f"Отработал get запрос (Получен список всех пользователей)")
    return await database.fetch_all(query)


# Получение пользователя по ID
@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    logger.info(f"Отработал get запрос (Получение пользователя по {user_id = })\n{database.fetch_one(query)}")
    return await database.fetch_one(query)


# Обновление пользователя по ID
@app.put("/users/{user_id}", response_model=UserIn)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    logger.info(f"Отработал get запрос (Обновление пользователя по ID {user_id = })")
    return {**new_user.dict(), "id": user_id}


# Удаление пользователя по ID
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    logger.info(f"Отработал delete запрос (пользователь с {user_id} удален")
    return {'message': 'User deleted'}


if __name__ == '__main__':
    uvicorn.run('main_02:app', host="127.0.0.1", port=8000)


