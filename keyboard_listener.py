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
            # Shortcut für einfache Aufnahme
            if key == self.app.shortcut_record:
                if not self.app.is_recording:
                    self.app.paste_after = False
                    self.app.start_recording()

            # Shortcut für Aufnahme mit Einfügen
            elif key == self.app.shortcut_paste_record:
                if not self.app.is_recording:
                    self.app.paste_after = True
                    self.app.start_recording()
                    # Sofort stoppen, da es sich nicht um Push-to-Talk handelt
                    self.app.stop_recording()

            # Push-to-Talk Taste
            elif key == self.app.push_to_talk_key:
                if not self.app.is_recording:
                    self.app.paste_after = True
                    self.app.start_recording()

        except Exception as e:
            print(f"Fehler in on_press: {e}")

    def on_release(self, key):
        try:
            if key == self.app.shortcut_record:
                if self.app.is_recording:
                    self.app.stop_recording()

            elif key == self.app.push_to_talk_key:
                if self.app.is_recording:
                    self.app.stop_recording()

        except Exception as e:
            print(f"Fehler in on_release: {e}")
