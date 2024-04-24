import argparse
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

from bs4 import BeautifulSoup
from environs import Env
from pathvalidate import sanitize_filename
import requests as rq


def download_txt(index_url: str,
                 text_url: str,
                 book_id: int,
                 title: str,
                 folder: str | None = 'books/') -> str:
    payload = {
        'id': book_id
    }

    response = rq.get(text_url, params=payload)
    response.raise_for_status()

    check_for_redirect(index_url, response)

    download_dir = Path(folder)
    download_dir.mkdir(exist_ok=True)
    filepath = download_dir / f'{book_id}. {title}.txt'

    with open(filepath, 'w') as file:
        file.write(response.text)

    return filepath


def download_image(url: str, folder: str | None = 'images/') -> None:
    filename = urlsplit(unquote(url)).path.split('/')[-1]
    if filename == 'nopic.gif':
        return

    response = rq.get(url)
    response.raise_for_status()

    download_dir = Path(folder)
    download_dir.mkdir(exist_ok=True)
    filepath = download_dir / filename

    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(index_url: str, book_id: int) -> dict:
    book_url = urljoin(index_url, f'b{book_id}')

    response = rq.get(book_url)
    response.raise_for_status()

    check_for_redirect(index_url, response)

    soup = BeautifulSoup(response.text, 'lxml')

    title, author = soup.find('td', class_='ow_px_td')\
                        .find('h1')\
                        .text.split(' \xa0 :: \xa0 ')
    image_url = soup.find('div', class_='bookimage')\
                    .find('img')['src']
    full_image_url = urljoin(index_url, image_url)

    comments = []
    div_comments = soup.find_all('div', class_='texts')
    for div_comment in div_comments:
        comment = div_comment.find('span', class_='black')
        comments.append(comment.text)

    genres = []
    span_genres = soup.find('span', class_='d_book').find_all('a')
    for span_genre in span_genres:
        genres.append(span_genre.text)

    return {
        'title': title,
        'author': author,
        'image_url': full_image_url,
        'comments': comments,
        'genres': genres,
    }


def print_book_info(book: dict):
    print(
        f'Заголовок: {book["title"]}',
        f'Автор: {book["author"]}',
        book["genres"],
        '\n'.join(book['comments']),
        sep='\n'
    )
    print()  # separate books with '\n'


def check_for_redirect(index_url: str, response: rq.Response) -> bool:
    if response.history and response.url == index_url:
        raise rq.exceptions.HTTPError


def main(book_ids: range) -> None:
    index_url = env.str('SITE_URL')
    text_url = env.str('BOOK_DOWNLOAD_URL')
    for book_id in book_ids:
        try:
            book = parse_book_page(index_url, book_id)
            print_book_info(book)

            download_txt(index_url,
                         text_url,
                         book_id,
                         sanitize_filename(book['title']))

            download_image(book['image_url'])
        except rq.exceptions.HTTPError:
            print(f'Книги с id={book_id} не существует.')
            continue
        except rq.exceptions.ConnectionError:
            print('Невозможно подключиться к серверу.'
                  'Проверьте ваше интернет-соединение и попробуйте снова.')


if __name__ == '__main__':
    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser(
        description='Парсер для онлайн библиотеки \"Tululu\"'
    )
    parser.add_argument('start_id',
                        type=int,
                        help='Начальный id запрашиваемого интервала книг.')
    parser.add_argument('end_id',
                        type=int,
                        help='Конечный id запрашиваемого интервала книг.')
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id

    main(range(start_id, end_id + 1))
