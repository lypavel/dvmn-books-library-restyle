from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_category_page(page_url: str, page_html: str) -> list[str]:
    soup = BeautifulSoup(page_html, 'lxml')

    book_tables = soup.select('.d_book')
    book_urls = []
    for book_table in book_tables:
        book_url = book_table.select_one('a')['href']
        full_book_url = urljoin(page_url, book_url)
        book_urls.append(full_book_url)

    return book_urls


def parse_book_page(book_url: str, book_html: str) -> dict:
    soup = BeautifulSoup(book_html, 'lxml')

    title, author = soup.select_one('.ow_px_td h1')\
                        .text.split(' \xa0 :: \xa0 ')

    image_url = soup.select_one('.bookimage img')['src']
    full_image_url = urljoin(book_url, image_url)

    comments = [comment.text for comment in soup.select('.texts .black')]

    genres = [genre.text for genre in soup.select('span.d_book a')]

    return {
        'title': title,
        'author': author,
        'image_url': full_image_url,
        'comments': comments,
        'genres': genres,
    }
