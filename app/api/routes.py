import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import calculate_percent
from app.api.schemas import PercentModel
from app.db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/getPercent", response_model=PercentModel)
async def get_percent(audience1: str,
                      audience2: str,
                      db: AsyncSession = Depends(get_db)):
    try:
        percent = await calculate_percent(db, audience1, audience2)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProgrammingError as exc:
        # Условие прошло проверку, но Postgres его не принял: "Age = 5 = 5"
        raise HTTPException(status_code=422, detail="Некорректное условие") from exc
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        logger.exception("Ошибка при работе с базой данных")
        raise HTTPException(status_code=503, detail="База данных недоступна") from exc
    return {"percent": percent}
