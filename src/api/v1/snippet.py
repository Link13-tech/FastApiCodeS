from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import get_current_user
from core import logger
from db.db import db_dependency
from models import User
from models.snippet import Snippet
from schemas.snippet import SnippetCreate, SnippetResponse
from typing import List
from sqlalchemy.future import select

# Создаем APIRouter с префиксом "/snippets" и тегом 'snippets'
snippet_router = APIRouter(prefix="/snippets", tags=['snippets'])


# Создание код-сниппета
@snippet_router.post("/", response_model=SnippetResponse)
async def create_snippet(snippet: SnippetCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(db_dependency)):
    db_snippet = Snippet(**snippet.dict(), author_id=current_user.id)
    db.add(db_snippet)
    await db.commit()
    await db.refresh(db_snippet)

    return {
        "id": db_snippet.id,
        "uuid": db_snippet.uuid,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Получение код-сниппета по ID
@snippet_router.get("/{snippet_id}", response_model=SnippetResponse)
async def get_snippet(snippet_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(db_dependency)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_snippet = await db.get(Snippet, snippet_id)
    if db_snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return {
        "id": db_snippet.id,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Получение код-сниппета по UUID
@snippet_router.get("/uuid/{snippet_uuid}", response_model=SnippetResponse)
async def get_snippet_by_uuid(snippet_uuid: str, db: AsyncSession = Depends(db_dependency)):
    db_snippet = await db.execute(select(Snippet).where(Snippet.uuid == snippet_uuid))
    db_snippet = db_snippet.scalars().first()

    if db_snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")

    return {
        "id": db_snippet.id,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Получение всех код-сниппетов для авторизованного пользователя
@snippet_router.get("/", response_model=List[SnippetResponse])
async def get_snippets(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(db_dependency)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = select(Snippet)
    result = await db.execute(query)
    snippets = result.scalars().all()

    # Возвращаем список словарей
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
async def update_snippet(snippet_id: int, snippet: SnippetCreate, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(db_dependency)):
    db_snippet = await db.get(Snippet, snippet_id)
    if db_snippet is None or db_snippet.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Snippet not found or not authorized")

    for key, value in snippet.dict().items():
        setattr(db_snippet, key, value)

    await db.commit()
    await db.refresh(db_snippet)

    return {
        "id": db_snippet.id,
        "title": db_snippet.title,
        "code": db_snippet.code,
        "is_public": db_snippet.is_public,
    }


# Удаление код-сниппета
@snippet_router.delete("/{snippet_id}", response_model=dict)
async def delete_snippet(snippet_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(db_dependency)):
    db_snippet = await db.get(Snippet, snippet_id)
    if db_snippet is None or db_snippet.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Snippet not found or not authorized")

    await db.delete(db_snippet)
    await db.commit()
    return {"detail": "Snippet deleted"}


# Генерация ссылки для общего доступа по UUID
@snippet_router.get("/share/{uuid}")
async def share_snippet(uuid: str, db: AsyncSession = Depends(db_dependency)):
    db_snippet = await db.execute(select(Snippet).where(Snippet.uuid == uuid))
    db_snippet = db_snippet.scalar_one_or_none()

    if db_snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    logger.debug(f"Генерация ссылки для сниппета с ID: {db_snippet.uuid}")
    return {"share_link": f"http://yourdomain.com/snippets/{db_snippet.uuid}"}
