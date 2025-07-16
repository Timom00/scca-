#7660678589:AAG5Bo3rAodVO_YiHs4f6jPniKQt8ZBVU1U
#1465940524

from keep_alive import keep_alive
import telebot
import json
import re
import datetime
from telebot import types
import os

# 🔐 Токен бота и ID администратора
TOKEN = "7660678589:AAG5Bo3rAodVO_YiHs4f6jPniKQt8ZBVU1U"
ADMIN_ID = 1465940524
bot = telebot.TeleBot(TOKEN)

# 📁 Файлы для хранения данных
VOTES_FILE = "votes.json"
REPORTS_FILE = "reports.json"

# ❗ Список слов для определения скама
SCAM_KEYWORDS = [
    "заработок", "легкие деньги", "быстрый доход", "инвестиции", "крипта",
    "100% прибыль", "без риска", "гарантированный доход", "пассивный доход",
    "скам", "лохотрон", "пирамида", "бесплатно", "вложение", "легко",
    "финансовая пирамида", "отзывы", "поддержка", "прибыль", "доход", "вывод",
    "минимальная сумма", "акция", "бонус", "платит", "торговля", "биткоин",
    "обман", "скам-проект", "мошенники", "легкие деньги", "работа на дому",
    "без вложений", "заработок в интернете", "прибыль с нуля", "сделай сам",
    "инвестируй", "токены", "форекс", "робот для торговли", "супер доход",
    "программа", "гарантия", "пассивный доход", "сеть", "маркетинг",
    "реферальная программа", "доход до", "заработок онлайн", "проверено",
    "секрет успеха", "мультипликатор", "обещают", "быстрая прибыль",
    "работай дома", "пассивный заработок", "финансовый консультант",
    "подработка", "трейдинг", "зарплата", "финансовый советник",
    "финансовые инвестиции", "акции", "инвестиционный фонд",
    "деньги без риска", "супер предложение", "онлайн бизнес", "платежи",
    "вывод средств", "автоматический доход", "прибыль 100%",
    "заработок с нуля", "гарантированная прибыль", "обучение трейдингу",
    "финансовая пирамида", "лохотрон", "проект с гарантией", "скрытые комиссии",
    "легкий заработок", "доход без вложений", "выплаты", "прямые инвестиции",
    "бот для заработка", "бот для торговли", "скам-проект", "мошенничество",
    "фейк", "обмануть", "ввод денег", "вывод денег", "криптовалюта",
    "финансовая афера", "пирамида", "схема", "быстрый обман", "скрытый обман",
    "сделать деньги быстро", "получить деньги", "сделай деньги",
    "обман пользователей", "платформа", "контакт", "пишите", "direct", 
    "личка", "telegram.me", "whatsapp", "viber", "лично", "персонально", 
    "гарант", "результат", "проверено", "отзывы", "доказательства", 
    "реферал", "партнер", "бонус", "акция", "скидка", "промокод", 
    "ограничено", "последний", "успей",
    "free", "bonus", "investment", "crypto", "earn", "quick", "fast", "money",
    "scam", "fake", "fraud", "win", "winner", "lottery", "prize", "guaranteed",
    "profit", "cash", "deal", "limited offer", "click here", "subscribe",
    "easy money", "work from home", "passive income", "trading bot", "forex",
    "bitcoin", "token", "blockchain", "giveaway", "money back", "investment plan",
    "get rich", "income", "automatic profit", "high returns", "no risk",
    "double your money", "earnings", "make money", "quick cash", "fast profit",
    "financial freedom", "referral", "commission", "multilevel marketing",
    "pyramid scheme", "bonus code", "secret", "exclusive", "urgent", "risk free"
]

# =============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ
# =============================================
def load_json(file):
    """Загружает данные из JSON-файла"""
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file, data):
    """Сохраняет данные в JSON-файл"""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_votes_for_channel(channel_username):
    """Инициализирует запись для канала, если её нет"""
    votes = load_json(VOTES_FILE)
    if channel_username not in votes:
        votes[channel_username] = {"scam": 0, "not_scam": 0, "voters": []}
        save_json(VOTES_FILE, votes)
    return votes[channel_username]

def update_vote(channel_username, user_id, vote_type):
    """Обновляет голосование с проверкой уникальности"""
    votes = load_json(VOTES_FILE)
    
    # Инициализируем, если записи нет
    if channel_username not in votes:
        votes[channel_username] = {"scam": 0, "not_scam": 0, "voters": []}
    
    # Проверяем, голосовал ли уже пользователь
    if str(user_id) in votes[channel_username]["voters"]:
        return False

    if vote_type == "scam":
        votes[channel_username]["scam"] += 1
    else:
        votes[channel_username]["not_scam"] += 1
        
    # Сохраняем ID пользователя как строку
    votes[channel_username]["voters"].append(str(user_id))
    
    save_json(VOTES_FILE, votes)
    return True

def get_vote_stats(channel_username):
    """Возвращает текущую статистику голосов"""
    votes = load_json(VOTES_FILE)
    if channel_username in votes:
        return votes[channel_username]["scam"], votes[channel_username]["not_scam"]
    return 0, 0

# 🔍 Проверка текста на скам-ключи
def contains_scam_keywords(text):
    if not text:
        return False
    text = text.lower()
    for kw in SCAM_KEYWORDS:
        if kw in text:
            return True
    return False

# 📊 ПРОСТАЯ И НАДЕЖНАЯ ПРОВЕРКА КАНАЛА
def check_scam_factors(chat):
    warnings = []
    scam_score = 0

    try:
        # 1. Проверка количества подписчиков
        try:
            members_count = bot.get_chat_members_count(chat.id)
            if members_count < 50:
                warnings.append(f"Мало подписчиков ({members_count})")
                scam_score += 1
        except:
            pass

        # 2. Проверка названия
        title = chat.title
        if title and contains_scam_keywords(title):
            warnings.append("Подозрительные слова в названии")
            scam_score += 2
        
        # 3. Проверка описания
        try:
            description = chat.description
            if description and contains_scam_keywords(description):
                warnings.append("Подозрительные слова в описании")
                scam_score += 2
        except:
            pass

        # 4. Проверка пригласительной ссылки
        try:
            invite_link = chat.invite_link
            if not invite_link:
                invite_link = bot.export_chat_invite_link(chat.id)
                
            if invite_link and ("free" in invite_link or "money" in invite_link or "earn" in invite_link):
                warnings.append("Подозрительная ссылка")
                scam_score += 1
        except:
            pass

        # 5. Проверка аватарки
        try:
            if not chat.photo:
                warnings.append("Нет аватарки")
                scam_score += 1
        except:
            pass

        # 6. Проверка закреплённого сообщения
        try:
            if not chat.pinned_message:
                warnings.append("Нет закрепленного сообщения")
                scam_score += 1
        except:
            pass

    except:
        warnings.append("Не удалось выполнить все проверки")

    return warnings, scam_score

# 💾 Сохранение отчёта
def save_report(report):
    try:
        if not os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, "w") as f:
                json.dump([], f)
                
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        data.append(report)
        
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except:
        pass

# 🚀 Команда /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    try:
        bot.send_message(
            message.chat.id,
            "👋 Привет! Я бот для проверки Telegram-каналов на признаки скама.\n\n"
            "Просто отправь мне @username канала, например:\n"
            "@example\n\n"
            "Или используй команды:\n"
            "/help - справка по использованию\n"
            "/status @канал - проверить статус канала"
        )
    except:
        pass

# 📘 Команда /help
@bot.message_handler(commands=["help"])
def help_handler(message):
    try:
        help_text = (
            "🆘 Помощь по боту\n\n"
            "🔍 Как проверить канал:\n"
            "Просто отправь @username канала (например, @example)\n\n"
            "📊 Команды:\n"
            "/start - начать работу с ботом\n"
            "/status @канал - показать статус канала\n"
            "/help - показать эту справку\n\n"
            "❗ Важно:\n"
            "Бот показывает вероятность скама на основе автоматической проверки."
        )
        bot.reply_to(message, help_text)
    except:
        pass

# 📦 Обработка @тегов каналов
@bot.message_handler(func=lambda m: m.text and m.text.startswith("@"))
def channel_check_handler(message):
    try:
        channel_tag = message.text.strip()
        
        if not re.match(r"^@[A-Za-z0-9_]{5,32}$", channel_tag):
            bot.reply_to(
                message,
                "❗ Пожалуйста, введите корректный тег канала, начинающийся с @ и без пробелов."
            )
            return

        try:
            chat = bot.get_chat(channel_tag)
        except:
            bot.reply_to(message, "❌ Не удалось получить информацию о канале")
            return

        warnings, scam_score = check_scam_factors(chat)
        
        channel_username = channel_tag[1:].lower()
        init_votes_for_channel(channel_username)
        scam_votes, not_scam_votes = get_vote_stats(channel_username)

        # Формирование отчета
        report_lines = [
            f"🔍 Проверка канала: {channel_tag}",
            f"📊 Скам-индекс: {scam_score}/10",
            f"💬 Результат: {'Высокий риск' if scam_score > 5 else 'Средний риск' if scam_score > 2 else 'Низкий риск'}"
        ]
        
        if warnings:
            report_lines.append("\n⚠ Обнаружено:")
            for i, warning in enumerate(warnings[:3], 1):
                report_lines.append(f"{i}. {warning}")
        
        report_text = "\n".join(report_lines)

        # Кнопки голосования
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_scam = types.InlineKeyboardButton("🚫 Скам", callback_data=f"scam|{channel_username}")
        btn_not_scam = types.InlineKeyboardButton("✅ Не скам", callback_data=f"not_scam|{channel_username}")
        markup.add(btn_scam, btn_not_scam)
        
        bot.send_message(
            message.chat.id, 
            report_text,
            reply_markup=markup
        )

        save_report({
            "channel_tag": channel_tag,
            "date": datetime.datetime.now().isoformat(),
            "score": scam_score,
            "user": message.from_user.id
        })
        
    except:
        bot.reply_to(message, "⚠ Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")

