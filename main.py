import datetime
import os
import random

import pytz
import telegram.ext
from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from secrets import TELEGRAM_TOKEN, VALENCIA_TIO_ID
from sunday_tour_helper import SundayTourHelper
from common import *


def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def hi(update, context):
    user_to_reply = update.effective_user.first_name
    context.bot.send_message(
        update.message.chat_id,
        "Hola %s, soy El Tio Vicente - ¡jolines que mola estar en este chat!"
        % user_to_reply,
        parse_mode=ParseMode.HTML,
    )


def bullmarket(update, context):
    user_to_reply = update.effective_user.first_name
    photo_caption = (
        "%s, ¡El Bull Market es Total, celebremos cantemos bailemos!" % user_to_reply
    )
    photo_name = random.choice(os.listdir(MASLATON_MEDIA))
    with open(MASLATON_MEDIA + "/%s" % photo_name, "rb") as photo_to_send:
        context.bot.send_photo(
            update.message.chat_id, photo=photo_to_send, caption=photo_caption
        )


def good_morning_job(context: telegram.ext.CallbackContext):
    logger.info("Sending good morning message")
    with open(TEXT_MEDIA + "/frases_motivacionales.txt") as text_file:
        phrase = random.choice(text_file.read().splitlines()).split("||")
        context.bot.send_message(
            VALENCIA_TIO_ID,
            "Buen día querido grupo.\nQue tengan un día de BM total, y recuerden como alguna vez "
            "dijo %s,\n<b>%s</b>" % (phrase[0], phrase[1]),
            parse_mode=ParseMode.HTML,
        )


def sunday_tour_handler(update, context):
    helper = SundayTourHelper()
    fecha_nr = helper.current_fecha_nr
    fecha_location = helper.current_fecha_location
    update.message.reply_text(
        "Recuerda que cuando estás solo en el cubículo nadie va a estar allí para decirte por quién debes "
        "votar.\nSolo estás tú, con tu conciencia.\nTú también ayudas a construir la democracia\n\n<b>Ahora "
        "al lio</b>.\nFecha %s @ %s\n\nPrimera pregunta:\n<b>%s</b> "
        % (fecha_nr, fecha_location, tour_questions[STEP1]),
        parse_mode=ParseMode.HTML,
    )
    return STEP1


def tour_handler_step1(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP2)


def tour_handler_step2(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP3)


def tour_handler_step3(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP4)


def tour_handler_step4(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    helper = SundayTourHelper()
    return helper.steps_handler(update, context, STEP5)


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def new_tour_fecha(update, context):
    context.bot.send_message(
        update.message.chat_id, "Numero de la nueva fecha: ", parse_mode=ParseMode.HTML
    )
    return STEP1


def new_tour_fecha_step1(update, context):
    helper = SundayTourHelper()
    return helper.set_fecha_nr(update, context)


def new_tour_fecha_step2(update, context):
    helper = SundayTourHelper()
    return helper.set_fecha_location(update, context)


def new_tour_fecha_step3(update, context):
    helper = SundayTourHelper()
    return helper.set_fecha_date(update, context)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    job_queue = updater.job_queue
    dp.add_handler(CommandHandler("hi", hi))
    dp.add_handler(CommandHandler("bullmarket", bullmarket))
    # dp.add_error_handler(error_callback)

    job_queue.run_daily(
        good_morning_job,
        datetime.time(9, 00, 00, 000000, tzinfo=pytz.timezone("Europe/Paris")),
        days=tuple(range(7)),
        context=updater,
    )

    tour_data_handler = ConversationHandler(
        entry_points=[CommandHandler("tour", sunday_tour_handler)],
        states={
            STEP1: [
                MessageHandler(
                    Filters.regex(DECIMAL_NUMBER_PATTERN), tour_handler_step1
                )
            ],
            STEP2: [
                MessageHandler(
                    Filters.regex(DECIMAL_NUMBER_PATTERN), tour_handler_step2
                )
            ],
            STEP3: [
                MessageHandler(
                    Filters.regex(DECIMAL_NUMBER_PATTERN), tour_handler_step3
                )
            ],
            STEP4: [
                MessageHandler(
                    Filters.regex(DECIMAL_NUMBER_PATTERN), tour_handler_step4
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    updater.dispatcher.add_handler(tour_data_handler)

    tour_metadata_handler = ConversationHandler(
        entry_points=[CommandHandler("newfecha", new_tour_fecha)],
        states={
            STEP1: [
                MessageHandler(
                    Filters.regex(DECIMAL_NUMBER_PATTERN), new_tour_fecha_step1
                )
            ],
            STEP2: [MessageHandler(Filters.text, new_tour_fecha_step2)],
            STEP3: [MessageHandler(Filters.text, new_tour_fecha_step3)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    updater.dispatcher.add_handler(tour_metadata_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    logger.info("VicenteLleBot Starting...")
    main()
