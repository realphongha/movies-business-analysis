import json


def read_json_file(path):
    file = open(path, "r")
    lines = file.read().splitlines()
    file.close()
    return [json.loads(line) for line in lines]
