import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.model import RespondentStats

from sqlalchemy import select, func

async def get_audience(db: AsyncSession, condition: str) -> dict:
    # Разрешаем только безопасный набор символов и SQL-слов
    allowed = {"age", "sex", "and", "or", "not", "between", "in"}

    query = text(f"""
        SELECT respondent, avg_weight
        FROM respondent_stats
        WHERE {condition}
    """)

    result = await db.execute(query).all()
    return dict(result)



async def calculate_percent(db: AsyncSession, condition1: str, condition2: str) -> float:

    # CTE 1: первая аудитория
    audience1 = (
        select(RespondentStats.respondent, RespondentStats.avg_weight)
        .where(text(condition1))
        .cte("audience1")
    )

    # CTE 2: вторая аудитория
    audience2 = (
        select(RespondentStats.respondent, RespondentStats.avg_weight)
        .where(text(condition2))
        .cte("audience2")
    )

    # CTE 3: пересечение аудиторий
    intersection = (
        select(audience1.c.avg_weight)
        .join(
            audience2,
            audience1.c.respondent == audience2.c.respondent
        )
        .cte("intersection")
    )

    # Сумма весов первой аудитории
    total = (
        select(func.sum(audience1.c.avg_weight))
        .scalar_subquery()
    )

    # Сумма весов пересечения
    common = (
        select(func.sum(intersection.c.avg_weight))
        .scalar_subquery()
    )

    # Финальный расчёт
    query = select(
        func.coalesce(
            common / func.nullif(total, 0),
            0
        ).label("percent")
    )

    return float(await db.scalar(query))