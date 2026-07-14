"""
KeySeller Bot — Телеграм-бот для продажи ключей AI
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение переменных
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_USERNAME = os.getenv("MANAGER_USERNAME", "manager")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/your_channel")
PAYMENT_LINK = os.getenv("PAYMENT_LINK", "https://example.com/payment")

# Данные о продуктах
PRODUCTS = {
    "chatgpt": {
        "name": "🤖 ChatGPT",
        "description": """<b>ChatGPT Plus</b> — Официальный ключ для доступа к самым мощным моделям OpenAI.

<b>Возможности:</b>
• Доступ к GPT-4o и GPT-4 Turbo
• Улучшенное качество ответов
• Приоритетный доступ к серверам
• Генерация изображений DALL-E 3
• Анализ файлов и документов""",
        "prices": "💰 <b>Цена:</b> от $20/мес",
        "icon": "🤖"
    },
    "gemini": {
        "name": "✨ Gemini Ultra + Veo",
        "description": """<b>Google Gemini Ultra</b> — Новейшие модели от Google для текста и видео.

<b>Возможности:</b>
• Доступ к Gemini 1.5 Ultra
• Генерация видео Veo 2
• Работа с файлами до 1M токенов
• Расширенный контекст
• Интеграция с Google сервисами""",
        "prices": "💰 <b>Цена:</b> от $25/мес",
        "icon": "✨"
    },
    "claude": {
        "name": "🎭 Claude",
        "description": """<b>Claude Pro</b> — Ключ Anthropic для доступа к самым умным моделям.

<b>Возможности:</b>
• Доступ к Claude 3.5 Sonnet
• Огромный контекст (200K токенов)
• Превосходное понимание логики
• Генерация и анализ кода
• Работа с длинными документами""",
        "prices": "💰 <b>Цена:</b> от $20/мес",
        "icon": "🎭"
    },
    "midjourney": {
        "name": "🎨 Midjourney",
        "description": """<b>Midjourney</b> — Подписка для генерации шедевров изображений.

<b>Возможности:</b>
• Генерация изображений высочайшего качества
• Стили: фотореализм, арт, аниме и др.
• Параметры: --ar, --stylize, --chaos
• Генерация вариаций
• Upscale и детализация""",
        "prices": "💰 <b>Цена:</b> от $30/мес",
        "icon": "🎨"
    },
    "klingai": {
        "name": "🎬 KlingAI",
        "description": """<b>KlingAI</b> — Профессиональная генерация видео.

<b>Возможности:</b>
• Генерация видео до 3 минут
• Разрешение до 1080p
• Продвинутая анимация
• Контроль движения
• Анимация по референсу""",
        "prices": "💰 <b>Цена:</b> от $15/мес",
        "icon": "🎬"
    },
    "sora2": {
        "name": "🎥 Sora 2",
        "description": """<b>Sora 2</b> — Революционный видеогенератор от OpenAI.

