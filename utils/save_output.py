import json

def save_mapping(mapping, output_file="mapping.json"):
    with open(output_file, "w") as f:
        json.dump(mapping, f, indent=2)