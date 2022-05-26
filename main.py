import pathlib

import requests


def main():

    url_book = "https://tululu.org/b{}/"
    link_book = "https://tululu.org/txt.php"
    
    
    for number in range(0, 10):
        file_path = f"{folder}/{number}.txt"
        params ={"id": number}
        response = requests.get(url_book.format(number))
        
        response.raise_for_status()
        try:
            response = requests.get(link_book, params=params)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.HTTPError as error:
            print("Такой книги нет")


if __name__ == "__main__":
    folder = "book"
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    main()