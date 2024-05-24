import json
import logging
from thefuzz import fuzz

class TextSearch:
    def __init__(self, json_data, mqtt_controller=None):
        self.json_data = json_data
        self.mqtt_controller = mqtt_controller

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
