from thefuzz import fuzz
import logging
import json

class TextSearch:
    def __init__(self, json_data):
        self.json_data = json_data

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

        logging.info(f"Best match: '{best_match}' (Similarity: {best_score}%)")
        return best_match
