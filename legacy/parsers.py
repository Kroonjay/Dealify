from models import CraigslistItem
from datetime import datetime
import re


def parse_price(source_price):
    if not source_price:
        return None
    out_price = ''.join(i for i in source_price if i.isalnum())
    return int(out_price)


def parse_special(source_text):
    if not source_text:
        return None
    # Simple regex to strip all special chars https://stackoverflow.com/questions/43358857/how-to-remove-special-characters-except-space-from-a-file-in-python/43358965
    out_text = re.sub(r"\W+|_", " ", source_text)
    return out_text
