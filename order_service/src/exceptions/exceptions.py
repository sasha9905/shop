class OrderServiceError(Exception):
    pass


class NotFoundError(OrderServiceError):
    pass


class InsufficientStockError(OrderServiceError):
    pass


class BusinessRuleError(OrderServiceError):
    pass
