#!/bin/bash
# Скрипт запуска KeySeller Bot

cd "$(dirname "$0")"

# Активация виртуального окружения
source venv/bin/activate

# Проверка BOT_TOKEN
if grep -q "YOUR_BOT_TOKEN_HERE" .env 2>/dev/null; then
	echo "⚠️  ВНИМАНИЕ: BOT_TOKEN не настроен!"
	echo "   1. Откройте файл .env"
	echo "   2. Замените YOUR_BOT_TOKEN_HERE на токен от @BotFather"
	echo "   3. Перезапустите скрипт"
	echo ""
fi

# Запуск бота
python bot.py
