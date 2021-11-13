from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler

CHOOSING, PREDICT, PREDICT_RESULT, TRAIN_NAME, TRAIN_PHOTOS = range(5)

def start(update, context):
    reply_keyboard = [['Predict', 'Train']]

    update.message.reply_text(
        'Hi! My name is MordaBot. Choose action:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Choose mode?'
        ),
    )
    return CHOOSING


def predict(update, context):
    reply_keyboard = [['Правильно', 'Неправильно']]

    update.message.reply_text(
        'Распознавание завершено с результатом (бла бла):',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Ну как?'
        ),
    )

    return PREDICT_RESULT


def predict_result_correct(update, context):
    return PREDICT

def predict_result_incorrect(update, context):
    reply_keyboard = [['Predict', 'Train']]

    update.message.reply_text(
        'Ок, понятно. Есть вариант дообучить модель...',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Choose next action?'
        ),
    )
    return CHOOSING

def name(update, context):
    update.message.reply_text(update.message.text + '_ и еще пару фоточек:')
    return TRAIN_PHOTOS


def photos(update, context):
    update.message.reply_text('Ок, учим модель. Попробуйте через пару минут.')
    return PREDICT

def cancel(update, context):
    return ConversationHandler.END

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(text)

    if text == 'Train':
        update.message.reply_text('Имя того кого распознаем:')
        return TRAIN_NAME

    return PREDICT


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.

    updater = Updater(token='2116791384:AAGdZw7wCpNgI_WiRsPwyd9F0RbTS9xkswo')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Predict|Train)$'), regular_choice
                ),
            ],
            PREDICT: [MessageHandler(Filters.photo, predict)],
            PREDICT_RESULT: [
                MessageHandler(Filters.regex('^(Правильно)$'), predict_result_correct),
                MessageHandler(Filters.regex('^(Неправильно)$'), predict_result_incorrect)
            ],
            TRAIN_NAME: [MessageHandler(Filters.text, name)],
            TRAIN_PHOTOS: [MessageHandler(Filters.photo, photos)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('start', start))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
