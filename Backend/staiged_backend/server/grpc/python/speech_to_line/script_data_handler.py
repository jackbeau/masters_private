import json
import logging

class ScriptDataHandler:
    def __init__(self, json_data_file):
        self.json_data_file = json_data_file
        self.json_data = []
        self.load_json_data()

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
