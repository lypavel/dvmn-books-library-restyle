from argparse import ArgumentParser, Namespace
import json
from pathlib import Path
import time
from urllib.parse import urljoin, urlsplit

from environs import Env
import requests as rq
from pathvalidate import sanitize_filename

from tululu_parse import parse_page, parse_book_data
from tululu_download import download_txt, download_image, check_for_redirect


def print_book_info(book: dict) -> None:
    print(
        f'Заголовок: {book["title"]}',
        f'Автор: {book["author"]}',
        f'Жанры: {book["genres"]}',
        sep='\n'
    )

    comments = book['comments']
    if comments:
        print(
            'Комментарии:',
            '\n'.join(book['comments']),
            sep='\n'
        )

    print()


def parse_script_arguments(last_page: int = 2) -> Namespace:
    parser = ArgumentParser(
        description='Парсер для онлайн библиотеки \"Tululu\"'
    )
    parser.add_argument(
        '--start_page',
        type=int,
        help='С какой страницы начать скачивание',
        required=False,
        default=1
    )
    parser.add_argument(
        '--end_page',
        type=int,
        help='На какой странице закончить скачивание (не включительно)',
        required=False,
        default=702
    )
    parser.add_argument(
        '--dest_folder',
        type=str,
        help='Путь к каталогу с результатами парсинга',
        required=False,
        default='.'
    )
    parser.add_argument(
        '--json_file',
        type=str,
        help='Путь к json-файлу с информацией о скачанных книгах',
        required=False,
        default='downloaded_books.json'
    )
    parser.add_argument(
        '--skip_imgs',
        help='Не скачивать обложки книг',
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '--skip_txt',
        help='Не скачивать текст книг',
        required=False,
        action='store_true'
    )

    return parser.parse_args()


def main() -> None:
    env = Env()
    env.read_env()

    args = parse_script_arguments()

    start_page = args.start_page
    end_page = args.end_page
    dest_folder = Path(args.dest_folder)
    dest_folder.mkdir(exist_ok=True)

    category_url = env.str('CATEGORY_URL')
    text_url = env.str('BOOK_DOWNLOAD_URL')
    books_json = []

    for page in range(start_page, end_page):
        try:
            page_url = urljoin(category_url, str(page))
            page_response = rq.get(page_url)
            page_response.raise_for_status()

            check_for_redirect(page_response)
        except rq.exceptions.HTTPError:
            print(f'Страницы с номером {page} не существует.\n')
            continue

        book_urls = parse_page(page_url, page_response.text)

        for book_url in book_urls:
            book_id = urlsplit(book_url).path.strip('/b')
            try:
                book_response = rq.get(book_url)
                book_response.raise_for_status()
                check_for_redirect(book_response)

                book = parse_book_data(book_response.url, book_response.text)
                print_book_info(book)

                book_path = None
                if not args.skip_txt:
                    book_path = download_txt(
                        text_url,
                        book_id,
                        sanitize_filename(book['title']),
                        dest_folder
                    ).as_posix()

                img_src = None
                if not args.skip_imgs:
                    img_src = download_image(
                        book['image_url'],
                        dest_folder
                    ).as_posix()

                book.update({
                    'book_path': book_path,
                    'img_src': img_src
                })
                book.pop('image_url')
                books_json.append(book)
            except rq.exceptions.HTTPError:
                print(f'Книги с id={book_id} не существует.\n')
                continue

    json_path = Path(args.json_file)
    with open(json_path, 'w') as json_file:
        json.dump(books_json, json_file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    try:
        main()
    except rq.exceptions.ConnectionError:
        print('Невозможно подключиться к серверу. Переподключение...')
        time.sleep(30)
