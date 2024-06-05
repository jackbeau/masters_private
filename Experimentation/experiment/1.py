import logging
import json
import sys
from ctypes import c_bool
import multiprocessing as mp
import os
import time
import tempfile
import wave
import pyaudio
import librosa
from faster_whisper import WhisperModel
from speech_to_script_pointer import ScriptDataHandler, TextSearch, AudioBuffer

# Configure logging for the main script
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Set logging level to the logger
logger = logging.getLogger("speech_to_script_pointer")
logger.setLevel(logging.INFO)

SAMPLE_RATE = 16000
BUFFER_SIZE = 512

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')
class SpeechToScriptPointer:
    def __init__(self,
                 mqtt_controller=None,
                 status_queue=None,
                 input_device_index: int = 1,
                 model_size="tiny.en",
                 json_data_file="server/storage/transcripts/output_extracted_data.json",
                 csv_file_path="results.csv"
                ):
        self.input_device_index = input_device_index
        self.wave_file_path = "./.audio_buffer.wav"
        self.model = WhisperModel(model_size, compute_type='float32')
        self.status_queue = status_queue
        self.stop = False

        self.data_cleanup = ScriptDataHandler(json_data_file)
        self.text_search = TextSearch(self.data_cleanup.chunks, csv_file_path, mqtt_controller)

        self.displayed_text = ""
        self.full_sentences = ""

        self.audio_buffer = AudioBuffer()

    def text_detected(self, text):
        logger.info("Processed text: %s", text)
        self.text_search.search_for_line(text)
        self.save_transcript(text)

    def save_transcript(self, text):
        transcript_file = "transcript2.txt"
        with open(transcript_file, "a") as f:
            f.write(text + "\n")

    def process_audio(self, audio_array):
        """
        Transcribe the audio array using the model and search for the most
        fitting line in the JSON data

        Parameters:
            audio_array (np.ndarray): The audio data to be transcribed.

        Returns:
            dict: The best match found in the JSON data.
        """
        segments, info = self.model.transcribe(audio_array, language="en")
        target_string = ""

        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (
                segment.start,
                segment.end,
                segment.text)
                )
            target_string += segment.text

        # self.save_transcript(target_string)
        logger.info("Transcribed text: %s", target_string)
        self.text_detected(target_string)

    def start(self):
        self.stop = False
        if self.status_queue:
            self.status_queue.put("Started")
        
        clear_console()
        logger.info("Started speech to line process.")

        self.audio_buffer.start()

        with tempfile.NamedTemporaryFile(
                suffix='.wav', delete=False
                ) as temp_wav_file:
            self.wave_file_path = temp_wav_file.name
            audio_buffer = AudioBuffer()
            audio_buffer.start()
            audio = pyaudio.PyAudio()

            try:
                while self.stop is False:
                    logging.info("\n ##### START #######")

                    with wave.open(self.wave_file_path, 'wb') as wave_file:
                        wave_file.setnchannels(1)
                        wave_file.setsampwidth(
                            audio.get_sample_size(pyaudio.paInt16)
                        )
                        wave_file.setframerate(AudioBuffer.RATE)
                        wave_file.writeframes(b''.join(audio_buffer.frames))

                    audio_array, _ = librosa.load(
                        self.wave_file_path,
                        sr=16_000
                        )
                    self.process_audio(audio_array)

            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt received. Stopping process.")
            finally:
                audio_buffer.stop()
                audio.terminate()
                os.remove(self.wave_file_path)
                self.stop_recording()


    def stop_recording(self):
        self.stop = True
        # self.audio_buffer.stop()
        # if self.status_queue:
        #     self.status_queue.put("Stopped")

if __name__ == '__main__':
    from mqtt_controller.mqtt_controller import MQTTController  # Adjust the import based on your module structure
    mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_script_pointer')
    mqtt_controller.connect()
    speech_to_script_pointer = SpeechToScriptPointer(mqtt_controller=mqtt_controller)
    speech_to_script_pointer.start()