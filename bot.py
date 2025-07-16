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

# ❗ Расширенный список слов для определения скама
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

# Список подозрительных доменов
SUSPICIOUS_DOMAINS = [
    "bit.ly", "t.me", "tinyurl.com", "cutt.ly", "shorte.st", "clck.ru",
    "cutt.us", "bc.vc", "adf.ly", "ouo.io", "shrinkme.io", "linkvertise.com",
    "shortconnect.com", "link.tl", "shorturl.at", "rebrand.ly"
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

# 🔗 Проверка ссылки на скамность
def check_url_scammy(url):
    if not url:
        return False
    url = url.lower()
    
    # Проверка ключевых слов
    scam_url_keywords = [
        "free", "bonus", "investment", "crypto", "earn", "quick", "fast", "money"
    ]
    for kw in scam_url_keywords:
        if kw in url:
            return True
            
    # Проверка подозрительных доменов
    for domain in SUSPICIOUS_DOMAINS:
        if domain in url:
            return True
            
    return False

# 📊 ПОЛНАЯ ПРОФЕССИОНАЛЬНАЯ ПРОВЕРКА КАНАЛА
def check_scam_factors(chat):
    warnings = []
    scam_score = 0

    # 1. Проверка количества подписчиков
    try:
        members_count = bot.get_chat_members_count(chat.id)
        if members_count < 50:
            warnings.append(f"Подписчиков всего {members_count} — подозрительно мало.")
            scam_score += 1
        elif members_count > 100000 and members_count % 1000 == 0:
            warnings.append(f"Слишком ровное количество подписчиков ({members_count}) — возможны боты.")
            scam_score += 1
    except Exception as e:
        warnings.append(f"⚠ Не удалось проверить количество подписчиков: {str(e)}")

    # 2. Проверка названия
    title = chat.title
    if contains_scam_keywords(title):
        warnings.append(f"В названии '{title}' есть подозрительные слова.")
        scam_score += 2
    
    # 3. Проверка эмодзи в названии
    emoji_count = sum(1 for char in title if char in "🎉🚀🔥💸💰💵💯🆓🤑💎✨🌟📈")
    if emoji_count > 3:
        warnings.append(f"Слишком много эмодзи в названии ({emoji_count}) — признак агрессивного маркетинга.")
        scam_score += 1

    # 4. Проверка описания
    try:
        description = bot.get_chat(chat.id).description
        if description:
            if contains_scam_keywords(description):
                warnings.append("В описании найдены подозрительные слова.")
                scam_score += 2
            
            # Проверка на контактные данные (признак мошенников)
            if re.search(r"\b(контакт|пишите|direct|личка|@|telegram\.me|whatsapp|viber)\b", description, re.IGNORECASE):
                warnings.append("В описании просят связаться лично — типичный признак мошенников.")
                scam_score += 2
                
            # Проверка на срочность
            if re.search(r"\b(срочно|быстро|успей|последний шанс|ограничено)\b", description, re.IGNORECASE):
                warnings.append("Используется давление через срочность — техника мошенников.")
                scam_score += 1
    except Exception as e:
        warnings.append(f"⚠ Не удалось проверить описание: {str(e)}")

    # 5. Проверка пригласительной ссылки
    try:
        invite_link = bot.export_chat_invite_link(chat.id)
        if invite_link:
            if check_url_scammy(invite_link):
                warnings.append("Ссылка приглашения содержит подозрительные слова.")
                scam_score += 1
            
            # Проверка на сокращенные URL
            if any(domain in invite_link for domain in SUSPICIOUS_DOMAINS):
                warnings.append("Используется сокращенная ссылка — может скрывать фишинговый URL.")
                scam_score += 1
    except Exception as e:
        warnings.append(f"⚠ Не удалось проверить пригласительную ссылку: {str(e)}")

    # 6. Проверка аватарки
    try:
        if bot.get_chat(chat.id).photo is None:
            warnings.append("Отсутствует аватарка — признак временного канала.")
            scam_score += 1
    except Exception as e:
        warnings.append(f"⚠ Не удалось проверить аватарку: {str(e)}")

    # 7. Проверка закреплённого сообщения
    try:
        pinned_msg = bot.get_chat(chat.id).pinned_message
        if pinned_msg is None:
            warnings.append("Нет закреплённого сообщения — необычно для нормального канала.")
            scam_score += 1
        elif pinned_msg.text:
            # Проверка закрепленного сообщения на скам-содержимое
            if contains_scam_keywords(pinned_msg.text):
                warnings.append("В закреплённом сообщении найдены подозрительные слова.")
                scam_score += 2
                
            # Проверка на просьбы перевести деньги
            if re.search(r"\b(переведите|оплатите|купите|взнос|инвестируйте)\b", pinned_msg.text, re.IGNORECASE):
                warnings.append("В закреплённом сообщении просят деньги — явный признак скама.")
                scam_score += 3
    except Exception as e:
        warnings.append(f"⚠ Не удалось проверить закрепленное сообщение: {str(e)}")

    # 8. Проверка даты создания канала (если доступно)
    try:
        if hasattr(chat, 'date'):
            creation_date = datetime.datetime.fromtimestamp(chat.date)
            channel_age = (datetime.datetime.now() - creation_date).days
            
            if channel_age < 7:
                warnings.append(f"Канал создан очень недавно ({channel_age} дней назад) — высокий риск.")
                scam_score += 2
            elif channel_age < 30:
                warnings.append(f"Канал создан недавно ({channel_age} дней назад) — средний риск.")
                scam_score += 1
    except:
        pass

    # 9. Проверка на скрытую рекламу
    try:
        # Проверка последних сообщений (если доступно)
        messages = bot.get_chat_history(chat.id, limit=5)
        scam_message_count = 0
        
        for msg in messages:
            if msg.text and contains_scam_keywords(msg.text):
                scam_message_count += 1
        
        if scam_message_count >= 3:
            warnings.append(f"В последних сообщениях найдены подозрительные слова ({scam_message_count}/5).")
            scam_score += 2
    except:
        # Обычно недоступно без админских прав
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
                    "❗ Важно:\n"
                    "Бот показывает вероятность скама на основе автоматической проверки и голосования сообщества. "
                    "Всегда проверяйте информацию самостоятельно!"
                    "🔍 Проверяю каналы на признаки скама\n"
                    "👍 Система голосования сообщества\n"
                    "📊 Статистика по каналам\n"
                    "🛡 Помогаю избегать мошенников\n"
                    "-----------------------------------\n"
                    "Просто отправь мне @username канала!\n\n"
                    "📌 Основные команды:\n"
                    "/start - показать это сообщение\n"
                    "/status @канал - показать статус канала\n"
                    "/help - справка по использованию"
                ),
                parse_mode="Markdown"
            )
    except Exception as e:
        bot.reply_to(message, "👋 Привет! Я бот для проверки каналов на скам. Просто отправь мне @username канала, который хочешь проверить!")

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
        except Exception as e:
            bot.reply_to(message, "❌ Не удалось получить данные канала. Возможно:\n- Канал не существует\n- Бот заблокирован в канале\n- Ошибка доступа")
            return

        warnings, scam_score = check_scam_factors(chat)
        
        channel_username = channel_tag[1:].lower()
        init_votes_for_channel(channel_username)
        scam_votes, not_scam_votes = get_vote_stats(channel_username)

        # Определение уровня риска
        if scam_score >= 8:
            verdict = "🚨🚨 КРИТИЧЕСКИЙ РИСК! Высокая вероятность скама!"
            risk_emoji = "🔴🔴🔴"
        elif scam_score >= 5:
            verdict = "⚠⚠ ВЫСОКИЙ РИСК! Вероятно скам!"
            risk_emoji = "🔴🔴"
        elif scam_score >= 3:
            verdict = "⚠ СРЕДНИЙ РИСК! Есть подозрительные признаки!"
            risk_emoji = "🟠"
        elif scam_score > 0:
            verdict = "🟡 НИЗКИЙ РИСК! Незначительные проблемы."
            risk_emoji = "🟡"
        else:
            verdict = "✅ БЕЗОПАСНЫЙ КАНАЛ! Риски не обнаружены."
            risk_emoji = "🟢"

        # Формирование отчета
        report_lines = [
            f"{risk_emoji} {verdict}",
            f"🔍 Канал: {channel_tag}",
            f"📊 Скам-индекс: {scam_score}/10"
        ]
        
        if warnings:
            report_lines.append("\n🔎 Обнаруженные проблемы:")
            for i, warning in enumerate(warnings[:5], 1):
                report_lines.append(f"{i}. {warning}")
            if len(warnings) > 5:
                report_lines.append(f"🔸 ...и еще {len(warnings)-5} других проблем")
        
        report_lines.append("\n👥 Голосование сообщества:")
        report_lines.append(f"🚫 Скам: {scam_votes}  |  ✅ Не скам: {not_scam_votes}")
        
        report_lines.append("\n❗ Важно: Это автоматическая оценка. Всегда проверяйте информацию самостоятельно!")

        report_text = "\n".join(report_lines)

        # Кнопки голосования
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_scam = types.InlineKeyboardButton(
            "🚫 Скам", callback_data=f"scam|{channel_username}")
        btn_not_scam = types.InlineKeyboardButton(
            "✅ Не скам", callback_data=f"not_scam|{channel_username}")
        markup.add(btn_scam, btn_not_scam)
        
        bot.send_message(
            message.chat.id, 
            report_text,
            parse_mode="Markdown",
            reply_markup=markup
        )

        save_report({
            "channel_tag": channel_tag,
            "check_date": datetime.datetime.utcnow().isoformat(),
            "scam_score": scam_score,
            "warnings": warnings,
            "user_id": message.from_user.id
        })
    except Exception as e:
        print(f"Ошибка при обработке канала: {e}")
        bot.reply_to(message, "⚠ Произошла внутренняя ошибка при обработке запроса. Пожалуйста, попробуйте позже.")

