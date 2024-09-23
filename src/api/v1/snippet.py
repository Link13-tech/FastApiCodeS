from fastapi import APIRouter, Depends, HTTPException
from auth.auth import get_current_user
import logging
from db.db import db_dependency
from models import User
from models.snippet import Snippet
from schemas.snippet import SnippetCreate, SnippetResponse
from typing import List
from sqlalchemy.future import select

snippet_router = APIRouter(prefix="/snippets", tags=['snippets'])
logger = logging.getLogger("my_app")


# Создание код-сниппета
@snippet_router.post("/", response_model=SnippetResponse)
async def create_snippet(snippet: SnippetCreate, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция create_snippet вызвана")
    logger.info(f"Создание сниппета для пользователя: {current_user.id} с заголовком: {snippet.title}")

    try:
        db_snippet = Snippet(**snippet.dict(), author_id=current_user.id)
        db.add(db_snippet)
        await db.commit()
        await db.refresh(db_snippet)

        logger.info(f"Сниппет создан с ID: {db_snippet.id}, UUID: {db_snippet.uuid}")
        return {
            "id": db_snippet.id,
            "uuid": db_snippet.uuid,
            "title": db_snippet.title,
            "code": db_snippet.code,
            "is_public": db_snippet.is_public,
        }
    except Exception as e:
        logger.error(f"Ошибка при создании сниппета: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании сниппета")


# Получение код-сниппета по ID
@snippet_router.get("/{snippet_id}", response_model=SnippetResponse)
async def get_snippet(snippet_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция get_snippet вызвана")
    logger.info(f"Запрос сниппета по ID: {snippet_id} для пользователя: {current_user.id}")

    db_snippet = await db.get(Snippet, snippet_id)
    if db_snippet is None:
        logger.warning(f"Сниппет с ID: {snippet_id} не найден")
        raise HTTPException(status_code=404, detail="Snippet not found")

    return {
        "id": db_snippet.id,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Получение код-сниппета по UUID
@snippet_router.get("/uuid/{snippet_uuid}", response_model=SnippetResponse)
async def get_snippet_by_uuid(snippet_uuid: str, db: db_dependency):
    logger.debug("Функция get_snippet_by_uuid вызвана")
    logger.info(f"Запрос сниппета по UUID: {snippet_uuid}")

    db_snippet = await db.execute(select(Snippet).where(Snippet.uuid == snippet_uuid))
    db_snippet = db_snippet.scalars().first()

    if db_snippet is None:
        logger.warning(f"Сниппет с UUID: {snippet_uuid} не найден")
        raise HTTPException(status_code=404, detail="Snippet not found")

    return {
        "id": db_snippet.id,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Получение всех код-сниппетов для авторизованного пользователя
@snippet_router.get("/", response_model=List[SnippetResponse])
async def get_snippets(db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция get_snippets вызвана")
    logger.info(f"Запрос всех сниппетов для пользователя: {current_user.id}")

    query = select(Snippet)
    result = await db.execute(query)
    snippets = result.scalars().all()

    return [
        {
            "id": snippet.id,
            "title": snippet.title,
            "code": snippet.code,
            "is_public": snippet.is_public,
        } for snippet in snippets
    ]


# Обновление код-сниппета
@snippet_router.put("/{snippet_id}", response_model=SnippetResponse)
async def update_snippet(snippet_id: int, snippet: SnippetCreate, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция update_snippet вызвана")
    logger.info(f"Обновление сниппета с ID: {snippet_id} для пользователя: {current_user.id}")

    db_snippet = await db.get(Snippet, snippet_id)
    if db_snippet is None or db_snippet.author_id != current_user.id:
        logger.warning(f"Сниппет с ID: {snippet_id} не найден или доступ запрещен")
        raise HTTPException(status_code=404, detail="Snippet not found or not authorized")

    for key, value in snippet.dict().items():
        setattr(db_snippet, key, value)

    await db.commit()
    await db.refresh(db_snippet)

    logger.info(f"Сниппет с ID: {snippet_id} обновлен")
    return {
        "id": db_snippet.id,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Удаление код-сниппета
@snippet_router.delete("/{snippet_id}", response_model=dict)
async def delete_snippet(snippet_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция delete_snippet вызвана")
    logger.info(f"Удаление сниппета с ID: {snippet_id} для пользователя: {current_user.id}")

    db_snippet = await db.get(Snippet, snippet_id)
    if db_snippet is None or db_snippet.author_id != current_user.id:
        logger.warning(f"Сниппет с ID: {snippet_id} не найден или доступ запрещен")
        raise HTTPException(status_code=404, detail="Snippet not found or not authorized")

    await db.delete(db_snippet)
    await db.commit()
    logger.info(f"Сниппет с ID: {snippet_id} удален")
    return {"detail": "Snippet deleted"}


# Генерация ссылки для общего доступа по UUID
@snippet_router.get("/share/{uuid}")
async def share_snippet(uuid: str, db: db_dependency):
    logger.debug("Функция share_snippet вызвана")
    logger.info(f"Генерация ссылки для сниппета с UUID: {uuid}")

    db_snippet = await db.execute(select(Snippet).where(Snippet.uuid == uuid))
    db_snippet = db_snippet.scalar_one_or_none()

    if db_snippet is None:
        logger.warning(f"Сниппет с UUID: {uuid} не найден")
        raise HTTPException(status_code=404, detail="Snippet not found")

    logger.debug(f"Ссылка для сниппета с UUID: {uuid} сгенерирована")
    return {"share_link": f"http://yourdomain.com/snippets/{db_snippet.uuid}"}