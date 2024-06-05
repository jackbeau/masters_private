import logging
import json
import csv
from thefuzz import fuzz
import string
from concurrent.futures import ThreadPoolExecutor
import sys

# Configure logging for the TextSearch class
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Use the same logger instance
logger = logging.getLogger("speech_to_script_pointer")
logger.setLevel(logging.INFO)

MAX_FAILED_ATTEMPTS = 5
INTERMEDIATE_THRESHOLD_LOWER = 50
INTERMEDIATE_THRESHOLD_UPPER = 60
FORWARD_WINDOW_SIZE = 10
BACKWARD_WINDOW_SIZE = 10

class TextSearch:
    def __init__(self, chunks, mqtt_controller=None, log_file='search_log.csv'):
        self.chunks = chunks
        self.mqtt_controller = mqtt_controller
        self.current_window = self.chunks[:FORWARD_WINDOW_SIZE]  # Start with the first 10 chunks
        self.current_window_start_index = 0  # Start index of the current window
        self.intermediate_attempts = 0
        self.failed_transcriptions = []
        self.executor = ThreadPoolExecutor(max_workers=1)  # Executor for running global search
        self.best_match = None
        self.global_search_active = False
        self.last_input = None  # To store the last input string
        self.log_file = log_file

        # Initialize CSV file with headers
        with open(self.log_file, 'w', newline='') as csvfile:
            fieldnames = ['search_type', 'best_score', 'target_string', 'chunk_text', 'page_number']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def clean_text(self, text):
        # Convert text to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def log_search(self, search_type, best_score, target_string, chunk_text, page_number):
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['search_type', 'best_score', 'target_string', 'chunk_text', 'page_number'])
            writer.writerow({
                'search_type': search_type,
                'best_score': best_score,
                'target_string': target_string,
                'chunk_text': chunk_text,
                'page_number': page_number
            })

    def search_for_line(self, target_string):
        if not target_string or target_string == self.last_input:
            logger.info("Empty or duplicate input. Skipping search.")
            return None
        
        self.last_input = target_string  # Update the last input string
        best_match = None
        best_score = 0

        cleaned_target_string = self.clean_text(target_string)
        target_words = cleaned_target_string.split()

        for i, chunk in enumerate(self.current_window):
            chunk_text = ' '.join(chunk['text'])
            chunk_words = chunk_text.split()

            # Crop the target string to the length of the chunk if it's longer
            if len(target_words) > len(chunk_words):
                cropped_target_string = ' '.join(target_words[:len(chunk_words)])
            else:
                cropped_target_string = cleaned_target_string

            similarity_score = fuzz.token_set_ratio(
                chunk_text,
                cropped_target_string
            )

            if similarity_score > INTERMEDIATE_THRESHOLD_LOWER and similarity_score > best_score:
                best_score = similarity_score
                best_match = {
                    'page_number': chunk.get('last_page_number'),
                    'y_coordinate': chunk.get('last_y_coordinate'),
                    'chunk_index': chunk.get('id'),
                    'chunk_text': chunk_text,
                    'input_line': cropped_target_string,
                    'similarity_score': similarity_score,
                }

        # Log the best score for the local search
        if best_match:
            self.log_search('local', best_score, cropped_target_string, best_match['chunk_text'], best_match['page_number'])
        else:
            # Log when no match is found
            self.log_search('local', best_score, cropped_target_string, '', '')

        if best_match:
            # Adjust the window based on the best match
            self.adjust_window(best_match['chunk_index'])
            self.best_match = best_match
        if best_match and best_score >= INTERMEDIATE_THRESHOLD_UPPER:
            # Reset the global search flag if the score is above the upper threshold
            self.intermediate_attempts = 0
            self.failed_transcriptions.clear()
        else:
            # Increment intermediate_attempts if the score is within the intermediate threshold
            self.intermediate_attempts += 1
            self.failed_transcriptions.append(target_string)  # Use the original target_string here
            if self.intermediate_attempts >= MAX_FAILED_ATTEMPTS and not self.global_search_active:
                self.global_search_active = True
                self.executor.submit(self.global_search)  # Run global search in a separate thread

        if self.mqtt_controller is not None and self.best_match is not None:
            try:
                result = self.mqtt_controller.publish(
                    "local_server/tracker/position",
                    json.dumps(self.best_match),
                    retain=True
                )
                logger.info(f"Published to MQTT topic, result: {result}")
            except Exception as e:
                logger.error(f"Failed to publish MQTT message: {e}")

        logger.info(f"Best match: '{self.best_match}'")
        return best_match

    def adjust_window(self, best_chunk_index):
        # Move the window so that the best chunk is within the new window
        new_start_index = max(0, best_chunk_index - BACKWARD_WINDOW_SIZE)
        new_end_index = min(len(self.chunks), best_chunk_index + FORWARD_WINDOW_SIZE)
        self.current_window = self.chunks[new_start_index:new_end_index]
        self.current_window_start_index = new_start_index

    def global_search(self):
        logger.info("Initiating global search")
        highest_cumulative_score = 0
        best_window = None
        best_global_match = None
        best_global_score = 0

        num_chunks = len(self.chunks)
        window_size = FORWARD_WINDOW_SIZE + BACKWARD_WINDOW_SIZE
        overlap = max(1, window_size // 2)

        for i in range(0, num_chunks, overlap):
            start_index = max(0, i - BACKWARD_WINDOW_SIZE)
            end_index = min(num_chunks, start_index + window_size)
            window = self.chunks[start_index:end_index]
            cumulative_score = 0
            match_count = 0

            for transcription in self.failed_transcriptions:
                best_chunk_score = 0
                cleaned_transcription = self.clean_text(transcription)
                transcription_words = cleaned_transcription.split()

                for chunk in window:
                    chunk_text = " ".join(chunk['text'])
                    chunk_words = chunk_text.split()

                    # Crop the transcription to the length of the chunk if it's longer
                    if len(transcription_words) > len(chunk_words):
                        cropped_transcription = ' '.join(transcription_words[:len(chunk_words)])
                    else:
                        cropped_transcription = cleaned_transcription

                    similarity_score = fuzz.partial_token_sort_ratio(chunk_text, cropped_transcription)
                    if similarity_score > best_chunk_score:
                        best_chunk_score = similarity_score
                        best_global_match = {
                            'page_number': chunk.get('last_page_number'),
                            'y_coordinate': chunk.get('last_y_coordinate'),
                            'chunk_index': chunk.get('id'),
                            'chunk_text': chunk_text,
                            'input_line': cropped_transcription,
                            'similarity_score': similarity_score,
                        }
                cumulative_score += best_chunk_score
                if best_chunk_score >= INTERMEDIATE_THRESHOLD_UPPER:
                    match_count += 1

            if match_count >= 4 and cumulative_score > highest_cumulative_score:
                highest_cumulative_score = cumulative_score
                best_window = window
                best_global_score = best_chunk_score

        if best_window:
            self.current_window = best_window
            self.current_window_start_index = self.chunks.index(best_window[0])
            logger.info(f"New window set based on global search with cumulative score: {highest_cumulative_score}")

            # Log the best score for the global search
            if best_global_match:
                self.log_search('global', best_global_score, best_global_match['input_line'], best_global_match['chunk_text'], best_global_match['page_number'])
        else:
            # Log when no match is found during global search
            self.log_search('global', best_global_score, ','.join(self.failed_transcriptions), '', '')

        self.intermediate_attempts = 0
        self.failed_transcriptions.clear()
        self.global_search_active = False
