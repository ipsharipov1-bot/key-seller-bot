"""
KeySeller Bot — Телеграм-бот для продажи ключей AI
VanessPay — Официальные ключи от нейросетей
"""

import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
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
MANAGER_ID = os.getenv("MANAGER_ID", "")  # Telegram ID менеджера для доступа к админке
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/vanesspayofficial")
PAYMENT_LINK = os.getenv("PAYMENT_LINK", "https://online.sberbank.ru/")

# Путь к логотипу
LOGO_PATH = "assets/logo.png"

# URL Mini App
MINI_APP_URL = "https://ipsharipov1-bot.github.io/key-seller-bot/"

# ============================================
# БАЗА ДАННЫХ
# ============================================

DB_NAME = "users.db"

def init_db():
    """Инициализация базы данных пользователей"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            joined_at TEXT,
            last_activity TEXT,
            total_messages INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_at TEXT,
            total_recipients INTEGER,
            success_count INTEGER,
            failed_count INTEGER,
            message_preview TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str, first_name: str, last_name: str = None):
    """Добавить или обновить пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, joined_at, last_activity)
        VALUES (?, ?, ?, ?, COALESCE((SELECT joined_at FROM users WHERE user_id = ?), ?), ?)
    """, (user_id, username, first_name, last_name, user_id, now, now))
    
    conn.commit()
    conn.close()

def get_all_users():
    """Получить всех пользователей"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_users_count():
    """Количество пользователей"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def update_user_activity(user_id: int):
    """Обновить время последней активности"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET last_activity = ?, total_messages = total_messages + 1 
        WHERE user_id = ?
    """, (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

# Инициализация БД при запуске
init_db()

# ============================================
# КОНТЕНТ — ИНФОРМАЦИЯ О КОМПАНИИ
# ============================================

ABOUT_US = """
🏪 <b>VanessPay — Ваш надёжный поставщик AI-решений</b>

Мы специализируемся на продаже официальных подписок и ключей от ведущих AI-сервисов мира.

<b>Наши преимущества:</b>

✅ <b>100% Официальность</b>
Все ключи поставляются напрямую от провайдеров. Никаких пиратских решений!

🔒 <b>Безопасность</b>
Работаем только через защищённые каналы оплаты. Ваши данные под защитой.

⚡ <b>Моментальная активация</b>
После оплаты ключ приходит в течение 15 минут

💬 <b>Поддержка 24/7</b>
Всегда на связи и готовы помочь

🔄 <b>Гарантия возврата</b>
Вернём деньги, если что-то пойдёт не так

━━━━━━━━━━━━━━━━━━━━

📊 <b>Наша статистика:</b>
• 👥 Более 2,000+ довольных клиентов
• ⭐ Средний рейтинг: 4.9/5
• 🕐 Работаем с 2022 года
• 🌐 География: СНГ, Европа, Азия
"""

GUARANTEES = """
🛡️ <b>Гарантии и безопасность</b>

━━━━━━━━━━━━━━━━━━━━

✅ <b>Юридическая чистота</b>
Все операции официальны. Мы работаем в правовом поле.

✅ <b>Оригинальные ключи</b>
Поставляем только официальные подписки от компаний-разработчиков.

✅ <b>Конфиденциальность</b>
Ваши платёжные данные не хранятся на наших серверах.

✅ <b>Гарантия работоспособности</b>
Если ключ не работает — заменим или вернём деньги.

✅ <b>Поддержка при настройке</b>
Поможем активировать и настроить, если возникнут сложности.

✅ <b>Прозрачное ценообразование</b>
Цены без скрытых платежей. Что видите — то платите.

━━━━━━━━━━━━━━━━━━━━

❓ Остались вопросы? Напишите менеджеру!
"""

REVIEWS = """
⭐ <b>Отзывы наших клиентов</b>

━━━━━━━━━━━━━━━━━━━━

<b>💬 Алексей М., Москва</b>
⭐⭐⭐⭐⭐
«Заказывал ChatGPT Plus на месяц. Ключ пришёл за 10 минут, всё работает идеально. Рекомендую!»

<b>💬 Екатерина К., Киев</b>
⭐⭐⭐⭐⭐
«Пользуюсь Midjourney через VanessPay уже полгода. Никаких проблем, цены адекватные, поддержка отвечает быстро.»

