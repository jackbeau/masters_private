"""
SpeechToScriptPointer Module

This module provides functionality to record audio, transcribe it using
a Whisper model, and search for corresponding lines in a JSON data file.
The results can be published via MQTT and logged for further use.

Classes:
    SpeechToScriptPointer - Handles audio recording, transcription, and
                            searching.

Logging:
    Configured to log information, warnings, and errors to standard output.
"""

import logging
import sys
import os
import tempfile
import wave
import pyaudio
import librosa
from faster_whisper import WhisperModel
from speech_to_script_pointer import ScriptDataHandler, TextSearch, AudioBuffer

# Configure logging for the main script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Set logging level to the logger
logger = logging.getLogger("speech_to_script_pointer")
logger.setLevel(logging.INFO)

SAMPLE_RATE = 16000
BUFFER_SIZE = 512


def clear_console():
    """Clear the console screen."""
    os.system("clear" if os.name == "posix" else "cls")


class SpeechToScriptPointer:
    """
    SpeechToScriptPointer class to handle audio recording, transcription, and
    searching.

    Attributes:
        input_device_index (int): Index of the input audio device.
        model (WhisperModel): Instance of the WhisperModel for transcription.
        status_queue (Queue): Queue to send status messages.
        stop (bool): Flag to control the recording loop.
        data_cleanup (ScriptDataHandler): Instance of ScriptDataHandler to
                                          handle text data.
        text_search (TextSearch): Instance of TextSearch to perform text
                                  searching.
        displayed_text (str): Displayed transcribed text.
        full_sentences (str): Full sentences of transcribed text.
        audio_buffer (AudioBuffer): Instance of AudioBuffer to handle audio
                                    buffering.
        temp_dir (str): Directory for temporary files.
    """

    def __init__(
        self,
        mqtt_controller=None,
        status_queue=None,
        settings=None,
        model_size="tiny.en",
        json_data_file="server/storage/transcripts/output_extracted_data.json",
    ):
        """
        Initialize the SpeechToScriptPointer object.

        Parameters:
            mqtt_controller (MQTTController): Instance of the MQTTController
                                              class.
            status_queue (Queue): Queue to send status messages.
            settings (dict): Dictionary of settings.
            model_size (str): Size of the Whisper model. Defaults to "tiny.en".
            json_data_file (str): Path to the JSON data file. Defaults to
                                  "output_extracted_data.json".
        """
        self.input_device_index = settings["microphone"]["microphone_device"]
        self.model = WhisperModel(model_size, compute_type="float32")
        self.status_queue = status_queue
        self.stop = False

        self.data_cleanup = ScriptDataHandler(json_data_file)
        self.text_search = TextSearch(
            self.data_cleanup.chunks, mqtt_controller
        )

        self.displayed_text = ""
        self.full_sentences = ""

        self.audio_buffer = AudioBuffer()

        # Ensure the temp_files directory exists
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)

    def text_detected(self, text):
        """
        Handle the detected text, performing a search and saving the
        transcript.

        Parameters:
            text (str): The detected text.
        """
        logger.info("Processed text: %s", text)
        self.text_search.search_for_line(text)
        self.save_transcript(text)

    def save_transcript(self, text):
        """
        Save the transcribed text to a file.

        Parameters:
            text (str): The text to be saved.
        """
        transcript_file = "transcript2.txt"
        with open(transcript_file, "a") as f:
            f.write(text + "\n")

    def process_audio(self, audio_array):
        """
        Transcribe the audio array using the model and search for the most
        fitting line in the JSON data.

        Parameters:
            audio_array (np.ndarray): The audio data to be transcribed.

        Returns:
            None
        """
        segments, info = self.model.transcribe(audio_array, language="en")
        target_string = ""

        for segment in segments:
            logger.info(
                "[%.2fs -> %.2fs] %s", segment.start, segment.end, segment.text
            )
            target_string += segment.text

        logger.info("Transcribed text: %s", target_string)
        self.text_detected(target_string)

    def start(self):
        """Start the audio recording and processing."""
        self.stop = False
        if self.status_queue:
            self.status_queue.put("Started")

        clear_console()
        logger.info("Started speech to line process.")

        self.audio_buffer.start()

        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False, dir=self.temp_dir
        ) as temp_wav_file:
            self.wave_file_path = temp_wav_file.name
            audio_buffer = AudioBuffer()
            audio_buffer.start()
            audio = pyaudio.PyAudio()

            try:
                while self.stop is False:
                    logger.info("\n ##### START #######")

                    with wave.open(self.wave_file_path, "wb") as wave_file:
                        wave_file.setnchannels(1)
                        wave_file.setsampwidth(
                            audio.get_sample_size(pyaudio.paInt16)
                        )
                        wave_file.setframerate(AudioBuffer.RATE)
                        wave_file.writeframes(b"".join(audio_buffer.frames))

                    audio_array, _ = librosa.load(
                        self.wave_file_path, sr=16_000
                    )
                    self.process_audio(audio_array)

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received. Stopping process.")
            finally:
                audio_buffer.stop()
                audio.terminate()
                os.remove(self.wave_file_path)
                self.stop_recording()

    def stop_recording(self):
        """Stop the audio recording and processing."""
        self.stop = True
        self.audio_buffer.stop()
        if self.status_queue:
            self.status_queue.put("Stopped")


if __name__ == "__main__":
    from mqtt_controller.mqtt_controller import (
        MQTTController,
    )  # Adjust the import based on your module structure

    mqtt_controller = MQTTController(
        "0.0.0.0", 1883, "speech_to_script_pointer"
    )
    mqtt_controller.connect()
    speech_to_script_pointer = SpeechToScriptPointer(
        mqtt_controller=mqtt_controller
    )
    speech_to_script_pointer.start()
