import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

from bs4 import BeautifulSoup
from environs import Env
from pathvalidate import sanitize_filename
import requests as rq


def download_txt(book_id: int, folder: str | None = 'books/') -> str:
    text_url = env.str('BOOK_DOWNLOAD_URL')

    payload = {
        'id': book_id
    }

    response = rq.get(text_url, params=payload)
    response.raise_for_status()

    check_for_redirect(response)

    book = get_book_credits(book_id)
    title = sanitize_filename(book['title'])

    os.makedirs(folder, exist_ok=True)
    filepath = Path(folder, f'{book_id}. {title}.txt')
    with open(filepath, 'w') as file:
        file.write(response.text)

    download_image(book['image_url'])

    return filepath


def download_image(url: str, folder: str | None = 'images/') -> None:
    filename = urlsplit(unquote(url)).path.split('/')[-1]
    if filename == 'nopic.gif':
        return

    response = rq.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)
    filepath = Path(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_book_credits(book_id: int) -> dict:
    index_url = env.str('SITE_URL')
    book_url = urljoin(index_url, f'b{book_id}')

    response = rq.get(book_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    title, author = soup.find('td', class_='ow_px_td')\
                        .find('h1')\
                        .text.split(' \xa0 :: \xa0 ')
    image_url = soup.find('div', class_='bookimage')\
                    .find('img')['src']
    full_image_url = urljoin(index_url, image_url)

    return {
        'title': title,
        'author': author,
        'image_url': full_image_url,
        'comments': '',
        'genre': '',
    }


def check_for_redirect(response: rq.Response) -> bool:
    if response.history:
        raise rq.exceptions.HTTPError


def main(book_ids: range) -> None:
    for book_id in book_ids:
        try:
            download_txt(book_id)
        except rq.exceptions.HTTPError:
            continue


if __name__ == '__main__':
    env = Env()
    env.read_env()

    main(range(1, 11))
