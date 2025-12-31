set -e

echo "======================================="
echo "СОЗДАНИЕ БАЗ ДАННЫХ ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ"
echo "======================================="

# Ждём запуска PostgreSQL
echo "Ожидание PostgreSQL..."
until pg_isready -U "$POSTGRES_USER"; do
    echo "PostgreSQL ещё не готов, ждём 2 секунды..."
    sleep 2
done

echo "✅ PostgreSQL готов!"

# Получаем список баз из переменной окружения
if [ -z "$POSTGRES_DATABASES" ]; then
    echo "❌ Переменная POSTGRES_DATABASES не установлена!"
    echo "Используем базы по умолчанию: shop_auth,shop_catalog,shop_order"
    DATABASES=("shop_auth" "shop_catalog" "shop_order")
else
    echo "Получены базы из POSTGRES_DATABASES: $POSTGRES_DATABASES"
    # Разбиваем строку по запятой
    IFS=',' read -ra DATABASES <<< "$POSTGRES_DATABASES"
fi

echo "Создаём базы данных..."

# Создаём каждую базу
for DB_NAME in "${DATABASES[@]}"; do
    # Убираем лишние пробелы
    DB_NAME_CLEAN=$(echo "$DB_NAME" | xargs)
    
    echo ""
    echo "Обработка базы: '$DB_NAME_CLEAN'"
    
    # Проверяем, существует ли уже база
    DB_EXISTS=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME_CLEAN'" 2>/dev/null || echo "0")
    
    if [ "$DB_EXISTS" = "1" ]; then
        echo "✅ База '$DB_NAME_CLEAN' уже существует"
    else
        echo "Создаём базу: '$DB_NAME_CLEAN'"
        if psql -U "$POSTGRES_USER" -c "CREATE DATABASE \"$DB_NAME_CLEAN\";" 2>/dev/null; then
            echo "✅ База '$DB_NAME_CLEAN' создана успешно!"
            
            # Даём права пользователю
            psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME_CLEAN\" TO \"$POSTGRES_USER\";" 2>/dev/null || true
        else
            echo "⚠️ Не удалось создать базу '$DB_NAME_CLEAN'"
        fi
    fi
done

echo ""
echo "======================================="
echo "ВСЕ БАЗЫ ДАННЫХ ОБРАБОТАНЫ!"
echo "======================================="
echo "Текущие базы в PostgreSQL:"
psql -U "$POSTGRES_USER" -c "\l" 2>/dev/null || echo "Не удалось получить список баз"