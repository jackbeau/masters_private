import json
import logging
from thefuzz import fuzz
import string
from concurrent.futures import ThreadPoolExecutor
import sys
import csv
# Configure logging for the TextSearch class
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Use the same logger instance
logger = logging.getLogger("speech_to_script_pointer")
logger.setLevel(logging.INFO)

MAX_FAILED_ATTEMPTS = 5
SIMILARITY_THRESHOLD = 1
FORWARD_WINDOW_SIZE = 10
BACKWARD_WINDOW_SIZE = 1

class TextSearch:
    def __init__(self, chunks, csv_file_path, mqtt_controller=None):
        self.chunks = chunks
        self.mqtt_controller = mqtt_controller
        self.csv_file_path = csv_file_path
        self.current_windows = {
            "simple_ratio": self.chunks[44:44+FORWARD_WINDOW_SIZE],
            "partial_ratio": self.chunks[44:44+FORWARD_WINDOW_SIZE],
            "token_sort_ratio": self.chunks[44:44+FORWARD_WINDOW_SIZE],
            "token_set_ratio": self.chunks[44:44+FORWARD_WINDOW_SIZE],
            "partial_token_sort_ratio": self.chunks[44:44+FORWARD_WINDOW_SIZE],
        }
        self.current_window_start_indices = {
            "simple_ratio": 0,
            "partial_ratio": 0,
            "token_sort_ratio": 0,
            "token_set_ratio": 0,
            "partial_token_sort_ratio": 0
        }
        self.failed_attempts = 0
        self.failed_transcriptions = []
        self.similarity_threshold = SIMILARITY_THRESHOLD  # Example threshold for similarity score
        self.executor = ThreadPoolExecutor(max_workers=1)  # Executor for running global search
        self._initialize_csv()

    def _initialize_csv(self):
        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['method', 'page_number', 'y_coordinate', 'chunk_index', 'chunk_text', 'input_line', 'similarity_score'])
            writer.writeheader()

    def _append_to_csv(self, result):
        with open(self.csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['method', 'page_number', 'y_coordinate', 'chunk_index', 'chunk_text', 'input_line', 'similarity_score'])
            writer.writerow(result)

    def clean_text(self, text):
        # Convert text to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def search_for_line(self, target_string):
        cleaned_target_string = self.clean_text(target_string)
        target_words = cleaned_target_string.split()
        best_matches = {}
        
        for method in ["simple_ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio", "partial_token_sort_ratio"]:
            best_match = None
            best_score = 0
            current_window = self.current_windows[method]

            for i, chunk in enumerate(current_window):
                chunk_text = ' '.join(chunk['text'])
                chunk_words = chunk_text.split()

                # Crop the target string to the length of the chunk if it's longer
                if len(target_words) > len(chunk_words):
                    cropped_target_string = ' '.join(target_words[:len(chunk_words)])
                else:
                    cropped_target_string = cleaned_target_string

                if method == "simple_ratio":
                    similarity_score = fuzz.ratio(chunk_text, cropped_target_string)
                elif method == "partial_ratio":
                    similarity_score = fuzz.partial_ratio(chunk_text, cropped_target_string)
                elif method == "token_sort_ratio":
                    similarity_score = fuzz.token_sort_ratio(chunk_text, cropped_target_string)
                elif method == "token_set_ratio":
                    similarity_score = fuzz.token_set_ratio(chunk_text, cropped_target_string)
                elif method == "partial_token_sort_ratio":
                    similarity_score = fuzz.partial_token_sort_ratio(chunk_text, cropped_target_string)

                if similarity_score > best_score:
                    best_score = similarity_score
                    best_match = {
                        'method': method,
                        'page_number': chunk.get('last_page_number'),
                        'y_coordinate': chunk.get('last_y_coordinate'),
                        'chunk_index': chunk.get('id'),
                        'chunk_text': chunk_text,
                        'input_line': cropped_target_string,
                        'similarity_score': similarity_score,
                    }

            best_matches[method] = best_match

            if best_match and best_score >= self.similarity_threshold:
                # Adjust the window based on the best match
                self.adjust_window(best_match['chunk_index'], method)
                self.failed_attempts = 0
                self.failed_transcriptions.clear()
            else:
                self.failed_attempts += 1
                self.failed_transcriptions.append(cleaned_target_string)

            logger.info(f"Best match for {method}: '{best_match}' (Similarity: {best_score}%)")

            if best_match:
                self._append_to_csv(best_match)
        
        if self.mqtt_controller is not None:
            try:
                result = self.mqtt_controller.publish(
                    "local_server/tracker/position",
                    json.dumps(best_matches),
                    retain=True
                )
                logger.info(f"Published to MQTT topic, result: {result}")
            except Exception as e:
                logger.error(f"Failed to publish MQTT message: {e}")

        return best_matches

    def adjust_window(self, best_chunk_index, method):
        # Move the window so that the best chunk is the second in the new window
        new_start_index = max(0, best_chunk_index - BACKWARD_WINDOW_SIZE)
        self.current_windows[method] = self.chunks[new_start_index:new_start_index + FORWARD_WINDOW_SIZE]
        self.current_window_start_indices[method] = new_start_index

    def global_search(self):
        logger.info("Initiating global search")
        highest_cumulative_score = 0
        best_window = None

        num_chunks = len(self.chunks)
        window_size = FORWARD_WINDOW_SIZE + BACKWARD_WINDOW_SIZE
        overlap = window_size // 2

        for i in range(0, num_chunks, overlap):  # Overlapping windows
            start_index = max(0, i - BACKWARD_WINDOW_SIZE)
            window = self.chunks[start_index:start_index + window_size]
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
            self.current_windows = {method: best_window for method in self.current_windows}
            self.current_window_start_indices = {method: self.chunks.index(best_window[0]) for method in self.current_windows}
            self.failed_attempts = 0
            self.failed_transcriptions.clear()
            logger.info(f"New window set based on global search with cumulative score: {highest_cumulative_score}")

# Usage example
if __name__ == "__main__":
    # This is an example. You need to ensure you have a file "server/storage/transcripts/output_extracted_data.json"
    # with the appropriate format for this to work correctly.
    chunks = [
        # Example chunks
        {"id": 0, "text": ["this", "is", "a", "test"], "last_page_number": 1, "last_y_coordinate": 100},
        {"id": 1, "text": ["another", "chunk", "of", "text"], "last_page_number": 1, "last_y_coordinate": 150},
        # Add more chunks as needed for testing
    ]
    text_search = TextSearch(chunks)
    result = text_search.search_for_line("test")
    print(result)
