import re
# import urllib.request
# import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

if __name__ == '__main__':
    URL_CELESTE = """https://steamcommunity.com/app/
        504230/reviews/
        ?filterLanguage=english"""
    URL_PALWORDLS = """https://steamcommunity.com/app/
        1623730/reviews/
        ?browsefilter=toprated&snr=1_5_100010_&filterLanguage=english"""

    reviews_all = []

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-cerificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')

    driver = webdriver.Chrome("./chromedriver-win64/chromedriver.exe",
                              options=options)
    # driver.get(URL_CELESTE)
    driver.get(URL_CELESTE)
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, 'page1')))

    actions = ActionChains(driver)
    for i in range(1, 30):
        actions.scroll_by_amount(delta_x=0, delta_y=10_000).perform()
        element_loading = (By.ID, 'action_wait')
        WebDriverWait(driver, 15).until_not(EC.element_to_be_clickable(element_loading))


    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'lxml')
    reviews_all = soup.find_all('div', re.compile('apphub_CardTextContent'))
    for review in reviews_all:
        print(review.get_text().replace('\t', ''))

    # print(*reviews_all, sep='\n')
    print(f'\n Num of Reviews Souped: {len(reviews_all)}')


    # response = requests.get(URL, headers=headers, params=payload, timeout=10)
    # soup = BeautifulSoup(response.text, 'lxml')


    # with urllib.request.urlopen(URL, ) as response:
    #     soup = BeautifulSoup(response, 'html5lib')
    #     # print(soup.prettify())
    #
    #     reviews = soup.find_all('div', re.compile('apphub_CardTextContent'))
    #     # for link in reviews:
    #     #     print(link.get_text())
    #
    #     print(f'\n Num of Reviews Souped: {len(reviews)}')
