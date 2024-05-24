import sys
import os
import json
import logging
import tempfile
import pyaudio
import wave
from speech_to_line.audio_buffer import AudioBuffer
from speech_to_line.audio_cleanup import AudioCleanup
from speech_to_line.stt import STT
from speech_to_line.json_data_handler import JSONDataHandler
from speech_to_line.text_search import TextSearch
from multiprocessing import Queue
import paho.mqtt.client as mqtt

class SpeechToLine:
    def __init__(
            self,
            model_size="tiny.en",
            json_data_file="server/storage/transcripts/output_extracted_data.json",
            mqtt_controller=None,
            status_queue=None,
            settings=None
            ):
        # Calculate the correct path relative to the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
        self.json_data_file = os.path.join(project_root, json_data_file)
        
        self.stt = STT(model_size)
        self.json_handler = JSONDataHandler(self.json_data_file)
        self.text_search = TextSearch(self.json_handler.json_data)
        self.mqtt_controller = mqtt_controller
        self.status_queue = status_queue
        self.settings = settings
        logging.basicConfig(level=logging.INFO)
        self.project_temp_dir = os.path.join(os.getcwd(), 'temp_audio_files')
        os.makedirs(self.project_temp_dir, exist_ok=True)
        self.stop = False
        self.original_wave_file_path = None
        self.noise_reduced_wave_file_path = None

    def start(self):
        self.stop = False
        if self.status_queue:
            self.status_queue.put("Started")
        with tempfile.NamedTemporaryFile(suffix='original.wav', delete=False, dir=self.project_temp_dir) as temp_wav_file:
            self.original_wave_file_path = temp_wav_file.name
            logging.info(f"Temporary original audio file path: {self.original_wave_file_path}")
        with tempfile.NamedTemporaryFile(suffix='cleaned.wav', delete=False, dir=self.project_temp_dir) as temp_wav_file:
            self.noise_reduced_wave_file_path = temp_wav_file.name
            logging.info(f"Temporary noise-reduced audio file path: {self.noise_reduced_wave_file_path}")

        audio_buffer = AudioBuffer(input_device_index=self.settings['microphone']['microphone_device'])
        audio_buffer.start()
        audio = pyaudio.PyAudio()

        try:
            while not self.stop:
                logging.info("\n ##### START #######")

                # Save the original audio
                original_frames = b''.join(audio_buffer.frames)
                with wave.open(self.original_wave_file_path, 'wb') as wave_file:
                    wave_file.setnchannels(1)
                    wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wave_file.setframerate(AudioBuffer.RATE)
                    wave_file.writeframes(original_frames)

                audio_cleanup = AudioCleanup(self.original_wave_file_path)
                reduced_noise = audio_cleanup.reduce_noise()
                reduced_noise_int16 = audio_cleanup.to_int16(reduced_noise)

                # Save the noise-reduced audio
                with wave.open(self.noise_reduced_wave_file_path, 'wb') as wave_file:
                    wave_file.setnchannels(1)
                    wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wave_file.setframerate(16000)
                    wave_file.writeframes(reduced_noise_int16.tobytes())

                self.transcribe_and_search(reduced_noise)

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt received. Stopping process.")
        finally:
            audio_buffer.stop()
            audio.terminate()
            logging.info(f"Temporary original audio file retained for review: {self.original_wave_file_path}")
            logging.info(f"Temporary noise-reduced audio file retained for review: {self.noise_reduced_wave_file_path}")
            if self.status_queue:
                self.status_queue.put("Stopped")
            if self.mqtt_controller is not None:
                self.mqtt_controller.disconnect()

    def transcribe_and_search(self, audio_array):
        segments = self.stt.transcribe(audio_array)
        target_string = "".join([segment.text for segment in segments])
        best_match = self.text_search.search_for_line(target_string)

        if self.mqtt_controller is not None:
            try:
                result = self.mqtt_controller.publish(
                    "local_server/tracker/position",
                    json.dumps(best_match),
                    retain=True
                )
                logging.info(f"Published to MQTT topic, result: {result}")
            except Exception as e:
                logging.error(f"Failed to publish MQTT message: {e}")

        logging.info(f"Best match: '{best_match}'")
        return best_match

    def stop(self):
        self.stop = True
        if self.status_queue:
            self.status_queue.put("Stopped")
        if self.mqtt_controller is not None:
            self.mqtt_controller.disconnect()

if __name__ == '__main__':
    from mqtt_controller.mqtt_controller import MQTTController
    settings = json.loads(sys.argv[1])
    mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_line')
    mqtt_controller.connect()
    speech_to_line = SpeechToLine(mqtt_controller=mqtt_controller, settings=settings)
    speech_to_line.start()
