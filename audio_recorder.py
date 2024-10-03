# audio_recorder.py
import sounddevice as sd
import numpy as np
import wave
import threading
import logging


class AudioRecorder:
    def __init__(self, device_index, filename="output.wav"):
        self.device_index = device_index
        self.filename = filename
        self.channels = 1
        self.rate = 44100  # Standard-Abtastrate
        self.recording = False
        self.frames = []

    def start_recording(self):
        logging.debug("Start recording")
        self.recording = True
        threading.Thread(target=self.record).start()

    def stop_recording(self):
        logging.debug("Stop recording requested")
        self.recording = False

    def record(self):
        def callback(indata, frames, time, status):
            if status:
                logging.error(f"Recording status: {status}")
            if self.recording:
                self.frames.append(indata.copy())
            else:
                raise sd.CallbackStop()

        try:
            with sd.InputStream(samplerate=self.rate,
                                channels=self.channels,
                                callback=callback,
                                device=self.device_index):
                logging.debug(
                    "InputStream opened with device index {}".format(self.device_index))
                while self.recording:
                    sd.sleep(100)
            self.save_wave_file()
            logging.debug("Recording finished and file saved")
        except Exception as e:
            logging.error(f"Fehler während der Aufnahme: {e}", exc_info=True)

    def save_wave_file(self):
        try:
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.rate)
            wf.writeframes(b''.join([frame.tobytes()
                           for frame in self.frames]))
            wf.close()
            logging.debug("WAV file saved successfully")
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Datei: {
                          e}", exc_info=True)
