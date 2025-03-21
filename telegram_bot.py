import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import re
from dotenv import load_dotenv
from telegram_db import (
    app as telegram_app,
    verify_code,
    mark_code_used,
    is_user_registered,
    get_all_registered_user_ids,
    create_tables
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Send notification to a specific user
async def send_notification_to_user(bot, user_id, message, keyboard=None):
    try:
        # إرسال الرسالة بدون علامات تنسيق نصي
        if keyboard:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=keyboard,
                parse_mode=None  # تعطيل وضع التنسيق
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=None  # تعطيل وضع التنسيق
            )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {user_id}: {e}")
        return False

# Send notification to all registered users
async def send_notification_to_all_users(message, include_button=True):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN not set. Cannot send notifications.")
        return False
    
    try:
        application = Application.builder().token(token).build()
        bot = application.bot
        
        # Get all registered users
        with telegram_app.app_context():
            users = get_all_registered_user_ids()
        
        # Create keyboard if needed
        keyboard = None
        if include_button:
            # تأكد من أن عنوان URL صحيح وكامل
            webapp_url = "https://kyc-metabit-test.onrender.com/"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="فتح تطبيق MetaBit Safety",
                    web_app=WebAppInfo(url=webapp_url)
                )]
            ])
        
        # Send notification to each user
        success_count = 0
        for user_id in users:
            success = await send_notification_to_user(bot, user_id, message, keyboard)
            if success:
                success_count += 1
        
        logging.info(f"Notification sent to {success_count}/{len(users)} users")
        return success_count > 0
    except Exception as e:
        logging.error(f"Error sending notifications: {e}")
        return False

# Send notification about new report
async def send_new_report_notification(report_data):
    """
    Send notification about a new report to all registered users
    
    Args:
        report_data: Dictionary containing report information
    
    Returns:
        bool: True if notification was sent successfully
    """
    # Create message with report details
    scammer_name = report_data.get('scammer_name', 'غير محدد').split('|')[0]
    report_type = report_data.get('type', 'غير محدد')
    
    # Translate report type to Arabic
    report_type_ar = {
        'scam': 'نصب واحتيال',
        'debt': 'مديونية',
        'other': 'آخر'
    }.get(report_type, report_type)
    
    message = f"⚠️ تنبيه: تم إضافة بلاغ جديد ⚠️\n\n"
    message += f"📌 نوع البلاغ: {report_type_ar}\n"
    message += f"👤 اسم المبلغ عنه: {scammer_name}\n"
    message += f"\nلمزيد من التفاصيل، يرجى فتح التطبيق."
    
    # Send notification to all registered users
    return await send_notification_to_all_users(message)

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # Check if user is already registered
    with telegram_app.app_context():
        registered = is_user_registered(user_id)
    
    if registered:
        # User is already registered
        webapp_url = "https://kyc-metabit-test.onrender.com/"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="فتح تطبيق MetaBit Safety",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        
        await update.message.reply_text(
            "مرحباً بك مجدداً في MetaBit Safety!\n\n"
            "يمكنك الآن استخدام التطبيق للتحقق من بلاغات النصب والاحتيال.",
            reply_markup=keyboard
        )
    else:
        # User is not registered, ask for registration code
        await update.message.reply_text(
            "مرحباً بك في MetaBit Safety!\n\n"
            "للتسجيل، يرجى إدخال كود التسجيل الخاص بك:"
        )

# Handle registration code verification
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and verify registration codes."""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    message_text = update.message.text
    
    # Check if user is already registered
    with telegram_app.app_context():
        registered = is_user_registered(user_id)
    
    if registered:
        # User is already registered, provide access to the web app
        webapp_url = "https://kyc-metabit-test.onrender.com/"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="فتح تطبيق MetaBit Safety",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        
        await update.message.reply_text(
            "أنت مسجل بالفعل في MetaBit Safety.\n\n"
            "يمكنك استخدام التطبيق للتحقق من بلاغات النصب والاحتيال.",
            reply_markup=keyboard
        )
    else:
        # User is not registered, verify the code
        with telegram_app.app_context():
            valid_code = verify_code(message_text)
        
        if valid_code:
            # Code is valid, register the user
            with telegram_app.app_context():
                mark_code_used(valid_code, user_id, username)
            
            # Provide access to the web app
            webapp_url = "https://kyc-metabit-test.onrender.com/"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="فتح تطبيق MetaBit Safety",
                    web_app=WebAppInfo(url=webapp_url)
                )]
            ])
            
            await update.message.reply_text(
                "تم تسجيلك بنجاح في MetaBit Safety!\n\n"
                "يمكنك الآن استخدام التطبيق للتحقق من بلاغات النصب والاحتيال.",
                reply_markup=keyboard
            )
        else:
            # Code is invalid
            await update.message.reply_text(
                "عذراً، كود التسجيل غير صحيح.\n\n"
                "يرجى التأكد من الكود وإعادة المحاولة، أو التواصل مع المسؤول للحصول على كود جديد."
            )

# Handle web app button
async def web_app_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle web app button click."""
    user = update.effective_user
    user_id = user.id
    
    # Check if user is registered
    with telegram_app.app_context():
        registered = is_user_registered(user_id)
    
    if registered:
        # User is registered, provide access to the web app
        webapp_url = "https://kyc-metabit-test.onrender.com/"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="فتح تطبيق MetaBit Safety",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        
        await update.callback_query.message.reply_text(
            "يمكنك استخدام التطبيق للتحقق من بلاغات النصب والاحتيال.",
            reply_markup=keyboard
        )
    else:
        # User is not registered
        await update.callback_query.message.reply_text(
            "يجب عليك التسجيل أولاً باستخدام كود التسجيل.\n\n"
            "يرجى إدخال كود التسجيل الخاص بك:"
        )

# Command handlers
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "هذا البوت يتيح لك الوصول إلى تطبيق MetaBit Safety.\n"
        "استخدم الأوامر التالية:\n"
        "/start - لبدء استخدام البوت\n"
        "/help - لعرض هذه الرسالة المساعدة\n"
        "/open - لفتح التطبيق المصغر (متاح فقط للمستخدمين المسجلين)"
    )

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the mini app if user is registered."""
    user = update.effective_user
    
    if is_user_registered(user.id):
        webapp_url = "https://kyc-metabit-test.onrender.com/"
        keyboard = [
            [InlineKeyboardButton(
                text="فتح تطبيق MetaBit Safety",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "اضغط على الزر أدناه لفتح التطبيق المصغر:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "عذراً، يجب عليك التسجيل أولاً باستخدام كود التسجيل.\n"
            "استخدم الأمر /start للبدء."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set. Cannot start bot.")
        return
    
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("open", open_app))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add callback query handler for web app button
    application.add_handler(CallbackQueryHandler(web_app_button, pattern="^webapp$"))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    with telegram_app.app_context():
        create_tables()
    main()
