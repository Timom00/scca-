#7660678589:AAG5Bo3rAodVO_YiHs4f6jPniKQt8ZBVU1U
#1465940524

import telebot
import json
import datetime
from telebot import types

# ✅ Если ты хочешь работать на Render — импортируем веб-сервер
from keep_alive import keep_alive

# 🔐 Токен бота
TOKEN = "7660678589:AAG5Bo3rAodVO_YiHs4f6jPniKQt8ZBVU1U"
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# 📁 Файлы для хранения отчётов и голосов
REPORTS_FILE = "reports.json"
VOTES_FILE = "votes.json"

# ❗️ Слова, по которым определяется возможный скам
SCAM_KEYWORDS = [
    "free", "bonus", "investment", "crypto", "earn", "quick", "fast",
    "money", "scam", "fake", "click", "win"
]

# 🔍 Проверка текста на скам-ключи
def contains_scam_keywords(text):
    if not text:
        return False
    text = text.lower()
    return any(kw in text for kw in SCAM_KEYWORDS)

# 🔗 Проверка ссылки на скамность
def check_url_scammy(url):
    if not url:
        return False
    url = url.lower()
    return any(kw in url for kw in SCAM_KEYWORDS)

# 📊 Основная проверка канала
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
    except:
        data = []
    data.append(report)
    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 💾 Сохранение голоса
def save_vote(channel_tag, vote):
    try:
        with open(VOTES_FILE, "r", encoding="utf-8") as f:
            votes = json.load(f)
    except:
        votes = {}

    if channel_tag not in votes:
        votes[channel_tag] = {"scam": 0, "not_scam": 0}

    if vote == "scam":
        votes[channel_tag]["scam"] += 1
    elif vote == "not_scam":
        votes[channel_tag]["not_scam"] += 1

    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(votes, f, indent=4, ensure_ascii=False)

# 📥 Получение статистики по голосам
def get_votes(channel_tag):
    try:
        with open(VOTES_FILE, "r", encoding="utf-8") as f:
            votes = json.load(f)
        return votes.get(channel_tag, {"scam": 0, "not_scam": 0})
    except:
        return {"scam": 0, "not_scam": 0}

# 🚀 Команда /start
@bot.message_handler(commands=["start"])
def start_handler(message):
    try:
        with open("_655fbf78-b4c0-4ecc-81cc-e50ef3a8830f.jpeg", "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=("✨" * 10 + "\n"
                         "         🤖 *Этот бот умеет:*         \n"
                         "-----------------------------------\n"
                         "🔍 Проверять каналы на скам\n"
                         "👍 Позволяет голосовать за канал\n"
                         "📊 Показывать статистику голосов\n"
                         "🛡 Помогать избегать мошенников\n"
                         "-----------------------------------\n"
                         "Отправь `@username` канала, чтобы проверить его!\n"
                         "Отправь `/status @username`, чтобы узнать статус!"),
                parse_mode="Markdown"
            )
    except Exception as e:
        bot.reply_to(message, "Не удалось отправить стартовую картинку.")

# 📦 Обработка @тегов каналов
@bot.message_handler(func=lambda m: m.text and m.text.startswith("@"))
def channel_check_handler(message):
    channel_tag = message.text.strip()

    try:
        chat = bot.get_chat(channel_tag)
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось получить канал: {e}")
        return

    warnings, scam_score = check_scam_factors(chat)

    report_lines = [
        f"📊 Проверка канала: {channel_tag}",
        f"Название: {chat.title}",
        f"ID: {chat.id}",
        f"Скам-баллы: {scam_score}",
        ""
    ]

    if warnings:
        report_lines.append("⚠️ Предупреждения:")
        report_lines += [f" - {w}" for w in warnings]
    else:
        report_lines.append("✅ Подозрений не найдено.")

    report_text = "\n".join(report_lines)

    try:
        bot.reply_to(message, report_text)
    except:
        pass

    # 🗳 Голосование
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("💀 Скам", callback_data=f"vote_scam|{channel_tag}"),
            types.InlineKeyboardButton("✅ Не скам", callback_data=f"vote_not_scam|{channel_tag}")
        )
        bot.send_message(message.chat.id, "Как ты думаешь, это скам?", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при показе голосования: {e}")

    # 💾 Сохраняем отчёт
    save_report({
        "channel_tag": channel_tag,
        "check_date": datetime.datetime.utcnow().isoformat(),
        "scam_score": scam_score,
        "warnings": warnings,
        "user_id": message.from_user.id
    })

# ✅ Обработка голосов
@bot.callback_query_handler(func=lambda call: call.data.startswith("vote_"))
def handle_vote(call):
    action, channel_tag = call.data.split("|")
    vote_type = "scam" if action == "vote_scam" else "not_scam"
    save_vote(channel_tag, vote_type)
    bot.answer_callback_query(call.id, "Спасибо за голос!")

# 📊 Команда /status
@bot.message_handler(commands=["status"])
def status_handler(message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        bot.reply_to(message, "❌ Используй формат: /status @канал")
        return

    channel_tag = parts[1]
    votes = get_votes(channel_tag)

    try:
        chat = bot.get_chat(channel_tag)
        title = chat.title
        channel_id = chat.id
    except:
        title = "Неизвестно"
        channel_id = "Неизвестно"

    msg = (
        f"📊 Статистика канала {channel_tag}\n"
        f"Название: {title}\n"
        f"ID: {channel_id}\n\n"
        f"💀 Голосов 'скам': {votes['scam']}\n"
        f"✅ Голосов 'не скам': {votes['not_scam']}"
    )

    bot.reply_to(message, msg)
# Команда /export — отправка файлов с голосами и отчётами (только для владельца)
@bot.message_handler(commands=["export"])
def export_handler(message):
    ADMIN_ID = 1465940524  # Замени на свой Telegram ID (число)
    
    if message.from_user.id == ADMIN_ID:
        try:
            with open("votes.json", "rb") as v:
                bot.send_document(message.chat.id, v, caption="🗳 Голоса")
            with open("reports.json", "rb") as r:
                bot.send_document(message.chat.id, r, caption="📋 Отчёты")
        except Exception as e:
            bot.reply_to(message, "❌ Не удалось отправить файлы.")
    else:
        bot.reply_to(message, "⛔ У тебя нет доступа к этой команде.")

# 📥 Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "Пожалуйста, отправь тег канала (@example) для проверки.")

# 🚀 Запуск бота
if __name__ == "__main__":
    keep_alive()  # 🟢 Включаем фоновый веб-сервер
    print("Бот запущен...")
    bot.infinity_polling()
