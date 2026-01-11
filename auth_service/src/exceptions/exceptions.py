class AuthServiceError(Exception):
    """Базовое исключение для ошибок сервиса аутентификации"""
    pass


class NotFoundError(AuthServiceError):
    """Исключение при отсутствии запрашиваемого ресурса"""
    pass


class ValidationError(AuthServiceError):
    """Исключение при ошибке валидации данных"""
    pass


class AuthenticationError(AuthServiceError):
    """Исключение при ошибке аутентификации"""
    pass

class AlreadyExistError(AuthServiceError):
    """Исключение при попытке добавить уже существующую запись"""
    pass

