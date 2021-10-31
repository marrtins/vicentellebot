import logging
import sqlite3

MASLATON_MEDIA = "media/maslaton"
TEXT_MEDIA = "media/text"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

sunday_tour_states = {}

STEP0, STEP1, STEP2, STEP3, STEP4, STEP5 = range(6)

tour_questions = {
    STEP1: "Precio/Calidad",
    STEP2: "Tiempo",
    STEP3: "Atención",
    STEP4: "Ambiente",
}

conn = sqlite3.connect("bot_db.sqlite")
DECIMAL_NUMBER_PATTERN = "^[0-9]*[.,]{0,1}[0-9]*$"


TOUR_DOMINICAL_TEMPLATE = """#tourdominical #fecha{fecha_nr} #Tradicion

*Fecha {fecha_nr} @ {fecha_location} ({fecha_date})*

1.Precio/Calidad
2.Tiempo
3.Atención
4.Ambiente
5.Promedio Final
                         
{fecha_all_strings}

Otorgó palabra: *{otorgo_palabra}*
                          
*Total: {fecha_average}*
"""

DIO_EH_FECHA = "DIO_EH_FECHA_KEY"
COMMON_USER_NAME = "COMMON"
DIO_EH_CATEGORY = "Palabra Magica"


BOT_COMMANDS = [
    ("bullmarket", "una regia foto de maslata y el deseo de bullmarket total"),
    ("fecha", "fecha [fecha_nr] para resultado de una o todas las fechas"),
    ("tour", "para agregar los resultados de la fecha vigente"),
    ("newfecha", "para setear y dar comienzo a una nueva fecha"),
    ("diouneh", "para agregar el eh de la fecha vigente"),
]
