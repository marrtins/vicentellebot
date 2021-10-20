from telegram import ParseMode
from telegram.ext import ConversationHandler
from common import logger, STEP1, STEP2, STEP3, STEP4, STEP5, tour_questions
from common_helper import CommonHelper
from datetime import datetime


class SundayTourHelper(CommonHelper):
    user_values = {}
    states = {}
    data_table_name = "sunday_tour_values"
    current_fecha_data = {"nr": None, "location": None}

    def __init__(self):
        super().__init__()
        self._current_fecha_nr = (
            self.current_fecha_data["nr"]
            if self.current_fecha_data["nr"]
            else self.get_current_fecha_nr_from_db()
        )
        self._current_fecha_location = (
            self.current_fecha_data["location"]
            if self.current_fecha_data["location"]
            else self.get_current_fecha_location_from_db()
        )

    @property
    def current_fecha_nr(self):
        return self._current_fecha_nr

    @current_fecha_nr.setter
    def current_fecha_nr(self, val):
        self.current_fecha_data["nr"] = val
        self._current_fecha_nr = val

    @property
    def current_fecha_location(self):
        return self._current_fecha_location

    @current_fecha_location.setter
    def current_fecha_location(self, val):
        self.current_fecha_data["location"] = val
        self._current_fecha_location = val

    def get_current_fecha_nr_from_db(self):
        sql_select_query = """select fecha_nr from sunday_tour_metadata ORDER BY fecha_nr DESC LIMIT 1"""
        val = self.db_cursor.execute(sql_select_query).fetchone()[0]
        self.current_fecha_data["nr"] = val
        return val

    def get_current_fecha_location_from_db(self):
        sql_select_query = """select location from sunday_tour_metadata ORDER BY fecha_nr DESC LIMIT 1"""
        val = self.db_cursor.execute(sql_select_query).fetchone()[0]
        self.current_fecha_data["location"] = val
        return val

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
        self.persist_vote(
            self.current_fecha_nr, user_full_name, tour_questions[step - 1], step_value
        )
        if step == STEP5:
            return self.finish_voting(update, context)
        update.message.reply_text(
            "Siguiente pregunta: \n <b>%s</b> " % tour_questions[step],
            parse_mode=ParseMode.HTML,
        )
        return step

    def finish_voting(self, update, context):
        user_full_name, user_id = self.get_user_values_from_message(update)
        step_value = update.message.text
        logger.info("STEP4 for %s: %s", user_full_name, step_value)
        average = str(sum(self.user_values[user_id]) / 4)
        update.message.reply_text(
            "Gracias por tu aporte a la democracia, el promedio final es: %s" % average
        )
        self.persist_vote(
            self.current_fecha_nr, user_full_name, "Promedio Final", step_value
        )
        return ConversationHandler.END

    def persist_vote(self, fecha_nr, user_name, category, value):
        sql_insert_query = """insert into sunday_tour_values('fecha_nr', 'user_name','category', 'value') values (?, ?, ?, ?)"""
        self.db_cursor.execute(sql_insert_query, (fecha_nr, user_name, category, value))
        self.conn.commit()

    def set_fecha_nr(self, update, context):
        self.current_fecha_nr = int(update.message.text)
        context.bot.send_message(
            update.message.chat_id,
            "Location de la nueva fecha: ",
            parse_mode=ParseMode.HTML,
        )
        return STEP2

    def set_fecha_location(self, update, context):
        self.current_fecha_location = update.message.text
        context.bot.send_message(
            update.message.chat_id,
            "Date(DD/MM/YY) de la nueva fecha: ",
            parse_mode=ParseMode.HTML,
        )
        return STEP3

    def set_fecha_date(self, update, context):
        current_fecha_date = datetime.strptime(update.message.text, "%d/%m/%y")
        sql_insert_query = """insert into sunday_tour_metadata('fecha_nr', 'location','date') values (?, ?, ?)"""
        self.db_cursor.execute(
            sql_insert_query,
            (self.current_fecha_nr, self.current_fecha_location, current_fecha_date),
        )
        self.conn.commit()
        context.bot.send_message(
            update.message.chat_id,
            "Nueva fecha added: %s @ %s on %s "
            % (
                self.current_fecha_nr,
                self.current_fecha_location,
                str(current_fecha_date),
            ),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END
