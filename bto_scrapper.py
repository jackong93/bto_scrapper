import datetime
import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlencode


def start_from_home_page(driver):
    # go to home page
    HOME_PAGE_URL = "https://esales.hdb.gov.sg/bp25/launch/19sep/bto/19SEPBTO_page_2671/about0.html#"  # noqa
    driver.get(HOME_PAGE_URL)

    # hover over Punggol's dropdown menu and click the availability button
    punggol_dropdown = driver.find_element_by_xpath(
        '//*[@id="bto-icon-nav"]/section/ul/li[1]'
    )
    availability_redirect = driver.find_element_by_xpath(
        '//*[@id="bto-icon-nav"]/section/ul/li[1]/ul/li[11]/a'
    )
    hover_action = (
        ActionChains(driver)
        .move_to_element(punggol_dropdown)
        .move_to_element(availability_redirect)
    )
    hover_action.click().perform()

    # this will open up a new tab, switch to that new tab
    driver.switch_to_window(driver.window_handles[1])

    # wait for the new tab to load completely
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchButtonId"))
    )

    # select 5-room
    driver.find_element_by_xpath('//*[@id="Flat"]/option[4]').click()
    driver.find_element_by_xpath('//*[@id="searchButtonId"]').click()

    return driver


def start_from_5room_URL(driver):
    # Construct URL
    FIVE_ROOM_URL_PARAMS = (
        ("Town", "PUNGGOL"),
        ("Flat_Type", "BTO"),
        ("DesType", "A"),
        ("ethnic", "Y"),
        ("Flat", "5-Room"),
        ("ViewOption", "A"),
        ("dteBallot", "201909"),
        ("projName", "A"),
        ("brochure", "true"),
    )
    FIVE_ROOM_URL = "https://services2.hdb.gov.sg/webapp/BP13AWFlatAvail/BP13EBSFlatSearch?"  # noqa
    FIVE_ROOM_URL = FIVE_ROOM_URL + urlencode(FIVE_ROOM_URL_PARAMS)
    driver.get(FIVE_ROOM_URL)

    return driver


def get_all_block_details(driver):
    table = driver.find_element_by_xpath(
        '//*[@id="blockDetails"]/div[1]/table/tbody'
    )

    blocks_row_and_col = []
    for row_number, row in enumerate(table.find_elements_by_xpath(".//tr")):
        for col_number, col in enumerate(row.find_elements_by_xpath(".//td")):
            blocks_row_and_col.append((row_number + 1, col_number + 1))

    all_details = []

    for row, col in blocks_row_and_col:
        block = driver.find_element_by_xpath(
            '//*[@id="blockDetails"]/div[1]/table/tbody/'
            f'tr[{row}]/td[{col}]/div/font/a/font'
        )
        block_number = block.text
        block.click()

        all_details.extend(get_block_details(block_number, driver.page_source))

    return all_details


def get_block_details(block_number, page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    units = (
        soup.find("div", {"id": "blockDetails"})
        .find_all("table")[1]
        .find("tbody")
        .find_all("td")
    )
    price_regex = r"^(\$\d+,\d+)<br>_*<br>(\d+)"

    units_details = []

    for unit in units:
        detail = unit.find("font").attrs
        print(detail)

        if detail.get("color") == "#cc0000":
            _id = unit.find("font").text.strip()
            floor, unit_number = _id.split("-")

            units_details.append({
                "block_number": block_number,
                "floor": floor,
                "unit_number": unit_number,
                "unit_available": False
            })

        else:
            # get floor unit number
            _id = detail["id"]
            floor, unit_number = _id.split("-")

            # get price and area
            price_area_info = soup.find("span", {"data-selector": _id}).attrs
            price, area = re.findall(price_regex, price_area_info["title"])[0]

            units_details.append({
                "block_number": block_number,
                "floor": floor,
                "unit_number": unit_number,
                "price": price,
                "area": area,
                "unit_available": True
            })

    return units_details


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(
        "/usr/local/bin/chromedriver",
        options=options
    )
    driver = start_from_5room_URL(driver)
    # driver = start_from_home_page(driver)
    all_details = get_all_block_details(driver)

    df = pd.DataFrame(all_details)
    datetime_now = datetime.datetime.now().strftime("%FT%H:%m")
    df.to_csv(f"scrapped_data/prices_{datetime_now}.csv")

    driver.quit()
