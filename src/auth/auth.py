from calendar import timegm
from datetime import timedelta, datetime
from typing import Optional, Annotated

import bcrypt
from asyncpg import UniqueViolationError
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status

from core.config import settings
from db.db import db_dependency
from models import User
from schemas.user import UserRegisterSchema, UserLoginSchema


auth_router = APIRouter(prefix="/auth", tags=['auth'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

# Секретная фраза для генерации и валидации токенов
JWT_SECRET = settings.jwt_secret  # your_super_secret
# Алгоритм хеширования
ALGORITHM = settings.algorithm  # 'HS256'
# Контекст для валидации и хеширования
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Генерация соли
def generate_salt():
    return bcrypt.gensalt().decode("utf-8")


# Хэширование пароля с использованием соли
def hash_password(password: str, salt: str):
    return bcrypt_context.hash(password + salt)


# Создание нового токена
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    # копируем исходные данные, чтобы случайно их не испортить
    to_encode = data.copy()

    # устанавливаем временной промежуток жизни токена
    expire = timegm((datetime.now() + expires_delta).utctimetuple())

    # добавляем время смерти токена
    to_encode.update({"exp": expire})

    # генерируем токен из данных, секрета и алгоритма
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


# Регистрация пользователя
async def reg_user(user_data: UserRegisterSchema, db: db_dependency):
    user_salt: str = generate_salt()
    try:
        create_user_statement: User = User(
            **user_data.model_dump(exclude={'password'}),  # распаковываем объект пользователя, исключая пароль
            salt=user_salt,
            hashed_password=hash_password(user_data.password, user_salt)
        )
        # создаём пользователя в базе данных
        db.add(create_user_statement)
        await db.commit()
        return {"response": "User created successfully"}
    except UniqueViolationError:
        # если возникает ошибка UniqueViolationError, то считаем, что пользователь с такими данными уже есть
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with such credentials already exists')
    except Exception as ex:
        raise ex


# Аутентификация пользователя
async def authenticate_user(login_data: UserLoginSchema, db: db_dependency):
    # делаем SELECT-запрос в базу данных для нахождения пользователя по email
    result = await db.execute(select(User)
                              .where(User.email == login_data.email))
    user: Optional[User] = result.scalars().first()
    # пользователь будет авторизован, если он зарегистрирован и ввёл корректный пароль
    if not user:
        return False
    if not bcrypt_context.verify(login_data.password + user.salt, user.hashed_password):
        return False
    return user


async def get_current_user(db: db_dependency, token: str = Depends(oauth2_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодируем токен и получаем email из поля 'sub'
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.algorithm])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ищем пользователя в базе данных по email
    result = await db.execute(select(User).where(User.email == user_email))
    user: Optional[User] = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user
user_dependency = Annotated[User, Depends(get_current_user)]
