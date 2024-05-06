import json
from pathlib import Path

from environs import Env
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def load_json(json_path: Path) -> list:
    with open(json_path, 'r', encoding='utf-8') as books_json:
        books = json.loads(books_json.read())
    return books


def on_reload(env: Environment, books: list, pages_dir: Path) -> None:
    books_per_page = 20
    book_pages = list(chunked(books, books_per_page))
    last_page = len(book_pages)

    for page_num, book_page in enumerate(book_pages, start=1):

        books_in_row = 2
        book_rows = chunked(book_page, books_in_row)

        index_template = env.get_template('index_template.html')

        rendered_page = index_template.render(
            book_rows=book_rows,
            current_page=page_num,
            last_page=last_page
        )

        pages_dir.mkdir(exist_ok=True)
        with open(pages_dir / f'index{page_num}.html',
                  'w',
                  encoding='utf-8') as index:
            index.write(rendered_page)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    templates_path = Path('templates')
    jinja_env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )

    json_path = Path(
        env.str('PATH_TO_BOOKS_JSON', 'static/downloaded_books.json')
    )
    books = load_json(json_path)
    pages_dir = Path('pages')

    on_reload(jinja_env, books, pages_dir)

    host = env.str('SITE_HOST', '127.0.0.1')
    port = env.str('SITE_PORT', '5500')

    server = Server()
    server.watch('templates/index_template.html',
                 lambda: on_reload(jinja_env, books, pages_dir))
    server.serve(port=port, host=host, root='.')
