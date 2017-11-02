import pyautogui
import random
import threading
import time

from repeat_click_thread import RepeatClickThread
from util import *

pyautogui.PAUSE = .1
pyautogui.FAILSAFE = True


class _SingleValueWrapper:
    """
    Simple wrapper for one value.
    """

    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FiniteStateClickingMachine:
    """
    A finite state machine that actively seeks first available targets to transition fo any subsequent state.
    """

    def __init__(self):
        """
        Initializes an empty finite state clicking machine.
        """
        # A double map keyed first by from_state, then to_state, and holds the click_target_path as values.
        # All states should exist as keys of this map. Existence at second level depends on the presence of transitions.
        self.transitions = {}
        self.state_click_pos = {}
        self.click_thread = None
        self.click_pos_provider = None
        self.mouse_action_lock = None
        self.alive = True

    def add_state(self, state_name, repeated_click_pos=None):
        """
        Adds a state. No-op if the state name already exists.
        :param state_name: A unique identifying string of the state
        :param repeated_click_pos: A tuple that represents where the state want the mouse to click while it in
        """
        check_not_none(state_name)
        self.transitions[state_name] = self.transitions.get(state_name, {})
        self.state_click_pos[state_name] = repeated_click_pos

    def add_transition(self, from_state, to_state, click_target_path):
        """
        Adds a transition: from_state ---click_target---> to_state, overriding existing ones if conflicts exist.
        :param from_state: The state where we will be actively detecting the click target to click on.
        :param to_state: The state that the machine transitions to after clicking on the target.
        :param click_target_path: The path to the click target png.
        """
        to_state_target_map = self.transitions[from_state]
        click_targets = to_state_target_map.get(to_state, [])
        click_targets.append(click_target_path)
        to_state_target_map[to_state] = click_targets

    def run(self, state):
        """
        Runs the finite state clicking machine with a delay of 3s. This is forever-blocking.
        :param state: Starting state of the machine.
        """
        self.mouse_action_lock = threading.Lock()
        self.click_pos_provider = _SingleValueWrapper(None)
        self.click_thread = RepeatClickThread(self.click_pos_provider, self.mouse_action_lock,
                                              name='background_clicking_daemon')
        self.click_thread.start()
        while self.alive:
            print('Start polling at state {}'.format(state))
            state = self._pollAtState(state)
            # Sleep a random period of time
            time.sleep(random.expovariate(2))
        self.click_thread.join()

    def die(self):
        self.alive = False
        self.click_thread.die()

    def _pollAtState(self, state):
        """
        Polls until any applicable click target is found, and click on the target.
        :param state: State at which we are polling.
        :return: State to which we are transitioning to after the click.
        """
        self.click_pos_provider.set(self.state_click_pos[state])
        possible_transitions = self.transitions[state]
        while self.alive:
            for to_state in possible_transitions:
                for click_target in possible_transitions[to_state]:
                    if not self.alive:
                        return
                    print("\tTrying to match {}".format(click_target))
                    # Either the tuple (x,y) where we want to click, or None.
                    match_pos_center = pyautogui.locateCenterOnScreen(click_target)
                    if match_pos_center is None:
                        continue
                    # Click and move the mouse out so that in case the click failed, we can re-detect.
                    self.mouse_action_lock.acquire()
                    pyautogui.click(match_pos_center)
                    pyautogui.moveTo(RESET_POS)
                    self.mouse_action_lock.release()
                    # Stop the background clicking.
                    self.click_pos_provider.set(None)
                    return to_state
