from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

SCROLL_LIMIT = 30 # How many times does the bot scroll down

def load_full(url: str) -> str:
    """
    Load steam full review page by scrolling with selenium 

    :param url: string of url that should be read
    :return: data structure representing parsed HTML
    """

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-cerificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')

    driver = webdriver.Chrome("./chromedriver-win64/chromedriver.exe",
                              options=options)

    driver.get(url)
    # wait for the page to load
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, 'page1')))

    actions = ActionChains(driver)
    for _ in range(1, SCROLL_LIMIT):
        actions.scroll_by_amount(delta_x=0, delta_y=10_000).perform()
        element_loading = (By.ID, 'action_wait')
        # wait each time it is loading new reviews
        WebDriverWait(driver, 15).until_not(
                EC.element_to_be_clickable(element_loading))

    page_source = driver.page_source # get source code

    soup = BeautifulSoup(page_source, 'lxml')
    return soup
