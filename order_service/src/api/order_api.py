import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core import get_order_service, get_db_session, get_current_user
from src.schemas import UpdateOrderDTO, OrderAddDTO
from src.models import User, Product, Order, OrderItem
from src.services.order_service import OrderService

router = APIRouter()


@router.put("/update_order/{order_id}")
async def update_order(
        data: UpdateOrderDTO,
        order_service: OrderService = Depends(get_order_service),
        user: User = Depends(get_current_user)
):
    try:
        result = await order_service.update_order_item(data)
        return {
            "message": "Order updated successfully",
            "order_item": {
                "id": result.id,
                "order_id": result.order_id,
                "product_id": result.product_id,
                "quantity": result.product_quantity
            }
        }

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/order")
async def add_order(
        data: OrderAddDTO,
        session: AsyncSession = Depends(get_db_session),
        user: User = Depends(get_current_user)
):
    client_result = await session.execute(
        select(User).where(User.id == data.client_id)
    )
    user = client_result.scalar_one_or_none()

    if not user:
        return {"detail": "Client not found"}

    order = Order(
        user_id=data.client_id,
        total_quantity=sum(item.quantity for item in data.items)
    )

    session.add(order)
    await session.flush()  # Получаем ID заказа без коммита

    # Добавляем элементы заказа
    order_items = []
    for item_data in data.items:
        product_result = await session.execute(
            select(Product).where(Product.id == item_data.product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            return {"detail": f"Product with id {item_data.product_id} not found"}

        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            product_quantity=item_data.quantity
        )

        session.add(order_item)
        order_items.append(order_item)

    await session.commit()

    result = await session.execute(
        select(Order).where(Order.id == order.id).options(
            selectinload(Order.user),
            selectinload(Order.product_items).selectinload(OrderItem.product)
        )
    )
    order = result.scalar_one()

    return {
        "id": order.id,
        "client_id": order.client_id,
        "client_name": user.name,
        "user_quantity": order.total_quantity,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.product_quantity,
                "price": item.product.price
            }
            for item in order_items
        ]
    }


@router.get("/order/{order_id}")
async def get_order(
        order_id: int,
        session: AsyncSession = Depends(get_db_session),
        user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        return {"detail": "Order not found"}

    # Явно загружаем связанные данные
    await session.refresh(order, ['client', 'product_items'])
    for item in order.product_items:
        await session.refresh(item, ['product'])

    return {
        "id": order.id,
        "client_id": order.client_id,
        "client_name": order.client.name,
        "total_quantity": order.total_quantity,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.product_quantity,
                "price": item.product.price
            }
            for item in order.product_items
        ]
    }
