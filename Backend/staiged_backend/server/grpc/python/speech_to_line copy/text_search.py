import json
import logging
from thefuzz import fuzz
import string
from concurrent.futures import ThreadPoolExecutor
import sys

# Configure logging for the TextSearch class
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Use the same logger instance
logger = logging.getLogger("speech_to_line")
logger.setLevel(logging.INFO)

class TextSearch:
    def __init__(self, chunks, mqtt_controller=None):
        self.chunks = chunks
        self.mqtt_controller = mqtt_controller
        self.current_window = self.chunks[:10]  # Start with the first 10 chunks
        self.failed_attempts = 0
        self.failed_transcriptions = []
        self.similarity_threshold = 70  # Example threshold for similarity score
        self.executor = ThreadPoolExecutor(max_workers=1)  # Executor for running global search

    def clean_text(self, text):
        # Convert text to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def search_for_line(self, target_string):
        best_match = None
        best_score = 0

        cleaned_target_string = self.clean_text(target_string)

        for i, chunk in enumerate(self.current_window):
            chunk_text = ' '.join(chunk['text'])
            similarity_score = fuzz.partial_token_sort_ratio(
                chunk_text,
                cleaned_target_string
            )
            
            if similarity_score > best_score:
                best_score = similarity_score
                best_match = {
                    'chunk_index': i,
                    'chunk_text': chunk_text,
                    'input_line': cleaned_target_string,
                    'similarity_score': similarity_score
                }

        if best_match and best_score >= self.similarity_threshold:
            # Adjust the window based on the best match
            self.adjust_window(best_match['chunk_index'])
            self.failed_attempts = 0
            self.failed_transcriptions.clear()
        else:
            self.failed_attempts += 1
            self.failed_transcriptions.append(cleaned_target_string)
            if self.failed_attempts >= 5:
                self.executor.submit(self.global_search)  # Run global search in a separate thread

        if self.mqtt_controller is not None:
            try:
                result = self.mqtt_controller.publish(
                    "local_server/tracker/position",
                    json.dumps(best_match),
                    retain=True
                )
                logger.info(f"Published to MQTT topic, result: {result}")
            except Exception as e:
                logger.error(f"Failed to publish MQTT message: {e}")

        logger.info(f"Best match: '{best_match}' (Similarity: {best_score}%)")
        return best_match

    def adjust_window(self, best_chunk_index):
        # Move the window so that the best chunk is the second in the new window
        new_start_index = max(0, best_chunk_index - 1)
        self.current_window = self.chunks[new_start_index:new_start_index + 10]

    def global_search(self):
        logger.info("Initiating global search")
        highest_cumulative_score = 0
        best_window = None

        num_chunks = len(self.chunks)
        window_size = 10
        overlap = 5

        for i in range(0, num_chunks, overlap):  # Overlapping windows
            window = self.chunks[i:i + window_size]
            cumulative_score = 0

            for transcription in self.failed_transcriptions:
                for chunk in window:
                    chunk_text = " ".join(chunk['text'])
                    similarity_score = fuzz.partial_token_sort_ratio(chunk_text, transcription)
                    cumulative_score += similarity_score

            if cumulative_score > highest_cumulative_score and cumulative_score >= self.similarity_threshold * len(self.failed_transcriptions):
                highest_cumulative_score = cumulative_score
                best_window = window

        if best_window:
            self.current_window = best_window
            self.failed_attempts = 0
            self.failed_transcriptions.clear()
            logger.info(f"New window set based on global search with cumulative score: {highest_cumulative_score}")