<b>💬 Дмитрий В., Алматы</b>
⭐⭐⭐⭐⭐
«Получил Gemini Ultra + Veo. Всё официально, можно проверить в своём аккаунте Google. Супер сервис!»

<b>💬 Анна С., Минск</b>
⭐⭐⭐⭐⭐
«Claude Pro — это просто космос! Спасибо команде за быструю активацию и адекватные цены.»

<b>💬 Максим Т., Ташкент</b>
⭐⭐⭐⭐⭐
«Заказывал Sora 2 для своего проекта. Результат превзошёл ожидания. Профессиональный подход!»

━━━━━━━━━━━━━━━━━━━━

📝 <b>Хотите оставить отзыв?</b> Напишите менеджеру после покупки!
"""

FAQ = """
❓ <b>Частые вопросы</b>

━━━━━━━━━━━━━━━━━━━━

<b>❓ Это официальные ключи?</b>
Да, мы продаём только официальные подписки от компаний-разработчиков (OpenAI, Google, Anthropic и др.)

<b>❓ Как быстро придёт ключ?</b>
Обычно в течение 15 минут после подтверждения оплаты.

<b>❓ Что если ключ не будет работать?</b>
Гарантируем замену или полный возврат средств в течение 24 часов.

<b>❓ Можно ли продлить подписку?</b>
Да, просто напишите менеджеру за несколько дней до окончания срока.

<b>❓ Как происходит оплата?</b>
Оплата через безопасные каналы: криптовалюта, банковская карта, ЮMoney, СБП.

<b>❓ Есть ли скидки?</b>
Да! При заказе от 3 месяцев — скидка 10%. От 6 месяцев — 15%.

<b>❓ Поддерживаете ли вы клиентов?</b>
Да, поддержка работает 24/7 через Telegram.

━━━━━━━━━━━━━━━━━━━━

❓ Не нашли ответ? Напишите менеджеру!
"""

# ============================================
# ПРОДУКТЫ
# ============================================

PRODUCTS = {
    "chatgpt_plus": {
        "name": "🤖 ChatGPT Plus",
        "short_desc": "GPT-4o, DALL-E 3, анализ файлов",
        "description": """<b>ChatGPT Plus</b> — Премиум доступ к самым мощным моделям OpenAI

<b>Что входит в подписку:</b>

🧠 <b>GPT-4o</b> — Новейшая мультимодальная модель
• Лучшее качество ответов
• Работа с изображениями
• Анализ файлов и документов
• До 128K контекстных токенов

🎨 <b>DALL-E 3</b> — Генерация изображений
• Создание фотореалистичных изображений
• Редактирование и вариации
• Высокое разрешение

⚡ <b>Приоритетный доступ</b>
• Быстрые ответы даже в пиковые часы
• Ранний доступ к новым функциям

💡 <b>Подходит для:</b> разработчиков, копирайтеров, аналитиков, студентов, бизнеса
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>1 990₽</b>""",
    },
    "chatgpt_pro_5x": {
        "name": "🚀 ChatGPT Pro 5x",
        "short_desc": "5x ускорение, безлимит GPT-4o",
        "description": """<b>ChatGPT Pro 5x</b> — Максимальная производительность OpenAI

<b>Что входит в подписку:</b>

⚡ <b>5x Ускорение</b>
• В 5 раз быстрее ответы
• Безлимитный GPT-4o
• Приоритетный доступ

🧠 <b>Все модели OpenAI</b>
• Доступ ко всем最新 моделям
• GPT-4o с расширенными возможностями
• Ранний доступ к новым функциям

💡 <b>Подходит для:</b> профессионалов, интенсивной работы, бизнеса
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>9 800₽</b>""",
    },
    "chatgpt_pro_20x": {
        "name": "🔥 ChatGPT Pro 20x",
        "short_desc": "20x ускорение, топ производительность",
        "description": """<b>ChatGPT Pro 20x</b> — Флагманская подписка OpenAI

<b>Что входит в подписку:</b>

🚀 <b>20x Ускорение</b>
• Максимальная скорость ответов
• Безлимитный доступ ко всем моделям
• Номера отключены (для команд)

🧠 <b>Полный доступ</b>
• Все модели и функции
• Sora для генерации видео
• Расширенные лимиты

