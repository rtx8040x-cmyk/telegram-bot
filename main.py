import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")  # مهم جدًا
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

def add_invite(user_id):
    cursor.execute("UPDATE users SET invites = invites + 1 WHERE user_id=?", (user_id,))
    conn.commit()

# ========= MENU =========
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 فري فاير", callback_data="ff"),
         InlineKeyboardButton("🎮 ببجي", callback_data="pubg")],

        [InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
         InlineKeyboardButton("💳 شحن", callback_data="deposit")],

        [InlineKeyboardButton("🎁 هدية", callback_data="daily"),
         InlineKeyboardButton("🏆 المتصدرين", callback_data="top")],

        [InlineKeyboardButton("👥 دعوة", callback_data="ref"),
         InlineKeyboardButton("ℹ️ شرح", callback_data="help")]
    ])

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

    await update.message.reply_text("👋 أهلاً بيك في البوت 🔥", reply_markup=main_menu())

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
        await query.edit_message_text(f"👥 رابط الدعوة:\n{link}\n\n💰 كل دعوة = 0.10 ₽")

    elif query.data == "help":
        await query.edit_message_text(
            "📌 شرح البوت:\n\n💰 اشحن رصيد\n🎁 هدية يومية\n🔥 شحن ألعاب\n👥 اربح من الدعوات"
        )

    elif query.data == "top":
        cursor.execute("SELECT user_id, invites FROM users ORDER BY invites DESC LIMIT 5")
        data = cursor.fetchall()
        text = "🏆 المتصدرين:\n\n"
        for i, u in enumerate(data, 1):
            text += f"{i}- {u[0]} | {u[1]} دعوة\n"
        await query.edit_message_text(text)

    elif query.data == "deposit":
        await query.message.reply_text(
            "💳 فودافون كاش\n📱 01003052922\n\n💰 10 روبل = 55 جنيه\n📸 ابعت صورة التحويل"
        )
        context.user_data["pay"] = True

    elif query.data.startswith("ff_") or query.data.startswith("pubg_"):
        keyboard = [[InlineKeyboardButton("تم التنفيذ ✅", callback_data=f"done_{user_id}")]]
        await context.bot.send_message(
            ADMIN_ID,
            f"📥 طلب جديد\n👤 {user_id}\n📦 {query.data}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.edit_message_text("⏳ تم إرسال الطلب")

    elif query.data.startswith("done_"):
        if user_id == ADMIN_ID:
            target = int(query.data.split("_")[1])
            await context.bot.send_message(target, "✅ تم تنفيذ طلبك")
            await query.edit_message_text("تم التنفيذ")

# ========= MESSAGE =========
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get("pay"):
        if update.message.photo:
            await context.bot.send_photo(
                ADMIN_ID,
                update.message.photo[-1].file_id,
                caption=f"💰 إثبات\n👤 {user_id}"
            )
        await update.message.reply_text("⏳ تم إرسال الإثبات")
        context.user_data["pay"] = False

# ========= RUN =========
print("BOT RUNNING 🔥")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.ALL, msg))

app.run_polling()
