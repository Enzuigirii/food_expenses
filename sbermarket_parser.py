from __future__ import annotations

import json
import time
from datetime import date

from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.common import StaleElementReferenceException
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import get_driver
from settings import save_path_temp_files
from settings import sbermarket_url
from settings import temp_json_shipments


driver = get_driver()


def get_html_shipments():
    load_more_shipments_button_class = 'LoadMoreShipmentsButton_loadMoreShipments__aa47z'
    driver.maximize_window()
    driver.get(sbermarket_url)
    scrolling_and_save_pages(load_more_shipments_button_class, file_name='shipments')


def get_html_shipment():
    shipment_load_more_button_class = 'styles_btnLoadMore__mTtLf'
    original_window = driver.current_window_handle

    with open(f'{save_path_temp_files}/shipment_urls.txt') as file:
        for line in file:
            shipment_url = line.rstrip()
            shipment = shipment_url.split('/')[-1]
            driver.switch_to.new_window('tab')
            WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
            print('Start loading', shipment)
            driver.get(f'{sbermarket_url}/{shipment}')
            (WebDriverWait(driver, 5, ignored_exceptions=StaleElementReferenceException)
             .until(lambda driver: driver.execute_script('return document.readyState') == 'complete'))
            scrolling_and_save_pages(shipment_load_more_button_class, file_name=shipment)
            print(shipment, ' is uploaded')
            driver.close()
            driver.switch_to.window(original_window)


def get_shipment_urls():
    with open(f'{save_path_temp_files}/shipments.html') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    shipments_a = soup.find('div', class_='styles_list___dvv1').find_all('a')
    urls = []

    for shipment in shipments_a:
        shipment_url = shipment.get('href')
        urls.append(shipment_url)

    with open(f'{save_path_temp_files}/shipment_urls.txt', 'w') as file:
        for url in urls:
            file.write(f'{url}\n')


def scrolling_and_save_pages(button_xpath: str, file_name: str):
    try:
        errors = [NoSuchElementException, StaleElementReferenceException]
        while True:
            loading_element = WebDriverWait(driver, 10, ignored_exceptions=errors).until(
                EC.presence_of_element_located((By.CLASS_NAME, button_xpath))
            )
            if driver.find_elements(By.CLASS_NAME, button_xpath):
                scroll_origin = ScrollOrigin.from_element(loading_element)
                (
                    ActionChains(driver)
                    .scroll_from_origin(scroll_origin, 0, 100)
                    .pause(2)
                    .move_to_element(loading_element)
                    .pause(1)
                    .click()
                    .pause(1)
                    .perform()
                )
    except TimeoutException:
        with open(f'{save_path_temp_files}/{file_name}.html', 'w') as shipments:
            shipments.write(driver.page_source)


