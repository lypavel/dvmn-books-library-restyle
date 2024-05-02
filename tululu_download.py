from pathlib import Path

import requests as rq
from urllib.parse import urlsplit, unquote


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

    response = rq.get(text_url, params=payload)
    response.raise_for_status()

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

    if filename == 'nopic.gif':
        return filepath

    response = rq.get(url)
    response.raise_for_status()

    if filepath.exists():
        return filepath

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath
