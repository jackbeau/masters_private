"""
File: __init__.py
Author: Jack Beaumont
Date: 2024-01-26

Description: Using an audio source, transcribes speech and uses fuzzy
matching to find the most relevant line from a JSON script object."
"""

import json
import wave
import pyaudio
import librosa
from thefuzz import fuzz
from faster_whisper import WhisperModel
from .audio_buffer import AudioBuffer
import logging
import tempfile
import os
from multiprocessing import Queue

class SpeechToLine:
    def __init__(
            self,
            model_size="tiny.en",
            json_data_file="server/storage/transcripts/output_extracted_data.json",
            mqtt_controller=None,
            status_queue=None,
            settings=None
            ):
        """
        Initialize the SpeechToText class with the specified model size and
        paths to JSON data and WAV file.

        Parameters:
            mqtt_controller (MQTTController): Instance of the MQTTController class.
            model_size (str): The size of the model to be used for
                transcription. Defaults to 'tiny.en'.
            json_data_file (str): The path to the JSON data file. Defaults to
                'output_extracted_data.json'.
            wave_file_path (str): The path to the output WAV file. Defaults to
                'output.wav'.
            status_queue (Queue): A queue to send status messages to the gRPC server.
            settings (dict): A dictionary of settings.
        """
        self.model = WhisperModel(model_size, compute_type='float32')
        self.json_data = []
        self.json_data_file = json_data_file
        self.wave_file_path = "./.audio_buffer.wav"
        self.stop = False
        self.mqtt_controller = mqtt_controller
        self.status_queue = status_queue
        self.settings = settings
        self.load_json_data()
        logging.basicConfig(level=logging.INFO)

    def load_json_data(self):
        """
        Load JSON data from specified file and convert to better format.
        """
        try:
            with open(self.json_data_file, 'r') as json_file:
                json_data = json.load(json_file)
                prev_line = None
                for page in json_data['pages']:
                    for fragment in page['fragments']:
                        # Rename to current_fragment
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
        """
        Search for the best match in the JSON data based on fuzzy matching
        with the target string.

        Parameters:
            target_string (str): The string to search for in the JSON data.

        Returns:
            dict: The best match found in the JSON data.
        """
        best_match = None
        best_score = 0

        for line in self.json_data:
            similarity_score = fuzz.partial_ratio(
                line['text'].lower(),
                target_string.lower()
                )
            if similarity_score > best_score:
                best_score = similarity_score
                best_match = {
                    'page_number': line.get('page_number'),
                    'y_coordinate': line.get('y_coordinate'),
                    }
                
        if self.mqtt_controller is not None:
            self.mqtt_controller.publish("local_server/tracker/position",
                                        json.dumps(best_match), retain=True)

        logging.info(f"Best match: '{best_match}' (Similarity: {best_score}%)")
        return best_match

    def transcribe_and_search(self, audio_array):
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

        best_match = self.search_for_line(target_string)

        return best_match

    def start(self):
        """
        Start the speech-to-line process.
        """
        self.stop = False
        if self.status_queue:
            self.status_queue.put("Started")
        with tempfile.NamedTemporaryFile(
                suffix='.wav', delete=False
                ) as temp_wav_file:
            self.wave_file_path = temp_wav_file.name
            audio_buffer = AudioBuffer(input_device_index=self.settings['microphone']['microphone_device'])
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
                    self.transcribe_and_search(audio_array)

            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt received. Stopping process.")
            finally:
                audio_buffer.stop()
                audio.terminate()
                os.remove(self.wave_file_path)
                if self.status_queue:
                    self.status_queue.put("Stopped")

    def stop(self):
        """
        Stop the speech-to-line process.
        """
        self.stop = True
        if self.status_queue:
            self.status_queue.put("Stopped")


if __name__ == '__main__':
    from mqtt_controller.mqtt_controller import MQTTController
    import json
    import sys
    settings = json.loads(sys.argv[1])
    mqtt_controller = MQTTController('0.0.0.0', 1883, 'speech_to_line')
    mqtt_controller.connect()
    speech_to_line = SpeechToLine(mqtt_controller=mqtt_controller, settings=settings)
    speech_to_line.start()
