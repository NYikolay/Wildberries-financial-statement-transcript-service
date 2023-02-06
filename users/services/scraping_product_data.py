from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup


def get_product_data_dict(html, article: int, brand: str) -> dict:
    """
    Scrapy the html page it receives from the get_scraping_data function and returns a dictionary
    of key-value pairs of values such as image, nm_id, title. They all relate to the product
    """

    values_data = {}

    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('div', class_='product-page__header')
    img_container = soup.find('div', class_='zoom-image-container')
    img = img_container.find_all('img')

    for elem in img:
        values_data['img'] = f"https:{elem['src']}"

    values_data['nm_id'] = article
    values_data['brand'] = brand
    values_data['title'] = title.find('h1').text

    return values_data


def get_scraping_data(article: int, brand: str) -> dict:
    """
    The func takes a unique product identifier (article) as a parameter,
    then uses selenium to go to the page of this product.
    The func waits until the page is fully loaded and returns the html code of the page for get_product_data_dict func
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
    url_template = f"https://www.wildberries.ru/catalog/{article}/detail.aspx?targetUrl=SP"
    driver.get(url=url_template)
    desired_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'zoom-image-container')))
    html = driver.page_source

    driver.quit()

    return get_product_data_dict(html, article, brand)