💡 <b>Подходит для:</b> команд, агентств, интенсивного использования
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>18 900₽</b>""",
    },
    "claude_pro": {
        "name": "🎭 Claude Pro",
        "short_desc": "200K токенов, идеален для кода",
        "description": """<b>Claude Pro</b> — Самый умный AI-ассистент от Anthropic

<b>Что входит в подписку:</b>

🧬 <b>Claude 3.5 Sonnet</b> — Флагманская модель
• Контекст до 200K токенов
• Лучшее понимание логики
• Превосходный анализ документов

💻 <b>Artifact</b> — Интерактивные проекты
• Создание веб-приложений
• Генерация и запуск кода

💡 <b>Подходит для:</b> программистов, писателей, консультантов
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>1 990₽</b>""",
    },
    "claude_max_5x": {
        "name": "💎 Claude Max 5x",
        "short_desc": "5x ускорение, расширенные лимиты",
        "description": """<b>Claude Max 5x</b> — Продвинутая подписка Anthropic

<b>Что входит в подписку:</b>

⚡ <b>5x Ускорение</b>
• В 5 раз быстрее ответы
• Расширенные лимиты сообщений
• Приоритетная поддержка

🧬 <b>Claude 3.5 + Max Features</b>
• Все возможности Claude Pro
• Доступ к расширенным функциям
• Улучшенная память

💡 <b>Подходит для:</b> профессионалов и команд
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>10 900₽</b>""",
    },
    "claude_max_20x": {
        "name": "👑 Claude Max 20x",
        "short_desc": "20x ускорение, максимальная мощь",
        "description": """<b>Claude Max 20x</b> — Топ подписка Anthropic

<b>Что входит в подписку:</b>

🚀 <b>20x Ускорение</b>
• Максимальная скорость
• Безлимитный доступ
• Для интенсивной работы

🧬 <b>Все функции Claude</b>
• Все модели и возможности
• Расширенные лимиты
• Sora и видео

💡 <b>Подходит для:</b> команд и агентств
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>20 450₽</b>""",
    },
    "heygen": {
        "name": "🎬 HeyGen Creator",
        "short_desc": "AI видео с аватарами, безлимит",
        "description": """<b>HeyGen Creator</b> — Профессиональная AI-видеоплатформа

<b>Что входит в подписку:</b>

🎥 <b>AI Аватары</b>
• Создание видео с реалистичными аватарами
• 100+ готовых аватаров
• Custom Avatar (свой аватар)

🎬 <b>Безлимитный видеогенератор</b>
• Генерация без ограничений
• Высокое качество экспорта
• Шаблоны и сценарии

💡 <b>Подходит для:</b> маркетологов, создателей контента, бизнеса
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>3 490₽</b>""",
    },
    "capcut_pro_6": {
        "name": "✂️ CapCut Pro 6 мес",
        "short_desc": "AI видеоредактор, 6 месяцев",
        "description": """<b>CapCut Pro</b> — Продвинутый AI-видеоредактор от ByteDance

<b>Что входит в подписку:</b>

🎬 <b>AI Функции</b>
• AI генерация и редактирование
• Автоматические субтитры
• Удаление фона
• Масштабирование видео

💎 <b>CapCut Pro Преимущества</b>
• Без водяных знаков
• Безлимитные экспорты
• Расширенные инструменты

💡 <b>Подходит для:</b> блогеров, SMM, маркетологов
""",
        "prices": """💰 <b>Цена:</b>
• 6 месяцев — <b>3 990₽</b>""",
    },
    "capcut_pro_1": {
        "name": "✂️ CapCut Pro 1 мес",
        "short_desc": "AI видеоредактор, 1 месяц",
        "description": """<b>CapCut Pro</b> — Продвинутый AI-видеоредактор от ByteDance

<b>Что входит в подписку:</b>

🎬 <b>AI Функции</b>
• AI генерация и редактирование
• Автоматические субтитры
• Удаление фона
• Масштабирование видео

💎 <b>CapCut Pro Преимущества</b>
• Без водяных знаков
• Безлимитные экспорты
• Расширенные инструменты

💡 <b>Подходит для:</b> блогеров, SMM, маркетологов
""",
        "prices": """💰 <b>Цена:</b>
• 1 месяц — <b>990₽</b>""",
    },
    "grok_super": {
        "name": "🤖 Grok Super 2 мес",
        "short_desc": "xAI Илона Маска, 2 месяца",
        "description": """<b>Grok Super</b> — AI от xAI Илона Маска

