# Sentiment Analysis
Steam review analysis with nltk.
Program uses Selenium to scroll through the review website, there are two ways of loading the URL
- load_quick(url): loads URL directly, gets only ~10 reviews
- load_full(url): loads URL with selenium, scrolls to the bottom of page. Might take a while.

After getting HTML with Selenium or BeatifulSoup4, 
text is parsed in this order:
1. Removes "found helpful" reactions
2. Removes early access tag
3. Translates Recommended/Not recommended from CZ to EN
4. Splits review text into dictionary:
    - verdict (recommend/not recommend)
    - hour (playtime hours, not used)
    - date (date when reviewed, not used)
    - text (content of review)

Review text is then stripped of punctuation and separated into words.
Words are saved in 2 lists - 
one with all words, the other allows each word only once per user.
Reason for the unique per-user word list is to find what most users "agreed" on and not to have a word count inflated by an ASCII art or spam.

The original review text is also taken sentence by sentence and evaluated by nltk Sentiment Intensity Analyzer. 
The program calculates average polarity score of each sentence in selected review.
From that it chooses its own verdict - if the average compound is greater or equal zero it recommends, otherwise it doesn't.

The final result of the program are 2 figures.
Figure 1a contains verdicts of all reviews by users and by AI based on their text. 
Figure 1b shows where AI have chosen the same result as the user writing the review.
From the graphs we can see, that it marks much more reviews negatively than users.
Figure 2a shows 10 most frequent words in order. There are some words filtered like
'I', 'and', or 'the', that are used in also every English sentence. 
This means the shown words better represent selected game.
Same filter was applied on the unique per-user words in Figure 2b.
The graph represents how many users used the word and also how many times it was used in total.
