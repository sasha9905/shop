# Микросервисная система управления интернет-магазином

## Описание проекта

Микросервисная архитектура для управления интернет-магазином, реализующая полный цикл работы с пользователями, каталогом товаров и заказами. Система демонстрирует современные подходы к разработке распределенных приложений с использованием Python, FastAPI, PostgreSQL и RabbitMQ.

## Архитектура

Система состоит из трех независимых микросервисов:

- **auth_service** (порт 8000) - аутентификация и авторизация пользователей
- **catalog_service** (порт 8001) - управление каталогом товаров и категориями
- **order_service** (порт 8002) - управление заказами

Каждый сервис имеет собственную базу данных PostgreSQL и взаимодействует с другими через HTTP API и асинхронные сообщения RabbitMQ.

## Технологический стек

- **Python 3.11** - основной язык разработки
- **FastAPI** - современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** (async) - ORM с поддержкой асинхронных операций
- **PostgreSQL** - реляционная база данных (по одной БД на сервис)
- **RabbitMQ** - брокер сообщений для асинхронной коммуникации
- **FastStream** - библиотека для работы с RabbitMQ
- **JWT (python-jose)** - токены авторизации
- **Docker & Docker Compose** - контейнеризация и оркестрация

## Структура проекта

```
shop/
├── auth_service/          # Сервис аутентификации
│   ├── src/
│   │   ├── api/          # REST API
│   │   ├── services/     # Бизнес-логика
│   │   ├── repositories/ # Доступ к данным
│   │   └── ...
│   ├── tests/            # Тесты
│   └── Dockerfile
├── catalog_service/      # Сервис каталога
├── order_service/        # Сервис заказов
├── docker-compose.yml    # Оркестрация
└── README.md
```

## Ключевые особенности реализации

### 1. Архитектурные паттерны

- **Repository Pattern** - абстракция доступа к данным
- **Service Layer** - бизнес-логика отделена от API
- **Dependency Injection** - через FastAPI Depends
- **Event-Driven Architecture** - асинхронная синхронизация через RabbitMQ

### 2. Структура кода

```
service/
├── api/              # REST API endpoints
├── services/         # Бизнес-логика
├── repositories/     # Доступ к данным
├── models/           # SQLAlchemy модели
├── schemas/          # Pydantic схемы (request/response)
├── core/             # Конфигурация, DI, логирование
├── consumer/         # RabbitMQ подписчики
└── exceptions/       # Кастомные исключения
```

### 3. Неограниченная вложенность категорий

Реализована система категорий с поддержкой неограниченной вложенности:

- Каждая категория может иметь родительскую категорию (`parent_id`)
- Автоматический расчет уровня вложенности (`level`)
- Рекурсивная структура через self-referencing foreign key
- Поддержка иерархических запросов с оптимизацией через SQLAlchemy relationships

**Пример структуры:**
```
Электроника (level=0)
  ├── Смартфоны (level=1)
  │   ├── Android (level=2)
  │   └── iOS (level=2)
  └── Ноутбуки (level=1)
      └── Игровые (level=2)
```

### 4. Логирование и мониторинг

- Структурированное логирование с записью в файлы
- Разделение уровней логирования (INFO, ERROR)
- Логи сохраняются в Docker volumes для персистентности
- Health check endpoints для каждого сервиса

### 5. Обработка ошибок

- Кастомные исключения для каждого сервиса
- Централизованная обработка ошибок в API слое
- Детальное логирование ошибок с traceback
- Корректные HTTP статус коды

### 6. Безопасность

- JWT токены для аутентификации
- Роли пользователей (USER, ADMIN)
- Валидация данных через Pydantic
- Хеширование паролей (bcrypt)

## API Endpoints

### Auth Service
- `POST /api/v1/auth/register` - регистрация пользователя
- `POST /api/v1/auth/login` - авторизация
- `POST /api/v1/auth/verify` - верификация токена
- `GET /api/v1/users/me` - текущий пользователь
- `GET /api/v1/users/` - список пользователей (admin)
- `PUT /api/v1/users/me` - обновление профиля
- `DELETE /api/v1/users/{id}` - удаление пользователя (admin)

### Catalog Service
- `POST /api/v1/product` - создание товара (admin)
- `GET /api/v1/products` - список товаров
- `GET /api/v1/products_with_category/{id}` - товары по категории
- `POST /api/v1/category` - создание категории (admin)
- `GET /api/v1/categories` - список категорий

### Order Service
- `POST /api/v1/order` - создание заказа
- `GET /api/v1/order/{id}` - получение заказа
- `GET /api/v1/orders` - список заказов
- `PUT /api/v1/update_order/{id}` - обновление заказа
- `DELETE /api/v1/delete_order/{id}` - удаление заказа

## Асинхронная синхронизация

Сервисы синхронизируются через RabbitMQ события:

- **user_created** - создание пользователя (auth → catalog, order)
- **user_updated** - обновление пользователя (auth → catalog, order)
- **user_deleted** - удаление пользователя (auth → catalog, order)
- **product.created** - создание товара (catalog → order)

## Запуск проекта

### Через Docker Compose

```bash
# Клонировать репозиторий
git clone <repository-url>
cd shop

# Создать .env файл с настройками
cp .env.example .env

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps
```

### Локальный запуск

```bash
# Установить зависимости для каждого сервиса
cd auth_service && pip install -r requirements.txt
cd ../catalog_service && pip install -r requirements.txt
cd ../order_service && pip install -r requirements.txt

# Запустить сервисы (в разных терминалах)
cd auth_service/src && uvicorn main:app --port 8000
cd catalog_service/src && uvicorn main:app --port 8001
cd order_service/src && uvicorn main:app --port 8002
```

## Тестирование

```bash
# Запустить тесты для всех сервисов
pytest auth_service/tests/
pytest catalog_service/tests/
pytest order_service/tests/

# Запустить интеграционные тесты
pytest tests/integration/
```

## Демонстрация навыков

### Backend разработка
- Проектирование RESTful API
- Работа с асинхронным кодом (async/await)
- Оптимизация запросов к БД
- Транзакционная обработка данных

### Архитектура
- Микросервисная архитектура
- Event-driven design
- Dependency Injection
- Repository и Service patterns

### Базы данных
- Проектирование схем БД
- Работа с реляционными связями
- Миграции и управление схемой
- Оптимизация запросов

### DevOps
- Docker контейнеризация
- Docker Compose оркестрация
- Настройка volumes для логов
- Health checks

### Качество кода
- Структурированное логирование
- Обработка ошибок
- Валидация данных
- Документация кода (docstrings)

## Лицензия

Учебный проект
