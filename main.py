import sqlite3
import os
from telegram import *
from telegram.ext import *

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 6528742142
bot_username = "Num_67bot"

# ========= DATABASE =========
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    invites INTEGER DEFAULT 0
)
""")
conn.commit()

# ========= FUNCTIONS =========
def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    return r[0] if r else 0

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def remove_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def add_invite(user_id):
    cursor.execute("UPDATE users SET invites = invites + 1 WHERE user_id=?", (user_id,))
    conn.commit()

# ========= MENU =========
def main_menu(user_id):
    keyboard = [
        [InlineKeyboardButton("🔥 فري فاير", callback_data="ff"),
         InlineKeyboardButton("🎮 ببجي", callback_data="pubg")],

        [InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
         InlineKeyboardButton("💳 شحن", callback_data="deposit")],

        [InlineKeyboardButton("🎁 هدية", callback_data="daily"),
         InlineKeyboardButton("🏆 المتصدرين", callback_data="top")],

        [InlineKeyboardButton("👥 دعوة", callback_data="ref"),
         InlineKeyboardButton("ℹ️ شرح", callback_data="help")]
    ]

    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("👑 لوحة التحكم", callback_data="admin")])

    return InlineKeyboardMarkup(keyboard)

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    if context.args:
        try:
            inviter = int(context.args[0])
            if inviter != user_id:
                add_balance(inviter, 0.10)
                add_invite(inviter)
        except:
            pass

    await update.message.reply_text("👋 أهلاً بيك في البوت 🔥", reply_markup=main_menu(user_id))

# ========= BUTTON =========
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "balance":
        await query.edit_message_text(f"💰 رصيدك: {get_balance(user_id)} ₽")

    elif query.data == "daily":
        add_balance(user_id, 0.15)
        await query.edit_message_text("🎁 خد 0.15 ₽")

    elif query.data == "ref":
        link = f"https://t.me/{bot_username}?start={user_id}"
        await query.edit_message_text(f"👥 رابطك:\n{link}\n\n💰 كل دعوة = 0.10 ₽")

    elif query.data == "help":
        await query.edit_message_text("بوت شحن ألعاب + رصيد 💰🔥")

    elif query.data == "top":
        cursor.execute("SELECT user_id, invites FROM users ORDER BY invites DESC LIMIT 5")
        data = cursor.fetchall()
        text = "🏆 المتصدرين:\n\n"
        for i, u in enumerate(data, 1):
            text += f"{i}- {u[0]} | {u[1]} دعوة\n"
        await query.edit_message_text(text)

    elif query.data == "deposit":
        await query.message.reply_text(
            "💳 فودافون كاش\n\n📱 01003052922\n\n💰 10 روبل = 55 جنيه\n\nابعت إثبات 📸"
        )
        context.user_data["pay"] = True

    elif query.data == "ff":
        await query.message.reply_text("🎮 ابعت ID:")
        context.user_data["game"] = "ff"
        context.user_data["wait_id"] = True

    elif query.data == "pubg":
        await query.message.reply_text("🎮 ابعت ID:")
        context.user_data["game"] = "pubg"
        context.user_data["wait_id"] = True

    elif query.data.startswith("ff_") or query.data.startswith("pubg_"):

        prices = {
            "ff_100": 10, "ff_310": 25, "ff_520": 40, "ff_1060": 75,
            "pubg_60": 10, "pubg_325": 45, "pubg_660": 80, "pubg_1800": 200
        }

        price = prices.get(query.data, 0)

        if get_balance(user_id) < price:
            await query.edit_message_text("❌ رصيدك مش كفاية")
            return

        remove_balance(user_id, price)

        player_id = context.user_data.get("player_id")

        keyboard = [[InlineKeyboardButton("تم التنفيذ ✅", callback_data=f"done_{user_id}")]]

        await context.bot.send_message(
            ADMIN_ID,
            f"📥 طلب جديد\n👤 {user_id}\n🎮 ID: {player_id}\n📦 {query.data}\n💰 {price}₽",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await query.edit_message_text("⏳ تم خصم الرصيد وإرسال الطلب")

    elif query.data.startswith("done_"):
        if user_id == ADMIN_ID:
            target = int(query.data.split("_")[1])
            await context.bot.send_message(target, "✅ تم تنفيذ طلبك 🔥")
            await query.edit_message_text("تم التنفيذ")

    elif query.data == "admin":
        keyboard = [
            [InlineKeyboardButton("➕ إضافة رصيد", callback_data="addbal")],
            [InlineKeyboardButton("📢 إذاعة", callback_data="bc")]
        ]
        await query.edit_message_text("👑 لوحة التحكم", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "addbal":
        await query.message.reply_text("ابعت: id المبلغ")
        context.user_data["addbal"] = True

    elif query.data == "bc":
        await query.message.reply_text("ابعت الرسالة")
        context.user_data["bc"] = True

# ========= MESSAGE =========
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get("wait_id"):
        context.user_data["player_id"] = update.message.text
        context.user_data["wait_id"] = False

        game = context.user_data["game"]

        if game == "ff":
            keyboard = [
                [InlineKeyboardButton("💎100 = 10₽", callback_data="ff_100"),
                 InlineKeyboardButton("💎310 = 25₽", callback_data="ff_310")],
                [InlineKeyboardButton("💎520 = 40₽", callback_data="ff_520"),
                 InlineKeyboardButton("💎1060 = 75₽", callback_data="ff_1060")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("60 UC = 10₽", callback_data="pubg_60"),
                 InlineKeyboardButton("325 UC = 45₽", callback_data="pubg_325")],
                [InlineKeyboardButton("660 UC = 80₽", callback_data="pubg_660"),
                 InlineKeyboardButton("1800 UC = 200₽", callback_data="pubg_1800")]
            ]

        await update.message.reply_text("💎 اختار الباقة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif context.user_data.get("pay"):
        keyboard = [[InlineKeyboardButton("تم الشحن ✅", callback_data=f"donepay_{user_id}")]]

        if update.message.photo:
            await context.bot.send_photo(
                ADMIN_ID,
                update.message.photo[-1].file_id,
                caption=f"💰 إثبات من {user_id}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        await update.message.reply_text("⏳ تم الإرسال")
        context.user_data["pay"] = False

    elif context.user_data.get("addbal"):
        uid, amount = update.message.text.split()
        add_balance(int(uid), float(amount))
        await update.message.reply_text("تم ✅")
        context.user_data["addbal"] = False

    elif context.user_data.get("bc"):
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        for u in users:
            try:
                await context.bot.send_message(u[0], update.message.text)
            except:
                pass

        await update.message.reply_text("تم الإرسال ✅")
        context.user_data["bc"] = False

# ========= RUN =========
print("BOT RUNNING 🔥")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.ALL, msg))

app.run_polling()
