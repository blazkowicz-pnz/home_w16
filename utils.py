import json

def load_data_from_json(path):
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
        return data



