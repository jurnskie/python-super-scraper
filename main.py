# This is a sample Python script.
from selenium.common import NoSuchElementException

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import requests
from tabulate import tabulate

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
browser = webdriver.Chrome(options=chrome_options)


def sort(sub_li):
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using first (x[1]) element of
    # sublist lambda has been used
    sub_li.sort(key=lambda x: x[3], reverse=True)
    print(sub_li)
    return sub_li


def get_price_ah(grocery_name):
    price_collection = []
    url = 'https://www.ah.nl/zoeken?query=' + grocery_name
    print('getting url:' + url)

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    productcards = soup.findAll('article', attrs={"data-testhook": "product-card"})
    for product in productcards:
        anchor = product.findNext('a', href=True)
        priceContainer = product.find('div', attrs={"data-testhook": "price-amount"})

        if priceContainer:
            priceElement = priceContainer.select("span")
            integer = priceElement[0].text
            cents = priceElement[2].text
            price = integer + '.' + cents
            price = float(price)
            price_collection.append(["AH", grocery_name, price, anchor['href']])
    return sort(price_collection)[-1]


def get_price_aldi(grocery_name):
    price_collection = []
    url = 'https://www.aldi.nl/zoeken.html?query=' + grocery_name
    print('getting url:' + url)
    browser.get(url)
    prices = browser.find_elements(By.CLASS_NAME, 'mod-article-tile')
    if len(prices) and prices is not None:
        for price in prices:
            try:
                price_wrapper = price.find_element(By.CLASS_NAME, 'price__wrapper')
                link = price.find_element(By.CLASS_NAME, 'mod-article-tile__action')
                if price_wrapper is None \
                        or price_wrapper.text == '' \
                        or link is None \
                        or link.get_attribute('href') is None:
                    print('not adding because of empty link or price')
                else:
                    print(price_wrapper.text)
                    price_collection.append(
                        ["ALDI", grocery_name, float(price_wrapper.text), link.get_attribute('href')])
            except NoSuchElementException:
                print('price element not found, skipping')
    else:
        print('no product found')

    if len(price_collection):
        return sort(price_collection)[-1]


def get_price_jumbo(grocery_name):
    price_collection = []
    url = 'https://www.jumbo.com/zoeken/?searchType=keyword&searchTerms=' + grocery_name
    print('getting url:' + url)
    browser.get(url)
    products = browser.find_elements(By.CLASS_NAME, 'card-product')

    if len(products):

        for product in products:
            price = product.find_element(By.CLASS_NAME, 'current-price')
            link = product.find_element(By.CLASS_NAME, 'title-link')
            price_whole = price.find_element(By.CLASS_NAME, 'whole')
            price_fractional = price.find_element(By.CLASS_NAME,'fractional')
            glued_price = price_whole.text+'.'+price_fractional.text
            if price is not None and link is not None and price.text:
                price_collection.append(["JUMBO", grocery_name, float(glued_price), link.get_attribute('href')])
            else:
                print('not adding product')
    if len(price_collection):
        return sort(price_collection)[-1]


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

def list_prices(groceries):
    ah_collection = []
    aldi_collection = []
    jumbo_collection = []
    for grocery in groceries:

        ah_list_item = get_price_ah(grocery)
        if ah_list_item is not None and len(ah_list_item) > 0:
            ah_collection.append(ah_list_item)
        aldi_list_item = get_price_aldi(grocery)
        if aldi_list_item is not None and len(aldi_list_item) > 0:
            aldi_collection.append(aldi_list_item)

        jumbo_list_item = get_price_jumbo(grocery)
        if jumbo_list_item is not None and len(jumbo_list_item) > 0:
            jumbo_collection.append(jumbo_list_item)

    if ah_collection is not None:
        total_ah = 0
        for row in ah_collection:
            total_ah += float(row[2])
        ah_collection.append(["AH", "Totaal:", total_ah, ''])

        print(tabulate(ah_collection, headers=["Winkel", "Product", "Prijs", "Link"]))
    if aldi_collection is not None:
        total_aldi = 0
        for row in aldi_collection:
            total_aldi += float(row[2])
        aldi_collection.append(["ALDI", "Totaal:", total_aldi, ''])
        print(tabulate(aldi_collection, headers=["Winkel", "Product", "Prijs", "Link"]))
    if jumbo_collection is not None:
        total_jumbo = 0
        for row in jumbo_collection:
            total_jumbo += float(row[2])
        jumbo_collection.append(["JUMBO", "Totaal:", total_jumbo, ''])
        print(tabulate(jumbo_collection, headers=["Winkel", "Product", "Prijs", "Link"]))


list_prices([
    "pindakaas",
    "halfvolle%25melk",
    "volkoren%25brood",
    "hagelslag",
    "eieren",
    "blok%25kaas",
    "roomboter%25ongezouten",
    "flessen%25water",
    "bananen"
])