<b>Возможности:</b>
• Генерация реалистичных видео до 60 сек
• Текст в видео
• Продолжение существующих видео
• Высокое разрешение
• Продвинутая физика движения""",
        "prices": "💰 <b>Цена:</b> от $50/мес",
        "icon": "🎥"
    },
}


# ============================================
# КЛАВИАТУРЫ
# ============================================

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню приветствия"""
    keyboard = [
        [InlineKeyboardButton("📚 Каталог нейросетей", callback_data="catalog")],
        [InlineKeyboardButton("💬 Связаться с менеджером", callback_data="contact_manager")],
        [InlineKeyboardButton("📢 Подписаться на канал", callback_data="subscribe_channel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_catalog_keyboard() -> InlineKeyboardMarkup:
    """Каталог с выбором нейросетей"""
    keyboard = [
        [InlineKeyboardButton("🤖 ChatGPT", callback_data="product_chatgpt")],
        [InlineKeyboardButton("✨ Gemini Ultra + Veo", callback_data="product_gemini")],
        [InlineKeyboardButton("🎭 Claude", callback_data="product_claude")],
        [InlineKeyboardButton("🎨 Midjourney", callback_data="product_midjourney")],
        [InlineKeyboardButton("🎬 KlingAI", callback_data="product_klingai")],
        [InlineKeyboardButton("🎥 Sora 2", callback_data="product_sora2")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_product_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """Кнопки для конкретного продукта"""
    keyboard = [
        [InlineKeyboardButton("💬 Написать менеджеру", callback_data="contact_manager")],
        [InlineKeyboardButton("💳 Оплатить сейчас", callback_data=f"pay_{product_id}")],
        [InlineKeyboardButton("◀️ В каталог", callback_data="catalog")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# КОМАНДЫ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start — приветственное сообщение"""
    welcome_text = """
🏪 <b>Добро пожаловать в KeyStore AI!</b>

Здесь вы можете приобрести официальные ключи от лучших нейросетей мира.

🎯 <b>Выберите действие:</b>
"""

    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 <b>Как это работает:</b>

1️⃣ Выберите продукт в каталоге
2️⃣ Ознакомьтесь с описанием и ценами
3️⃣ Нажмите «Оплатить сейчас» или напишите менеджеру
4️⃣ Получите ваш ключ!

💡 <b>Все ключи официальные</b> — поставляются напрямую от провайдеров.

📩 <b>Возникли вопросы?</b> Напишите менеджеру!
"""
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )


# ============================================
# ОБРАБОТЧИКИ CALLBACK
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback-кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data
    manager_link = f"https://t.me/{MANAGER_USERNAME}"

    # --- Главное меню ---
    if data == "back_to_menu":
        welcome_text = """
🏪 <b>Добро пожаловать в KeyStore AI!</b>

Здесь вы можете приобрести официальные ключи от лучших нейросетей мира.

🎯 <b>Выберите действие:</b>
"""
        await query.edit_message_text(
            welcome_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # --- Каталог ---
    if data == "catalog":
        catalog_text = """
📚 <b>Каталог нейросетей</b>

Выберите продукт для просмотра подробной информации:

━━━━━━━━━━━━━━━━━━━━
"""
        # Добавляем краткий список
        for product in PRODUCTS.values():
            name = product['name']
            price = product['prices'].replace("💰 <b>Цена:</b> ", "")
            catalog_text += f"{name} — {price}\n"
        
        catalog_text += "━━━━━━━━━━━━━━━━━━━━"
        
        await query.edit_message_text(
            catalog_text,
            parse_mode="HTML",
            reply_markup=get_catalog_keyboard()
        )
        return

    # --- Продукты ---
    if data.startswith("product_"):
        product_id = data.replace("product_", "")
        if product_id in PRODUCTS:
            product = PRODUCTS[product_id]
            product_text = f"""
{product['name']}

{product['description']}

{product['prices']}

━━━━━━━━━━━━━━━━━━━━
"""
            await query.edit_message_text(
                product_text,
                parse_mode="HTML",
                reply_markup=get_product_keyboard(product_id)
            )
        return

    # --- Связь с менеджером ---
    if data == "contact_manager":
        contact_text = f"""
💬 <b>Связь с менеджером</b>

Для оформления заказа, консультации или оплаты свяжитесь с нашим менеджером:

👉 <a href="{manager_link}">@{MANAGER_USERNAME}</a>

⏰ Среднее время ответа: 5-15 минут
"""
        keyboard = [
            [InlineKeyboardButton("💬 Написать менеджеру", url=manager_link)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
        ]
        await query.edit_message_text(
            contact_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- Подписка на канал ---
    if data == "subscribe_channel":
        channel_text = f"""
📢 <b>Подписка на канал</b>

Присоединяйтесь к нашему каналу для получения:
• Новостей и обновлений
• Скидок и акций
• Гайдов и обзоров

👉 <a href="{CHANNEL_LINK}">Перейти в канал</a>

💡 После подписки возвращайтесь сюда для покупки!
"""
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
        ]
        await query.edit_message_text(
            channel_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- Оплата продукта ---
    if data.startswith("pay_"):
        product_id = data.replace("pay_", "")
        if product_id in PRODUCTS:
            product = PRODUCTS[product_id]
            payment_text = f"""
💳 <b>Оформление заказа</b>

📦 <b>{product['name']}</b>
{product['prices']}

━━━━━━━━━━━━━━━━━━━━

⚠️ Для оплаты перейдите по ссылке и свяжитесь с менеджером для подтверждения.

👉 <a href="{PAYMENT_LINK}">💳 Оплатить</a>

📩 Или напишите менеджеру для уточнения деталей:
<a href="{manager_link}">@{MANAGER_USERNAME}</a>
"""
            keyboard = [
                [InlineKeyboardButton("💳 Оплатить сейчас", url=PAYMENT_LINK)],
                [InlineKeyboardButton("💬 Написать менеджеру", url=manager_link)],
                [InlineKeyboardButton("◀️ К продукту", callback_data=f"product_{product_id}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
            ]
            await query.edit_message_text(
                payment_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    unknown_text = """
🤔 Извините, я не понимаю это сообщение.

Используйте команды:
• /start — Главное меню
• /help — Помощь
"""
    await update.message.reply_text(
        unknown_text,
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )


# ============================================
# ЗАПУСК БОТА
# ============================================

def main():
    """Запуск бота"""
    # Проверка токена
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN не установлен!")
        print("\n⚠️  ВНИМАНИЕ: BOT_TOKEN не настроен!")
        print("   1. Откройте .env файл")
        print("   2. Добавьте ваш токен бота")
        print("   3. Перезапустите бота\n")
        return

    logger.info("🤖 KeySeller Bot запускается...")

    # Создание приложения
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Обработчик callback-кнопок
    app.add_handler(CallbackQueryHandler(button_handler))

    # Обработчик неизвестных сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    logger.info("✅ Бот готов к работе!")
    print("\n" + "="*50)
    print("🤖 KeySeller Bot успешно запущен!")
    print("="*50 + "\n")

    # Запуск бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
