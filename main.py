import os
import pathlib
import argparse
from time import sleep

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin, urlsplit
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book_page(response, template_url):

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find(id="content").find('h1').text

    book_title, book_author = title_tag.split(" :: ")

    image_url = soup.find("div", class_="bookimage").find("img")["src"]
    full_image_url = urljoin(template_url, image_url)

    book_comments = soup.find_all("div", class_="texts")
    book_comments_texts = [comment_book.find("span", class_="black").text 
                           for comment_book in book_comments]

    book_genres = soup.find("span", class_="d_book").find_all("a")
    book_genres = [genre_tag.text for genre_tag in book_genres]


    book_parameters = {
        "name": book_title.strip(),
        "author": book_author.strip(),
        "image": full_image_url,
        "comments": book_comments_texts,
        "genre": book_genres,
    }

    return book_parameters


def save_book(response, filename, book_number, folder='books/'):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    file_path =  os.path.join(folder, f"{book_number}.{sanitize_filename(filename)}.txt")

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(response.text)


def download_image(image_url, folder="images/"):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()

    filename = urlsplit(image_url).path.split("/")[-1]
    filepath = os.path.join(folder, filename)

    with open(unquote(filepath), "wb") as file:
        file.write(response.content)
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description= "Проект скачивает книги и соответствующие им картинки,\
                     а также выводит дополнительную информацию "
    )
    parser.add_argument("--start_id", type=int,
                        help="Стартовая книга для скачивания", default=1)
    parser.add_argument("--end_id", type=int,
                        help="Конечная книга для скачивания", default=10)
    args = parser.parse_args()


    book_url = "https://tululu.org/b{}/"
    link_download_book = "https://tululu.org/txt.php"


    for book_number in range(args.start_id, args.end_id):

        params = {"id": book_number}
        book_response = requests.get(link_download_book, params)

        try:
            book_response.raise_for_status()
            check_for_redirect(book_response)

            response = requests.get(book_url.format(book_number))
            response.raise_for_status()
            check_for_redirect(response)

            book_parameters = parse_book_page(response, book_url)
            save_book(book_response, book_parameters["name"], book_number)
            download_image(book_parameters["image"])

        except requests.exceptions.HTTPError:
            print("Такой книги нет")
        except requests.exceptions.ConnectionError:
            print("Повторное подключение к серверу")
            sleep(20)


if __name__ == "__main__":
    main()
