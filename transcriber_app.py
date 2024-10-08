# transcriber_app.py
import tkinter as tk
from tkinter import ttk
import threading
import pyperclip
import platform
import logging
import sounddevice as sd
from audio_recorder import AudioRecorder
from sieve_transcriber import SieveTranscriber
from keyboard_listener import KeyboardListener


class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Push-to-Talk Transcriber")
        self.is_recording = False
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
        devices = sd.query_devices()
        input_devices = [
            device for device in devices if device['max_input_channels'] > 0]
        device_names = [device['name'] for device in input_devices]
        for idx, name in enumerate(device_names):
            logging.debug(f"Found audio device: {name} (Index: {idx})")
        return device_names

    def update_shortcuts(self, event=None):
        self.shortcut_record = self.shortcut_entry_record.get().lower()
        self.shortcut_paste_record = self.shortcut_entry_paste_record.get().lower()
        self.push_to_talk_key = self.push_to_talk_entry.get().lower()
        # Aktualisieren der Shortcuts im KeyboardListener
        self.init_keyboard_listener()

        self.status_label.config(
            text=f"Bereit - Aufnahme: '{self.shortcut_record}', "
            f"Aufnahme+Einfügen: '{self.shortcut_paste_record}', "
            f"Push-to-Talk: '{self.push_to_talk_key}'"
        )
        logging.debug("Shortcuts updated")

    def init_keyboard_listener(self):
        # Initialisieren des KeyboardListeners
        self.keyboard_listener = KeyboardListener(self)
        logging.debug("Keyboard listener initialized")

    def start_recording(self):
        if not self.is_recording:
            logging.debug("Starting recording")
            self.status_label.config(text="Aufnahme läuft...")
            device_name = self.selected_device.get()
            device_index = self.get_device_index_by_name(device_name)
            logging.debug(f"Selected device: {
                          device_name} (Index: {device_index})")
            self.audio_recorder = AudioRecorder(device_index)
            self.audio_recorder.start_recording()
            self.is_recording = True

    def stop_recording(self, paste_after=False):
        if self.is_recording:
            logging.debug("Stopping recording")
            self.audio_recorder.stop_recording()
            self.is_recording = False
            self.status_label.config(text="Verarbeitung läuft...")
            threading.Thread(target=self.process_audio,
                             args=(paste_after,)).start()

    def get_device_index_by_name(self, name):
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['name'] == name and device['max_input_channels'] > 0:
                logging.debug(f"Device '{name}' has index {idx}")
                return idx
        logging.error(f"Audio device '{name}' not found")
        return None

    def process_audio(self, paste_after=False):
        logging.debug("Starting audio processing")
        self.transcribed_text = ""
        audio_file_path = 'output.wav'

        transcriber = SieveTranscriber()
        self.transcribed_text = transcriber.transcribe(audio_file_path)

        if self.transcribed_text:
            try:
                pyperclip.copy(self.transcribed_text)
                logging.debug("Transcribed text copied to clipboard")
            except pyperclip.PyperclipException:
                self.root.after(0, lambda: self.output_text.insert(
                    tk.END, "Fehler beim Kopieren in die Zwischenablage. Stellen Sie sicher, dass xclip oder xsel installiert ist.\n"))
                logging.error(
                    "Failed to copy text to clipboard", exc_info=True)
            # GUI-Updates im Hauptthread ausführen
            self.root.after(0, lambda: self.output_text.insert(
                tk.END, f"Transkript kopiert:\n{self.transcribed_text}\n"))
            self.root.after(0, lambda: self.status_label.config(text="Bereit"))
            # Roten Punkt im Hauptthread anzeigen
            self.root.after(0, self.show_red_dot_at_cursor)

            # Automatisches Einfügen, falls gewünscht
            if paste_after:
                self.root.after(100, self._paste_text)
        else:
            self.root.after(0, lambda: self.output_text.insert(
                tk.END, "Kein Text im Ergebnis gefunden.\n"))
            self.root.after(0, lambda: self.status_label.config(
                text="Fehler aufgetreten"))
            logging.error("No text found in transcription result")
        self.root.after(0, self.output_text.see(tk.END))
        logging.debug("Audio processing completed")

    def paste_transcribed_text(self):
        if self.transcribed_text:
            # Einfügeoperation im Hauptthread nach kurzer Verzögerung planen
            self.root.after(100, self._paste_text)
        else:
            self.root.after(0, lambda: self.output_text.insert(
                tk.END, "Kein Text zum Einfügen verfügbar.\n"))
            self.root.after(0, self.output_text.see(tk.END))
            logging.error("No text available to paste")

    def _paste_text(self):
        from pynput.keyboard import Controller, Key
        keyboard = Controller()
        # Sicherstellen, dass die Modifikatortasten losgelassen sind
        keyboard.release(Key.ctrl)
        keyboard.release(Key.cmd)
        # Strg+V oder Cmd+V zum Einfügen simulieren
        if platform.system() == 'Darwin':
            with keyboard.pressed(Key.cmd):
                keyboard.press('v')
                keyboard.release('v')
            logging.debug("Pasted text using Cmd+V")
        else:
            with keyboard.pressed(Key.ctrl):
                keyboard.press('v')
                keyboard.release('v')
            logging.debug("Pasted text using Ctrl+V")

    def show_red_dot_at_cursor(self):
        try:
            import pyautogui

            # Position des Mauszeigers erhalten
            x, y = pyautogui.position()

            # Roten Punkt zeichnen
            dot_size = 10  # Größe des roten Punkts
            duration = 500  # Dauer in Millisekunden

            # Neues Top-Level-Fenster erstellen
            dot_window = tk.Toplevel(self.root)
            dot_window.overrideredirect(True)  # Fensterrahmen entfernen
            dot_window.attributes('-topmost', True)  # Immer im Vordergrund
            dot_window.configure(background='red')
            dot_window.geometry(
                f"{dot_size}x{dot_size}+{x - dot_size // 2}+{y - dot_size // 2}")

            # Fenster nach bestimmter Zeit zerstören
            dot_window.after(duration, dot_window.destroy)
            logging.debug("Red dot displayed at cursor position")
        except Exception as e:
            self.root.after(0, lambda: self.output_text.insert(
                tk.END, f"Fehler beim Anzeigen des roten Punkts: {e}\n"))
            self.root.after(0, self.output_text.see(tk.END))
            logging.error("Error displaying red dot", exc_info=True)