<b>Что входит в подписку:</b>

🚀 <b>Grok 2 + Grok 3</b>
• Доступ к самым новым моделям xAI
• Анализ изображений
• Реальное время (Realtime)

💡 <b>Особенности</b>
• Уникальный юмор и стиль
• Анализ рентгенов и документов
• Свободная подача информации

💡 <b>Подходит для:</b> tech-энтузиастов, исследователей, фанатов Илона Маска
""",
        "prices": """💰 <b>Цена:</b>
• 2 месяца — <b>1 990₽</b>""",
    },
}


# ============================================
# КЛАВИАТУРЫ
# ============================================

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню приветствия"""
    keyboard = [
        [InlineKeyboardButton("📚 Каталог нейросетей", callback_data="catalog")],
        [InlineKeyboardButton("💬 Связаться с менеджером", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton("📱 О нас | FAQ | Гарантии", web_app=WebAppInfo(url=MINI_APP_URL))],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_catalog_keyboard() -> InlineKeyboardMarkup:
    """Каталог с выбором нейросетей"""
    keyboard = [
        [InlineKeyboardButton("🤖 ChatGPT Plus — 1 990₽", callback_data="product_chatgpt_plus")],
        [InlineKeyboardButton("🚀 ChatGPT Pro 5x — 9 800₽", callback_data="product_chatgpt_pro_5x")],
        [InlineKeyboardButton("🔥 ChatGPT Pro 20x — 18 900₽", callback_data="product_chatgpt_pro_20x")],
        [InlineKeyboardButton("🎭 Claude Pro — 1 990₽", callback_data="product_claude_pro")],
        [InlineKeyboardButton("💎 Claude Max 5x — 10 900₽", callback_data="product_claude_max_5x")],
        [InlineKeyboardButton("👑 Claude Max 20x — 20 450₽", callback_data="product_claude_max_20x")],
        [InlineKeyboardButton("🎬 HeyGen Creator — 3 490₽", callback_data="product_heygen")],
        [InlineKeyboardButton("✂️ CapCut Pro 6 мес — 3 990₽", callback_data="product_capcut_pro_6")],
        [InlineKeyboardButton("✂️ CapCut Pro 1 мес — 990₽", callback_data="product_capcut_pro_1")],
        [InlineKeyboardButton("🤖 Grok Super 2 мес — 1 990₽", callback_data="product_grok_super")],
        [InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_product_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """Кнопки для конкретного продукта"""
    keyboard = [
        [InlineKeyboardButton("💬 Написать менеджеру", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("💳 Оплатить сейчас", url=PAYMENT_LINK)],
        [InlineKeyboardButton("📱 О нас | FAQ | Гарантии", web_app=WebAppInfo(url=MINI_APP_URL))],
        [InlineKeyboardButton("◀️ В каталог", callback_data="catalog")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_info_keyboard() -> InlineKeyboardMarkup:
    """Кнопки для информационных страниц"""
    keyboard = [
        [InlineKeyboardButton("📚 В каталог", callback_data="catalog")],
        [InlineKeyboardButton("💬 Написать менеджеру", url=f"https://t.me/{MANAGER_USERNAME}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Кнопки админ-панели"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Сделать рассылку", callback_data="broadcast_start")],
        [InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton("◀️ Выйти", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# КОМАНДЫ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start — приветственное сообщение"""
    # Сохраняем пользователя в БД
    user = update.effective_user
    add_user(user.id, user.username or "", user.first_name, user.last_name)
    
    welcome_text = """🏪 Добро пожаловать в VanessPay!

Мы предоставляем услуги по оплате подписок и ключей от ведущих AI-сервисов мира.

🤖 Продаём подписки от:
OpenAI • Google • Anthropic • Midjourney • Kuaishou

⭐ Наши преимущества:
✅ Официальные ключи
✅ Активация за 5 минут
✅ Поддержка 24/7
✅ Гарантия возврата

📊 Уже помогли 2,000+ клиентам получить доступ к топовым AI!

🎯 Выберите действие:"""

    try:
        with open(LOGO_PATH, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=get_main_menu_keyboard()
            )
    except FileNotFoundError:
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
4️⃣ Получите ключ в течение 15 минут
5️⃣ Активируйте в своём аккаунте

💡 <b>Все ключи официальные</b> — поставляются напрямую от провайдеров.

📩 <b>Возникли вопросы?</b> Напишите менеджеру!
"""
    await update.message.reply_text(
        help_text,
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-панель — доступ только для MANAGER_ID"""
    user_id = update.effective_user.id
    manager_id = int(MANAGER_ID) if MANAGER_ID and MANAGER_ID.isdigit() else 0
    
    # Проверка доступа
    if user_id != manager_id and str(user_id) != MANAGER_ID:
        await update.message.reply_text(
            "⛔ У вас нет доступа к админ-панели.",
            parse_mode="HTML"
        )
        return
    
    admin_text = f"""
🔐 <b>Админ-панель VanessPay</b>

━━━━━━━━━━━━━━━━━━━━

👥 <b>Пользователей в базе:</b> {get_users_count()}

━━━━━━━━━━━━━━━━━━━━

<b>Выберите действие:</b>
"""
    
    await update.message.reply_text(
        admin_text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


# ============================================
# ОБРАБОТЧИКИ CALLBACK
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback-кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id
    manager_link = f"https://t.me/{MANAGER_USERNAME}"
    
    # Проверка доступа к админке
    admin_id = int(MANAGER_ID) if MANAGER_ID and MANAGER_ID.isdigit() else 0
    is_admin = user_id == admin_id or str(user_id) == MANAGER_ID

    # Игнорируем разделители
    if data == "divider":
        return

    # --- Открыть Mini App ---
    if data == "open_app":
        app_text = """
📱 <b>VanessPay Mini App</b>

━━━━━━━━━━━━━━━━━━━━

Перейдите в наше приложение, чтобы:
• Узнать больше о нас
• Прочитать отзывы клиентов
• Получить ответы на вопросы
• Узнать о гарантиях

━━━━━━━━━━━━━━━━━━━━

<i>Нажмите кнопку ниже, чтобы открыть приложение:</i>
"""
        # Используем URL-кнопку если MINI_APP_URL настроен
        try:
            from telegram import WebAppInfo, MenuButtonWebApp
            keyboard = [
                [InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url="https://ipsharipov1-bot.github.io/key-seller-bot/"))],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
            ]
            await query.edit_message_text(
                app_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except ImportError:
            # Fallback для старых версий
            keyboard = [
                [InlineKeyboardButton("📱 Открыть приложение", url="https://ipsharipov1-bot.github.io/key-seller-bot/")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
            ]
            await query.edit_message_text(
                app_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return

    # --- Главное меню ---
    if data == "back_to_menu":
        welcome_text = f"""
🏪 <b>Добро пожаловать в VanessPay!</b>

Мы предоставляем услуги по оплате подписок от ведущих AI-сервисов мира.

<b>💡 Актуальные цены:</b>
• ChatGPT Plus — от 1 990₽
• Claude Pro — от 1 990₽
• Grok Super — 1 990₽
• HeyGen Creator — 3 490₽
• CapCut Pro — от 990₽

<b>⭐ Наши преимущества:</b>
✅ Все подписки официальные
✅ Активация за 5 минут
✅ Полная гарантия
✅ Поддержка 24/7

🎯 <b>Выберите действие:</b>
"""
        await query.edit_message_text(
            welcome_text,
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # --- Админ-панель ---
    if data == "admin_panel":
        if not is_admin:
            await query.answer("⛔ Нет доступа", show_alert=True)
            return
        
        admin_text = f"""
🔐 <b>Админ-панель VanessPay</b>

👥 <b>Пользователей в базе:</b> {get_users_count()}

<b>Выберите действие:</b>
"""
        await query.edit_message_text(
            admin_text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
        return

    # --- Статистика ---
    if data == "admin_stats":
        if not is_admin:
            await query.answer("⛔ Нет доступа", show_alert=True)
            return
        
        users_count = get_users_count()
        stats_text = f"""
📊 <b>Статистика бота</b>

👥 <b>Всего пользователей:</b> {users_count}

💡 Подробная статистика будет доступна в будущих обновлениях.
"""
        keyboard = [
            [InlineKeyboardButton("◀️ В админку", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
        ]
        await query.edit_message_text(
            stats_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- Список пользователей ---
    if data == "admin_users":
        if not is_admin:
            await query.answer("⛔ Нет доступа", show_alert=True)
            return
        
        users = get_all_users()
        users_text = f"""
👥 <b>Список пользователей</b>

Всего: {len(users)} пользователей

"""
        if len(users) <= 50:
            for i, (uid, uname, fname) in enumerate(users[:50], 1):
                name = uname if uname else fname if fname else f"User{uid}"
                users_text += f"{i}. @{name} (ID: {uid})\n"
        else:
            for i, (uid, uname, fname) in enumerate(users[:10], 1):
                name = uname if uname else fname if fname else f"User{uid}"
                users_text += f"{i}. @{name} (ID: {uid})\n"
            users_text += f"\n...и ещё {len(users) - 10} пользователей"
        
        keyboard = [
            [InlineKeyboardButton("◀️ В админку", callback_data="admin_panel")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
        ]
        await query.edit_message_text(
            users_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- Начать рассылку ---
    if data == "broadcast_start":
        if not is_admin:
            await query.answer("⛔ Нет доступа", show_alert=True)
            return
        
        context.user_data['broadcasting'] = True
        
        broadcast_text = """
📢 <b>Режим рассылки</b>

⚠️ <b>Внимание!</b> Отправьте сообщение для рассылки.

<b>Формат:</b>
Просто напишите текст сообщения.

<b>Получатели:</b> все пользователи бота

👥 Количество получателей будет показано перед отправкой.

<i>Отмена: /cancel</i>
"""
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data="broadcast_cancel")],
        ]
        await query.edit_message_text(
            broadcast_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # --- Отмена рассылки ---
    if data == "broadcast_cancel":
        context.user_data['broadcasting'] = False
        await query.answer("Рассылка отменена")
        
        admin_text = f"""
🔐 <b>Админ-панель</b>

👥 <b>Пользователей:</b> {get_users_count()}

<i>Рассылка отменена.</i>
"""
        await query.edit_message_text(
            admin_text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
        return

    # --- Каталог ---
    if data == "catalog":
        catalog_text = """
📚 <b>Каталог AI-подписок</b>

Выберите продукт для просмотра описания и цен:

"""
        for product in PRODUCTS.values():
            name = product['name']
            short = product['short_desc']
            catalog_text += f"{name}\n📝 {short}\n\n"
        
        catalog_text += "\n💡 Все подписки официальные с полной гарантией!"
        
        await query.edit_message_text(
            catalog_text,
            parse_mode="HTML",
            reply_markup=get_catalog_keyboard()
        )
        return

    # --- О нас ---
    if data == "about_us":
        await query.edit_message_text(
            ABOUT_US,
            parse_mode="HTML",
            reply_markup=get_info_keyboard()
        )
        return

    # --- Отзывы ---
    if data == "reviews":
        await query.edit_message_text(
            REVIEWS,
            parse_mode="HTML",
            reply_markup=get_info_keyboard()
        )
        return

    # --- FAQ ---
    if data == "faq":
        await query.edit_message_text(
            FAQ,
            parse_mode="HTML",
            reply_markup=get_info_keyboard()
        )
        return

    # --- Гарантии ---
    if data == "guarantees":
        await query.edit_message_text(
            GUARANTEES,
            parse_mode="HTML",
            reply_markup=get_info_keyboard()
        )
        return

    # --- Продукты ---
    if data.startswith("product_"):
        product_id = data.replace("product_", "")
        if product_id in PRODUCTS:
            product = PRODUCTS[product_id]
            product_text = f"""
{product['description']}

{product['prices']}
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

⏰ Среднее время ответа: <b>5-15 минут</b>
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
📢 <b>Подписка на канал VanessPay</b>

━━━━━━━━━━━━━━━━━━━━

📰 <b>Что вы получите:</b>

• Новости и обновления AI-индустрии
• Эксклюзивные скидки и акции
• Гайды и обзоры нейросетей
• Советы по использованию
• Ранний доступ к новым продуктам

👉 <a href="{CHANNEL_LINK}">Перейти в канал</a>
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

⚠️ <b>Для продолжения:</b>

Напишите менеджеру для:
• Подтверждения заказа
• Выбора способа оплаты
• Получения ключа после оплаты

💳 <b>Способы оплаты:</b>
• Банковская карта (РФ/СНГ)
• СБП (Россия)
• ЮMoney / ЮKassa
• Криптовалюта (BTC, ETH, USDT)

👉 <a href="{manager_link}">@{MANAGER_USERNAME}</a>
"""
            keyboard = [
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


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений для рассылки"""
    user_id = update.effective_user.id
    admin_id = int(MANAGER_ID) if MANAGER_ID and MANAGER_ID.isdigit() else 0
    is_admin = user_id == admin_id or str(user_id) == MANAGER_ID
    
    # Проверяем, активен ли режим рассылки
    if not context.user_data.get('broadcasting'):
        return
    
    if not is_admin:
        await update.message.reply_text("⛔ Только администратор может делать рассылку.")
        context.user_data['broadcasting'] = False
        return
    
    message_text = update.message.text
    users = get_all_users()
    total = len(users)
    
    # Подтверждение перед отправкой
    confirm_text = f"""
📢 <b>Подтверждение рассылки</b>

━━━━━━━━━━━━━━━━━━━━

📝 <b>Сообщение:</b>
{message_text[:500]}{'...' if len(message_text) > 500 else ''}

━━━━━━━━━━━━━━━━━━━━

👥 <b>Получателей:</b> {total}

⚠️ Отправить рассылку?
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Отправить", callback_data=f"broadcast_confirm_{total}")],
        [InlineKeyboardButton("❌ Отмена", callback_data="broadcast_cancel")],
    ]
    
    # Сохраняем сообщение для рассылки
    context.user_data['broadcast_message'] = message_text
    context.user_data['broadcasting'] = False
    
    await update.message.reply_text(
        confirm_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def broadcast_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и отправка рассылки"""
    query = update.callback_query
    await query.answer("Отправляем рассылку...", show_alert=True)
    
    data = query.data
    if not data.startswith("broadcast_confirm_"):
        return
    
    message_text = context.user_data.get('broadcast_message', "")
    if not message_text:
        await query.edit_message_text("❌ Сообщение не найдено. Начните рассылку заново.")
        return
    
    # Получаем пользователей
    users = get_all_users()
    
    # Клавиатура для сообщения
    keyboard = [
        [InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_menu")],
    ]
    message_reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем
    success = 0
    failed = 0
    
    status_msg = await query.message.reply_text(
        f"📤 Отправка рассылки...\n\n👥 Прогресс: 0/{len(users)}",
        parse_mode="HTML"
    )
    
    for i, (user_id, _, _) in enumerate(users, 1):
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode="HTML",
                reply_markup=message_reply_markup
            )
            success += 1
        except Exception:
            failed += 1
        
        # Обновляем прогресс каждые 10 пользователей
        if i % 10 == 0:
            await status_msg.edit_text(
                f"📤 Отправка рассылки...\n\n👥 Прогресс: {i}/{len(users)}\n✅ Отправлено: {success}\n❌ Ошибок: {failed}",
                parse_mode="HTML"
            )
    
    # Финальный результат
    result_text = f"""
✅ <b>Рассылка завершена!</b>

━━━━━━━━━━━━━━━━━━━━

👥 <b>Всего получателей:</b> {len(users)}

✅ <b>Успешно:</b> {success}

❌ <b>Не доставлено:</b> {failed}

━━━━━━━━━━━━━━━━━━━━
"""
    
    await status_msg.edit_text(result_text, parse_mode="HTML")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена рассылки"""
    context.user_data['broadcasting'] = False
    context.user_data['broadcast_message'] = None
    await update.message.reply_text("✅ Рассылка отменена.")


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    # Сохраняем активность пользователя
    user = update.effective_user
    if user:
        update_user_activity(user.id)
    
    unknown_text = """
🤔 Извините, я не понимаю это сообщение.

Используйте команды:
• /start — Главное меню
• /help — Помощь
• /admin — Админ-панель (только для менеджера)

или выберите действие в меню 👇
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

    logger.info("🤖 VanessPay Bot запускается...")

    # Создание приложения
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    
    # Обработчик callback-кнопок (нужен для рассылки)
    app.add_handler(CallbackQueryHandler(broadcast_confirm_handler, pattern="^broadcast_confirm_"))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Обработчик сообщений для рассылки
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_handler))
    
    # Обработчик неизвестных сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    logger.info("✅ Бот готов к работе!")
    print("\n" + "="*50)
    print("🤖 VanessPay Bot успешно запущен!")
    print("📊 База данных: users.db")
    print("="*50 + "\n")

    # Запуск бота
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        timeout=60,  # Долгий polling для Railway
        bootstrap_retries=-1,  # Бесконечные попытки переподключения
    )


if __name__ == "__main__":
    main()
