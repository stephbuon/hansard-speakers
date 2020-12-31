import re
import os


DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT2 = '%Y/%m/%d'

MP_ALIAS_PATTERN = re.compile(r'\(([^\)]+)\)')


INPUT_DIR = os.environ.get('SCRATCH', 'data')
OUTPUT_DIR = os.environ.get('SCRATCH', '.')


DATA_FILE = os.path.join(INPUT_DIR, 'hansard_justnine_12192019.csv')

CHUNK_SIZE = 10**6


def cleanse_string(s):
    # Cleanse string from trailing and leading white space.
    s = s.lower().strip()

    # Remove characters that are not alphabetical, a hyphen, or a space.
    s = re.sub(r"[^a-zA-Z\- ]", "", s)

    # Change multiple whitespaces to single spaces.
    s = re.sub(r' +', ' ', s)
    return s
