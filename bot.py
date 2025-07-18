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
SCAMLIST_FILE = "scamlist.json"
VOTES_FILE = "votes.json"
REPORTS_FILE = "reports.json"

# ❗ Полный список слов для определения скама
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
    "обман пользователей", "платформа",
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
# ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ (ПЕРЕРАБОТАННЫЕ)
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
# =============================================

# 🔍 Проверка текста на скам-ключи
def contains_scam_keywords(text):
    if not text:
        return False
    text = text.lower()
    for kw in SCAM_KEYWORDS:
        if kw in text:
            return True
    return False

# 🔗 Проверка ссылки на скамность
def check_url_scammy(url):
    scam_url_keywords = [
        "free", "bonus", "investment", "crypto", "earn", "quick", "fast", "money"
    ]
    if not url:
        return False
    url = url.lower()
    for kw in scam_url_keywords:
        if kw in url:
            return True
    return False

# 📊 ПОЛНАЯ проверка канала
def check_scam_factors(chat):
    warnings = []
    scam_score = 0

    try:
        members_count = bot.get_chat_members_count(chat.id)
        if members_count < 50:
            warnings.append(f"Подписчиков всего {members_count} — мало.")
            scam_score += 1
    except:
        pass

    if contains_scam_keywords(chat.title):
        warnings.append("В названии канала есть подозрительные слова.")
        scam_score += 2

    try:
        description = bot.get_chat(chat.id).description
        if description and contains_scam_keywords(description):
            warnings.append("В описании канала есть подозрительные слова.")
            scam_score += 2
    except:
        pass

    try:
        invite_link = bot.export_chat_invite_link(chat.id)
        if invite_link and check_url_scammy(invite_link):
            warnings.append("Ссылка канала содержит подозрительные слова.")
            scam_score += 1
    except:
        pass

    try:
        if bot.get_chat(chat.id).photo is None:
            warnings.append("У канала нет аватарки.")
            scam_score += 1
    except:
        pass

    try:
        if bot.get_chat(chat.id).pinned_message is None:
            warnings.append("У канала нет закреплённого сообщения.")
            scam_score += 1
    except:
        pass

    return warnings, scam_score

# 💾 Сохранение отчёта
def save_report(report):
    try:
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Убедимся, что data - это список
        if not isinstance(data, list):
            data = []
    except:
        data = []
    data.append(report)
    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 🚀 Команда /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    try:
        with open("_655fbf78-b4c0-4ecc-81cc-e50ef3a8830f.jpeg", "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=(
                     "✨✨✨✨✨✨✨✨✨✨\n"
                    "         🤖 ScamDetector Bot         \n"
                    "-----------------------------------\n"
                    "🔍 Проверяю каналы на признаки скама\n"
                    "👍 Система голосования сообщества\n"
                    "📊 Статистика по каналам\n"
                    "🛡 Помогаю избегать мошенников\n"
                    "-----------------------------------\n"
                    "Просто отправь мне @username канала!\n\n"
                    "📌 Основные команды:\n"
                    "/start - показать это сообщение\n"
                    "/status @канал - показать статус канала\n"
                    "/help - справка по использованию\n"
                     "-----------------------------------\n"
                    "❗ Важно:\n"
                    "Бот показывает вероятность скама на основе автоматической проверки и голосования сообщества. "
                    "Всегда проверяйте информацию самостоятельно!"

                )
            )
    except Exception as e:
        bot.reply_to(message, "Не удалось отправить стартовую картинку.")

