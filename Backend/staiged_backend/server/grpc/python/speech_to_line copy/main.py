import logging
import json
import sys
from ctypes import c_bool
import multiprocessing as mp
from speech_to_line.RealtimeSTT.audio_recorder import AudioToTextRecorder
from speech_to_line import ScriptDataHandler, TextSearch
import os

# Configure logging for the main script
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Set logging level to the logger
logger = logging.getLogger("speech_to_line")
logger.setLevel(logging.INFO)

SAMPLE_RATE = 16000
BUFFER_SIZE = 512

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

class SpeechToLine:
    def __init__(self,
                 mqtt_controller=None,
                 status_queue=None,
                 use_microphone=True,
                 input_device_index: int = 1,
                ):
        self.use_microphone = mp.Value(c_bool, use_microphone)
        self.input_device_index = input_device_index

        json_data_file = "server/storage/transcripts/output_extracted_data.json"
        self.data_cleanup = ScriptDataHandler(json_data_file)
        self.text_search = TextSearch(self.data_cleanup.chunks, mqtt_controller)
        self.status_queue = status_queue

        self.displayed_text = ""
        self.full_sentences = ""

        self.recorder_config = {
            'model': 'base.en',
            'language': 'en',
            'webrtc_sensitivity': 2,
            'post_speech_silence_duration': 0.4,
            'min_length_of_recording': 0,
            'min_gap_between_recordings': 0,
            "ensure_sentence_starting_uppercase": False,
            'enable_realtime_transcription': True,
            'realtime_processing_pause': 0.2,
            'realtime_model_type': 'base.en',
            'on_realtime_transcription_update': self.text_detected,
            "input_device_index": self.input_device_index,
            "compute_type": "int8_float32",
            "beam_size_realtime": 5
        }

        self.recorder = AudioToTextRecorder(**self.recorder_config)
        self.stop = False

    def text_detected(self, text):
        new_text = self.full_sentences + " " + text if len(self.full_sentences) > 0 else text

        if new_text != self.displayed_text:
            self.displayed_text = new_text
            logger.info("Processed text: %s", self.displayed_text)
            # Maybe do not clear past words all the time
            self.text_search.search_for_line(self.displayed_text)

    def process_text(self, text):
        self.full_sentences = text
        self.text_detected("")

    def start(self):
        if self.status_queue:
            self.status_queue.put("Started")
        
        clear_console()
        logger.info("Started speech to pointer process.")

        try:
            while not self.stop:
                self.recorder.text(self.process_text)
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt received. Stopping process.")
        finally:
            self.stop_recording()

    def stop_recording(self):
        self.stop = True
        if self.status_queue:
            self.status_queue.put("Stopped")

if __name__ == '__main__':

    from mqtt_controller.mqtt_controller import MQTTController  # Adjust the import based on your module structure
    mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_line')
    mqtt_controller.connect()
    speech_to_line = SpeechToLine(mqtt_controller=mqtt_controller)
    speech_to_line.start()
