from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_json(json_path: Path) -> list:
    with open(json_path, 'r', encoding='utf-8') as books_json:
        books = json.loads(books_json.read())
    return books


if __name__ == '__main__':
    templates_path = Path('templates')
    env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )

    index_template = env.get_template('index_template.html')

    rendered_page = index_template.render(
        books=load_json('downloaded_books.json')
    )

    with open('index.html', 'w', encoding='utf-8') as index:
        index.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()
