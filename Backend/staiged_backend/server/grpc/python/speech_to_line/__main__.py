import sys
import os
import json
import wave
import pyaudio
import librosa
import noisereduce as nr
import numpy as np
from thefuzz import fuzz
from faster_whisper import WhisperModel
from speech_to_line.audio_buffer import AudioBuffer
import logging
import tempfile
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
        self.model = WhisperModel(model_size, compute_type='float32')
        self.json_data = []
        self.json_data_file = json_data_file
        self.original_wave_file_path = None
        self.noise_reduced_wave_file_path = None
        self.stop = False
        self.mqtt_controller = mqtt_controller
        self.status_queue = status_queue
        self.settings = settings
        self.load_json_data()
        logging.basicConfig(level=logging.INFO)
        self.project_temp_dir = os.path.join(os.getcwd(), 'temp_audio_files')
        os.makedirs(self.project_temp_dir, exist_ok=True)

    def load_json_data(self):
        try:
            with open(self.json_data_file, 'r') as json_file:
                json_data = json.load(json_file)
                prev_line = None
                for page in json_data['pages']:
                    for fragment in page['fragments']:
                        current_line = ({
                            "page_number": page['page_number'],
                            "y_coordinate": int(fragment['bounds']['bottom'] + fragment['bounds']['height'] / 2),
                            "text": fragment['text']
                        })
                        if prev_line is not None:
                            self.json_data.append({
                                "page_number": prev_line['page_number'],
                                "y_coordinate": prev_line['y_coordinate'],
                                "text": prev_line['text'] + current_line['text']
                            })
                        self.json_data.append(current_line)
                        prev_line = current_line
        except FileNotFoundError:
            logging.error(f"JSON file '{self.json_data_file}' not found.")
            raise

    def search_for_line(self, target_string):
        best_match = None
        best_score = 0

        for line in self.json_data:
            similarity_score = fuzz.partial_token_sort_ratio(
                line['text'].lower(),
                target_string.lower()
            )
            if similarity_score > best_score:
                best_score = similarity_score
                best_match = {
                    'page_number': line.get('page_number'),
                    'y_coordinate': line.get('y_coordinate'),
                    'matched_line': line['text'].lower(),
                    'input_line': target_string.lower(),
                }

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

        logging.info(f"Best match: '{best_match}' (Similarity: {best_score}%)")
        return best_match

    def transcribe_and_search(self, audio_array):
        segments, info = self.model.transcribe(audio_array, language="en")
        target_string = ""

        for segment in segments:
            logging.info("[%.2fs -> %.2fs] %s" % (
                segment.start,
                segment.end,
                segment.text)
            )
            target_string += segment.text

        best_match = self.search_for_line(target_string)

        return best_match

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
                with wave.open(self.original_wave_file_path, 'wb') as wave_file:
                    wave_file.setnchannels(1)
                    wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wave_file.setframerate(AudioBuffer.RATE)
                    wave_file.writeframes(b''.join(audio_buffer.frames))

                audio_array, sr = librosa.load(self.original_wave_file_path, sr=16_000)

                # Apply noise reduction
                reduced_noise = audio_array

                # Save the noise-reduced audio
                with wave.open(self.noise_reduced_wave_file_path, 'wb') as wave_file:
                    wave_file.setnchannels(1)
                    wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wave_file.setframerate(AudioBuffer.RATE)
                    wave_file.writeframes(b''.join(audio_buffer.frames))

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
            # Properly stop MQTT client
            if self.mqtt_controller is not None:
                self.mqtt_controller.disconnect()

    def stop(self):
        self.stop = True
        if self.status_queue:
            self.status_queue.put("Stopped")
        if self.mqtt_controller is not None:
            self.mqtt_controller.disconnect()

if __name__ == '__main__':
    from mqtt_controller.mqtt_controller import MQTTController  # Adjust the import based on your module structure
    settings = json.loads(sys.argv[1])
    mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_line')
    mqtt_controller.connect()
    speech_to_line = SpeechToLine(mqtt_controller=mqtt_controller, settings=settings)
    speech_to_line.start()
