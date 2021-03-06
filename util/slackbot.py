import requests
from typing import List

SLACK_URL = 'https://hooks.slack.com/services/'


class Blocks:
    @staticmethod
    def section(text):
        return {'type': 'section', 'text': {'type:': 'mrkdwn', 'text': text}}

    @staticmethod
    def header(text):
        return {'type': 'header', 'text': {'type': 'plain_text', 'text': text, 'emoji': True}}

    @staticmethod
    def image(url, alt_text):
        return {'type': 'image', 'image_url': url, 'alt_text': alt_text}


def send_slack_post(secret, blocks: List[dict]) -> requests.Response:
    return requests.post(f'{SLACK_URL}{secret}', json={'blocks': blocks})
