import datetime
import os
import random

import pytz
import telegram.ext
from telegram import (ParseMode, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext)
from secrets import TELEGRAM_TOKEN, MS_ID, VALENCIA_TIO_ID
from sunday_tour_helper import SundayTourHelper
from common import *


def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def hi(update, context):
    user_to_reply = update.effective_user.first_name
    context.bot.send_message(update.message.chat_id,
                             "Hola %s, soy El Tio Vicente - ¡jolines que mola estar en este chat!" % user_to_reply,
                             parse_mode=ParseMode.HTML)


def bullmarket(update, context):
    user_to_reply = update.effective_user.first_name
    photo_caption = "%s, ¡El Bull Market es Total, celebremos cantemos bailemos!" % user_to_reply
    photo_name = random.choice(os.listdir(MASLATON_MEDIA))
    with open(MASLATON_MEDIA + '/%s' % photo_name, 'rb') as photo_to_send:
        context.bot.send_photo(update.message.chat_id, photo=photo_to_send, caption=photo_caption)


def good_morning_job(context: telegram.ext.CallbackContext):
    logger.info('Sending good morning message')
    with open(TEXT_MEDIA + '/frases_motivacionales.txt') as text_file:
        phrase = random.choice(text_file.read().splitlines()).split('||')
        context.bot.send_message(VALENCIA_TIO_ID,
                                 "Buen día querido grupo.\nQue tengan un día de BM total, y recuerden como alguna vez "
                                 "dijo %s,\n<b>%s</b>" % (
                                     phrase[0], phrase[1]), parse_mode=ParseMode.HTML)


def test(update, context):
    print('asd')


def sunday_tour_handler(update, context):
    user_full_name, user_id = update.effective_user.full_name, update.effective_user.id
    sunday_tour_states['user_id'] = STEP0

    update.message.reply_text(
        'Recuerda que cuando estás solo en el cubículo nadie va a estar allí para decirte por quién debes '
        'votar.\nSolo estás tú, con tu conciencia.\nTú también ayudas a construir la democracia\n\n<b>Ahora '
        'al lio</b>. Primera pregunta:\n<b>%s</b> ' % tour_questions[STEP1], parse_mode=ParseMode.HTML
    )
    return STEP1


def tour_handler_step1(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP2)
    user_full_name, user_id, step1_value = update.effective_user.full_name, update.effective_user.id, update.message.text
    logger.info("STEP1 for %s: %s", user_full_name, step1_value)
    update.message.reply_text(
            'Segunda pregunta: \n <b>%s</b> ' % tour_questions[STEP2], parse_mode=ParseMode.HTML
    )
    return STEP2


def tour_handler_step2(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP3)
    user_full_name, user_id, step1_value = update.effective_user.full_name, update.effective_user.id, update.message.text
    logger.info("STEP2 for %s: %s", user_full_name, step1_value)
    update.message.reply_text(
            'Tercera pregunta: \n <b>%s</b> ' % tour_questions[STEP3], parse_mode=ParseMode.HTML
    )
    return STEP3

def tour_handler_step3(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP4)
    user_full_name, user_id, step1_value = update.effective_user.full_name, update.effective_user.id, update.message.text
    logger.info("STEP3 for %s: %s", user_full_name, step1_value)
    update.message.reply_text(
            'Cuarta pregunta: \n <b>%s</b> ' % tour_questions[STEP4], parse_mode=ParseMode.HTML
    )
    return STEP4

def tour_handler_step4(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP5)
    user_full_name, user_id, step1_value = update.effective_user.full_name, update.effective_user.id, update.message.text
    logger.info("STEP4 for %s: %s", user_full_name, step1_value)
    update.message.reply_text(
            'Gracias por tu aporte a la democracia, el promedio final es: 0'
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


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue
    dp.add_handler(CommandHandler('hi', hi))
    dp.add_handler(CommandHandler('bullmarket', bullmarket))
    dp.add_handler(CommandHandler('test', test))
    dp.add_error_handler(error_callback)

    job_queue.run_daily(good_morning_job, datetime.time(9, 00, 00, 000000, tzinfo=pytz.timezone('Europe/Paris')),
                        days=tuple(range(7)), context=updater)
    decimal_number_pattern = '^[0-9]*[.,]{0,1}[0-9]*$'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('tour', sunday_tour_handler)],
        states={
            STEP1: [MessageHandler(Filters.regex(decimal_number_pattern), tour_handler_step1)],
            STEP2: [MessageHandler(Filters.regex(decimal_number_pattern), tour_handler_step2)],
            STEP3: [MessageHandler(Filters.regex(decimal_number_pattern), tour_handler_step3)],
            STEP4: [MessageHandler(Filters.regex(decimal_number_pattern), tour_handler_step4)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logger.info('VicenteLleBot Starting...')
    main()
