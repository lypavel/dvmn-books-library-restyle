from argparse import ArgumentParser, Namespace
import json
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
    parser.add_argument('--start_page',
                        type=int,
                        help='Начальный id запрашиваемого интервала книг.',
                        required=False,
                        default=1)
    parser.add_argument('--end_page',
                        type=int,
                        help='Конечный id запрашиваемого интервала книг.',
                        required=False,
                        default=702)

    return parser.parse_args()


def main() -> None:
    env = Env()
    env.read_env()

    args = parse_script_arguments()

    start_page = args.start_page
    end_page = args.end_page

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
                book_path = download_txt(text_url,
                                         book_id,
                                         sanitize_filename(book['title']))
                img_src = download_image(book['image_url'])

                book.update({
                    'book_path': book_path.as_posix(),
                    'img_src': img_src.as_posix()
                })
                book.pop('image_url')
                books_json.append(book)
            except rq.exceptions.HTTPError:
                print(f'Книги с id={book_id} не существует.\n')
                continue

    with open('downloaded_books.json', 'w') as json_file:
        json.dump(books_json, json_file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    try:
        main()
    except rq.exceptions.ConnectionError:
        print('Невозможно подключиться к серверу. Переподключение...')
        time.sleep(30)
