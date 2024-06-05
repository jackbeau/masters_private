import json
import logging
import string

class ScriptDataHandler:
    def __init__(self, json_data_file):
        self.json_data_file = json_data_file
        self.segments = []
        self.chunks = []
        self.load_json_data()
        self.create_chunks()

    def normalize_text(self, text):
        # Convert text to lowercase
        text = text.lower()
        # Remove punctuation and newlines
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.replace('\n', ' ')
        return text

    def load_json_data(self):
        try:
            with open(self.json_data_file, 'r') as json_file:
                json_data = json.load(json_file)
                for page in json_data['pages']:
                    for idx, fragment in enumerate(page['fragments']):
                        normalized_text = self.normalize_text(fragment['text'])
                        if normalized_text.strip():  # Skip empty lines
                            self.segments.append({
                                "page_number": page['page_number'],
                                "y_coordinate": int(fragment['bounds']['bottom'] + fragment['bounds']['height'] / 2),
                                "text": normalized_text.split(),  # Store as list of words
                                "fragment_id": idx  # Use index as ID
                            })
        except FileNotFoundError:
            logging.error(f"JSON file '{self.json_data_file}' not found.")
            raise

    def create_chunks(self):
        words = []
        fragment_ids = []
        coordinates = []
        page_numbers = []
        for fragment in self.segments:
            words.extend(fragment['text'])
            fragment_ids.extend([fragment['fragment_id']] * len(fragment['text']))
            coordinates.extend([fragment['y_coordinate']] * len(fragment['text']))
            page_numbers.extend([fragment['page_number']] * len(fragment['text']))

        chunk_size = 10
        overlap = 5
        chunk_id = 0
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_fragment_ids = fragment_ids[i:i + chunk_size]
            chunk_coordinates = coordinates[i:i + chunk_size]
            chunk_page_numbers = page_numbers[i:i + chunk_size]
            if len(chunk_words) < chunk_size:
                break
            chunk = {
                "id": chunk_id,
                "text": chunk_words,
                "first_fragment_id": chunk_fragment_ids[0],
                "last_fragment_id": chunk_fragment_ids[-1],
                "last_y_coordinate": chunk_coordinates[-1],
                "last_page_number": chunk_page_numbers[-1]
            }
            self.chunks.append(chunk)
            chunk_id += 1

if __name__ == "__main__":
    data_cleanup = ScriptDataHandler("server/storage/transcripts/output_extracted_data.json")
    print(data_cleanup.json_data)
    print(data_cleanup.segments)
