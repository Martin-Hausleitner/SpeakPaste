# transcriber_app.py
import tkinter as tk
from tkinter import ttk
import threading
import pyperclip
from audio_recorder import AudioRecorder
from sieve_transcriber import SieveTranscriber
from sound_player import SoundPlayer
from keyboard_listener import KeyboardListener


class TranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Push-to-Talk Transcriber")
        self.is_recording = False
        self.audio_recorder = None
        self.transcribed_text = ""
        self.sound_player = SoundPlayer()
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

    def init_keyboard_listener(self):
        # Entfernen bestehender Hotkeys
        try:
            import keyboard
            keyboard.unhook_all_hotkeys()
        except:
            pass

        # Initialisieren des KeyboardListeners
        self.keyboard_listener = KeyboardListener(self)

    def start_recording(self):
        if not self.is_recording:
            self.status_label.config(text="Aufnahme läuft...")
            threading.Thread(target=self.sound_player.play_sound,
                             args=('start_sound.wav',)).start()
            device_name = self.selected_device.get()
            device_index = self.get_device_index_by_name(device_name)
            self.audio_recorder = AudioRecorder(device_index)
            self.audio_recorder.start_recording()
            self.is_recording = True

    def stop_recording(self, paste_after=False):
        if self.is_recording:
            self.audio_recorder.stop_recording()
            self.is_recording = False
            self.status_label.config(text="Verarbeitung läuft...")
            threading.Thread(target=self.process_audio,
                             args=(paste_after,)).start()

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

    def process_audio(self, paste_after=False):
        self.output_text.insert(tk.END, "Audio wird verarbeitet...\n")
        self.output_text.see(tk.END)
        self.transcribed_text = ""

        # Pfad zur Audiodatei
        audio_file_path = 'output.wav'

        # Transkription mit der Sieve-API
        transcriber = SieveTranscriber()
        self.transcribed_text = transcriber.transcribe(audio_file_path)

        if self.transcribed_text:
            pyperclip.copy(self.transcribed_text)
            self.output_text.insert(tk.END, f"Transkript kopiert:\n{
                                    self.transcribed_text}\n")
            self.status_label.config(text="Bereit")

            # Finish-Sound abspielen
            threading.Thread(target=self.sound_player.play_sound,
                             args=('finish_sound.wav',)).start()

            # Roten Punkt anzeigen
            self.show_red_dot_at_cursor()

            # Automatisches Einfügen, falls gewünscht
            if paste_after:
                self.paste_transcribed_text()
        else:
            self.output_text.insert(
                tk.END, "Kein Text im Ergebnis gefunden.\n")
            self.status_label.config(text="Fehler aufgetreten")
        self.output_text.see(tk.END)

    def paste_transcribed_text(self):
        if self.transcribed_text:
            # Kleinen Moment warten, um sicherzustellen, dass der Fokus korrekt ist
            threading.Timer(0.1, self._paste_text).start()
        else:
            self.output_text.insert(
                tk.END, "Kein Text zum Einfügen verfügbar.\n")
            self.output_text.see(tk.END)

    def _paste_text(self):
        import keyboard
        keyboard.write(self.transcribed_text)

    def show_red_dot_at_cursor(self):
        try:
            import pyautogui

            # Position des Mauszeigers erhalten
            x, y = pyautogui.position()

            # Roten Punkt zeichnen
            dot_size = 10  # Größe des roten Punkts
            duration = 500  # Dauer in Millisekunden

            # Neues Top-Level-Fenster erstellen
            dot_window = tk.Toplevel()
            dot_window.overrideredirect(True)  # Fensterrahmen entfernen
            dot_window.attributes('-topmost', True)  # Immer im Vordergrund
            dot_window.configure(background='red')
            dot_window.geometry(
                f"{dot_size}x{dot_size}+{x - dot_size // 2}+{y - dot_size // 2}")

            # Fenster nach bestimmter Zeit zerstören
            dot_window.after(duration, dot_window.destroy)
        except Exception as e:
            self.output_text.insert(
                tk.END, f"Fehler beim Anzeigen des roten Punkts: {e}\n")
            self.output_text.see(tk.END)
