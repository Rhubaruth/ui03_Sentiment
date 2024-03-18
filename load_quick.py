import urllib.request
from bs4 import BeautifulSoup

def load_quick(url: str) -> str:
    """ 
    Load steam review page without scrolling 
    
    :param url: string of url that should be read
    :return: data structure representing parsed HTML
    """

    soup = None
    with urllib.request.urlopen(url) as response:
        soup = BeautifulSoup(response, 'html5lib')
    return soup
