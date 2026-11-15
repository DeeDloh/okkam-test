from sqlalchemy.ext.asyncio import AsyncSession
from app.api.conditions import parse_condition
from app.db.model import RespondentStats

from sqlalchemy import select, func


async def calculate_percent(db: AsyncSession, condition1: str, condition2: str) -> float:

    weight = RespondentStats.avg_weight

    first = parse_condition(condition1)
    second = parse_condition(condition2)

    total = func.sum(weight).filter(first)

    common = func.sum(weight).filter(first, second)

    # Расчёт доли
    query = select(
        func.coalesce(
            common / func.nullif(total, 0),
            0
        ).label("percent")
    )

    return float(await db.scalar(query))


#async def get_audience(db: AsyncSession, condition: str) -> dict:
#    # Разрешаем только безопасный набор символов и SQL-слов
#    allowed = {"age", "sex", "and", "or", "not", "between", "in"}
#
#    query = text(f"""
#        SELECT respondent, avg_weight
#        FROM respondent_stats
#        WHERE {condition}
#    """)
#
#    result = await db.execute(query).all()
#    return dict(result)