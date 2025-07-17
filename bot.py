#7660678589:AAG5Bo3rAodVO_YiHs4f6jPniKQt8ZBVU1U
#1465940524

from keep_alive import keep_alive
import telebot
import json
import re
import datetime
from telebot import types
import os
import psycopg2
from psycopg2 import sql
import io

# 🔐 Токен бота и ID администратора
TOKEN = "7660678589:AAG5Bo3rAodVO_YiHs4f6jPniKQt8ZBVU1U"
ADMIN_ID = 1465940524
bot = telebot.TeleBot(TOKEN)

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
# 🗄 КЛАСС ДЛЯ РАБОТЫ С POSTGRESQL
# =============================================
class Database:
    def _init_(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
        self.create_tables()
    
    def create_tables(self):
        with self.conn.cursor() as cur:
            # Таблица для голосов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    id SERIAL PRIMARY KEY,
                    channel_username TEXT NOT NULL UNIQUE,
                    scam_votes INTEGER NOT NULL DEFAULT 0,
                    not_scam_votes INTEGER NOT NULL DEFAULT 0
                );
            """)
            
            # Таблица для голосовавших пользователей
            cur.execute("""
                CREATE TABLE IF NOT EXISTS voters (
                    id SERIAL PRIMARY KEY,
                    vote_id INTEGER NOT NULL REFERENCES votes(id) ON DELETE CASCADE,
                    user_id BIGINT NOT NULL,
                    UNIQUE(vote_id, user_id)
                );
            """)
            
            # Таблица для отчетов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    channel_tag TEXT NOT NULL,
                    check_date TIMESTAMP NOT NULL,
                    scam_score INTEGER NOT NULL,
                    warnings JSONB NOT NULL,
                    user_id BIGINT NOT NULL
                );
            """)
            self.conn.commit()
    
    def init_votes_for_channel(self, channel_username):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO votes (channel_username) 
                VALUES (%s)
                ON CONFLICT (channel_username) DO NOTHING;
            """, (channel_username,))
            self.conn.commit()
    
    def update_vote(self, channel_username, user_id, vote_type):
        try:
            with self.conn.cursor() as cur:
                # Получаем ID голосования
                cur.execute("SELECT id FROM votes WHERE channel_username = %s", (channel_username,))
                vote_row = cur.fetchone()
                if not vote_row:
                    return False
                vote_id = vote_row[0]
                
                # Проверяем, голосовал ли уже
                cur.execute("""
                    SELECT 1 FROM voters 
                    WHERE vote_id = %s AND user_id = %s
                """, (vote_id, user_id))
                if cur.fetchone():
                    return False
                
                # Добавляем голос
                if vote_type == "scam":
                    cur.execute("""
                        UPDATE votes 
                        SET scam_votes = scam_votes + 1 
                        WHERE id = %s
                    """, (vote_id,))
                else:
                    cur.execute("""
                        UPDATE votes 
                        SET not_scam_votes = not_scam_votes + 1 
                        WHERE id = %s
                    """, (vote_id,))
                
                # Фиксируем голосующего
                cur.execute("""
                    INSERT INTO voters (vote_id, user_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (vote_id, user_id))
                
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            return False
    
    def get_vote_stats(self, channel_username):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT scam_votes, not_scam_votes 
                FROM votes 
                WHERE channel_username = %s
            """, (channel_username,))
            result = cur.fetchone()
            return result or (0, 0)
    
    def save_report(self, report_data):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO reports (
                        channel_tag, check_date, scam_score, warnings, user_id
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    report_data['channel_tag'],
                    datetime.datetime.fromisoformat(report_data['check_date']),
                    report_data['scam_score'],
                    json.dumps(report_data['warnings']),
                    report_data['user_id']
                ))
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            self.conn.rollback()
            return False

    def export_votes(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        v.channel_username,
                        v.scam_votes,
                        v.not_scam_votes,
                        ARRAY_AGG(vr.user_id) AS voters
                    FROM votes v
                    LEFT JOIN voters vr ON vr.vote_id = v.id
                    GROUP BY v.id
                """)
                results = {}
                for row in cur.fetchall():
                    results[row[0]] = {
                        "scam": row[1],
                        "not_scam": row[2],
                        "voters": row[3] if row[3] else []
                    }
                return results
        except Exception as e:
            print(f"Error exporting votes: {e}")
            return {}

    def export_reports(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id, channel_tag, check_date, 
                        scam_score, warnings, user_id 
                    FROM reports
                """)
                columns = [desc[0] for desc in cur.description]
                return [
                    dict(zip(columns, row)) 
                    for row in cur.fetchall()
                ]
        except Exception as e:
            print(f"Error exporting reports: {e}")
            return []

# Инициализируем базу данных
db = Database()
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

# 📦 Обработка @тегов каналов
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
    db.init_votes_for_channel(channel_username)
    scam_votes, not_scam_votes = db.get_vote_stats(channel_username)

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

    db.save_report({
        "channel_tag": channel_tag,
        "check_date": datetime.datetime.utcnow().isoformat(),
        "scam_score": scam_score,
        "warnings": warnings,
        "user_id": message.from_user.id
    })

# ✅ Обработка голосов
@bot.callback_query_handler(func=lambda call: True)
def handle_vote(call):
    if '|' not in call.data:
        bot.answer_callback_query(call.id, "❗ Ошибка данных голосования.")
        return
        
    vote_type, channel_username = call.data.split('|', 1)
    
    if vote_type not in ['scam', 'not_scam']:
        bot.answer_callback_query(call.id, "❗ Неизвестный тип голоса.")
        return

    user_id = call.from_user.id
    success = db.update_vote(channel_username, user_id, vote_type)
    
    if not success:
        bot.answer_callback_query(call.id, "❗ Ты уже голосовал за этот канал.")
        return

    bot.answer_callback_query(call.id, "✅ Спасибо за голос!")
    
    scam_votes, not_scam_votes = db.get_vote_stats(channel_username)
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

# 📊 Команда /status
@bot.message_handler(commands=["status"])
def status_handler(message):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        bot.reply_to(message, "❌ Используй формат: /status @канал")
        return

    channel_tag = parts[1]
    channel_username = channel_tag[1:].lower()
    
    scam_votes, not_scam_votes = db.get_vote_stats(channel_username)

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

    bot.reply_to(message, msg)

# 📤 Команда /export (только для администратора)
@bot.message_handler(commands=["export"])
def export_handler(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У тебя нет доступа к этой команде.")
        return

    try:
        # Формируем данные для экспорта
        votes_data = db.export_votes()
        reports_data = db.export_reports()
        
        # Создаем файлы в памяти
        votes_json = json.dumps(votes_data, ensure_ascii=False, indent=2).encode('utf-8')
        reports_json = json.dumps(reports_data, ensure_ascii=False, indent=2, default=str).encode('utf-8')
        
        # Отправляем файлы
        bot.send_document(
            message.chat.id, 
            ('votes.json', io.BytesIO(votes_json)),
            caption="🗳 Экспорт голосов"
        )
        
        bot.send_document(
            message.chat.id, 
            ('reports.json', io.BytesIO(reports_json)),
            caption="📋 Экспорт отчетов"
        )
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при экспорте: {e}")

# 📥 Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "Пожалуйста, отправь тег канала (@example) для проверки.")

# 🚀 Запуск бота
if __name__ == "__main__":
    keep_alive()
    print("Бот запущен с PostgreSQL...")
    bot.infinity_polling()
