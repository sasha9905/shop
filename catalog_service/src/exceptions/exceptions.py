class CatalogServiceError(Exception):
    """Базовое исключение для ошибок сервиса каталога"""
    pass


class NotFoundError(CatalogServiceError):
    """Исключение при отсутствии запрашиваемого ресурса"""
    pass


class ValidationError(CatalogServiceError):
    """Исключение при ошибке валидации данных"""
    pass


class BusinessRuleError(CatalogServiceError):
    """Исключение при нарушении бизнес-правил"""
    pass

