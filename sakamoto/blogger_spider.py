import requests
from bs4 import BeautifulSoup


def drug_data():
    url = 'http://www.tatsuojapan.com/'
    while url:
        print(url)
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        # next page url
        url = soup.findAll('a', {
            'class': 'blog-pager-older-link',
            'id': 'Blog1_blog-pager-older-link'
        })
        url = 'http://www.tatsuojapan.com/' + url[i].get('href')
        if url != None:
            i++
            continue
        else:
            break


drug_data()
