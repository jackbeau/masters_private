import sys
import json
import logging
from ctypes import c_bool
import multiprocessing as mp
import paho.mqtt.client as mqtt
from speech_to_line import ScriptDataHandler, audio_data_worker, SpeechToText, TextSearch

SAMPLE_RATE = 16000
BUFFER_SIZE = 512

class SpeechToLine:
    def __init__(self,
                 settings,
                 mqtt_controller=None,
                 status_queue=None,
                 use_microphone=True,
                 input_device_index: int = 1,
                 buffer_size: int = BUFFER_SIZE,
                 sample_rate: int = SAMPLE_RATE,
                ):
        self.use_microphone = mp.Value(c_bool, use_microphone)
        self.input_device_index = input_device_index
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.audio_queue = mp.Queue()

        self.shutdown_event = mp.Event()
        self.interrupt_stop_event = mp.Event()




        json_data_file = "server/storage/transcripts/output_extracted_data.json"
        self.data_cleanup = ScriptDataHandler(json_data_file)
        self.audio_buffer = AudioBuffer(settings['microphone']['microphone_device'], self.frames_queue)
        self.stt = SpeechToText()
        self.text_search = TextSearch(self.data_cleanup.json_data, mqtt_controller)
        self.status_queue = status_queue
        self.audio_process = None

        # Start audio data reading process
        if self.use_microphone.value:
            logging.info("Initializing audio recording"
                         " (creating pyAudio input stream,"
                         f" sample rate: {self.sample_rate}"
                         f" buffer size: {self.buffer_size}"
                         )
            self.reader_process = mp.Process(
                target=audio_data_worker,
                args=(
                    self.audio_queue,
                    self.sample_rate,
                    self.buffer_size,
                    self.input_device_index,
                    self.shutdown_event,
                    self.interrupt_stop_event,
                    self.use_microphone
                )
            )
            self.reader_process.start()

    def start(self):
        self.stop = False
        if self.status_queue:
            self.status_queue.put("Started")

        self.audio_process = Process(target=self.audio_buffer.start_recording)
        self.audio_process.start()

        try:
            while not self.stop:
                if not self.frames_queue.empty():
                    self.audio_buffer.save_original_audio()
                    audio_array = self.audio_buffer.load_audio()

                    # Apply noise reduction (if necessary)
                    reduced_noise = audio_array  # Add noise reduction here if needed

                    self.audio_buffer.save_noise_reduced_audio(reduced_noise)
                    target_string = self.stt.transcribe(reduced_noise)
                    self.text_search.search_for_line(target_string)

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt received. Stopping process.")
        finally:
            self.stop_recording()

    def stop_recording(self):
        self.stop = True
        self.audio_buffer.stop_recording()
        self.audio_process.join()
        if self.status_queue:
            self.status_queue.put("Stopped")

if __name__ == '__main__':
    from mqtt_controller.mqtt_controller import MQTTController  # Adjust the import based on your module structure
    settings = json.loads(sys.argv[1])
    mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_line')
    mqtt_controller.connect()
    speech_to_line = SpeechToLine(settings=settings, mqtt_controller=mqtt_controller)
    speech_to_line.start()
