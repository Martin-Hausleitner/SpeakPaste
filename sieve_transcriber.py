# sieve_transcriber.py
import sieve

class SieveTranscriber:
    def __init__(self):
        pass

    def transcribe(self, audio_file_path):
        try:
            file = sieve.File(path=audio_file_path)

            # Parameter gemäß Ihren Anforderungen
            word_level_timestamps = False
            speaker_diarization = False
            speed_boost = True
            backend = "stable-ts"
            source_language = "de"
            target_language = "de"
            min_speakers = -1
            max_speakers = -1
            min_silence_length = 0.4
            min_segment_length = -1
            chunks = ""
            denoise_audio = False
            use_vad = False
            use_pyannote_segmentation = False
            vad_threshold = 0.2
            pyannote_segmentation_threshold = 0.8
            initial_prompt = ""

            speech_transcriber = sieve.function.get("sieve/speech_transcriber")
            output = speech_transcriber.run(
                file,
                word_level_timestamps,
                speaker_diarization,
                speed_boost,
                backend,
                source_language,
                target_language,
                min_speakers,
                max_speakers,
                min_silence_length,
                min_segment_length,
                chunks,
                denoise_audio,
                use_vad,
                use_pyannote_segmentation,
                vad_threshold,
                pyannote_segmentation_threshold,
                initial_prompt
            )

            for output_object in output:
                transcribed_text = output_object.get("text", "")
                return transcribed_text

        except Exception as e:
            print(f"Ein Fehler ist während der Transkription aufgetreten: {e}")
            return ""