# 📘 Команда /help
@bot.message_handler(commands=["help"])
def help_handler(message):
    help_text = (
        "🆘 Помощь по боту\n\n"
        "🔍 Как проверить канал:\n"
        "Просто отправь @username канала (например, @example)\n\n"
        "📊 Команды:\n"
        "/start - начать работу с ботом\n"
        "/status @канал - показать статус канала\n"
        "/help - показать эту справку\n\n"
        "❗ Важно:\n"
        "Бот показывает вероятность скама на основе автоматической проверки и голосования сообщества. "
        "Всегда проверяйте информацию самостоятельно!"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")


# 📦 Обработка @тегов каналов (ИСПРАВЛЕНО ФОРМИРОВАНИЕ CALLBACK_DATA)
@bot.message_handler(func=lambda m: m.text and m.text.startswith("@"))
def channel_check_handler(message):
    channel_tag = message.text.strip()
    
    if not re.match(r"^@[A-Za-z0-9_]{5,32}$", channel_tag):
        bot.reply_to(
            message,
            "❗ Пожалуйста, введите корректный тег канала, начинающийся с @ и без пробелов."
        )
        return

    try:
        chat = bot.get_chat(channel_tag)
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось получить канал: {e}")
        return

    warnings, scam_score = check_scam_factors(chat)
    
    channel_username = channel_tag[1:].lower()
    init_votes_for_channel(channel_username)
    scam_votes, not_scam_votes = get_vote_stats(channel_username)

    if scam_score >= 3:
        verdict = "🚨 Высокая вероятность скама!"
    elif scam_score == 0:
        verdict = "✅ Канал выглядит безопасным."
    else:
        verdict = "⚠ Есть подозрительные признаки."

    report_lines = [verdict]
    
    if warnings:
        report_lines.append("\n⚠ Предупреждения:")
        report_lines += [f"- {w}" for w in warnings]
    
    report_lines.append(f"\n📊 Скам-баллы: {scam_score}/7")
    report_lines.append(f"🚫 Голосов 'Скам': {scam_votes}")
    report_lines.append(f"✅ Голосов 'Не скам': {not_scam_votes}")

    report_text = "\n".join(report_lines)

    bot.reply_to(message, report_text)

    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # ИСПРАВЛЕНО: используем новый формат callback_data
    btn_scam = types.InlineKeyboardButton(
        "🚫 Скам", callback_data=f"scam|{channel_username}")
    btn_not_scam = types.InlineKeyboardButton(
        "✅ Не скам", callback_data=f"not_scam|{channel_username}")
    markup.add(btn_scam, btn_not_scam)
    
    bot.send_message(
        message.chat.id, 
        "Как ты думаешь, это скам?", 
        reply_markup=markup
    )

    save_report({
        "channel_tag": channel_tag,
        "check_date": datetime.datetime.utcnow().isoformat(),
        "scam_score": scam_score,
        "warnings": warnings,
        "user_id": message.from_user.id
    })

# ✅ Обработка голосов (ПОЛНОСТЬЮ ПЕРЕРАБОТАННАЯ)
@bot.callback_query_handler(func=lambda call: True)
def handle_vote(call):
    # Проверяем формат callback_data
    if '|' not in call.data:
        bot.answer_callback_query(call.id, "❗ Ошибка данных голосования.")
        return
        
    # Разбиваем данные на тип голоса и username канала
    vote_type, channel_username = call.data.split('|', 1)
    
    if vote_type not in ['scam', 'not_scam']:
        bot.answer_callback_query(call.id, "❗ Неизвестный тип голоса.")
        return

    user_id = call.from_user.id

    success = update_vote(channel_username, user_id, vote_type)
    if not success:
        bot.answer_callback_query(call.id, "❗ Ты уже голосовал за этот канал.")
        return

    bot.answer_callback_query(call.id, "✅ Спасибо за голос!")
    
    scam_votes, not_scam_votes = get_vote_stats(channel_username)
    stat_text = (
        f"📊 Обновленная статистика для @{channel_username}:\n"
        f"🚫 Скам: {scam_votes}\n"
        f"✅ Не скам: {not_scam_votes}"
    )
    
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_scam = types.InlineKeyboardButton(
            "🚫 Скам", callback_data=f"scam|{channel_username}")
        btn_not_scam = types.InlineKeyboardButton(
            "✅ Не скам", callback_data=f"not_scam|{channel_username}")
        markup.add(btn_scam, btn_not_scam)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=stat_text,
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"{stat_text}\n\nОбнови сообщение вручную.", reply_markup=markup)

# 📊 Команда /status (ИСПРАВЛЕННЫЙ ФОРМАТ CALLBACK_DATA)
@bot.message_handler(commands=["status"])
def status_handler(message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        bot.reply_to(message, "❌ Используй формат: /status @канал")
        return

    channel_tag = parts[1]
    channel_username = channel_tag[1:].lower()
    
    scam_votes, not_scam_votes = get_vote_stats(channel_username)

    try:
        chat = bot.get_chat(channel_tag)
        title = chat.title
        channel_id = chat.id
        warnings, scam_score = check_scam_factors(chat)
    except Exception as e:
        title = "Неизвестно"
        channel_id = "Неизвестно"
        scam_score = 0
        warnings = []

    msg = (
        f"📊 Статистика канала {channel_tag}\n"
        f"🔖 Название: {title}\n"
        f"🆔 ID: {channel_id}\n\n"
        f"🔍 Результаты проверки:\n"
        f"⚠ Скам-баллы: {scam_score}/7\n\n"
        f"🗳 Голосование сообщества:\n"
        f"🚫 Голосов 'Скам': {scam_votes}\n"
        f"✅ Голосов 'Не скам': {not_scam_votes}"
    )

    #markup = types.InlineKeyboardMarkup(row_width=2)
    #btn_scam = types.InlineKeyboardButton(
     #   "🚫 Скам", callback_data=f"scam|{channel_username}")
    #btn_not_scam = types.InlineKeyboardButton(
     #   "✅ Не скам", callback_data=f"not_scam|{channel_username}")
    #markup.add(btn_scam, btn_not_scam)

    bot.reply_to(message, msg)#, reply_markup=markup)

# 📤 Команда /export (только для администратора)
@bot.message_handler(commands=["export"])
def export_handler(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У тебя нет доступа к этой команде.")
        return

    try:
        # Отправляем файл с голосами
        if os.path.exists(VOTES_FILE):
            with open(VOTES_FILE, "rb") as v:
                bot.send_document(message.chat.id, v, caption="🗳 Файл голосований")
        else:
            bot.reply_to(message, "Файл голосований не найден.")
        
        # Отправляем файл с отчетами
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, "rb") as r:
                bot.send_document(message.chat.id, r, caption="📋 Файл отчетов")
        else:
            bot.reply_to(message, "Файл отчетов не найден.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при экспорте: {e}")

# 📥 Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "Пожалуйста, отправь тег канала (@example) для проверки.")

# 🚀 Запуск бота
if __name__ == "__main__":
    # Инициализация файлов при первом запуске
    if not os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    
    if not os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    
    if not os.path.exists(SCAMLIST_FILE):
        with open(SCAMLIST_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    
    keep_alive()
    print("Бот запущен...")
    bot.infinity_polling()
