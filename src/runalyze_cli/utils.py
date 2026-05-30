import json
import os


def load_token():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("RUNALYZE_AUTH_TOKEN="):
                    return line.split("=", 1)[1].strip()
    return os.getenv("RUNALYZE_AUTH_TOKEN")


def parse_props(props):
    data = {}
    if not props:
        return data
    for prop in props:
        if "=" in prop:
            k, v = prop.split("=", 1)
            if not k:
                continue
            try:
                data[k] = json.loads(v)
            except json.JSONDecodeError:
                data[k] = v
    return data
