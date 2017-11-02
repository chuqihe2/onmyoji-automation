import pyautogui
import threading
import time

from util import *


class RepeatClickThread(threading.Thread):
    """
    A background daemon that keeps clicking at whatever position given to it, until notified to die.
    """

    def __init__(self, pos_provider, mouse_action_lock, group=None, name=None, interval=0.3):
        super().__init__(group=group, name=name, daemon=True)
        # The lock that should be obtained while performing any mouse action.
        self.mouse_action_lock = mouse_action_lock
        # True only when this daemon is notified to die.
        self.alive = True
        # Position on the screen that
        self.pos_provider = check_not_none(pos_provider)
        # Rest time between clicks in seconds
        self.interval = interval

    def die(self):
        self.alive = False

    def run(self):
        while self.alive:
            if self.pos_provider.get() is not None:
                self.mouse_action_lock.acquire()
                pyautogui.click(self.pos_provider.get())
                pyautogui.moveTo(RESET_POS)
                self.mouse_action_lock.release()
            time.sleep(self.interval)
