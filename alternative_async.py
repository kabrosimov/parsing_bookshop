import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import csv
import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

list_of_books = []


async def send_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=HEADERS) as response:
            return await response.text()


async def get_page_data(page):

    url = f"https://www.labirint.ru/genres/2308/?order=date&way=back&available=1&price_min=&price_max=&page={page}"
    # if session.closed:
    #     session = aiohttp.ClientSession()
    # async with session.get(url=url, headers=HEADERS) as response:

    # src = await response.text()
    src = await send_request(url)
    soup = BeautifulSoup(src, 'lxml')
    tag_line = soup.find('div', id='catalog-navigation')
    # print(tag_line)
    t = tag_line.find_all_next(
        'div', class_='genres-carousel__item')
    for el in t:
        try:
            book_title = el.find('span', class_='product-title').text
        except:
            book_title = 'Нет названия'

        # print(book_title)
        try:
            book_authors_list = el.find(
                'div', class_='product-author').find_all('a')
            book_authors = ', '.join([author['title'].strip()
                                      for author in book_authors_list])
        except:
            book_authors = 'Не указан автор'
        try:
            book_pubhouse_list = el.find(
                'div', class_='product-pubhouse').find_all('a')
            book_pubhouse = ' : '.join([pubhouse['title'].strip()
                                        for pubhouse in book_pubhouse_list])
        except:
            book_pubhouse = 'Не указан издатель'

        try:
            book_new_price = el.find(
                'span', class_='price-val').find('span').text
        except:
            book_new_price = 'Нет новой цены'

        try:
            book_old_price = el.find(
                'span', class_='price-old').find('span').text
        except:
            book_old_price = 'Нет старой цены'
        # print(book_old_price.replace(' ', ''),
        #       book_new_price.replace(' ', ''))
        try:
            discount = round((int(book_old_price.replace(' ', '')) - int(book_new_price.replace(' ', ''))
                              ) / int(book_old_price.replace(' ', '')) * 100)

        except:
            discount = 'Ошибка'

# print(book_new_price, book_old_price)
        list_of_books.append({
            "book_title": book_title,
            "book_authors": book_authors,
            "book_pubhouse": book_pubhouse,
            "book_new_price": book_new_price,
            "book_old_price": book_old_price,
            "discount": discount,
        })
    print(f"[INFO] Завершено: {page}")

    # pass


async def gather_data():
    url = f"https://www.labirint.ru/genres/2308/?order=date&way=back&available=1&price_min=&price_max=&page=1"
    async with aiohttp.ClientSession() as session:

        response = await session.get(url=url, headers=HEADERS)
        soup = BeautifulSoup(await response.text(), 'lxml')
        tag_page = soup.find('div', class_='mb65').find_all('a')
        page_count = int(tag_page[-2].text)
        tasks = []

        for page in range(1, page_count + 1):
            task = asyncio.create_task(get_page_data(page))
            tasks.append(task)
        await asyncio.gather(*tasks)

        # print(page_count)
    # page_count = 1
    # list_of_books = []


def create_file():
    # print(len(list_of_books))
    # запись в файлы
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(list_of_books, file, indent=4, ensure_ascii=False)

    with open('result.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Authors', 'Pubhouse',
                        'NewPrice', 'OldPrice', 'Discount'])
    with open('result.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        for el in list_of_books:
            writer.writerow(
                (
                    el['book_title'],
                    el['book_authors'],
                    el['book_pubhouse'],
                    el['book_new_price'],
                    el['book_old_price'],
                    el['discount']
                )
            )


def main():
    start_datetime = datetime.datetime.now()
    asyncio.run(gather_data())
    create_file()

    difdatetime = datetime.datetime.now() - start_datetime
    print(difdatetime)


if __name__ == '__main__':
    main()
