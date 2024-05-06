import json
from livereload import Server
from math import ceil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def load_json(json_path: Path) -> list:
    with open(json_path, 'r', encoding='utf-8') as books_json:
        books = json.loads(books_json.read())
    return books


def on_reload() -> None:
    templates_path = Path('templates')
    env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )

    index_template = env.get_template('index_template.html')

    books = load_json('downloaded_books.json')
    books_in_row = 2
    book_rows = chunked(books, books_in_row)

    rendered_page = index_template.render(
        book_rows=book_rows
    )

    with open('index.html', 'w', encoding='utf-8') as index:
        index.write(rendered_page)


if __name__ == '__main__':
    on_reload()

    server = Server()
    server.watch('templates/*.html', on_reload)
    server.serve(port=8000, host='0.0.0.0', root='.')
