from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from requests_html import HTMLSession, AsyncHTMLSession
import time
import yaml

config = yaml.safe_load(open('config.yaml', 'r'))
base_url = 'https://www.bestbuy.com/'


def get_product_links():
    """
    Returns list of elements "items",
    each containing a link to product detail page
    """
    base_shop = base_url + 'site/computer-cards-components/video-graphics-cards/abcat0507002.c?id=abcat0507002&qp=gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3060^gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3060 Ti^gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3070^gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3080'
    session = HTMLSession()
    r = session.get(base_shop)
    items = r.html.find('ol.sku-item-list', first=True).find('li.sku-item')

    base_shop = base_url + 'site/computer-cards-components/video-graphics-cards/abcat0507002.c?cp=2&id=abcat0507002&qp=gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3060^gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3060 Ti^gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3070^gpusv_facet%3DGraphics Processing Unit (GPU)~NVIDIA GeForce RTX 3080'
    session = HTMLSession()
    r = session.get(base_shop)
    items += r.html.find('ol.sku-item-list', first=True).find('li.sku-item')

    return items, session


def get_matched_and_available(target_name):
    """
    Given a target name, filter the product on main page,
    and return links to products with available items

    checked_urls: if already checked (and not a match in product name),
    skip in future checks

    Exactly how this should work, depends on how the drop works - is the page already there,
    just not for sale yet? Or page is added at drop time?
    """
    target_name_list = [x.lower() for x in target_name.split(' ')]
    potential_urls = []
    items, session = get_product_links()
    for item in items:
        target_url = base_url + item.find('h4.sku-header', first=True).find('a', first=True).attrs['href']
        r = session.get(target_url)
        product_name = r.html.find('div.sku-title[itemprop=name]', first=True).text.lower()
        found = True
        for q in target_name_list:
            if q not in product_name:
                found = False
                break

        # Grab listed price
        price = r.html.find('div[class="priceView-hero-price priceView-customer-price"]', first=True).find('span[aria-hidden="true"]', first=True).text
        price = price.strip('$')
        price = float(price.replace(',', '')) # Convert to float

        # Here we specify target prices for certain products. These are arbitrarily set and you can modify based on
        # your budget constraints.
        target_price = 0
        if '3060' in product_name:
            target_price = float(config.get('TARGET_PRICE_3060'))
        if '3070' in product_name:
            target_price = float(config.get('TARGET_PRICE_3070'))
        if '3080' in product_name:
            target_price = float(config.get('TARGET_PRICE_3080'))

        if price > target_price:
            found = False

        print('**************************')
        if found:
            print(f'Found a match: {product_name}')
            print(f'Price: {price}')
            # check if can buy
            if check_can_buy(r):
                print('Still available.')
                potential_urls.append(target_url)
            else:
                print('No longer available')

        else:
            print(f'Not a match: {product_name}')
            print(f'{price} is above target price {target_price}')

    return potential_urls


# check_can_buy invoked above:
def check_can_buy(r):
    """
    Given a page (returned by session.get(target_url)),
    find if there is such html code within:
    <input type="submit" name="commit" value="add to cart" class="button">
    Returns True if so, False if not
    """
    buy_btn = r.html.find('button[class="btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button"]', first=True)
    return buy_btn is not None


