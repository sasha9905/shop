from src.database.db_dependency import get_db_dependency

db_dependency_instance = get_db_dependency()

__all__ = [
    "db_dependency_instance",
]