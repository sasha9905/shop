from src.api import router
from src.core.db_dependency import get_db_dependency

db_dependency_instance = get_db_dependency()

__all__ = [
    "router",
    "db_dependency_instance",
]
