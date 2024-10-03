from playsound import playsound
import threading


class SoundPlayer:
    def __init__(self):
        pass

    def play_sound(self, sound_file):
        threading.Thread(target=self._play_sound_thread,
                         args=(sound_file,)).start()

    def _play_sound_thread(self, sound_file):
        try:
            playsound(sound_file)
        except Exception as e:
            print(f"Fehler beim Abspielen von {sound_file}: {e}")
