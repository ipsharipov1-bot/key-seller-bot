"""
KeySeller Bot — Телеграм-бот для продажи ключей AI
VanessPay — Официальные ключи от нейросетей
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
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/vanesspayofficial")
PAYMENT_LINK = os.getenv("PAYMENT_LINK", "https://t.me/vanesspayer")

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

STATISTICS = """
📊 <b>VanessPay в цифрах:</b>

━━━━━━━━━━━━━━━━━━━━

👥 <b>2,047</b> клиентов обслужено

⭐ <b>4.9/5</b> средний рейтинг

🕐 <b>С 2022 года</b> на рынке

🌍 <b>30+</b> стран доставки

💰 <b>$500K+</b> успешных операций

⏱️ <b>15 мин</b> среднее время активации

🔄 <b>98%</b> клиентов возвращаются

━━━━━━━━━━━━━━━━━━━━

💬 Присоединяйтесь к тысячам довольных пользователей!
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

HOW_IT_WORKS = """
📋 <b>Как это работает</b>

━━━━━━━━━━━━━━━━━━━━

<b>Шаг 1️⃣ — Выберите продукт</b>
Выберите нужную нейросеть в каталоге и ознакомьтесь с описанием и ценами.

<b>Шаг 2️⃣ — Оформите заказ</b>
Нажмите «Оплатить сейчас» или напишите менеджеру для уточнения деталей.

<b>Шаг 3️⃣ — Произведите оплату</b>
Оплатите удобным способом: карта, криптовалюта, СБП, ЮMoney.

<b>Шаг 4️⃣ — Получите ключ</b>
После подтверждения оплаты вы получите ключ в течение 15 минут.

<b>Шаг 5️⃣ — Активируйте</b>
Активируйте ключ в личном кабинете сервиса. При необходимости поможем с настройкой!

━━━━━━━━━━━━━━━━━━━━

💬 Готовы начать? Выберите продукт в каталоге!
"""

# ============================================
# ПРОДУКТЫ
# ============================================

