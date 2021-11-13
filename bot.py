# import telegram
import requests
import json
import logging

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CallbackQueryHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
NAME, PHOTO = range(2)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")

    return


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def train(update, context):
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Boy or Girl?'
        ),
    )

    return NAME


def name(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'I see! Please send me a photo of yourself, '
        'so I know what you look like, or send /skip if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def echo(update, context: CallbackContext) -> None:
    file_id = update.message.effective_attachment[3].file_id
    file_obj = context.bot.get_file(file_id=file_id)
    file_raw_url = file_obj['file_path']

    model_url = 'http://localhost:8000/predict_by_url'
    querystring = {'file_url': file_raw_url}
    model_response = requests.post(model_url, params=querystring)

    matched_person = json.loads(model_response.content)

    keyboard = [
        [
            InlineKeyboardButton("Match", callback_data='1'),
            InlineKeyboardButton("Mismatch", callback_data='2'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(matched_person))
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


updater = Updater(token='2116791384:AAGdZw7wCpNgI_WiRsPwyd9F0RbTS9xkswo', use_context=True)

updater.dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
# train_handler = CommandHandler('train', train)
dispatcher.add_handler(start_handler)
# dispatcher.add_handler(train_handler)

echo_handler = MessageHandler(Filters.photo & (~Filters.command), echo)

# Add conversation handler with the states NAME, PHOTO
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('train', train)],
    states={
        NAME: [MessageHandler(Filters.text, name)],
        PHOTO: [MessageHandler(Filters.photo, photo)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)

dispatcher.add_handler(echo_handler)

updater.start_polling()

