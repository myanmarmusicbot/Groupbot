#!/usr/bin/env python3
"""
Telegram Group Management Bot
Owner and Support သီးခြားခွဲထားပါတယ်
Railway အတွက် Environment Variable သုံးထားပါတယ်
"""

import os
import logging
import re
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.constants import ChatMemberStatus

# ==================== CONFIGURATION ====================
# Environment Variables ကနေ ဖတ်မယ် (Railway အတွက်)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))  # Owner Telegram ID
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "owner_username")  # without @
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "support_username")  # without @
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "channel_username")  # without @
LOGGER_GROUP_ID = int(os.environ.get("LOGGER_GROUP_ID", "-100"))  # Logger Group ID

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== FILTERS DATABASE ====================
# Simple in-memory storage (Use MongoDB for production)
filters_db = {}

# ==================== HELPER FUNCTIONS ====================
async def is_admin(update: Update, user_id: int = None) -> bool:
    """Check if user is admin in the group"""
    if not user_id:
        user_id = update.effective_user.id
    
    # Owner ဆိုရင် admin လို့ သတ်မှတ်မယ်
    if user_id == OWNER_ID:
        return True
    
    try:
        chat_member = await update.effective_chat.get_member(user_id)
        return chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

def get_user_info(update: Update) -> dict:
    """Get user information for logging"""
    user = update.effective_user
    chat = update.effective_chat
    
    return {
        "user_id": user.id,
        "username": f"@{user.username}" if user.username else "No username",
        "first_name": user.first_name,
        "chat_id": chat.id,
        "chat_title": chat.title if chat.title else "Private Chat",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

async def log_user_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log user activity to logger group"""
    if LOGGER_GROUP_ID == -100:  # Not configured
        return
    
    user_info = get_user_info(update)
    log_message = (
        f"**New User Activity**\n\n"
        f"User ID: `{user_info['user_id']}`\n"
        f"Username: {user_info['username']}\n"
        f"Name: {user_info['first_name']}\n"
        f"Group ID: `{user_info['chat_id']}`\n"
        f"Group: {user_info['chat_title']}\n"
        f"Time: {user_info['date']}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=LOGGER_GROUP_ID,
            text=log_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

# ==================== LINK SHORTENER FUNCTION ====================
async def shorten_links_in_text(text: str) -> str:
    """Detect and shorten links in text"""
    # Simple URL regex
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        return text
    
    for url in urls:
        try:
            # Using TinyURL API (free)
            response = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=5)
            if response.status_code == 200:
                short_url = response.text
                text = text.replace(url, short_url)
        except Exception as e:
            logger.error(f"Error shortening URL {url}: {e}")
            continue
    
    return text

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Shows owner, support, channel info"""
    user = update.effective_user
    
    # Log user activity
    await log_user_activity(update, context)
    
    # Create buttons (Owner, Support, Channel သီးခြားစီ)
    keyboard = [
        [InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("💬 Support Group", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"မင်္ဂလာပါ {user.first_name}!\n\n"
        f"**Bot Information**\n"
        f"👑 Owner: @{OWNER_USERNAME}\n"
        f"💬 Support: @{SUPPORT_USERNAME}\n"
        f"📢 Channel: @{CHANNEL_USERNAME}\n\n"
        f"Group ထဲမှာ Admin လုပ်ပြီး /help ရိုက်ကြည့်ပါ။"
    )
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup, 
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = (
        "**Available Commands:**\n\n"
        "**User Commands:**\n"
        "/start - Bot စတင်ခြင်း\n"
        "/help - ဒီအကူအညီစာ\n\n"
        "**Filter Commands (Admin only):**\n"
        "/filter <keyword> <reply> - Filter ထည့်ရန်\n"
        "/filters - Filter အားလုံးကြည့်ရန်\n"
        "/del <keyword> - Filter ဖျက်ရန်\n\n"
        "**Admin Commands:**\n"
        "/ban - User ကို Ban လုပ်ရန် (Reply နဲ့သုံးပါ)\n"
        "/mute - User ကို Mute လုပ်ရန် (Reply နဲ့သုံးပါ)\n"
        "/unmute - User ကို Unmute လုပ်ရန် (Reply နဲ့သုံးပါ)\n\n"
        "**Features:**\n"
        "• Links တွေကို အလိုအလျောက် Shorten လုပ်ပေးမယ်\n"
        "• User Activity ကို Logger Group ကို ပို့မယ်\n"
        "• Owner ဝင်လာရင် Special Message ပြမယ်"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new members joining"""
    for member in update.message.new_chat_members:
        # Log new member
        await log_user_activity(update, context)
        
        # If owner joins, send special message
        if member.id == OWNER_ID:
            await update.message.reply_text(
                f"👑 **ကျွန်တော့်ကို ဖန်တီးထားတဲ့သူ ရောက်ရှိလာပါပြီ** 👑\n\n"
                f"Welcome Master @{OWNER_USERNAME}",
                parse_mode="Markdown"
            )
        else:
            # Normal welcome message
            welcome_msg = f"Welcome {member.mention_html()} to the group!"
            await update.message.reply_text(welcome_msg, parse_mode="HTML")

# ==================== FILTERS ====================
async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new filter"""
    if not await is_admin(update):
        await update.message.reply_text("❌ ဒီ Command ကို Admin များသာ သုံးနိုင်ပါသည်။")
        return
    
    chat_id = update.effective_chat.id
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text("Usage: /filter <keyword> <reply>")
        return
    
    keyword = args[0].lower()
    reply_text = " ".join(args[1:])
    
    if chat_id not in filters_db:
        filters_db[chat_id] = {}
    
    filters_db[chat_id][keyword] = reply_text
    await update.message.reply_text(
        f"✅ Filter ထည့်ပြီးပါပြီ။\nKeyword: `{keyword}`", 
        parse_mode="Markdown"
    )

async def list_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all filters in the chat"""
    chat_id = update.effective_chat.id
    
    if chat_id not in filters_db or not filters_db[chat_id]:
        await update.message.reply_text("📭 Filter တစ်ခုမှ မရှိသေးပါ။")
        return
    
    filter_list = "**Filters in this chat:**\n\n"
    for keyword in filters_db[chat_id]:
        filter_list += f"• `{keyword}`\n"
    
    await update.message.reply_text(filter_list, parse_mode="Markdown")

async def delete_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a filter"""
    if not await is_admin(update):
        await update.message.reply_text("❌ Admin များသာ သုံးနိုင်ပါသည်။")
        return
    
    chat_id = update.effective_chat.id
    args = context.args
    
    if not args:
        await update.message.reply_text("Usage: /del <keyword>")
        return
    
    keyword = args[0].lower()
    
    if chat_id in filters_db and keyword in filters_db[chat_id]:
        del filters_db[chat_id][keyword]
        await update.message.reply_text(
            f"✅ Filter `{keyword}` ကို ဖျက်ပြီးပါပြီ။", 
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ `{keyword}` filter မရှိပါ။", 
            parse_mode="Markdown"
        )

async def check_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if message matches any filter"""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()
    
    if chat_id in filters_db:
        for keyword, reply in filters_db[chat_id].items():
            if keyword in message_text:
                await update.message.reply_text(reply)
                break

# ==================== BAN / MUTE ====================
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user from the group"""
    if not await is_admin(update):
        await update.message.reply_text("❌ Admin များသာ သုံးနိုင်ပါသည်။")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User တစ်ယောက်ကို Reply လုပ်ပြီးမှ သုံးပါ။")
        return
    
    user_to_ban = update.message.reply_to_message.from_user
    
    try:
        await update.effective_chat.ban_member(user_to_ban.id)
        await update.message.reply_text(f"✅ {user_to_ban.first_name} ကို Ban လိုက်ပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ Ban လုပ်လို့မရပါ။ Error: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mute a user (restrict from sending messages)"""
    if not await is_admin(update):
        await update.message.reply_text("❌ Admin များသာ သုံးနိုင်ပါသည်။")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User တစ်ယောက်ကို Reply လုပ်ပြီးမှ သုံးပါ။")
        return
    
    user_to_mute = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    
    try:
        # Mute for 1 hour by default
        until_date = datetime.now() + timedelta(hours=1)
        await context.bot.restrict_chat_member(
            chat_id,
            user_to_mute.id,
            permissions=ChatMember(can_send_messages=False),
            until_date=until_date
        )
        await update.message.reply_text(f"✅ {user_to_mute.first_name} ကို 1 နာရီ Mute လိုက်ပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ Mute လုပ်လို့မရပါ။ Error: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unmute a user"""
    if not await is_admin(update):
        await update.message.reply_text("❌ Admin များသာ သုံးနိုင်ပါသည်။")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ User တစ်ယောက်ကို Reply လုပ်ပြီးမှ သုံးပါ။")
        return
    
    user_to_unmute = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    
    try:
        await context.bot.restrict_chat_member(
            chat_id,
            user_to_unmute.id,
            permissions=ChatMember(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(f"✅ {user_to_unmute.first_name} ကို Unmute လိုက်ပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ Unmute လုပ်လို့မရပါ။ Error: {e}")

# ==================== MESSAGE HANDLER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    if not update.message or not update.message.text:
        return
    
    # First check filters
    await check_filter(update, context)
    
    # Then shorten links if any
    original_text = update.message.text
    shortened_text = await shorten_links_in_text(original_text)
    
    # If links were shortened, send the shortened version
    if shortened_text != original_text:
        await update.message.reply_text(
            f"**Shortened Links:**\n\n{shortened_text}",
            parse_mode="Markdown"
        )

# ==================== CALLBACK HANDLER ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Button clicked: {query.data}")

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    # Check required environment variables
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Please set environment variable.")
        return
    
    if OWNER_ID == 0:
        logger.warning("OWNER_ID not set! Some features may not work.")
    
    if OWNER_USERNAME == "owner_username":
        logger.warning("OWNER_USERNAME not set! Using default.")
    
    if SUPPORT_USERNAME == "support_username":
        logger.warning("SUPPORT_USERNAME not set! Using default.")
    
    if CHANNEL_USERNAME == "channel_username":
        logger.warning("CHANNEL_USERNAME not set! Using default.")
    
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Filter Commands
    application.add_handler(CommandHandler("filter", add_filter))
    application.add_handler(CommandHandler("filters", list_filters))
    application.add_handler(CommandHandler("del", delete_filter))
    
    # Admin Commands
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    
    # Message Handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Callback Handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error Handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    logger.info(f"Owner: @{OWNER_USERNAME}")
    logger.info(f"Support: @{SUPPORT_USERNAME}")
    logger.info(f"Channel: @{CHANNEL_USERNAME}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
