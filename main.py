import datetime
import logging
import os
import random

import pytz
import telegram.ext
from telegram import (ParseMode)
from telegram.ext import (Updater, CommandHandler)
from secrets import TELEGRAM_TOKEN, MS_ID, VALENCIA_TIO_ID

MASLATON_MEDIA = 'media/maslaton'
TEXT_MEDIA = 'media/text'


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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
                                 "Buen día querido grupo. Que tengan un día de BM total, y recuerden como alguna vez "
                                 "dijo %s, <b>%s</b>" % (
                                     phrase[0], phrase[1]), parse_mode=ParseMode.HTML)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue
    dp.add_handler(CommandHandler('hi', hi))
    dp.add_handler(CommandHandler('bullmarket', bullmarket))
    dp.add_error_handler(error_callback)

    job_queue.run_daily(good_morning_job, datetime.time(9, 00, 00, 000000, tzinfo=pytz.timezone('Europe/Paris')),
                        days=tuple(range(7)), context=updater)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logger.info('VicenteLleBot Starting...')
    main()
