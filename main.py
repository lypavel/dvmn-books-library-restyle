import os
from pathlib import Path

from environs import Env
import requests as rq


def download_books(url: str, ids: range) -> None:
    os.makedirs('books', exist_ok=True)

    for id in ids:
        payload = {
            'id': id
        }

        response = rq.get(url, params=payload)
        response.raise_for_status()

        filepath = Path('books', f'book{id}.txt')
        with open(filepath, 'w') as book:
            book.write(response.text)


def main(site_url: str) -> None:
    download_books(site_url, range(1, 11))


if __name__ == '__main__':
    env = Env()
    env.read_env()

    site_url = env.str('SITE_URL')

    main(site_url)
