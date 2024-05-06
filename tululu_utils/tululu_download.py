import time
from pathlib import Path
from urllib.parse import urlsplit, unquote

import requests as rq


def send_get_request(url: str, payload: dict | None = None) -> rq.Response:
    attempt = 1
    max_fast_attempts = 3
    while True:
        try:
            response = rq.get(url, params=payload)
            response.raise_for_status()
            return response
        except rq.exceptions.ConnectionError:
            print('Невозможно подключиться к серверу. Переподключение...')
            if attempt > max_fast_attempts:
                time.sleep(30)
            attempt += 1


def check_for_redirect(response: rq.Response) -> None:
    if response.history:
        raise rq.exceptions.HTTPError


def download_txt(text_url: str,
                 book_id: int,
                 title: str,
                 dest_folder: Path,
                 folder: str | None = 'books/') -> Path:
    payload = {
        'id': book_id
    }

    response = send_get_request(text_url, payload=payload)
    check_for_redirect(response)

    download_dir = dest_folder / folder
    download_dir.mkdir(exist_ok=True)
    filepath = download_dir / f'{book_id}. {title}.txt'
    if filepath.exists():
        return filepath

    with open(filepath, 'w') as file:
        file.write(response.text)

    return filepath


def download_image(url: str,
                   dest_folder: Path,
                   folder: str | None = 'images/') -> Path:
    download_dir = dest_folder / folder
    download_dir.mkdir(exist_ok=True)

    filename = urlsplit(unquote(url)).path.split('/')[-1]
    filepath = download_dir / filename

    response = send_get_request(url)

    if filepath.exists():
        return filepath

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath
