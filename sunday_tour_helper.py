from telegram import ParseMode, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackContext
from common import (
    logger,
    STEP1,
    STEP2,
    STEP3,
    STEP4,
    STEP5,
    tour_questions,
    TOUR_DOMINICAL_TEMPLATE,
    DIO_EH_FECHA,
    COMMON_USER_NAME,
    DIO_EH_CATEGORY,
)
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

    def finish_voting(self, update: Update, context: CallbackContext):
        user_full_name, user_id = self.get_user_values_from_message(update)
        average = sum(self.user_values[user_id]) / 4
        update.message.reply_text(
            "Gracias por tu aporte a la democracia, el promedio final es: %s"
            % str(average)
        )
        self.persist_vote(
            self.current_fecha_nr, user_full_name, "Promedio Final", average
        )
        return ConversationHandler.END

    def persist_vote(self, fecha_nr, user_name, category, value):
        sql_insert_query = """insert into sunday_tour_values('fecha_nr', 'user_name','category', 'value') values (?, ?, ?, ?)"""
        self.db_cursor.execute(sql_insert_query, (fecha_nr, user_name, category, value))
        self.conn.commit()

    def set_fecha_nr(self, update: Update, context: CallbackContext):
        self.current_fecha_nr = int(update.message.text)
        update.message.reply_text(
            "Location de la nueva fecha: ",
            parse_mode=ParseMode.HTML,
        )
        return STEP2

    def set_fecha_location(self, update: Update, context: CallbackContext):
        self.current_fecha_location = update.message.text
        update.message.reply_text(
            "Date(DD/MM/YY) de la nueva fecha: ",
            parse_mode=ParseMode.HTML,
        )
        return STEP3

    def set_fecha_date(self, update: Update, context: CallbackContext):
        current_fecha_date = datetime.strptime(update.message.text, "%d/%m/%y").date()
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

    def get_date_and_location_of_fecha(self, fecha_nr):
        date_and_location_query = (
            """select  date, location from sunday_tour_metadata where fecha_nr = ?"""
        )
        result = self.get_one_value_query_result(date_and_location_query, [fecha_nr])
        return result[0], result[1]

    def get_otorgo_palabra(self, fecha_nr):
        otorgo_value_query = (
            """select value from sunday_tour_values where fecha_nr=? and category=?"""
        )
        result = self.get_one_value_query_result(
            otorgo_value_query, [fecha_nr, DIO_EH_CATEGORY]
        )
        if result:
            return result[0]
        return "No Value"

    def parse_fecha_result(self, fecha_nrs):
        if fecha_nrs:
            fecha_data_query = (
                """select * from v_groupped_fecha_results where fecha_nr in (%s)"""
                % self.parse_list_to_sqlite(fecha_nrs)
            )
        else:
            fecha_data_query = """select * from v_groupped_fecha_results """
        fecha_result_strings = {}
        fecha_totals = {}
        for (
            r_fecha_nr,
            r_user_name,
            r_pre_cal_val,
            r_tiem_val,
            r_aten_val,
            r_amb_val,
            r_prom_val,
        ) in self.conn.execute(fecha_data_query):
            args_fecha = (
                r_user_name,
                r_pre_cal_val,
                r_tiem_val,
                r_aten_val,
                r_amb_val,
                r_prom_val,
            )
            fecha_result_strings.setdefault(r_fecha_nr, []).append(args_fecha)
            fecha_totals[r_fecha_nr] = fecha_totals.get(r_fecha_nr, 0) + r_prom_val
        full_strings = []

        for fecha_nr in fecha_result_strings.keys():
            formatted_fecha = self.format_fecha(fecha_result_strings[fecha_nr])
            fecha_date, fecha_location = self.get_date_and_location_of_fecha(fecha_nr)
            fecha_participants_count = len(fecha_result_strings[fecha_nr])
            fecha_average = fecha_totals[fecha_nr] / fecha_participants_count
            otorgo_palabra = self.get_otorgo_palabra(fecha_nr)
            total_text = TOUR_DOMINICAL_TEMPLATE.format(
                fecha_nr=str(fecha_nr),
                fecha_location=fecha_location,
                fecha_date=fecha_date,
                fecha_all_strings=formatted_fecha,
                otorgo_palabra=otorgo_palabra,
                fecha_average=fecha_average,
            )
            full_strings.append(total_text)
        return full_strings

    def format_fecha(self, rows):
        lens = []
        to_ret = []
        for col in zip(*rows):
            lens.append(max([len(str(v)) for v in col]))
        format = "  ".join(["{:<" + str(l) + "}" for l in lens])
        for row in rows:
            to_ret.append(format.format(*row))
        return "```\n" + "\n".join(x for x in to_ret) + "\n```"

    def fecha_result_handler(self, update: Update, context: CallbackContext):
        try:
            fecha_nr = context.args
            results = self.parse_fecha_result(fecha_nr)
        except Exception as e:
            error_msg = ":( error parsing in fecha_result_handler - try with /fecha [fecha_nr] for specific fecha or /fecha for all fechas"
            return self.format_error_message(update, context, error_msg, e)

        for result_st in results:
            context.bot.send_message(
                update.message.chat_id,
                result_st,
                parse_mode=ParseMode.MARKDOWN,
            )

    def dioeh_handler_step0(self, update: Update, context: CallbackContext):
        update.message.reply_text("Dio un eh? Seleccione fecha")
        return STEP1

    def dioeh_handler_step1(self, update: Update, context: CallbackContext):
        fecha_nr = int(update.message.text)
        context.chat_data[DIO_EH_FECHA] = fecha_nr
        reply_keyboard = [["Eh", "Como", "Que", "No otorgó", "No fue pedido", "Otro"]]
        update.message.reply_text(
            "Palabra magica otorgada en la fecha %s? " % fecha_nr,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, selective=True),
        )
        return STEP2

    def dioeh_handler_step2(self, update: Update, context: CallbackContext):
        fecha = context.chat_data[DIO_EH_FECHA]
        palabra_otorgada = update.message.text
        self.persist_vote(fecha, COMMON_USER_NAME, DIO_EH_CATEGORY, palabra_otorgada)
        del context.chat_data[DIO_EH_FECHA]
        update.message.reply_text(
            "Palabra Otorgada %s, por la fecha %s ha sido registrada"
            % (palabra_otorgada, fecha),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
