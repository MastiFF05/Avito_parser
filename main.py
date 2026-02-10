import csv
import time
import requests
from bs4 import BeautifulSoup


def parse_avito_cars(max_pages=100):
    BASE_URL = 'https://www.avito.ru/'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    DELAY = 2

    session = requests.Session()
    session.headers.update(HEADERS)

    cars = []
    current_page = 1
    url = 'https://www.avito.ru/moskva/avtomobili?radius=0&searchRadius=0'

    # Парсинг страниц
    try:
        while current_page <= max_pages:
            response = session.get(url, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            print('='*100)
            print(f'Парсим страницу {current_page} из {max_pages}...')

            items = soup.select('[data-marker=item]')
            if items:
                print(f'Найдено {len(items)} товаров')
                for item in items:
                    title = item.select_one('[data-marker=item-title]')
                    title = title.text.strip() if title else 'N/A'

                    price = item.select_one('[data-marker=item-price-value]')
                    price = price.text.strip() if price else 'N/A'

                    params = item.select_one('[data-marker=item-specific-params]')
                    params = params.text.strip() if params else 'N/A'

                    link = item.select_one('[itemprop=url]')
                    link = f"{BASE_URL}{link.get('href').strip()}" if link and link.get('href') else 'N/A'

                    cars.append({
                        'title': title,
                        'price': price,
                        'params': params,
                        'link': link
                    })

                for i, car in enumerate(cars[len(cars)-len(items):], 1):
                    print('-'*100)
                    print(f"{current_page}.{i}. {car['title']}:")
                    print(f"Цена: {car['price']}")
                    print(f"Дополнительные параметры: {car['params']}")
                    print(f"Ссылка: {car['link']}")
            else:
                print(f'Карточки товаров на странице {current_page} не найдены')

            next_page_button = soup.select_one('[aria-label="Следующая страница"]')
            if next_page_button and next_page_button.get('href') and current_page < max_pages:
                next_page = next_page_button.get('href')
                url = f'{BASE_URL}{next_page}'
                current_page += 1
                time.sleep(DELAY)
            else:
                break

        print('='*100)
        print('='*100)
        print(f'Парсинг завершен. Собрано {len(cars)} товаров с {current_page} страниц')

    except Exception as e:
        print(f'Ошибка при парсинге {current_page}-й страницы: {e}')

    return cars


def save_to_csv(cars):
    print()

    try:
        with open('avito_cars.csv', 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Название', 'Цена', 'Дополнительные параметры', 'Ссылка на объявление'])
            for car in cars:
                row = car['title'], car['price'], car['params'], car['link']
                writer.writerow(row)
        print(f'Данные успешно сохранены в avito_cars.csv')

    except Exception as e:
        print(f'Ошибка при сохранении в csv-файл: {e}')


def main():
    try:
        print(f'Парсим данные с avito.ru...')
        cars_data = parse_avito_cars()
        if cars_data:
            save_to_csv(cars_data)
        else:
            print()
            print('Информации о товарах не найдено')

    except Exception as e:
        print(f'Основная ошибка: {e}')


if __name__ == '__main__':

    main()
