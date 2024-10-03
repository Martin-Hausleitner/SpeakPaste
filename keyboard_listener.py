# keyboard_listener.py
from pynput import keyboard
import logging

class KeyboardListener:
    def __init__(self, app):
        self.app = app
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()
        logging.debug("KeyboardListener started")

    def is_key_match(self, key, key_name):
        from pynput.keyboard import Key
        try:
            key_enum = getattr(Key, key_name.lower())
            return key == key_enum
        except AttributeError:
            try:
                return key.char.lower() == key_name.lower()
            except AttributeError:
                return False

    def on_press(self, key):
        try:
            if self.is_key_match(key, self.app.shortcut_record):
                logging.debug(f"Key pressed: {key}, toggling recording")
                self.toggle_recording()
            elif self.is_key_match(key, self.app.shortcut_paste_record):
                logging.debug(f"Key pressed: {key}, starting record and paste")
                self.start_record_and_paste()
            elif self.is_key_match(key, self.app.push_to_talk_key):
                logging.debug(f"Key pressed: {key}, starting push to talk")
                self.start_push_to_talk()
        except Exception as e:
            logging.error(f"Exception in on_press: {e}", exc_info=True)

    def on_release(self, key):
        try:
            if self.is_key_match(key, self.app.shortcut_paste_record):
                logging.debug(f"Key released: {key}, stopping record and paste")
                self.stop_record_and_paste()
            elif self.is_key_match(key, self.app.push_to_talk_key):
                logging.debug(f"Key released: {key}, stopping push to talk")
                self.stop_push_to_talk()
        except Exception as e:
            logging.error(f"Exception in on_release: {e}", exc_info=True)

    def toggle_recording(self):
        if not self.app.is_recording:
            self.app.start_recording()
        else:
            self.app.stop_recording(paste_after=False)

    def start_record_and_paste(self):
        if not self.app.is_recording:
            self.app.start_recording()

    def stop_record_and_paste(self):
        if self.app.is_recording:
            self.app.stop_recording(paste_after=True)

    def start_push_to_talk(self):
        if not self.app.is_recording:
            self.app.start_recording()

    def stop_push_to_talk(self):
        if self.app.is_recording:
            self.app.stop_recording(paste_after=True)
