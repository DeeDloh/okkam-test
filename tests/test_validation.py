import os
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.db.database import get_db
from app.main import app


@pytest.fixture
def client():
    async def fake_db():
        yield object()

    app.dependency_overrides[get_db] = fake_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"audience1": "Age >= 18"},
        {"audience2": "Age >= 18"},
    ],
)
def test_invalid_parameters(client, params):
    response = client.get("/getPercent", params=params)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "condition",
    [
        "",
        "Age >",
        "1=1) OR (1=1",
        "Weight > 1",
        "Age > 18; DROP TABLE observations",
        "Age > (SELECT 1)",
        "pg_sleep(10) IS NULL",
        "length(pg_read_file('/etc/hostname')) > 0",
        "Age > :x",
    ],
)
def test_forbidden_condition_returns_422(client, condition):
    for params in (
        {"audience1": condition, "audience2": "Sex = 2"},
        {"audience1": "Sex = 2", "audience2": condition},
    ):
        response = client.get("/getPercent", params=params)
        assert response.status_code == 422, response.text


def test_database_error_returns_503_and_does_not_expose_details(client, monkeypatch):
    error = OperationalError("SELECT secret", {}, Exception("private database error"))
    mock = AsyncMock(side_effect=[error, 0.5])
    monkeypatch.setattr("app.api.routes.calculate_percent", mock)
    params = {"audience1": "Age >= 18", "audience2": "Sex = 2"}

    response = client.get("/getPercent", params=params)
    assert response.status_code == 503
    assert response.json() == {"detail": "База данных недоступна"}
    assert "secret" not in response.text

    response = client.get("/getPercent", params=params)
    assert response.status_code == 200
    assert response.json() == {"percent": 0.5}


def test_unreachable_database_returns_503():
    url = make_url(os.environ["DATABASE_URL"]).set(host="127.0.0.1", port=1)
    engine = create_async_engine(url, connect_args={"timeout": 1})

    async def unavailable_db():
        async with AsyncSession(engine) as session:
            yield session

    app.dependency_overrides[get_db] = unavailable_db
    try:
        with TestClient(app) as client:
            response = client.get(
                "/getPercent",
                params={"audience1": "Age >= 18", "audience2": "Sex = 2"},
            )
        assert response.status_code == 503
        assert response.json() == {"detail": "База данных недоступна"}
    finally:
        app.dependency_overrides.pop(get_db, None)
