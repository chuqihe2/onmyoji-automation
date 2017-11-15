import signal

from finite_state_clicking_machine import FiniteStateClickingMachine

CLICK_TARGET_BASE_PATH = 'click_targets/'


def get_image_path(image_name):
    return CLICK_TARGET_BASE_PATH + image_name


fscm = FiniteStateClickingMachine()


def handler(signum, frame):
    fscm.die()


# Set the SIGINT handler to terminate the process cleanly.
signal.signal(signal.SIGINT, handler)

def nlls():
    # =========================================
    # ========= All state identifiers =========
    # =========================================

    REST_CLICK_POS = (2280, 450)

    INITIAL_OR_ZD = 'initial_or_zu_dui'
    fscm.add_state(INITIAL_OR_ZD, repeated_click_pos=REST_CLICK_POS)

    NLLS = 'nlls'
    fscm.add_state(NLLS, repeated_click_pos=REST_CLICK_POS)

    WAIT = 'wait'
    fscm.add_state(WAIT, repeated_click_pos=REST_CLICK_POS)

    # ===============================================
    # ========= FSCM transition definitions =========
    # ===============================================

    fscm.add_transition(INITIAL_OR_ZD, INITIAL_OR_ZD, get_image_path('zudui.png'))
    fscm.add_transition(INITIAL_OR_ZD, NLLS, get_image_path('nlls.png'))
    fscm.add_transition(NLLS, WAIT, get_image_path('auto_queue.png'))
    fscm.add_transition(WAIT, INITIAL_OR_ZD, get_image_path('ready.png'))

    return INITIAL_OR_ZD

def hun10():
    # =========================================
    # ========= All state identifiers =========
    # =========================================

    # The state where we should choose YH difficulty level and start the fight.
    # While waiting, this state might cover the fighting process, in which case we need to repeatedly target the monsters.
    YH_DIFFICULTY_LEVEL = 'yh_difficulty_level'
    YH_DIFFICULTY_LEVEL_CLICK_TARGET = (1380, 580)
    fscm.add_state(YH_DIFFICULTY_LEVEL, YH_DIFFICULTY_LEVEL_CLICK_TARGET)

    # The state where we should set ready to start the actual fight.
    YH_READY = 'yh_ready'
    fscm.add_state(YH_READY)

    # ===============================================
    # ========= FSCM transition definitions =========
    # ===============================================

    fscm.add_transition(YH_DIFFICULTY_LEVEL, YH_DIFFICULTY_LEVEL, get_image_path('yuhun_level.png'))
    fscm.add_transition(YH_DIFFICULTY_LEVEL, YH_READY, get_image_path('yuhun_start.png'))
    fscm.add_transition(YH_READY, YH_DIFFICULTY_LEVEL, get_image_path('ready.png'))

    return YH_DIFFICULTY_LEVEL


try:
    initial_state = nlls()
    fscm.run(initial_state)
except Exception as err:
    print(err)
    fscm.die()
