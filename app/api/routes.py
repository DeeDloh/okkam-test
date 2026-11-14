from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.api.schemas import PercentModel
from app.api.dependencies import calculate_percent

router = APIRouter()


@router.get("/getPercent", response_model=PercentModel)
async def get_percent(audience1: str,
                      audience2: str,
                      db: AsyncSession = Depends(get_db)):
    result = {}
    result["percent"] = await calculate_percent(db=db, condition1=audience1, condition2=audience2)
    return result