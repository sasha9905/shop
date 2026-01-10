import logging
import sys
from pathlib import Path

# Настройка логирования
logger = logging.getLogger("order_service")
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)-8s - %(filename)-20s:%(lineno)-4d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Консольный обработчик
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Файловый обработчик (опционально)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_dir / "order_service.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

__all__ = ["logger"]

