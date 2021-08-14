import os
import re
import tempfile
import string
import random
import hashlib
from flask import current_app


def read_key_file(filename):
    key_path = current_app.config.get('KEYS_PATH').format(
        current_app.root_path,
        filename
    )
    with open(key_path, 'rb') as key_file:
        return key_file.read()


def random_string(length):
    return ''.join([random.choice(
        string.ascii_lowercase + string.digits
    ) for n in range(length)])


def hash_shake_128(s):
    m = hashlib.shake_128()
    m.update(bytes(s, 'utf-8'))
    return m.hexdigest(16)


def create_temp_file_from_bytes(data: bytes, suffix='txt'):
    """Create and returns a temporary file.
        The returned file is a copy of the file argument
        Arguments:
        'file' -- The file to copy
        'title' -- title of copied file.
        MUST CLOSE THE FILE FOR REMOVAL
        """
    dir = 'tmp'
    os.makedirs(dir, exist_ok=True)
    temp_file = tempfile.NamedTemporaryFile(dir=dir, suffix='.' + suffix)
    temp_file.write(data)

    return temp_file


def get_action_in_url(url):
    result = re.search('[^/]+(?=/$|$)', url)
    if result:
        return result.group(0).split('?')[0]
