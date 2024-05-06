# Библиотека научной фантастики

Готовый макет оффлайн сайта-библиотеки с возможностью самостоятельно скачивать интересующие вас книги с сайта онлайн-библиотеки [tululu.org](https://tululu.org/)

## Установка

1. Скачайте код репозитория.
2. Установите Python [3.10.12](https://www.python.org/downloads/release/python-31012/) и создайте [виртуальное окружение](https://docs.python.org/3/library/venv.html), если нужно.
3. Установите все необходимые зависимости с помощью `pip`:
    ```shell
    pip install -r requirements.txt
    ```
4. Создайте в корневой директории с кодом файл `.env` со следующим содержимым:
    ```env
    BOOK_DOWNLOAD_URL='https://tululu.org/txt.php'
    CATEGORY_URL='https://tululu.org/l55/'  

    SITE_PORT='5500'
    SITE_HOST='127.0.0.1'
    PATH_TO_BOOKS_JSON='static/downloaded_books.json'
    ```

    `BOOK_DOWNLOAD_URL` - общий URL с текстами книг<br>
    `CATEGORY_URL` - URL нужной категории книг<br>
    `SITE_PORT` - порт, на котором запустится локальный сайт<br>
    `SITE_HOST` - хост, на котором запустится локальный сайт<br>
    `PATH_TO_BOOKS_JSON` - путь к json файлу с информацией о скачанных книгах<br>

5. Удалите директории `./media` и `./pages`, а также `./static/downloaded_books.json`, если собираетесь скачивать книги самостоятельно.

## Скачивание книг с [tululu.org](https://tululu.org/)

С помощью этого скрипта вы сможете скачивать книги с обложками с сайта [tululu.org](https://tululu.org/), а также просматривать следующую информацию по каждой запрошенной книге:

* Название
* Автор
* Жанры
* Текст комментариев

### Использование

```shell
python3 download_books.py --start_page <start_page> --end_page <end_page> --dest_folder <dest_folder> --json_file <json_file> --skip_imgs --skip_txt
```

`<start_page>` - с какой страницы выбранной категории начать скачивание, по-умолчанию `1`<br>
`<end_page>` - на какой странице закончить скачивание (не включительно), по-умолчанию `702`<br>
`<dest_folder>` - в какой директории хранить скачанные тексты и обложки книг, по-умолчанию `.`<br>
`<json_file>` - путь к json-файлу с информацией о скачанных книгах, по-умолчанию `static/downloaded_books.json`<br>
`--skip_txt` - не скачивать тексты книг<br>
`--skip_imgs` - не скачивать обложки книг<br>

**ВНИМАНИЕ!** Если вы изменили путь в `<json_file>`, то его следует также изменить и в `PATH_TO_BOOKS_JSON` в `.env`.<br>

Все найденные книги скачиваются в директорию `<dest_folder>/books`<br>
Все найденные обложки скачиваются в директорию `<dest_folder>/images`<br>

## Запуск сайта со скачанными книгами

```shell
python3 render_website.py
```
В директории `./pages` будут созданы страницы, содержащие информацию о скачанных книгах.<br>
По-умолчанию сайт будет доступен по адресу [127.0.0.1:5500](127.0.0.1:5500).

### Пример работы сайта на Github Pages

<details>
  <summary>Внешний вид первой страницы библиотеки</summary>
  <img src="https://github.com/lypavel/dvmn-books-library-restyle/assets/157053921/eb53031b-b3a9-4f69-b9d0-3106f97a97cc" alt="Внешний вид первой страницы библиотеки" width="500">
</details>

[Пример работы сайта с первыми четырьмя скачанными страницами категории "Научная фантастика".](https://lypavel.github.io/dvmn-books-library-restyle/index.html)

***

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
