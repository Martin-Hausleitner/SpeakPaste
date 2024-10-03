# keyboard_listener.py
import threading
from pynput import keyboard


class KeyboardListener:
    def __init__(self, app):
        self.app = app
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try:
            if key == keyboard.Key[self.app.shortcut_record.lower()]:
                self.toggle_recording()
            elif key == keyboard.Key[self.app.shortcut_paste_record.lower()]:
                self.start_record_and_paste()
            elif key == keyboard.Key[self.app.push_to_talk_key.lower()]:
                self.start_push_to_talk()
        except (AttributeError, KeyError):
            pass

    def on_release(self, key):
        try:
            if key == keyboard.Key[self.app.shortcut_paste_record.lower()]:
                self.stop_record_and_paste()
            elif key == keyboard.Key[self.app.push_to_talk_key.lower()]:
                self.stop_push_to_talk()
        except (AttributeError, KeyError):
            pass

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
