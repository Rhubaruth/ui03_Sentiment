import re
import urllib.request

from string import punctuation
import numpy as np
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from nltk import tokenize, word_tokenize, FreqDist
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup


URLPART_ENGLISH_SEARCH = """?filterLanguage=english"""
URL_CELESTE = """https://steamcommunity.com/app/504230/reviews/"""
URL_PALWORDLS = """https://steamcommunity.com/app/1623730/reviews/"""
URL_RIMWORLD = """https://steamcommunity.com/app/294100/reviews/"""
URL_BALATRO = """https://steamcommunity.com/app/2379780/reviews/"""


SCROLL_LIMIT = 30


# nejpoužívanější slova v angličtině pro vyfiltrování častých slov specifických pro danou hru
# https://github.com/first20hours/google-10000-english/blob/master/google-10000-english.txt
MOST_USED_WORDS_ENGLISH = [
    'the', 'of', 'and', 'to', 'a',
    'in', 'for', 'is', 'on', 'that',
    'by', 'this', 'with', 'i', 'you',
    'it', 'not', 'or', 'be', 'are',
    'from', 'at', 'as', 'your', 'all',
    'have', 'new', 'more', 'an', 'was',
    'we', 'will', 'can', 'us', 'about',
    'if', 'my', 'has', 'but', 'our',
    'one', 'other', 'do', 'no', 'they',
    'he', 'up', 'may', 'what', 'which',
    'their', 'out', 'any', 'there', 'only',
    'so', 'his', 'when', 'here', 'who',
    'also', 'now', 'c', 'e', 'am',
    'been', 'would', 'how', 'were', 'me',
    's', 'some', 'these', 'its', 'like',
    'x', 'than', 'back', 'had', 'just',
    'over', 'into', 'two', 'n', 're',
    'go', 'b', 'last', 'most', 'buy',
    'make', 'them', 'should', 'her', 't',
    'add', 'such', 'please', 'after', 'best',
    'then', 'well', 'd', 'where', 'info',
    'rights', 'through', 'm', 'each', 'she',
    'very', 'r', 'need', 'many', 'de',
    'does', 'under', 'full',
]

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

    # soup = load_quick(URL_RIMWORLD + URLPART_ENGLISH_SEARCH)
    soup = load_full(URL_BALATRO + URLPART_ENGLISH_SEARCH)
    # soup = load_full(URL_PALWORDLS + URLPART_ENGLISH_SEARCH)
    # soup = load_full(URL_RIMWORLD + URLPART_ENGLISH_SEARCH)

    user_verdicts = {
        'Recommended': 0,
        'Not Recommended': 0,
    }

    ai_verdicts = {
        'Recommended': 0,
        'Not Recommended': 0,
    }

    eval_verdicts = {
        'Correct': [0, 0],
        'Wrong': [0, 0],
    }

    words_all = []
    words_per_user = []
    reviews_all = soup.find_all('div', re.compile('apphub_UserReviewCardContent'))
    for review in reviews_all:
        data = parse_review(review)
        review_text = data['text']

        text_without_punc = review_text
        for punc in punctuation:
            # print(punc)
            text_without_punc = text_without_punc.replace(punc, ' ')
        words_all.extend(word_tokenize(text_without_punc))
        words_per_user.extend(list(set(word_tokenize(text_without_punc))))
        sentences = tokenize.sent_tokenize(review_text)
        # skip reviews without text
        if len(sentences) == 0:
            continue

        # print(review_text)
        # print()

        # get user verdict
        user_verdicts[data['verdict']] += 1

        # get ai verdict
        total_review_compound: float = 0.0
        for s in sentences:
            # print(s)
            sid = SentimentIntensityAnalyzer()
            ss = sid.polarity_scores(s)
            total_review_compound += ss['compound']
        total_review_compound /= len(sentences)
        ai_verdict = ''
        if total_review_compound >= 0.0:
            ai_verdict = 'Recommended'
        elif total_review_compound < 0:
            ai_verdict = 'Not Recommended'
        ai_verdicts[ai_verdict] += 1

        # compare user verdict with ai
        if ai_verdict == data['verdict']:
            eval_verdicts['Correct'][data['verdict'] != 'Recommended'] += 1
        else:
            eval_verdicts['Wrong'][data['verdict'] != 'Recommended'] += 1

        # print(f'{total_review_compound / len(sentences)} {data["verdict"]}')
        # print()


    # print(user_verdicts)
    # print(ai_verdicts)

    # print(*reviews_all, sep='\n')
    print(eval_verdicts)
    print(f'\n Num of Reviews Souped: {len(reviews_all)}')


    # Reviews
    plt.figure(figsize=(10, 5))

    ax = plt.subplot(1, 2, 1)
    ax.set_title('Review Verdicts')
    verdict_labels = list(ai_verdicts.keys())
    n_groups = len(verdict_labels)
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
    plt.xticks(index + 0.15, verdict_labels)
    plt.legend()
    plt.tight_layout()

    ax = plt.subplot(1, 2, 2)
    ax.set_title('AI Sentiment Accuracy')
    ax.set_xlabel('User\'s verdict')
    plt.bar(index, list(eval_verdicts['Correct']), 0.3,
         alpha=0.8,
         color='g',
         label='AI\'s agrees with User')
    plt.bar(index + 0.3, list(eval_verdicts['Wrong']), 0.3,
         alpha=0.8,
         color='r',
         label='AI does not agree')
    plt.xticks(index + 0.15, verdict_labels)
    plt.legend()
    plt.tight_layout()


    # Word Frequency
    words_all = [word.lower() for word in words_all]
    words_per_user = [word.lower() for word in words_per_user]
    for frequent_word in MOST_USED_WORDS_ENGLISH:   # remove frequently used words in english
        while frequent_word in words_all:
            words_all.remove(frequent_word)
        while frequent_word in words_per_user:
            words_per_user.remove(frequent_word)
    all_counts = FreqDist(words_all)
    unique_words = np.unique(words_all)
    per_user_counts = FreqDist(words_per_user)
    num_words = 10

    print(all_counts.most_common(num_words))
    print('user unique:')
    print(per_user_counts.most_common(num_words))

    plt.figure(figsize=(10, 5))

    # Displey most common words and their count
    ax = plt.subplot(1, 2, 1)
    ax.set_title('Word frequency')
    word_labels: list[str] = []
    for idx, val in enumerate(all_counts.most_common(num_words)[::-1]):
        word, count = val
        plt.barh(idx, count, 0.3,
             alpha=0.8,
             color='b')
        word_labels.append(word)
    plt.yticks(range(num_words), word_labels)
    plt.tight_layout()

    # Displey longest words and their count
    ax = plt.subplot(1, 2, 2)
    ax.set_title('Word frequency (unique words/user)')
    word_labels: list[str] = []
    for idx, val in enumerate(per_user_counts.most_common(num_words)[::-1]):
        word, count = val
        plt.barh(idx, count, 0.3,
            alpha=0.8,
            color='b',
            )
        plt.barh(idx, words_all.count(word), 0.3,
            alpha=0.2,
            color='b',
            )
        word_labels.append(word)
    # just to add labes to legend
    plt.barh(0, 0, 0,
            alpha=0.2, color='b',
            label='From all words')
    plt.barh(0, 0, 0,
            alpha=0.8, color='b',
            label='From unique per user')
    plt.legend()
    plt.yticks(range(num_words), word_labels)
    plt.tight_layout()

    # unique_words = sorted(unique_words, key= len, reverse=True)
    # print(unique_words[:num_words])
    # word_labels: list[str] = []
    # for idx, word in enumerate(unique_words[:num_words]):
    #     count = words_all.count(word)
    #     plt.barh(idx, count, 0.3,
    #          alpha=0.8,
    #          color='b')
    #     word_labels.append(word)
    # plt.yticks(range(num_words), word_labels)
    # plt.tight_layout()

    plt.show()



if __name__ == '__main__':
    # import nltk
    # nltk.download('subjectivity')
    # nltk.download('vader_lexicon')
    # nltk.download('punkt')
    main()
