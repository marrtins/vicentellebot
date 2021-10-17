import logging
MASLATON_MEDIA = 'media/maslaton'
TEXT_MEDIA = 'media/text'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

sunday_tour_states = {}

STEP0, STEP1, STEP2, STEP3, STEP4, STEP5 = range(6)

tour_questions = {
    STEP1: 'Precio/Calidad',
    STEP2: 'Tiempo',
    STEP3: 'Atención',
    STEP4: 'Ambiente',
}

