from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db_session, get_current_admin
from src.schemas import CategoryAddDTO
from src.models import Category, User

router = APIRouter()


@router.post("/category")
async def add_category(data: CategoryAddDTO,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin)
):
    level = 0
    if data.parent_id == 0 or not data.parent_id:
        data.parent_id = None
    if data.parent_id:
        result = await session.execute(
            select(Category).where(Category.id == data.parent_id)
        )
        parent_category = result.scalar_one_or_none()
        level = 0
        if parent_category:
            level = parent_category.level + 1
    category = Category(
        name=data.name,
        parent_id=data.parent_id,
        level=level
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return {"Message": "Ok", "Category" : category}


@router.get("/categories")
async def get_all_categories(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Category))
    result = result.scalars().all()

    return result
