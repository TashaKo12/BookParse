import os
import pathlib
import argparse


import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin, urlsplit
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book_page(response, url_book, template_url):
     
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find(id="content").find('h1').text
    
    title_book, avtor_book = title_tag.split(" :: ")

    image_url = soup.find("div", class_="bookimage").find("img")["src"]
    full_image_url = urljoin(template_url, image_url)

    comments_book = soup.find_all("div", class_="texts")
    comments_texts_book = [comment_book.find("span", class_="black").text 
                           for comment_book in comments_book]

    book_genres = soup.find("span", class_="d_book").find_all("a")
    book_genres = [genre_tag.text for genre_tag in book_genres]


    book_parametrs = {
        "Название": title_book.strip(),
        "Автор": avtor_book.strip(),
        "Картинка": full_image_url,
        "Комментарии": comments_texts_book,
        "Жанр": book_genres,

    }
    
    return book_parametrs


def save_book(response, filename, number_book, folder='books/'):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    file_path =  os.path.join(folder, f"{number_book}.{sanitize_filename(filename)}.txt")

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


    template_img_url = "https://tululu.org/shots/nopic.gif"
    url_book = "https://tululu.org/b{}/"
    link_download_book = "https://tululu.org/txt.php"


    for number_book in range(args.start_id, args.end_id):
        
        params = {"id": number_book}
        response = requests.get(link_download_book, params)
        
        try:
            response.raise_for_status()
            check_for_redirect(response)

            response = requests.get(url_book.format(number_book))
            response.raise_for_status()
            check_for_redirect(response)

            book_parametrs = parse_book_page(response, url_book, template_img_url)
            save_book(response, book_parametrs["Название"], number_book)
            download_image(book_parametrs["Картинка"])
            
        except requests.exceptions.HTTPError:
            print("Такой книги нет")
            continue


if __name__ == "__main__":
    main()