from bs4 import BeautifulSoup, NavigableString #extract the html from the request
from selenium import webdriver #deal with the dynamic javascript
from multiprocessing import Process
import csv

#URLs of the specific products
URLS = []

#Load the path of the driver for use
def load_driver_path():
    path_file = open('DriverPath.txt', 'r')
    path = path_file.read().strip()
    path_file.close()
    return path

#Loads all the urls from the URLS.txt file and appends them to the array of urls
def load_urls_from_text_file():
    urls_file = open('URLS.txt', 'r')
    urls = urls_file.readlines()
    for url in urls:
        URLS.append(url.strip())
    urls_file.close()

#Establish the webdriver
def link_driver(path_to_driver):
    #Establish the driver
    driver = webdriver.Chrome(path_to_driver)
    return driver

#  1. Loads the html data
#  2. Turns it into soup
def load_data(webdriver):
    for url in URLS:
        #Get the contents of the URL
        webdriver.get(url)
        
        # Jialong add
        # select element by id:
        webdriver.find_element_by_css_selector("input[type='radio'][name='region'][value='QC']").click()
        webdriver.find_element_by_id("language-region-set").click()
        # time.sleep(10)

        #returns the inner HTML as a string
        innerHTML = webdriver.page_source
        #turns the html into an object to use with BeautifulSoup library
        soup = BeautifulSoup(innerHTML, "html.parser")

        extract_and_load_all_data(soup)

#closes the driver
def quit_driver(webdriver):
    webdriver.close()
    webdriver.quit()

## Now need to get the following from the page:
#    1. seo meta tags
#    2. product name
#    3. product description
#    4. product specifications
#    5. category
#    6. price
#    7. embedded images

# gets the seo meta tags
def get_meta_tags(soup):
    meta_tags = [tags.get('name') + " is " + tags.get('content') for tags in soup.find_all('meta')[3:8]]
    return meta_tags

# gets the product name
def get_product_name(soup):
    # Jialong change logic here
    prod_list = []

    for product_name in soup.find_all('p', {"class": "description"}):
        product_name = str(product_name)
        pos1 = product_name.index("html\">")
        pos2 = product_name.index("</p>")
        name = product_name[pos1+6: pos2-5]
        prod_list.append(name)
    '''
    product_name = soup.find_all('img', {"class": "img-responsive"})
    for prod in product_name:
        prod_list.append(prod.get('alt'))
    # product_name = soup.find('meta', property="og:description").get('content')
    '''
    return prod_list

# logic for getting product description/specification
def get_product_info(types, soup):
    # Jialong change logic here    
    # cannot read description or specification here
    if types == "description":
        tags = soup.find('img', {"class": "img-responsive"}).get('alt')
        # tags = soup.find('div', class_ = "product-info-description").descendants
    elif types == "specification":
        tags = soup.find('img', {"class": "img-responsive"}).get('alt')
        # tags = soup.find('div', id = "pdp-accordion-collapse-2").descendants
    else:
        return "Wrong String!"

    data = ""

    for tag in tags:
        if type(tag) is NavigableString and tag.string is not None:
            if(types == "description"):
                data += tag.string + "\n"
            else:
                data += tag.string
        else:
            continue

    return "\"" + data.replace("\"", "\"\"") + "\""

# gets the product description
def get_product_description(soup):
    return get_product_info("description", soup)

# gets the product specifications
def get_product_specification(soup):
    return get_product_info("specification", soup)

# gets the product category
def get_category(soup):
    tags = soup.find('ul', id = "crumbs_ul")
    data = tags.contents[-2].text

    return '\n'.join([x for x in data.split("\n") if x.strip()!=''])

# gets the product price
def get_price(soup):
    # Jialong change logic
    price_list = []
    for item in soup.find_all('div', {"class": "price price-with-linkfee hide"}, {"data-regionnav":"CAQC"}):
        price_list.append(item.get_text())

    return price_list

# gets the product image
def get_embedded_images(soup):
    # Jialong change logic
    img_list = []
    for img in soup.find_all('img', class_ = "img-responsive"):
        if img.get('src'):
            img_list.append(img.get('src'))
        else:
            img_list.append(img.get('data-src'))
    return img_list

# Load data to csv
def extract_and_load_all_data(soup):
    # field_names = ["Meta tags", "Name", "Description", "Specifications", "Category", "Price", "Image"]
    output_data = open('OutputData.txt', 'a')
    '''
    writer = csv.DictWriter(output_data, field_names,
        delimiter='\n')#,
        #dialect='excel',
        #lineterminator="\r\n")
    '''
    # writer.writerow({field: field for field in field_names})

    # Jialong delete 
    collected_data =[
            get_product_name(soup),
            get_price(soup),
            get_embedded_images(soup)]
    for i in range(len(collected_data[0])):
        output_data.write(collected_data[0][i])
        output_data.write("\n")
        output_data.write(collected_data[1][i])
        output_data.write("\n")
        output_data.write(collected_data[2][i])
        output_data.write("\n")   
    output_data.close()

#  1. Links the driver
#  2. Loads the html data
#  3. Turns it into soup
#  4. extracts correct elements and loads it to csv file
def run():
    load_urls_from_text_file()
    path = load_driver_path()
    driver = link_driver(path)
    load_data(driver)
    quit_driver(driver)

def main():
    #create multiple threads for selenium web scraping - ASYNC
    processes = []
    p = Process(target=run, args=())
    processes.append(p)
    p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
