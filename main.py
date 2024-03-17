import re
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from nltk import tokenize, word_tokenize, ngrams, FreqDist
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup

import numpy as np
import matplotlib.pyplot as plt

URLPART_ENGLISH_SEARCH = """?filterLanguage=english"""
URL_CELESTE = """https://steamcommunity.com/app/504230/reviews/"""
URL_PALWORDLS = """https://steamcommunity.com/app/1623730/reviews/"""
URL_RIMWORLD = """https://steamcommunity.com/app/294100/reviews/"""


SCROLL_LIMIT = 30


def load_quick(url) -> str:
    """ Load steam review page without scrolling """

    soup = None
    with urllib.request.urlopen(url) as response:
        soup = BeautifulSoup(response, 'html5lib')
    return soup

def load_full(url) -> str:
    """ Load steam full review page by scrolling with selenium """

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-cerificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')

    driver = webdriver.Chrome("./chromedriver-win64/chromedriver.exe",
                              options=options)

    driver.get(url)
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID, 'page1')))

    actions = ActionChains(driver)
    for _ in range(1, SCROLL_LIMIT):
        actions.scroll_by_amount(delta_x=0, delta_y=10_000).perform()
        element_loading = (By.ID, 'action_wait')
        WebDriverWait(driver, 15).until_not(EC.element_to_be_clickable(element_loading))


    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'lxml')
    return soup

def parse_review(review):
    """ Parse UserReviewCardContent """
    found_helpful = review.find('div', 'found_helpful')
    found_helpful.extract()

    found_early_access = review.find('div', 'early_access_review')
    if found_early_access:
        found_early_access.extract()

    review = review.get_text("|", strip=True).split('|')
    review[0] = review[0].replace(
            'Doporučuji', 'Recommended').replace(
            'Nedoporučuji', 'Not Recommended')

    hours = review[1].split(' ')[0].replace(',', '')
    review_dict = {
        'verdict': review[0],
        'hours': float(hours),
        'date': review[2],
        'text': ' '.join(review[3:]),
        }

    return review_dict


def main():
    """ main function """

    soup = load_full(URL_RIMWORLD + URLPART_ENGLISH_SEARCH)
    # soup = load_full(URL_CELESTE + URLPART_ENGLISH_SEARCH)

    user_verdicts = {
        'Recommended': 0,
        'Not Recommended': 0,
        'Not Sure': 0,

    }

    ai_verdicts = {
        'Recommended': 0,
        'Not Recommended': 0,
        'Not Sure': 0,

    }   

    words_all = []
    reviews_all = soup.find_all('div', re.compile('apphub_UserReviewCardContent'))
    for review in reviews_all:
        data = parse_review(review)

        review_text = data['text']

        user_verdicts[data['verdict']] += 1

        words_all.extend(word_tokenize(review_text))
        sentences = tokenize.sent_tokenize(review_text)

        total_review_compound: float = 0.0
        for s in sentences:
            # print(s)
            sid = SentimentIntensityAnalyzer()
            ss = sid.polarity_scores(s)
            total_review_compound += ss['compound']
        if len(sentences) == 0:
            ai_verdicts['Not Sure'] += 1
            # print(data)
            # print()
            continue
        total_review_compound /= len(sentences)
        if total_review_compound > 0.1:
            ai_verdicts['Recommended'] += 1
        elif total_review_compound < -0.1:
            ai_verdicts['Not Recommended'] += 1
        else:
            ai_verdicts['Not Sure'] += 1

        # print(f'{total_review_compound / len(sentences)} {data["verdict"]}')
        # print()


    # print(user_verdicts)
    # print(ai_verdicts)
    
    # # print(*reviews_all, sep='\n')
    print(f'\n Num of Reviews Souped: {len(reviews_all)}')


    # Reviews
    n_groups = 3
    plt.subplots()
    index = np.arange(n_groups)

    print(list(user_verdicts.values()))

    plt.bar(index, list(user_verdicts.values()), 0.3,
         alpha=0.8,
         color='b',
         label='user')
    plt.bar(index + 0.3, list(ai_verdicts.values()), 0.3,
         alpha=0.8,
         color='g',
         label='ai')
    plt.legend()
    plt.tight_layout()
    plt.show()


    # Word Frequency
    all_counts = FreqDist(words_all)
    num_words = 10

    print(all_counts.most_common(num_words))

    fig, ax = plt.subplots()

    x_labels = []
    for idx, val in enumerate(all_counts.most_common(num_words)):
        word, count = val
        plt.barh(idx, count, 0.3,
             alpha=0.8,
             color='b')
        x_labels.append(word)

    ax.invert_yaxis()
    plt.yticks(range(num_words), x_labels)
    plt.tight_layout()
    plt.show()



if __name__ == '__main__':
    # import nltk
    # nltk.download('subjectivity')
    # nltk.download('vader_lexicon')
    # nltk.download('punkt')
    main()