# 📊 Команда /status
@bot.message_handler(commands=["status"])
def status_handler(message):
    try:
        parts = message.text.split()
        if len(parts) < 2 or not parts[1].startswith("@"):
            bot.reply_to(message, "❌ Используйте формат: /status @канал")
            return

        channel_tag = parts[1]
        
        try:
            chat = bot.get_chat(channel_tag)
        except:
            bot.reply_to(message, "❌ Не удалось получить информацию о канале")
            return

        warnings, scam_score = check_scam_factors(chat)
        scam_votes, not_scam_votes = get_vote_stats(channel_tag[1:].lower())

        msg = (
            f"📊 Статус канала: {channel_tag}\n"
            f"🔖 Название: {chat.title}\n"
            f"📈 Скам-индекс: {scam_score}/10\n"
            f"💬 Риск: {'Высокий' if scam_score > 5 else 'Средний' if scam_score > 2 else 'Низкий'}\n"
            f"👥 Голоса: 🚫 {scam_votes} | ✅ {not_scam_votes}\n\n"
        )
        
        if warnings:
            msg += "⚠ Проблемы:\n"
            for warning in warnings[:3]:
                msg += f"- {warning}\n"
        
        # Кнопки голосования
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_scam = types.InlineKeyboardButton("🚫 Скам", callback_data=f"scam|{channel_tag[1:]}")
        btn_not_scam = types.InlineKeyboardButton("✅ Не скам", callback_data=f"not_scam|{channel_tag[1:]}")
        markup.add(btn_scam, btn_not_scam)
        
        bot.reply_to(message, msg, reply_markup=markup)
        
    except:
        bot.reply_to(message, "⚠ Произошла ошибка при обработке команды")

# ✅ Обработка голосов
@bot.callback_query_handler(func=lambda call: True)
def handle_vote(call):
    try:
        if '|' not in call.data:
            return
            
        vote_type, channel_username = call.data.split('|', 1)
        
        if vote_type not in ['scam', 'not_scam']:
            return

        success = update_vote(channel_username, call.from_user.id, vote_type)
        if not success:
            bot.answer_callback_query(call.id, "❗ Вы уже голосовали за этот канал")
            return
            
        bot.answer_callback_query(call.id, "✅ Спасибо за ваш голос!")
        
        scam_votes, not_scam_votes = get_vote_stats(channel_username)
        
        try:
            # Обновляем сообщение
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=call.message.text + f"\n\n✅ Ваш голос учтен! Текущие голоса: 🚫 {scam_votes} | ✅ {not_scam_votes}",
                reply_markup=call.message.reply_markup
            )
        except:
            pass
        
    except:
        try:
            bot.answer_callback_query(call.id, "⚠ Ошибка обработки голоса")
        except:
            pass

# 📤 Команда /export (только для администратора)
@bot.message_handler(commands=["export"])
def export_handler(message):
    try:
        if message.from_user.id != ADMIN_ID:
            return
            
        # Отправляем файл с голосами
        if os.path.exists(VOTES_FILE):
            with open(VOTES_FILE, "rb") as v:
                bot.send_document(message.chat.id, v, caption="Файл голосований")
        
        # Отправляем файл с отчетами
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, "rb") as r:
                bot.send_document(message.chat.id, r, caption="Файл отчетов")
            
    except:
        pass

# 📥 Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "👋 Для проверки канала отправьте его @username (например, @example)\nИспользуйте /help для справки")

# 🚀 Запуск бота
if __name__ == "__main__":
    # Создаем файлы, если не существуют
    for file in [VOTES_FILE, REPORTS_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({} if file == VOTES_FILE else [], f)
    
    print("Бот запущен...")
    bot.infinity_polling()