def perform_purchase(url):
    """
    Given url of product, add to cart then checkout
    """
    driver = webdriver.Firefox(executable_path='C:\\Users\\GBC-Mandarin\\Documents\\GitHub\\BestBuy-ShopBot\\shopBot\\venv\\Lib\\site-packages\\selenium\\webdriver\\firefox\\geckodriver.exe')
    # This driver needs to be pointed to your own path. You will also need to have the correct driver for the browser you want to use
    # Here we used Firefox driver which can be downloaded from Selenemium website
    driver.get(url)

    # These waits may or may not be necessary based on the speed of your computer and internet connection.
    # I included them because I needed them still
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Add to Cart"]')))
        print
        "Page is ready!"
    except TimeoutException:
        print
        "Loading took too much time!"
        return False
    btn = driver.find_element_by_xpath('//button[text()="Add to Cart"]')
    if btn is None:
        print('not available, DONE')
        return False

    btn.click()
    time.sleep(0.5)

    # go to checkout
    checkout_url = 'https://www.bestbuy.com/checkout/r/fulfillment'
    driver.get(checkout_url)
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'consolidatedAddresses.ui_address_2.firstName')))
        print
        "Page is ready!"
    except TimeoutException:
        print
        "Loading took too much time!"
        return False
    # fill in form

    value = config.get('FIRST_NAME')
    element = driver.find_element_by_id('consolidatedAddresses.ui_address_2.firstName')
    for ch in value:
        element.send_keys(ch)

    value = config.get('LAST_NAME')
    element = driver.find_element_by_id('consolidatedAddresses.ui_address_2.lastName')
    for ch in value:
        element.send_keys(ch)

    value = config.get('ADDRESS')
    element = driver.find_element_by_id('consolidatedAddresses.ui_address_2.street')
    for ch in value:
        element.send_keys(ch)

    value = config.get('CITY')
    element = driver.find_element_by_id('consolidatedAddresses.ui_address_2.city')
    for ch in value:
        element.send_keys(ch)

    value = config.get('STATE')
    element = driver.find_element_by_id('consolidatedAddresses.ui_address_2.state')
    for ch in value:
        element.send_keys(ch)

    value = config.get('ZIPCODE')
    element = driver.find_element_by_id('consolidatedAddresses.ui_address_2.zipcode')
    for ch in value:
        element.send_keys(ch)

    # Need to scroll to get to last few fields
    driver.execute_script("window.scrollTo(0, 300)")
    driver.find_element_by_id('user.emailAddress').send_keys(config.get('EMAIL'))
    driver.find_element_by_id('user.phone').send_keys(config.get('PHONE'))
    btn = driver.find_element_by_css_selector('button[class="btn btn-lg btn-block btn-secondary"]')
    btn.click()
    time.sleep(1)
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'optimized-cc-card-number')))
        print
        "Page is ready!"
    except TimeoutException:
        print
        "Loading took too much time!"
        return False

    driver.find_element_by_id('optimized-cc-card-number').send_keys(config.get('CREDIT_CARD'))
    # Slight wait because remaining fields don't show up until credit card number is input into the field
    time.sleep(1)
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'expiration-month')))
        print
        "Page is ready!"
    except TimeoutException:
        print
        "Loading took too much time!"
        return False

    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'expiration-year')))
        print
        "Page is ready!"
    except TimeoutException:
        print
        "Loading took too much time!"
        return False

    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'credit-card-cvv')))
        print
        "Page is ready!"
    except TimeoutException:
        print
        "Loading took too much time!"
        return False

    driver.find_element_by_name('expiration-month').send_keys(config.get('EXP_DATE_MONTH'))
    driver.find_element_by_name('expiration-year').send_keys(config.get('EXP_DATE_YEAR'))

    value = config.get('CVV')
    element = driver.find_element_by_id('credit-card-cvv')
    for ch in value:
        element.send_keys(ch)
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 300)")

    # pay
    pay_btn = driver.find_element_by_css_selector('button[class="btn btn-lg btn-block btn-primary"]')
    pay_btn.click()
    return True


def main(target_product):
    urls = []
    while len(urls) < 1:
        urls = get_matched_and_available(target_product)
        print(f'Found {len(urls)} matches.')
        if len(urls) == 0:
            print('No match found - checking again')

    print('Found Match!!!')
    print(f'Processing first url: {urls[0]}')
    # just buy the first match

    for link in urls:
        url = link
        print(f'Attempting buy of url: {url}')
        success = perform_purchase(url)
        if success is True:
            break
        else:
            print('Buy failed...')

    print('Done.')


# define main
# if __name__ == '__main__':
#     import argparse
#     parser = argparse.ArgumentParser(description='Shop Bot main parser')
#     parser.add_argument('--name', required=True,
#                         help='Specify product name to find and purchase')
#     args = parser.parse_args()
#     main(target_product=args.name)
