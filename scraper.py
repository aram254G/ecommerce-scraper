import time

import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://books.toscrape.com/"


def get_page(url):
    """Download a webpage and return a BeautifulSoup object."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    response.encoding = response.apparent_encoding

    return BeautifulSoup(response.text, "html.parser")


def extract_books(soup):
    """Extract book information from one page."""
    products = []

    books = soup.find_all("article", class_="product_pod")

    for book in books:
        title = book.h3.a["title"]

        price = book.find(
            "p",
            class_="price_color"
        ).get_text(strip=True)

        rating_element = book.find(
            "p",
            class_="star-rating"
        )

        availability_element = book.find(
            "p",
            class_="instock availability"
        )

        rating = rating_element["class"][1]

        availability = availability_element.get_text(strip=True)

        products.append({
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability
        })

    return products


def scrape_books():
    """Scrape all book pages and return the collected products."""
    products = []
    url = BASE_URL

    while url:
        soup = get_page(url)

        page_products = extract_books(soup)
        products.extend(page_products)

        next_button = soup.find("li", class_="next")

        if next_button:
            next_page = next_button.a["href"]
            url = requests.compat.urljoin(url, next_page)
        else:
            url = None

        time.sleep(1)

    return products


def save_to_csv(products):
    """Convert products to a DataFrame and save them to CSV."""
    df = pd.DataFrame(products)

    df.to_csv("products.csv", index=False)

    return df


def main():
    products = scrape_books()

    df = save_to_csv(products)

    print(f"Scraping completed: {len(df)} products collected.")
    print("Saved to products.csv")


if __name__ == "__main__":
    main()
