import os, sys
import time
import json

from win10toast import ToastNotifier

def read_conf_file(file_path: str = 'conf.json') -> dict:
    with open(file_path, encoding='utf-8') as file:
        res = json.load(file)
    return res

def send_notification() -> None:
    if sys.platform == 'win32':
        send_windows_notification()
    elif sys.platform == 'linux':
        send_linux_notification()
    elif sys.platform == 'darwin':
        send_macos_notification()
    else:
        sys.exit('Error: Cannot determine your operation system.')

def send_linux_notification() -> None:
    os.system(
        'notify-send "{text}" "{title}"'\
        .format(
        text=notification_text,
        title=notification_title)
    )

def send_macos_notification() -> None:
    os.system(
        'osascript -e \'display notification "{text}" with title "{title}"\''\
        .format(
        text=notification_text,
        title=notification_title,
        )
    )

def send_windows_notification() -> None:
    Toaster: ToastNotifier = ToastNotifier()
    Toaster.show_toast(
        notification_title,
        notification_text,
        'media/attention.ico')

if __name__ == '__main__':
    conf_data: dict = read_conf_file()
    notification_text: str = conf_data['notification_text']
    notification_title: str = conf_data['notification_title']
    program_sleep_delay: int = conf_data['delay']
    
    while True:
        time.sleep(program_sleep_delay)
        send_notification()
