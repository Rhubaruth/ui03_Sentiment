from nltk import FreqDist

# list of most use English words, to filter
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

def get_word_frequency(all_words: list[str]):
    """ Gets word frequency in a list. Ignores commonly used words in English. """
    all_lowercase = [word.lower() for word in all_words]
    for frequent_word in MOST_USED_WORDS_ENGLISH:   # remove frequently used words in english
        while frequent_word in all_lowercase:
            all_lowercase.remove(frequent_word)
    return FreqDist(all_lowercase)
