import logging
import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr, constr
from sqlalchemy import create_engine, ForeignKey
from typing import List
from datetime import datetime

logging.basicConfig(filename='log_main/main_06_log.log',
                    level=logging.INFO,
                    encoding='utf-8',
                    format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///main_06_database.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("product_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("description", sqlalchemy.String(200)),
    sqlalchemy.Column("price", sqlalchemy.Float(decimal_return_scale=2)),
)


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("surname", sqlalchemy.String(32)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(16)),
)


orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("id_users", sqlalchemy.Integer, ForeignKey("users.user_id"), nullable=False),
    sqlalchemy.Column("id_products", sqlalchemy.Integer,  ForeignKey("products.product_id"), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
    sqlalchemy.Column("status", sqlalchemy.Boolean, default=False)
)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)

app = FastAPI()


# для создания и валидации объектов таблицы products
class ProductsIn(BaseModel):
    name: str = Field(title="Name", min_length=2, max_length=32)
    description: str = Field(title="Description", max_length=300, default=None)
    price: float = Field(title="price", gt=0.00, le=100000.00)


# для вызова и валидации объектов с таблицы product
class Products(BaseModel):
    product_id: int
    name: str = Field(title="Name", min_length=2, max_length=32)
    description: str = Field(title="Description", max_length=300, default=None)
    password: constr(min_length=3, max_length=16)


# для создания и валидации объектов таблицы users
class UserIn(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    surname: str = Field(min_length=2, max_length=32)
    email: EmailStr()
    password: constr(min_length=3, max_length=16)


# для вызова и валидации объектов с таблицы users
class User(BaseModel):
    user_id: int
    name: str = Field(min_length=2, max_length=32)
    surname: str = Field(min_length=2, max_length=32)
    email: str = EmailStr()
    password: str = constr(min_length=3, max_length=16)


# для создания и валидации объектов таблицы orders
class OrderIn(BaseModel):
    id_users: int = Field(ForeignKey("users.user_id"))
    id_products: int = Field(ForeignKey("products.product_id"))
    status: bool = Field(title='статус выполнения задачи', default=False)


# для вызова и валидации объектов с таблицы orders
class Order(BaseModel):
    id: int
    id_users: int = Field(ForeignKey("users.user_id"))
    id_products: int = Field(ForeignKey("products.product_id"))
    status: bool = Field(title='статус выполнения задачи', default=False)


""" Start Product """


# Добавление новых товаров
@app.post("/product_in/", response_model=ProductsIn)
async def create_user(product: ProductsIn):
    query = products.insert().values(**product.dict())
    last_record_id = await database.execute(query)
    logger.info(f"Отработал post запрос (Добавление {product.name} в базу данных)")
    return {**product.dict(), "id": last_record_id}


# Получение списка всех товаров
@app.get("/products/", response_model=List[Products])
async def read_users():
    query = products.select()
    logger.info(f"Отработал get product запрос (Получен список всех пользователей)")
    return await database.fetch_all(query)


# Получение товара по ID
@app.get("/products/{product_id}", response_model=Products)
async def read_user(product_id: int):
    query = products.select().where(products.c.product_id == product_id)
    logger.info(f"Отработал get products запрос (Получение пользователя по {product_id = }")
    return await database.fetch_one(query)


# Обновление товара по ID
@app.put("/products/{product_id}", response_model=ProductsIn)
async def update_user(product_id: int, new_product: ProductsIn):
    query = products.update().where(products.c.product_id == product_id).values(**new_product.dict())
    await database.execute(query)
    logger.info(f"Отработал get product запрос (Обновление пользователя по ID {product_id = })")
    return {**new_product.dict(), "id": product_id}


# Удаление товара по ID
@app.delete("/products/{product_id}")
async def delete_user(product_id: int):
    query = products.delete().where(products.c.product_id == product_id)
    await database.execute(query)
    logger.info(f"Отработал delete product запрос (пользователь с {product_id} удален")
    return {'message': 'Product deleted'}


""" Finish Products """
""" Start Users """


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
    query = users.select().where(users.c.user_id == user_id)
    logger.info(f"Отработал get запрос (Получение пользователя по {user_id = })")
    return await database.fetch_one(query)


# Обновление пользователя по ID
@app.put("/users/{user_id}", response_model=UserIn)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.user_id == user_id).values(**new_user.dict())
    await database.execute(query)
    logger.info(f"Отработал get запрос (Обновление пользователя по ID {user_id = })")
    return {**new_user.dict(), "id": user_id}


# Удаление пользователя по ID
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.user_id == user_id)
    await database.execute(query)
    logger.info(f"Отработал delete запрос (пользователь с {user_id} удален")
    return {'message': 'User delete'}


""" Finish Product """
""" Start Order """


# Добавление заказа в базу данных
@app.post("/order/", response_model=OrderIn)
async def create_order(order: OrderIn):
    query = orders.insert().values(**order.dict())
    last_record_id = await database.execute(query)
    logger.info(f"Отработал post запрос order")
    return {**order.dict(), "id": last_record_id}


# Получение списка всех заказов в базе данных
@app.get("/order/", response_model=List[Order])
async def read_order():
    query = orders.select()
    logger.info(f"Отработал get запрос (Получен список всех пользователей)")
    return await database.fetch_all(query)


# Получение заказов по ID
@app.get("/order/{order_id}", response_model=Order)
async def read_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    logger.info(f"Отработал get запрос (Получение пользователя по {order_id = })")
    return await database.fetch_one(query)


# Обновление заказа по ID
@app.put("/order/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.order_id == order_id).values(**new_order.dict())
    await database.execute(query)
    logger.info(f"Отработал get запрос (Обновление пользователя по ID {order_id = })")
    return {**new_order.dict(), "id": order_id}


# Удаление заказа по ID
@app.delete("/order/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.order_id == order_id)
    await database.execute(query)
    logger.info(f"Отработал delete запрос (пользователь с {order_id} удален")
    return {'message': 'Order deleted'}


if __name__ == '__main__':
    uvicorn.run("main_06:app", host='127.0.0.1', port=8000)
