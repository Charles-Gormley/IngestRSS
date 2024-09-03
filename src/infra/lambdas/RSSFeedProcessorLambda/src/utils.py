import logging
import os
import hashlib

def setup_logging():
    logger = logging.getLogger()
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger.setLevel(logging.getLevelName(log_level))
    return logger


def generate_key(input_string, length=10):
    # Create a SHA256 hash of the input string
    hash_object = hashlib.sha256(input_string.encode())
    hex_dig = hash_object.hexdigest()
    
    # Return the first 'length' characters of the hash
    return hex_dig[:length]