PRODUCTS = {
    "chatgpt": {
        "name": "🤖 ChatGPT Plus",
        "short_desc": "GPT-4o, DALL-E 3, анализ файлов",
        "description": """<b>ChatGPT Plus</b> — Премиум доступ к самым мощным моделям OpenAI

━━━━━━━━━━━━━━━━━━━━

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

📊 <b>Advanced Data Analysis</b>
• Анализ данных и код
• Построение графиков
• Работа с файлами Excel, CSV

⚡ <b>Приоритетный доступ</b>
• Быстрые ответы даже в пиковые часы
• Ранний доступ к новым функциям

━━━━━━━━━━━━━━━━━━━━

💡 <b>Подходит для:</b> разработчиков, копирайтеров, аналитиков, студентов, бизнеса
""",
        "prices": """💰 <b>Тарифы:</b>

• 1 месяц — $20
• 3 месяца — $55 <i>(-8%)</i>
• 6 месяцев — $100 <i>(-17%)</i>
• 12 месяцев — $180 <i>(-25%)</i>""",
        "features": ["GPT-4o", "DALL-E 3", "Advanced Analysis", "ПриоритетGPT", "API Access"]
    },
    "gemini": {
        "name": "✨ Gemini Ultra + Veo",
        "short_desc": "Google AI, 1M токенов, генерация видео",
        "description": """<b>Gemini Ultra + Veo 2</b> — Флагманские модели от Google

━━━━━━━━━━━━━━━━━━━━

<b>Что входит в подписку:</b>

🌟 <b>Gemini 1.5 Ultra</b> — Самая мощная модель Google
• Контекст до 1 миллиона токенов
• Работа с длинными документами
• Мультимодальность (текст, код, видео)
• Превосходный анализ изображений

🎬 <b>Veo 2</b> — Генерация видео от Google
• Реалистичные видео до 60 секунд
• Различные стили и эффекты
• Высокое разрешение
• Продвинутая физика движения

🔍 <b>Deep Research</b>
• Автоматический поиск и анализ
• Структурированные отчёты
• Актуальные данные из сети

📱 <b>Gemini в приложениях Google</b>
• Интеграция с Gmail, Docs, Sheets
• Умный поиск в интернете

━━━━━━━━━━━━━━━━━━━━

💡 <b>Подходит для:</b> исследователей, аналитиков данных, видеокреаторов, разработчиков
""",
        "prices": """💰 <b>Тарифы:</b>

• 1 месяц — $25
• 3 месяца — $70 <i>(-7%)</i>
• 6 месяцев — $130 <i>(-13%)</i>
• 12 месяцев — $230 <i>(-24%)</i>""",
        "features": ["Gemini Ultra", "Veo 2 Video", "1M Context", "Deep Research", "Google Integration"]
    },
    "claude": {
        "name": "🎭 Claude Pro",
        "short_desc": "200K токенов, идеален для кода",
        "description": """<b>Claude Pro</b> — Самый умный AI-ассистент от Anthropic

━━━━━━━━━━━━━━━━━━━━

<b>Что входит в подписку:</b>

🧬 <b>Claude 3.5 Sonnet</b> — Флагманская модель
• Контекст до 200K токенов
• Лучшее понимание логики и нюансов
• Превосходный анализ документов
• Детекция собственных ошибок

💻 <b>Artifact</b> — Интерактивные проекты
• Создание веб-приложений
• Интерактивные презентации
• Генерация и запуск кода

📈 <b>Расширенные лимиты</b>
• В 5 раз больше сообщений
• Приоритетный доступ
• Ранние функции

🔒 <b>Безопасность и конфиденциальность</b>
• Данные не используются для обучения
• Корпоративная защита

━━━━━━━━━━━━━━━━━━━━

💡 <b>Подходит для:</b> программистов, писателей, консультантов, преподавателей
""",
        "prices": """💰 <b>Тарифы:</b>

• 1 месяц — $20
• 3 месяца — $55 <i>(-8%)</i>
• 6 месяцев — $100 <i>(-17%)</i>
• 12 месяцев — $180 <i>(-25%)</i>""",
        "features": ["Claude 3.5 Sonnet", "200K Context", "Artifact", "Priority Access", "Privacy First"]
    },
    "midjourney": {
        "name": "🎨 Midjourney",
        "short_desc": "Шедевры изображений, все стили",
        "description": """<b>Midjourney</b> — №1 для генерации изображений

━━━━━━━━━━━━━━━━━━━━

<b>Что входит в подписку:</b>

🎨 <b>Качество Standard/Basic</b>
• Быстрая генерация изображений
• До ~200 изображений в месяц
• Работа через Discord или Web

🖼️ <b>Стили и возможности</b>
• Фотореализм высочайшего уровня
• Все художественные стили
• Параметры: --ar, --stylize, --chaos
• Upscale и вариации

⚡ <b>Режимы генерации</b>
• Relax (без очереди)
• Turbo (ускоренный)
• Remix (вариации)

📊 <b>Разрешение</b>
• Генерация до 2K
• Upscale до 4K

━━━━━━━━━━━━━━━━━━━━

💡 <b>Подходит для:</b> дизайнеров, маркетологов, художников, SMM-специалистов, креаторов
""",
        "prices": """💰 <b>Тарифы:</b>

• Basic (200 img) — $10/мес
• Standard (200 img + unlimited relax) — $30/мес
• Pro (400 img + turbo) — $80/мес
• Mega (800 img + turbo) — $120/мес""",
        "features": ["200-800 img/мес", "Все стили", "Upscale 4K", "Turbo Mode", "Relax Mode"]
    },
    "klingai": {
        "name": "🎬 KlingAI",
        "short_desc": "Профессиональная генерация видео",
        "description": """<b>KlingAI</b> — Профессиональная видеогенерация от Kuaishou

━━━━━━━━━━━━━━━━━━━━

<b>Что входит в подписку:</b>

🎬 <b>Генерация видео</b>
• Видео до 3 минут
• Разрешение до 1080p
• Плавная анимация
• Реалистичные движения

🖼️ <b>Изображение в видео</b>
• Animate your image
• Продолжение существующего видео
• Стилизация и эффекты

⚡ <b>Продвинутые функции</b>
• Контроль движения
• Анимация по референсу
• Промт-ассистент

📱 <b>Доступ</b>
• Веб-интерфейс
• API доступ (включён)

━━━━━━━━━━━━━━━━━━━━

💡 <b>Подходит для:</b> видеографов, маркетологов, контент-креаторов, рекламщиков
""",
        "prices": """💰 <b>Тарифы:</b>

• Starter — $15/мес
• Professional — $49/мес
• Enterprise — $99/мес

<i>Точные цены уточняйте у менеджера</i>""",
        "features": ["3 мин видео", "1080p", "Motion Control", "Reference Animation", "API Access"]
    },
    "sora2": {
        "name": "🎥 Sora 2",
        "short_desc": "OpenAI видеогенератор, топ качество",
        "description": """<b>Sora 2</b> — Революционный видеогенератор от OpenAI

━━━━━━━━━━━━━━━━━━━━

<b>Что входит в подписку:</b>

🎥 <b>Генерация видео</b>
• Реалистичные видео до 60 секунд
• Самое высокое качество на рынке
• Продвинутая физика
• Плавные переходы

🖼️ <b>Мультимодальность</b>
• Текст в видео
• Изображение в видео
• Продолжение видео
• Цикличные видео

⚡ <b>Возможности</b>
• Генерация с нуля
• Storyboard режим
• Remix существующих видео
• Интерполяция FPS

💎 <b>Приоритет</b>
• Быстрая генерация
• Ранний доступ к функциям

━━━━━━━━━━━━━━━━━━━━

💡 <b>Подходит для:</b> кинематографистов, рекламщиков, режиссёров, креаторов контента
""",
        "prices": """💰 <b>Тарифы:</b>

• Starter (66 credits) — $50/мес
• Plus (200 credits) — $200/мес
• Pro (1000 credits) — $500/мес

<i>1 credit ≈ 1 секунда видео</i>""",
        "features": ["60 сек видео", "4K Quality", "Text/Image to Video", "Storyboard", "Priority"]
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
        [InlineKeyboardButton("─────────────", callback_data="divider")],
        [InlineKeyboardButton("ℹ️ О нас", callback_data="about_us")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="reviews")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton("🛡️ Гарантии", callback_data="guarantees")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_catalog_keyboard() -> InlineKeyboardMarkup:
    """Каталог с выбором нейросетей"""
    keyboard = [
        [InlineKeyboardButton("🤖 ChatGPT Plus", callback_data="product_chatgpt")],
        [InlineKeyboardButton("✨ Gemini Ultra + Veo", callback_data="product_gemini")],
        [InlineKeyboardButton("🎭 Claude Pro", callback_data="product_claude")],
        [InlineKeyboardButton("🎨 Midjourney", callback_data="product_midjourney")],
        [InlineKeyboardButton("🎬 KlingAI", callback_data="product_klingai")],
        [InlineKeyboardButton("🎥 Sora 2", callback_data="product_sora2")],
        [InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_menu")],
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


def get_info_keyboard() -> InlineKeyboardMarkup:
    """Кнопки для информационных страниц"""
    keyboard = [
        [InlineKeyboardButton("📚 В каталог", callback_data="catalog")],
        [InlineKeyboardButton("💬 Написать менеджеру", callback_data="contact_manager")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# КОМАНДЫ
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start — приветственное сообщение"""
    welcome_text = f"""
🏪 <b>Добро пожаловать в VanessPay!</b>

Ваш надёжный поставщик официальных AI-решений.

━━━━━━━━━━━━━━━━━━━━

<b>🤖 Продаём подписки от:</b>
OpenAI • Google • Anthropic • Midjourney • Kuaishou

<b>⭐ Наши преимущества:</b>
✅ Официальные ключи
✅ Активация за 15 минут
✅ Поддержка 24/7
✅ Гарантия возврата

━━━━━━━━━━━━━━━━━━━━

📊 Уже помогли <b>2,000+</b> клиентам получить доступ к топовым AI!

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


# ============================================
# ОБРАБОТЧИКИ CALLBACK
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback-кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data
    manager_link = f"https://t.me/{MANAGER_USERNAME}"

    # Игнорируем разделители
    if data == "divider":
        return

    # --- Главное меню ---
    if data == "back_to_menu":
        welcome_text = f"""
🏪 <b>Добро пожаловать в VanessPay!</b>

Ваш надёжный поставщик официальных AI-решений.

━━━━━━━━━━━━━━━━━━━━

<b>🤖 Продаём подписки от:</b>
OpenAI • Google • Anthropic • Midjourney • Kuaishou

<b>⭐ Наши преимущества:</b>
✅ Официальные ключи
✅ Активация за 15 минут
✅ Поддержка 24/7
✅ Гарантия возврата

━━━━━━━━━━━━━━━━━━━━

📊 Уже помогли <b>2,000+</b> клиентам получить доступ к топовым AI!

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
            short = product['short_desc']
            catalog_text += f"{name}\n📝 {short}\n\n"
        
        catalog_text += "━━━━━━━━━━━━━━━━━━━━"
        
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

    # --- Статистика ---
    if data == "statistics":
        await query.edit_message_text(
            STATISTICS,
            parse_mode="HTML",
            reply_markup=get_info_keyboard()
        )
        return

    # --- Как это работает ---
    if data == "how_it_works":
        await query.edit_message_text(
            HOW_IT_WORKS,
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
{product['name']}

━━━━━━━━━━━━━━━━━━━━

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

⏰ Среднее время ответа: <b>5-15 минут</b>

💡 <b>Мы поможем:</b>
• Подобрать оптимальный тариф
• Ответить на вопросы
• Провести оплату
• Помочь с активацией
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

💡 Канал обновляется ежедневно!

━━━━━━━━━━━━━━━━━━━━

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

━━━━━━━━━━━━━━━━━━━━

📦 <b>{product['name']}</b>

{product['prices']}

━━━━━━━━━━━━━━━━━━━━

⚠️ <b>Для продолжения:</b>

Напишите менеджеру для:
• Подтверждения заказа
• Выбора способа оплаты
• Получения ключа после оплаты

💳 <b>Доступные способы оплаты:</b>
• Банковская карта (РФ/СНГ)
• СБП (Россия)
• ЮMoney / ЮKassa
• Криптовалюта (BTC, ETH, USDT)
• Другие способы — уточните у менеджера

⏱️ <b>Активация:</b> в течение 15 минут после оплаты

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


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных сообщений"""
    unknown_text = """
🤔 Извините, я не понимаю это сообщение.

Используйте команды:
• /start — Главное меню
• /help — Помощь

или выберите действие в меню ниже 👇
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

    # Обработчик callback-кнопок
    app.add_handler(CallbackQueryHandler(button_handler))

    # Обработчик неизвестных сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    logger.info("✅ Бот готов к работе!")
    print("\n" + "="*50)
    print("🤖 VanessPay Bot успешно запущен!")
    print("="*50 + "\n")

    # Запуск бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
