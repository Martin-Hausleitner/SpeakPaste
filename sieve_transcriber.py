# sieve_transcriber.py
import os
import requests
import logging
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()


class SieveTranscriber:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            logging.error(
                "API_KEY ist nicht in den Umgebungsvariablen gesetzt.")
            raise ValueError("API_KEY ist erforderlich.")
        self.endpoint = "https://api.groq.com/openai/v1/audio/transcriptions"
        self.model = "whisper-large-v3"
        self.temperature = 0
        # Auf 'json' setzen, um die vollständige Antwort zu erhalten
        self.response_format = "json"
        self.language = "de"

    def transcribe(self, audio_file_path):
        if not os.path.exists(audio_file_path):
            logging.error(f"Audio-Datei nicht gefunden: {audio_file_path}")
            return None, None

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": audio_file,
                "model": (None, self.model),
                "temperature": (None, str(self.temperature)),
                "response_format": (None, self.response_format),
                "language": (None, self.language)
            }

            try:
                logging.debug(
                    f"Sende POST-Anfrage an {self.endpoint} mit Datei {audio_file_path}")
                response = requests.post(
                    self.endpoint, headers=headers, files=files)
                response.raise_for_status()

                if self.response_format == "json":
                    result = response.json()
                    transcribed_text = result.get('text', '')
                    request_id = result.get('x_groq', {}).get('id', 'N/A')
                    logging.debug(f"API-Antwort erhalten: {result}")
                    logging.info(
                        f"Transkription abgeschlossen. Request ID: {request_id}")
                    return transcribed_text, request_id
                else:
                    logging.error(f"Unbekanntes response_format: {
                                  self.response_format}")
                    return None, None
            except requests.exceptions.HTTPError as http_err:
                logging.error(
                    f"HTTP-Fehler: {http_err} - Antwort: {response.text}")
            except Exception as err:
                logging.error(f"Fehler bei der Transkription: {err}")
            return None, None
