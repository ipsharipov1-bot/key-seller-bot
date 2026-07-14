# 🤖 KeySeller Bot — Телеграм-бот для продажи ключей AI

## Описание
Телеграм-бот для продажи официальных ключей от нейросетей с кнопкой связи с менеджером.

## Продукты
- **ChatGPT** — Официальные ключи OpenAI
- **Gemini Ultra Veo** — Google AI
- **Claude** — Anthropic (орфография сохранена как "cloude" по запросу)
- **Midjourney** — Генерация изображений
- **KlingAI** — Видеогенерация
- **Sora 2** — OpenAI видеогенератор

## Оплата
Для оплаты заказа — кнопка «Написать менеджеру» в Telegram.

## Стек
- Python 3.10+
- python-telegram-bot (aiogram 3.x)
- SQLite (локальное хранение заказов)
- python-dotenv

## Запуск
```bash
pip install -r requirements.txt
cp .env.example .env
# Добавить BOT_TOKEN в .env
python bot.py
```

## Переменные окружения
- `BOT_TOKEN` — Токен бота от @BotFather
- `MANAGER_USERNAME` — Username менеджера (без @)
