import os
import pathlib


import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def parse_book(number_book, url_book):
    response = requests.get(url_book.format(number_book))
    response.raise_for_status()
    check_for_redirect(response)
    
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find(id="content").find('h1').text
    
    title_book, avtor_book = title_tag.split(" :: ")
    avtor_book = avtor_book.strip()
    title_book = title_book.strip()
    print(title_book)
    return title_book, avtor_book
    #image=soup.find('img', class_='attachment-post-image')['src']
    #post_text = soup.find(class_="entry-content").text


def save_book(response, filename, number_book, folder='С'):
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    file_path =  os.path.join(folder, f"{number_book}.{sanitize_filename(filename)}.txt")

    print(file_path)
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(response.text)


def main():
    
    url_book = "https://tululu.org/b{}/"
    link_download_book = "https://tululu.org/txt.php"

    

    for number_book in range(1, 11):
        
        params = {"id": number_book}
        response = requests.get(link_download_book, params)
        #response = requests.get(url_book.format(number_book))
        
        try:
            response.raise_for_status()
            check_for_redirect(response)
            title_book, avtor_book = parse_book(number_book, url_book)
            save_book(response, title_book, number_book)
           
            
        except requests.exceptions.HTTPError:
            print("Такой книги нет")
            continue


if __name__ == "__main__":
    
    main()