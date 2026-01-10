from fastapi import APIRouter, Depends, HTTPException

from src.core import get_order_service, get_user_service
from src.core.logging_config import logger
from src.schemas import (
    UpdateOrderDTO,
    OrderAddDTO,
    OrderResponseDTO,
    OrderDetailResponseDTO,
    OrderUpdateResponseDTO,
    OrderItemResponseDTO,
    OrderItemUpdateResponseDTO,
    OrdersListResponseDTO
)
from src.services.order_service import OrderService
from src.services.user_service import UserService
from src.exceptions import NotFoundError, InsufficientStockError, BusinessRuleError

router = APIRouter()


@router.post("/order", response_model=OrderResponseDTO)
async def add_order(
        data: OrderAddDTO,
        order_service: OrderService = Depends(get_order_service),
        user_service: UserService = Depends(get_user_service),
        #user: User = Depends(get_current_user)
):
    """
    Создать новый заказ
    
    Args:
        data: Данные для создания заказа (user_id, items)
        order_service: Сервис для работы с заказами
        user_service: Сервис для работы с пользователями
        user: Текущий авторизованный пользователь
        
    Returns:
        OrderResponseDTO: Созданный заказ с информацией о товарах
        
    Raises:
        HTTPException 404: Если пользователь или товар не найдены
        HTTPException 400: Если недостаточно товара на складе или нарушены бизнес-правила
    """
    try:
        # Проверяем существование пользователя
        client = await user_service.get_user_by_id(data.user_id)
        if not client:
            raise NotFoundError("Client not found")

        # Создаем заказ через сервис
        order = await order_service.create_order(data)

        return OrderResponseDTO(
            id=order.id,
            user_id=order.user_id,
            client_name=order.user.username,
            user_quantity=order.total_quantity,
            items=[
                OrderItemResponseDTO(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.product_quantity,
                    price=item.product.price
                )
                for item in order.product_items
            ]
        )
    except NotFoundError as e:
        logger.warning(f"Order creation failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientStockError as e:
        logger.warning(f"Order creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleError as e:
        logger.warning(f"Order creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in add_order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/order/{order_id}", response_model=OrderDetailResponseDTO)
async def get_order(
        order_id: int,
        order_service: OrderService = Depends(get_order_service),
        #user: User = Depends(get_current_user)
):
    """
    Получить заказ по ID
    
    Args:
        order_id: ID заказа
        order_service: Сервис для работы с заказами
        user: Текущий авторизованный пользователь
        
    Returns:
        OrderDetailResponseDTO: Детальная информация о заказе с товарами
        
    Raises:
        HTTPException 404: Если заказ не найден
    """
    try:
        order = await order_service.get_order_by_id(order_id)

        return OrderDetailResponseDTO(
            id=order.id,
            client_id=order.user_id,
            client_name=order.user.username,
            total_quantity=order.total_quantity,
            items=[
                OrderItemResponseDTO(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.product_quantity,
                    price=item.product.price
                )
                for item in order.product_items
            ]
        )
    except NotFoundError as e:
        logger.warning(f"Order retrieval failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/orders", response_model=OrdersListResponseDTO)
async def get_all_orders(
        skip: int = 0,
        limit: int = 100,
        order_service: OrderService = Depends(get_order_service),
        #user: User = Depends(get_current_user)
):
    """
    Получить список всех заказов с пагинацией
    
    Args:
        skip: Количество записей для пропуска (по умолчанию 0)
        limit: Максимальное количество записей (по умолчанию 100)
        order_service: Сервис для работы с заказами
        user: Текущий авторизованный пользователь
        
    Returns:
        OrdersListResponseDTO: Список заказов с общей информацией
    """
    try:
        orders = await order_service.get_all_orders(skip, limit)
        
        return OrdersListResponseDTO(
            orders=[
                OrderDetailResponseDTO(
                    id=order.id,
                    client_id=order.user_id,
                    client_name=order.user.username,
                    total_quantity=order.total_quantity,
                    items=[
                        OrderItemResponseDTO(
                            id=item.id,
                            order_id=item.order_id,
                            product_id=item.product_id,
                            product_name=item.product.name,
                            quantity=item.product_quantity,
                            price=item.product.price
                        )
                        for item in order.product_items
                    ]
                )
                for order in orders
            ],
            total=len(orders)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_all_orders: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/update_order/{order_id}", response_model=OrderUpdateResponseDTO)
async def update_order(
        data: UpdateOrderDTO,
        order_service: OrderService = Depends(get_order_service),
):
    """
    Обновить количество товара в заказе

    Args:
        data: Данные для обновления заказа (order_id, product_id, quantity)
        order_service: Сервис для работы с заказами
        user: Текущий авторизованный пользователь

    Returns:
        OrderUpdateResponseDTO: Результат обновления заказа

    Raises:
        HTTPException 404: Если заказ, товар или элемент заказа не найдены
        HTTPException 400: Если недостаточно товара на складе или нарушены бизнес-правила
    """
    try:
        result = await order_service.update_order_item(data)
        return OrderUpdateResponseDTO(
            message="Order updated successfully",
            order_item=OrderItemUpdateResponseDTO(
                id=result.id,
                order_id=result.order_id,
                product_id=result.product_id,
                quantity=result.product_quantity
            )
        )
    except NotFoundError as e:
        logger.warning(f"Order update failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientStockError as e:
        logger.warning(f"Order update failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleError as e:
        logger.warning(f"Order update failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete_order/{order_id}")
async def delete_order(
        order_id: int,
        order_service: OrderService = Depends(get_order_service),
):
    """
    Удалить заказ

    Args:
        order_id: ID заказа
        order_service: Сервис для работы с заказами

    Raises:
        HTTPException 404: Если заказ, товар или элемент заказа не найдены
    """
    try:
        await order_service.delete_order(order_id)
        return {"Status": "Ok"}

    except NotFoundError as e:
        logger.warning(f"Order update failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
