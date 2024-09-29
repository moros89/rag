import json

def read_json_config(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

public_config = read_json_config("./documents/config.json")
