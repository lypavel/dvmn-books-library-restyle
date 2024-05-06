import json
from livereload import Server
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def load_json(json_path: Path) -> list:
    with open(json_path, 'r', encoding='utf-8') as books_json:
        books = json.loads(books_json.read())
    return books


def on_reload(env: Environment, books: list, pages_dir: Path) -> None:
    books_per_page = 20
    book_pages = chunked(books, books_per_page)

    for page_num, book_page in enumerate(book_pages):

        books_in_row = 2
        book_rows = chunked(book_page, books_in_row)

        index_template = env.get_template('index_template.html')
        rendered_page = index_template.render(
            book_rows=book_rows
        )

        pages_dir.mkdir(exist_ok=True)
        with open(pages_dir / f'index{page_num + 1}.html',
                  'w',
                  encoding='utf-8') as index:
            index.write(rendered_page)


if __name__ == '__main__':
    templates_path = Path('templates')
    env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )

    json_path = Path('downloaded_books.json')
    books = load_json(json_path)
    pages_dir = Path('pages')

    on_reload(env, books)

    server = Server()
    server.watch('index_template.html', on_reload)
    server.serve(port=8000, host='0.0.0.0', root='.')
