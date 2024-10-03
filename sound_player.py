# sound_player.py
from playsound import playsound

class SoundPlayer:
    def __init__(self):
        pass

    def play_sound(self, sound_file):
        try:
            playsound(sound_file)
        except Exception as e:
            print(f"Fehler beim Abspielen von {sound_file}: {e}")
