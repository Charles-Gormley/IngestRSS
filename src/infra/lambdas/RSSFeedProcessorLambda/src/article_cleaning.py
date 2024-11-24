import re

def remove_newlines(text: str) -> str:
    return text.replace('\n', '')

def remove_urls(text: str) -> str:
    url_pattern = re.compile(r'http\S+|www\S+')
    return url_pattern.sub('', text)


def clean_text(text: str) -> str: 
    text = remove_newlines(text)
    text = remove_urls(text)
    return text