class OrderServiceError(Exception):
    """Базовое исключение для ошибок сервиса заказов"""
    pass


class NotFoundError(OrderServiceError):
    """Исключение при отсутствии запрашиваемого ресурса"""
    pass


class InsufficientStockError(OrderServiceError):
    """Исключение при недостаточном количестве товара на складе"""
    pass


class BusinessRuleError(OrderServiceError):
    """Исключение при нарушении бизнес-правил"""
    pass


class AccessDeniedError(OrderServiceError):
    """Исключение при отсутствии прав доступа"""
    pass
