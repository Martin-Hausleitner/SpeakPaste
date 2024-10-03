# sieve_transcriber.py
import sieve
import logging


class SieveTranscriber:
    def __init__(self):
        pass

    def transcribe(self, audio_file_path):
        logging.debug("Starting transcription with Sieve")
        try:
            # Replace sieve.File with the file path string
            file = audio_file_path

            # Parameters as per your requirements
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

            # Initialize the speech transcriber function
            # Ensure that 'functions' is the correct attribute in the sieve module
            speech_transcriber = sieve.functions.get(
                "sieve/speech_transcriber")
            if not speech_transcriber:
                logging.error(
                    "Could not retrieve 'sieve/speech_transcriber' function from sieve.")
                return ""

            # Run the transcriber with the provided parameters
            output = speech_transcriber.run(
                file=file,
                word_level_timestamps=word_level_timestamps,
                speaker_diarization=speaker_diarization,
                speed_boost=speed_boost,
                backend=backend,
                source_language=source_language,
                target_language=target_language,
                min_speakers=min_speakers,
                max_speakers=max_speakers,
                min_silence_length=min_silence_length,
                min_segment_length=min_segment_length,
                chunks=chunks,
                denoise_audio=denoise_audio,
                use_vad=use_vad,
                use_pyannote_segmentation=use_pyannote_segmentation,
                vad_threshold=vad_threshold,
                pyannote_segmentation_threshold=pyannote_segmentation_threshold,
                initial_prompt=initial_prompt
            )

            # Aggregate the transcribed text
            transcribed_text = ""
            for output_object in output:
                transcribed_text += output_object.get("text", "")
            logging.debug("Transcription completed")
            return transcribed_text

        except AttributeError as ae:
            logging.error(f"Attribute error during transcription: {
                          ae}", exc_info=True)
            return ""
        except Exception as e:
            logging.error(f"An error occurred during transcription: {
                          e}", exc_info=True)
            return ""
