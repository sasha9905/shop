from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db_session, get_current_admin, get_current_user
from src.schemas import ProductAddDTO
from src.models import Category, Product, User

router = APIRouter()


@router.post("/product")
async def create_product(data: ProductAddDTO,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin)
):
    result = await session.execute(
        select(Category).where(Category.id == data.category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        return {"detail": "Category not found"}

    # Создаем продукт
    product = Product(
        name=data.name,
        price=data.price,
        storage_quantity=data.quantity,
        category_id=data.category_id
    )

    session.add(product)
    await session.commit()
    await session.refresh(product)

    return product


@router.get("/products")
async def get_product(session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    result = await session.execute(select(Product))
    products = result.scalars().all()
    return products


@router.get("/products_with_category")
async def get_all_products(id: int, session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    result = await session.execute(select(Product).where(Product.category_id == id))
    products = result.scalars().all()
    return products
