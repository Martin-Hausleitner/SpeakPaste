import tkinter as tk
from tkinter import ttk
import threading
import pyperclip
from audio_recorder import AudioRecorder
from sieve_transcriber import SieveTranscriber
from keyboard_listener import KeyboardListener
from pynput import keyboard


class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Push-to-Talk Transcriber")
        self.is_recording = False
        self.paste_after = False
        self.audio_recorder = None
        self.transcribed_text = ""
        self.create_widgets()
        self.init_keyboard_listener()

    def create_widgets(self):
        devices = self.get_audio_devices()
        self.selected_device = tk.StringVar()
        self.selected_device.set(devices[0])

        ttk.Label(self.root, text="Wählen Sie ein Mikrofon:").pack(pady=5)
        self.device_menu = ttk.OptionMenu(
            self.root, self.selected_device, *devices)
        self.device_menu.pack(pady=5)

        # Shortcuts
        ttk.Label(self.root, text="Shortcut für Aufnahme (z.B. F9):").pack(pady=5)
        self.shortcut_entry_record = ttk.Entry(self.root)
        self.shortcut_entry_record.insert(0, 'F9')
        self.shortcut_entry_record.pack(pady=5)
        self.shortcut_entry_record.bind('<FocusOut>', self.update_shortcuts)

        ttk.Label(
            self.root, text="Shortcut für Aufnahme mit Einfügen (z.B. F10):").pack(pady=5)
        self.shortcut_entry_paste_record = ttk.Entry(self.root)
        self.shortcut_entry_paste_record.insert(0, 'F10')
        self.shortcut_entry_paste_record.pack(pady=5)
        self.shortcut_entry_paste_record.bind(
            '<FocusOut>', self.update_shortcuts)

        ttk.Label(self.root, text="Taste für Push-to-Talk (z.B. F12):").pack(pady=5)
        self.push_to_talk_entry = ttk.Entry(self.root)
        self.push_to_talk_entry.insert(0, 'F12')
        self.push_to_talk_entry.pack(pady=5)
        self.push_to_talk_entry.bind('<FocusOut>', self.update_shortcuts)

        self.status_label = ttk.Label(self.root, text="Bereit")
        self.status_label.pack(pady=5)

        self.output_text = tk.Text(
            self.root, wrap=tk.WORD, height=15, width=60)
        self.output_text.pack(pady=5)

        # Initialisierung der Shortcuts
        self.update_shortcuts()

    def get_audio_devices(self):
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        devices = []
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            devices.append(device_info['name'])
        p.terminate()
        return devices

    def update_shortcuts(self, event=None):
        self.shortcut_record = self.get_key(self.shortcut_entry_record.get())
        self.shortcut_paste_record = self.get_key(
            self.shortcut_entry_paste_record.get())
        self.push_to_talk_key = self.get_key(self.push_to_talk_entry.get())

        self.status_label.config(
            text=f"Bereit - Aufnahme: '{self.shortcut_record}', "
            f"Aufnahme+Einfügen: '{self.shortcut_paste_record}', "
            f"Push-to-Talk: '{self.push_to_talk_key}'"
        )

    def get_key(self, key_str):
        try:
            return getattr(keyboard.Key, key_str.lower())
        except AttributeError:
            return keyboard.KeyCode(char=key_str)

    def init_keyboard_listener(self):
        self.keyboard_listener = KeyboardListener(self)

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.status_label.config(text="Aufnahme läuft...")
            device_name = self.selected_device.get()
            device_index = self.get_device_index_by_name(device_name)
            self.audio_recorder = AudioRecorder(device_index)
            self.audio_recorder.start_recording()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.status_label.config(text="Verarbeitung läuft...")
            self.audio_recorder.stop_recording()
            threading.Thread(target=self.process_audio).start()

    def get_device_index_by_name(self, name):
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        index = None
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['name'] == name:
                index = i
                break
        p.terminate()
        return index

    def process_audio(self):
        transcriber = SieveTranscriber()
        self.transcribed_text = transcriber.transcribe('output.wav')
        print(f"Transkribierter Text: '{
              self.transcribed_text}'")  # Debug-Ausgabe

        if self.transcribed_text:
            pyperclip.copy(self.transcribed_text)
            self.root.after(0, lambda: self.output_text.insert(
                tk.END, f"Transkript kopiert:\n{self.transcribed_text}\n"))
            self.root.after(0, lambda: self.status_label.config(text="Bereit"))

            if self.paste_after:
                self.root.after(100, self.paste_transcribed_text)
                self.paste_after = False
        else:
            self.root.after(0, lambda: self.output_text.insert(
                tk.END, "Kein Text im Ergebnis gefunden.\n"))
            self.root.after(0, lambda: self.status_label.config(
                text="Fehler aufgetreten"))

        self.root.after(0, self.output_text.see(tk.END))

    def paste_transcribed_text(self):
        from pynput.keyboard import Controller, Key
        keyboard_controller = Controller()
        keyboard_controller.press(Key.ctrl)
        keyboard_controller.press('v')
        keyboard_controller.release('v')
        keyboard_controller.release(Key.ctrl)
