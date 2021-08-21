import os
import json
import pathlib


def get_json_data():
    json_data = {}
    for item in os.listdir(os.path.join(path, 'json_files')):
        if item[-5:] == '.json':
            key = item[:-5]
            with open(os.path.join(path, 'json_files', item), 'r', encoding='utf-8') as file:
                value = json.load(file)
            json_data[key] = value
    return json_data


path = pathlib.Path(__file__).parent
json_data = get_json_data()
