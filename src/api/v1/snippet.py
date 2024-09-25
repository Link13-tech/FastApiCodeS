from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_

from sqlalchemy.orm import joinedload

from auth.auth import get_current_user
import logging

from core.config import settings
from db.db import db_dependency
from models import User
from models.snippet import Snippet
from schemas.snippet import SnippetCreate, SnippetResponse, SnippetDisplay
from sqlalchemy.future import select

snippet_router = APIRouter(prefix="/snippets", tags=['snippets'])
logger = logging.getLogger("my_app")


# Создание код-сниппета
@snippet_router.post("/create_snippet", response_model=SnippetDisplay, name="Создать сниппет")
async def create_snippet(snippet: SnippetCreate, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция create_snippet вызвана")
    logger.info(f"Создание сниппета для пользователя: {current_user.id} с заголовком: {snippet.title}")

    try:
        db_snippet = Snippet(**snippet.dict(), author_id=current_user.id)
        db.add(db_snippet)
        await db.commit()
        await db.refresh(db_snippet)

        logger.info(f"Сниппет создан с UUID: {db_snippet.uuid}")
        return {
            "uuid": str(db_snippet.uuid),
            "title": db_snippet.title,
            "code": db_snippet.code,
            "author_name": db_snippet.author.name,
            "is_public": db_snippet.is_public,
            "share_link": f"http://{settings.app_host}:{settings.app_port}/snippets/get_snippet/{db_snippet.uuid}"
        }
    except Exception as e:
        logger.error(f"Ошибка при создании сниппета: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании сниппета")


# Получение код-сниппета по UUID
@snippet_router.get("/get_snippet/{snippet_uuid}", response_model=SnippetResponse, name="Получить сниппет по UUID")
async def get_snippet_by_uuid(snippet_uuid: str, db: db_dependency):
    logger.debug("Функция get_snippet_by_uuid вызвана")
    logger.info(f"Запрос сниппета по UUID: {snippet_uuid}")

    db_snippet = await db.execute(
        select(Snippet).options(joinedload(Snippet.author)).where(Snippet.uuid == snippet_uuid)
    )
    db_snippet = db_snippet.scalars().first()

    if db_snippet is None:
        logger.warning(f"Сниппет с UUID: {snippet_uuid} не найден")
        raise HTTPException(status_code=404, detail="Snippet not found")

    return {
        "uuid": str(db_snippet.uuid),
        "title": db_snippet.title,
        "code": db_snippet.code,
        "author_name": db_snippet.author.name,
        "is_public": db_snippet.is_public,
    }


# Получение всех публичных код-сниппетов
@snippet_router.get("/all_snippets", response_model=List[SnippetResponse], name="Получить все сниппеты")
async def get_all_snippets(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    logger.debug("Функция get_all_snippets вызвана")
    logger.info(f"Запрос всех сниппетов пользователем: {current_user.id}")

    try:
        # Получаем публичные сниппеты
        public_query = select(Snippet).options(joinedload(Snippet.author)).filter(Snippet.is_public.is_(True))
        public_result = await db.execute(public_query)
        public_snippets = public_result.scalars().all()

        # Получаем личные сниппеты текущего пользователя, которые не публичные
        personal_query = select(Snippet).options(joinedload(Snippet.author)).filter(
            Snippet.author_id == current_user.id,
            Snippet.is_public.is_(False)
        )
        personal_result = await db.execute(personal_query)
        personal_snippets = personal_result.scalars().all()

        # Объединяем списки, используя множество для уникальности
        snippets_set = {snippet.uuid: snippet for snippet in public_snippets + personal_snippets}

    except Exception as e:
        logger.error(f"Ошибка при получении всех сниппетов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении всех сниппетов")

    # Формируем ответ
    return [
        {
            "uuid": str(snippet.uuid),
            "title": snippet.title,
            "code": snippet.code,
            "author_name": snippet.author.name,
            "is_public": snippet.is_public,
        } for snippet in snippets_set.values()
    ]


# Обновление код-сниппета
@snippet_router.put("/update_snippet/{snippet_uuid}", response_model=SnippetResponse, name="Обновить сниппет")
async def update_snippet(snippet_uuid: str, snippet: SnippetCreate, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция update_snippet вызвана")
    logger.info(f"Обновление сниппета с UUID: {snippet_uuid} для пользователя: {current_user.id}")

    db_snippet = await db.execute(select(Snippet).where(Snippet.uuid == snippet_uuid))
    db_snippet = db_snippet.scalars().first()

    if db_snippet is None or db_snippet.author_id != current_user.id:
        logger.warning(f"Сниппет с UUID: {snippet_uuid} не найден или доступ запрещен")
        raise HTTPException(status_code=404, detail="Snippet not found or not authorized(Сниппет не найден или не принадлежит вам)")

    for key, value in snippet.dict().items():
        setattr(db_snippet, key, value)

    await db.commit()
    await db.refresh(db_snippet)

    logger.info(f"Сниппет с UUID: {snippet_uuid} обновлен")
    return {
        "uuid": str(db_snippet.uuid),
        "title": db_snippet.title,
        "code": db_snippet.code,
        "author_name": db_snippet.author.name,
        "is_public": db_snippet.is_public,
    }


# Удаление код-сниппета
@snippet_router.delete("/delete_snippet/{snippet_uuid}", response_model=dict, name="Удалить сниппет")
async def delete_snippet(snippet_uuid: str, db: db_dependency, current_user: User = Depends(get_current_user)):
    logger.debug("Функция delete_snippet вызвана")
    logger.info(f"Удаление сниппета с UUID: {snippet_uuid} для пользователя: {current_user.id}")

    db_snippet = await db.execute(select(Snippet).where(Snippet.uuid == snippet_uuid))
    db_snippet = db_snippet.scalars().first()

    if db_snippet is None or db_snippet.author_id != current_user.id:
        logger.warning(f"Сниппет с UUID: {snippet_uuid} не найден или доступ запрещен")
        raise HTTPException(status_code=404, detail="Snippet not found or not authorized(Сниппет не найден или не принадлежит вам)")

    await db.delete(db_snippet)
    await db.commit()
    logger.info(f"Сниппет с UUID: {snippet_uuid} удален")
    return {"detail": "Snippet deleted"}