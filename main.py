from string import punctuation
import matplotlib.pyplot as plt

from nltk import tokenize, word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from load_quick import load_quick
from load_full import load_full
from parse_review import parse_review
from get_frequency import get_word_frequency

from display_graphs import graph_data, display_vertical, display_horizontal


URLPART_ENGLISH_SEARCH = """?filterLanguage=english"""
URL_CELESTE = """https://steamcommunity.com/app/504230/reviews/"""
URL_PALWORDLS = """https://steamcommunity.com/app/1623730/reviews/"""
URL_RIMWORLD = """https://steamcommunity.com/app/294100/reviews/"""
URL_BALATRO = """https://steamcommunity.com/app/2379780/reviews/"""

def main():
    """ main function """

    # soup = load_quick(URL_RIMWORLD + URLPART_ENGLISH_SEARCH)
    # soup = load_quick(URL_PALWORDLS + URLPART_ENGLISH_SEARCH)
    # soup = load_quick(URL_CELESTE + URLPART_ENGLISH_SEARCH)

    # soup = load_full(URL_BALATRO + URLPART_ENGLISH_SEARCH)
    # soup = load_full(URL_PALWORDLS + URLPART_ENGLISH_SEARCH)
    soup = load_full(URL_RIMWORLD + URLPART_ENGLISH_SEARCH)

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
    reviews_all = soup.find_all('div', 'apphub_UserReviewCardContent')
    for review in reviews_all:
        data = parse_review(review)
        review_text = data['text']

        text_without_punc = review_text
        for punc in punctuation:
            text_without_punc = text_without_punc.replace(punc, ' ')
        words_all.extend(word_tokenize(text_without_punc))
        words_per_user.extend(list(set(word_tokenize(text_without_punc))))
        sentences = tokenize.sent_tokenize(review_text)
        # skip reviews without text
        if len(sentences) == 0:
            continue

        # save user's verdict
        user_verdicts[data['verdict']] += 1

        # get ai verdict
        total_review_compound: float = 0.0
        sid = SentimentIntensityAnalyzer()
        for s in sentences:
            ss = sid.polarity_scores(s)
            total_review_compound += ss['compound']
        total_review_compound /= len(sentences)
        ai_verdict = ''
        if total_review_compound >= 0.0:
            ai_verdict = 'Recommended'
        else:
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
    # print(eval_verdicts)
    # print(f'\n Num of Reviews Souped: {len(reviews_all)}')


    # Reviews
    plt.figure(figsize=(10, 5))
    ax: plt.Axes = plt.subplot(1, 2, 1)
    ax.set_title('Review Verdicts')
    display_vertical(plt, user_verdicts.keys(),
                     graph_data(user_verdicts.values(), 'User', 'g'),
                     graph_data(ai_verdicts.values(), 'AI', 'b')
                 )
    ylim = ax.get_ylim()

    ax = plt.subplot(1, 2, 2)
    ax.set_title('AI Sentiment Accuracy')
    ax.set_xlabel('User\'s verdict')
    display_vertical(plt, user_verdicts.keys(),
                     graph_data(eval_verdicts['Correct'], 'AI agreed', 'g'),
                     graph_data(eval_verdicts['Wrong'], 'AI disagreed', 'r')
                 )
    ax.set_ylim(ylim)


    # Word Frequency
    num_words = 10
    frequency_all = get_word_frequency(words_all).most_common(num_words)
    frequency_unique = get_word_frequency(words_per_user).most_common(num_words)

    plt.figure(figsize=(10, 5))

    # Displey most common words and their count
    ax = plt.subplot(1, 2, 1)
    ax.set_title('Word frequency')
    display_horizontal(plt, graph_data(frequency_all, ''))

    ax = plt.subplot(1, 2, 2)
    ax.set_title('Word frequency (unique words/user)')
    display_horizontal(plt, graph_data(frequency_unique, 'per user'))
    display_horizontal(plt, graph_data(
            [(word[0], words_all.count(word[0])) for word in frequency_unique],
            'all words', 'b', 0.2)
        )
    plt.legend()


    # Displey longest words and their count
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
