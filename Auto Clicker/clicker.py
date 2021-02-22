from threading import Thread, Event
from typing import Any, Optional
import logging
import json
import os

from pynput.keyboard import Listener, Key
import pyautogui
import pynput

FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%H:%M:%S')
logger = logging.getLogger()

# Events for LEFT MOUSE BUTTON & RIGHT MOUSE BUTTON can help
# stop running daemon threads
lmb_event = Event()
rmb_event = Event()


def exit_clicker() -> None:
    global lmb_thread, rmb_thread
    logging.info('Exiting..')
    exit(0)


def to_lower_case(obj: Any) -> Optional[str]:
    """
    Default ``str.lower()`` function useing only for strings,
    but this function can determine ``obj`` type and not
    getting AttributeError from interpreter.
    """
    if type(obj) is str:
        return obj.lower()


def _normalize_settings(settings: dict) -> None:
    """
    Normalize settings key values.
    """
    for k, v in settings.items():
        settings[k] = to_lower_case(v)


# Dictioanry with data from settings.json file
settings: dict = {}
def setup_settings(filename='settings.json') -> None:
    """
    This function convert json file to python dictionary
    and save data to 'settings' variable.
    """
    global settings
    try:
        with open(filename) as f:
            settings = json.load(f)
            _normalize_settings(settings)
    except FileNotFoundError:
        logging.fatal('Settings file \'%s\' doesn\'t exist.' % filename)
        exit_clicker()


def lmb_clicker(stop_event: Event):
    while not stop_event.is_set():
        pyautogui.leftClick()

def rmb_clicker(stop_event: Event):
    while not stop_event.is_set():
        pyautogui.rightClick()


def start_clicking(mouse_button: str):
    """
    Compact to one function all commands to start emulate
    clicking left or right mouse buttons.
    """
    global lmb_status, rmb_status
    
    if mouse_button == 'left':
        lmb_status = 'clicking'
        lmb_event.clear()
        Thread(target=lmb_clicker, daemon=True, args=(lmb_event,)).start()
        logging.info('Start clicking Left Mouse Button.')
    elif mouse_button == 'right':
        rmb_status = 'clicking'
        rmb_event.clear()
        Thread(target=rmb_clicker, daemon=True, args=(rmb_event,)).start()
        logging.info('Start clicking Right Mouse Button.')


def stop_clicking(mouse_button: str):
    """
    Compact to one function all commands to stop emulate
    clicking left or right mouse buttons.

    Args
     mouse_button: either 'left' (for left mouse button) or
                   'right' (for right mouse button).
    """
    global lmb_status, rmb_status

    if mouse_button == 'left':
        lmb_status = 'sleeping'
        logging.info('Stop clicking Left Mouse Button.')
        lmb_event.set()
    elif mouse_button == 'right':
        rmb_status = 'sleeping'
        logging.info('Stop clicking Right Mouse Button.')
        rmb_event.set()


def _on_press(key):
    global lmb_status, rmb_status
    global lmb_thread, rmb_thread

    if key == Key.backspace:
        exit_clicker()

    elif key.char == settings['LMB']:
        if lmb_status == 'sleeping':
            start_clicking('left')
        elif lmb_status == 'clicking':
            stop_clicking('left')
    
    elif key.char == settings['RMB']:
        if rmb_status == 'sleeping':
            start_clicking('right')
        elif rmb_status == 'clicking':
            stop_clicking('right')

def _on_release(key):
    pass


def action_listener() -> None:
    """
    Infinity loop which listen client keybord events.
    When client click hot key to start auto-clicker
    python scripts begin emulate left mouse button clicks
    (or right mouse button).
    """
    
    with Listener(on_press=_on_press, on_release=_on_release) as listener:
        listener.join()


if __name__ == '__main__':
    # Determine is clicker active: 'sleeping' or 'clicking'
    lmb_status = 'sleeping'
    rmb_status = 'sleeping'

    logger.info('Press BACKSPACE to exit.')
    logger.info('Listening..')
    
    setup_settings()
    action_listener()
