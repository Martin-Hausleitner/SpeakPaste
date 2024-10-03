import pyaudio
import wave
import threading


class AudioRecorder:
    def __init__(self, device_index, filename="output.wav"):
        self.device_index = device_index
        self.filename = filename
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording = False
        self.frames = []
        self.thread = None

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.thread = threading.Thread(target=self.record)
            self.thread.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            if self.thread is not None:
                self.thread.join()
            self.save_wave_file()

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk,
                        input_device_index=self.device_index)
        self.frames = []
        while self.recording:
            data = stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_wave_file(self):
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
