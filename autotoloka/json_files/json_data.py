import os
import json
import pathlib


def get_json_data():
    path = pathlib.Path(__file__).parent
    json_data = {}
    for item in os.listdir(path):
        if item[-5:] == '.json':
            key = item
            with open(f'{path}/{item}', 'r', encoding='utf-8') as file:
                value = json.load(file)
            json_data[key] = value
    return json_data


json_data = get_json_data()
