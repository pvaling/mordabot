from botocore.exceptions import ClientError
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler

from classes.s3uploader import S3Uploader

CHOOSING, PREDICT, PREDICT_RESULT, TRAIN_NAME, TRAIN_PHOTOS = range(5)

PREDICT_LABEL = 'Распознать'
TRAIN_LABEL = 'Обучить'

def start(update, context):
    reply_keyboard = [[PREDICT_LABEL, 'Train']]

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
    update.message.reply_text('Можно еще кого-нибудь распознать... Или /cancel')

    return PREDICT


def predict_result_incorrect(update, context):
    reply_keyboard = [[PREDICT_LABEL, 'Train']]

    update.message.reply_text(
        'Ок, понятно. Есть вариант дообучить модель...',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Choose next action?'
        ),
    )
    return CHOOSING


def name(update, context):
    context.user_data["training_item_label"] = update.message.text

    update.message.reply_text(update.message.text + '_ и еще пару фоточек:')
    return TRAIN_PHOTOS


def photos(update, context):
    # Send files to train dataset

    if update.message.text == 'Хватит':
        reply_keyboard = [[PREDICT_LABEL, 'Train']]

        update.message.reply_text(
            'Ок, учим модель по этим фоткам. Что дальше?:',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder='Choose mode?'
            ),
        )
        return CHOOSING

    uploader = S3Uploader(bucket_name='mordabot')

    tmp_photo_dir = 'tmp_files'

    photo = update.message.photo[-1]

    photo_file = photo.get_file()
    photo_file_extension = photo_file.file_path.split('.')[-1]

    file_full_path = tmp_photo_dir + '/' + photo.file_unique_id + '.' + photo_file_extension
    photo_file.download(file_full_path)

    try:
        response = uploader.upload(source_path=file_full_path, label=context.user_data['training_item_label'])
    except ClientError as e:
        print(e)
        update.message.reply_text('Проблема с заливкой на S3. Я сломался (.')
        return PREDICT


    update.message.reply_text('Круто, давай еще фотку или напиши /Хватит.')
    return TRAIN_PHOTOS


def cancel(update, context):
    return ConversationHandler.END


# def button(update: Update, context: CallbackContext) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query
#
#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     query.answer()
#
#     query.edit_message_text(text=f"Selected option: {query.data}")


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

    updater = Updater(token='2116791384:AAGdZw7wCpNgI_WiRsPwyd9F0RbTS9xkswo', use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex(f'^({PREDICT_LABEL}|Train)$'), regular_choice
                ),
            ],
            PREDICT: [MessageHandler(Filters.photo, predict)],
            PREDICT_RESULT: [
                MessageHandler(Filters.regex('^(Правильно)$'), predict_result_correct),
                MessageHandler(Filters.regex('^(Неправильно)$'), predict_result_incorrect)
            ],
            TRAIN_NAME: [MessageHandler(Filters.text, name)],
            TRAIN_PHOTOS: [MessageHandler(filters=(Filters.photo | Filters.regex('Хватит')), callback=photos)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler('start', start))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
