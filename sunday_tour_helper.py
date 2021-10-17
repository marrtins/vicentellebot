from telegram import ParseMode
from telegram.ext import ConversationHandler
from common import *


class SundayTourHelper:
    user_values = {}
    states = {}

    def get_user_values_from_message(self, update):
        return update.effective_user.full_name, update.effective_user.id

    def steps_handler(self, update, context, step):
        user_full_name, user_id = self.get_user_values_from_message(update)
        step_value = float(update.message.text)
        logger.info("STEP%d for %s: %s", step - 1, user_full_name, step_value)
        if user_id not in self.user_values:
            self.user_values[user_id] = []
        self.user_values[user_id].append(step_value)
        self.states[user_id] = step - 1
        if step == STEP5:
            return self.finish_voting(update, context)
        update.message.reply_text(
            'Siguiente pregunta: \n <b>%s</b> ' % tour_questions[step], parse_mode=ParseMode.HTML
        )
        return step

    def finish_voting(self, update, context):
        user_full_name, user_id = self.get_user_values_from_message(update)
        step_value = update.message.text
        logger.info("STEP4 for %s: %s", user_full_name, step_value)
        average = str(sum(self.user_values[user_id]) / 4)
        update.message.reply_text(
            'Gracias por tu aporte a la democracia, el promedio final es: %s' % average
        )
        return ConversationHandler.END
