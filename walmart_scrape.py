# Created by Jibben Hillen
# For L2 code test
# 2015-11-28

import urllib.request              # to construct url file-like objects
import json                 # to interpret json
from bs4 import BeautifulSoup, NavigableString #extract the html from the request
import re                   # regex parsing html
import csv                  # to write output at csv
import os.path              # to check if file exists for writing output
from datetime import date   # to put date on output
import sys                  # to get command line inputs
from selenium import webdriver #deal with the dynamic javascript

BASE_URL = "http://www.walmart.ca"

def load_driver_path():
    path_file = open('DriverPath.txt', 'r')
    path = path_file.read().strip()
    path_file.close()
    return path

def link_driver(path_to_driver):
    #Establish the driver
    driver = webdriver.Chrome(path_to_driver)
    return driver

# function to return a soup from a base and page link
def get_soup(webdriver, base, link):
    webdriver.get(base + link)
    # url = urllib.request.urlopen(base + link)
    innerHTML = webdriver.page_source
    # soup = bs4.BeautifulSoup(url.read(), "html.parser")
    soup = BeautifulSoup(innerHTML, "html.parser")
    return soup


# function to build list from all page dictionaries
def build_list(soup, query):
    # initialize list to hold products
    product_list = []
    price_list = []
    img_list = []
    # get all products from page
    # Jialong change
    # get item name
    for item in soup.find_all('h2', {"class": "thumb-header"}):
        product_list.append(item.get_text())

    # get item price
    for price in soup.find_all('div', {"class": "price-current"}):
        
        price = str(price)
        pos1 = price.index("data-analytics-value=")
        pos2 = price.index(" data-bind=\"attr")
        price_list.append(price[pos1+22 : pos2-1])
    
    # get image
    for img in soup.find_all('img', {"class": "image lazy-img"}):
        
        img_list.append('https:'+img.get('data-original'))
    


    # for each product, find url, get info, add to list
    '''
    rank = 1
    for prod in products:
        url = prod.find('a').get('href')
        prod_soup = get_soup(driver, BASE_URL, url)
        prod_info = build_dict(prod_soup, rank)
        prod_info["query"] = query
        prod_info["date"] = date.today().strftime("%Y-%m-%d")
        product_list.append(prod_info)
        rank += 1
    '''
    return product_list, price_list, img_list



def extract_and_load_all_data(products, price, image):
    # field_names = ["Meta tags", "Name", "Description", "Specifications", "Category", "Price", "Image"]
    output_data = open('WALMART_OutputData.txt', 'a')

    for prod, price, img in zip(products, price, image):
        output_data.write(prod)
        output_data.write("\n")
        output_data.write(price)
        output_data.write("\n")
        output_data.write(img)
        output_data.write("\n")   
    output_data.close()


def main():

    num_args = len(sys.argv)
    # if no additional arguments are given, pretend as if the following are:
    # walmart_scrape.py cereal cold+cereal walmart.csv
    if(num_args == 1):
        path = load_driver_path()
        driver = link_driver(path)


        # first do for cereal
        soup = get_soup(driver, BASE_URL, "/search/mower")
        products, price, image = build_list(soup, "mower")

        extract_and_load_all_data(products, price, image)

main()
