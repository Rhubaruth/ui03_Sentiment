def parse_review(review):
    """ 
    Parse inside of UserReviewCardContent HTML tag. 
    Removes other user's reactions and early access tag.
    Translates user's verdict from Czech when loaded with Selenium.

    :param review: string of html text from HTML
    :return: dictionary with picked data (verdict, hours of played, date of review, text of review)
    """
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