# ✅ Обработка голосов
@bot.callback_query_handler(func=lambda call: True)
def handle_vote(call):
    try:
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
            bot.answer_callback_query(call.id, "❗ Вы уже голосовали за этот канал.")
            return

        bot.answer_callback_query(call.id, "✅ Ваш голос учтен! Спасибо!")
        
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
                text=call.message.text + f"\n\n{stat_text}",
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception as e:
            bot.send_message(call.message.chat.id, f"{stat_text}\n\nОбновите сообщение вручную.", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка при обработке голоса: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠ Ошибка обработки. Попробуйте позже.")
        except:
            pass

# 📊 Команда /status
@bot.message_handler(commands=["status"])
def status_handler(message):
    try:
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].startswith("@"):
            bot.reply_to(message, "❌ Используйте формат: /status @канал")
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
            bot.reply_to(message, "❌ Не удалось получить данные канала. Проверьте правильность @username.")
            return

        # Определение уровня риска
        if scam_score >= 8:
            risk_level = "КРИТИЧЕСКИЙ РИСК 🔴🔴🔴"
        elif scam_score >= 5:
            risk_level = "ВЫСОКИЙ РИСК 🔴🔴"
        elif scam_score >= 3:
            risk_level = "СРЕДНИЙ РИСК 🟠"
        elif scam_score > 0:
            risk_level = "НИЗКИЙ РИСК 🟡"
        else:
            risk_level = "БЕЗОПАСНЫЙ 🟢"

        msg = (
            f"📊 Статус канала {channel_tag}\n"
            f"🔖 Название: {title}\n"
            f"🆔 ID: {channel_id}\n"
            f"📈 Скам-индекс: {scam_score}/10\n"
            f"⚠ Уровень риска: {risk_level}\n"
        )
        
        # Добавляем причины (первые 3)
        if warnings:
            msg += f"\n🔎 Основные проблемы:\n"
            for i, warning in enumerate(warnings[:3], 1):
                msg += f"▫ {warning}\n"
            if len(warnings) > 3:
                msg += f"▫ ...и еще {len(warnings)-3} проблем\n"
        
        msg += (
            f"\n👥 Голосование сообщества:\n"
            f"🚫 Скам: {scam_votes}  |  ✅ Не скам: {not_scam_votes}\n\n"
            f"❗ Результаты автоматической проверки. Требует вашего внимания!"
        )

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_scam = types.InlineKeyboardButton(
            "🚫 Скам", callback_data=f"scam|{channel_username}")
        btn_not_scam = types.InlineKeyboardButton(
            "✅ Не скам", callback_data=f"not_scam|{channel_username}")
        markup.add(btn_scam, btn_not_scam)

        bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в команде /status: {e}")
        bot.reply_to(message, "⚠ Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.")

# 📤 Команда /export (только для администратора)
@bot.message_handler(commands=["export"])
def export_handler(message):
    try:
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "⛔ У вас нет доступа к этой команде.")
            return

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
        print(f"Ошибка при экспорте: {e}")
        bot.reply_to(message, "⚠ Произошла ошибка при экспорте данных.")

# 📥 Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "👋 Для проверки канала отправьте его @username (например, @example)\nИспользуйте /help для справки")

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