def get_data_from_shipment():
    shipments_data = {}
    dict_months = {
        'янв': '01', 'февр': '02', 'марта': '03', 'апр': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'авг': '08',
        'сент': '09', 'окт': '10', 'нояб': '11', 'дек': '12',
    }
    prev_month_val = '00'
    year = date.today().year

    with open(f'{save_path_temp_files}/shipment_urls.txt') as file:
        shipments_list = [line.rstrip().split('/')[-1] for line in file]

    for shipment in shipments_list:
        with open(f'{save_path_temp_files}/{shipment}.html') as html:
            src = html.read()
        shipment_num = shipment
        soup = BeautifulSoup(src, 'lxml')
        item_divs = soup.findAll('div', class_='styles_assemblyItemContent__o1cVR')
        shipments_data.update({shipment_num: {}})
        try:
            shipment_merchant = soup.find('div', class_='order-goods-list__good-merchant').get_text()
        except Exception:
            shipment_merchant = None
        try:
            shipment_status = soup.find('p', class_='NewShipmentState_stateCompleteName__rKoqH').get_text()
        except Exception:
            shipment_status = None
        if shipment_status is None:
            try:
                shipment_status = soup.find('div', class_='NewShipmentState_stateCalcelText__XDxWj').get_text()
            except Exception:
                shipment_status = None
        try:
            sbermarket_date = soup.find('p', class_='NewShipmentState_time__uJGKF').get_text()
            sbermarket_date = sbermarket_date.split(',')[0]
            day = sbermarket_date.split(' ')[0]
            month = dict_months.get(sbermarket_date.split(' ')[1])

            if month == '12' and prev_month_val == '01':
                year -= 1
            prev_month_val = month
            shipment_date = f'{str(year)}-{month}-{day}'
        except Exception:
            shipment_date = None
        try:
            shipping_address = soup.find('span', class_='styles_textLarge__Vs7i4').get_text()
        except Exception:
            shipping_address = None
        try:
            shipping_cost = soup.find(attrs={'data-qa': 'user-shipment-total', 'class': 'styles_detailsText__Pnv_4'}).get_text()
            shipping_cost = float(shipping_cost[:-2].replace(',', '.').replace(u'\xa0', ''))
        except Exception:
            shipping_cost = None
        try:
            bonuses = soup.find(attrs={'data-qa': 'loyalty-accrual', 'class': 'styles_textSmall__haByG'}).get_text()
            bonuses = int(bonuses)
        except Exception:
            bonuses = None
        if bonuses is None:
            try:
                bonuses = soup.find(attrs={'class': '', 'data-qa': 'loyalty-accrual'}).get_text()
                if '+' in bonuses:
                    bonuses = 0
                else:
                    bonuses = int(bonuses)
            except Exception:
                bonuses = 0
        try:
            assembly_and_delivery = soup.find(attrs={'data-qa': 'user-shipment-cost', 'class': 'styles_total__9uFoP'}).get_text()
            assembly_and_delivery = 0 if assembly_and_delivery == 'бесплатно' else int(assembly_and_delivery)
        except Exception:
            assembly_and_delivery = 0
        try:
            discount = soup.find(attrs={'data-qa': 'user-shipment-product-discount', 'class': 'styles_textPromo__StcD0'}).get_text()
            discount = abs(float(discount[:-2].replace(',', '.').replace(u'\xa0', '')))
        except Exception:
            discount = 0

        shipments_data[shipment_num].update(shipment_merchant=shipment_merchant)
        shipments_data[shipment_num].update(shipment_status=shipment_status)
        shipments_data[shipment_num].update(shipment_date=shipment_date)
        shipments_data[shipment_num].update(shipping_address=shipping_address)
        shipments_data[shipment_num].update(shipping_cost=shipping_cost)
        shipments_data[shipment_num].update(bonuses=bonuses)
        shipments_data[shipment_num].update(assembly_and_delivery=assembly_and_delivery)
        shipments_data[shipment_num].update(discount=discount)

        products = {}
        product_id_by_shipment = 1
        for div in item_divs:
            try:
                product_name = div.find('div', class_='styles_name__V0VHp').get_text()
            except Exception:
                product_name = None
            try:
                quantity = div.find('div', class_='styles_quantity__JZCXN').get_text()
            except Exception:
                quantity = None
            try:
                purchase_price = div.find('div', class_='styles_currentPrice__Z3Whh').get_text()
                purchase_price = float(purchase_price[:-2].replace(',', '.').replace(u'\xa0', ''))
            except Exception:
                purchase_price = None
            try:
                purchase_status = div.find('div', class_='StatusBadge_md__U4hG8').get_text()
            except Exception:
                purchase_status = None

            products.update({product_id_by_shipment: {}})
            products[product_id_by_shipment].update(product_name=product_name)
            products[product_id_by_shipment].update(quantity=quantity)
            products[product_id_by_shipment].update(purchase_price=purchase_price)
            products[product_id_by_shipment].update(purchase_status=purchase_status)

            product_id_by_shipment += 1

        shipments_data[shipment_num].update(products=products)

    with open(f'{save_path_temp_files}/{temp_json_shipments}.json', 'w') as file:
        json.dump(shipments_data, file, indent=4)


def main():
    # if os.path.isdir(save_path_temp_files):
    #     shutil.rmtree(save_path_temp_files)
    # os.mkdir(save_path_temp_files)
    try:
        # get_html_shipments()
        # get_shipment_urls()
        # get_html_shipment()
        get_data_from_shipment()
    except Exception as ex:
        print(ex)
    finally:
        time.sleep(5)
        driver.close()
        driver.quit()
        print('Драйвер завершил работу')


if __name__ == '__main__':
    main()
