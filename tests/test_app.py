import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/register", json={
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 201
        assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_create_snippet():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Предположим, что у вас уже есть токен доступа
        token = "your_access_token"  # Получите токен через тестовые логи или мок
        response = await client.post("/snippets/", json={
            "title": "Test Snippet",
            "code": "print('Hello World')",
            "is_public": True
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        assert response.json()["title"] == "Test Snippet"


@pytest.mark.asyncio
async def test_update_snippet():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Получите токен и id сниппета
        token = "your_access_token"
        snippet_id = 1  # Укажите id существующего сниппета
        response = await client.put(f"/snippets/{snippet_id}", json={
            "title": "Updated Snippet",
            "code": "print('Updated Code')",
            "is_public": False
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Snippet"
