from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_page(page_url: str, page_html: str) -> list[str]:
    soup = BeautifulSoup(page_html, 'lxml')

    book_tables = soup.find_all('table', class_='d_book')
    book_urls = []
    for book_table in book_tables:
        book_url = book_table.find('a')['href']
        full_book_url = urljoin(page_url, book_url)
        book_urls.append(full_book_url)

    return book_urls


def parse_book_data(book_url: str, book_html: str) -> dict:
    soup = BeautifulSoup(book_html, 'lxml')

    title, author = soup.find('td', class_='ow_px_td')\
                        .find('h1')\
                        .text.split(' \xa0 :: \xa0 ')
    image_url = soup.find('div', class_='bookimage')\
                    .find('img')['src']
    full_image_url = urljoin(book_url, image_url)

    comments = []
    div_comments = soup.find_all('div', class_='texts')
    for div_comment in div_comments:
        comment = div_comment.find('span', class_='black')
        comments.append(comment.text)

    span_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in span_genres]

    return {
        'title': title,
        'author': author,
        'image_url': full_image_url,
        'comments': comments,
        'genres': genres,
    }