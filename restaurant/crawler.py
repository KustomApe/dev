from bs4 import BeautifulSoup
import requests
import time
import os
# timer
t1 = time.time()

# function
# get number of shop


def get_num(soup):
    num = soup.find('p', {'class': 'sercheResult fl'}).find('span', {'class': 'fcLRed bold fs18 padLR3'}).text
    print('num:{}'.format(num))

# get url of shop


def get_shop_urls(tags):
    shop_urls = []
    # ignore the first shop because it is PR
    tags = tags[1:]
    for tag in tags:
        shop_url = tag.a.get('href')
        shop_urls.append(shop_url)
    return shop_urls


def save_shop_urls(shop_urls, dir_path=None, test=False):
    # make directry
    if test:
        if dir_path is None:
            dir_path = './html_dir_test'
    elif dir_path is None:
        dir_path = './html_dir'

    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    for i, shop_url in enumerate(shop_urls):
        time.sleep(1)
        shop_url = 'https://www.hotpepper.jp' + shop_url
        r = requests.get(shop_url).text
        file_path = 'shop{:0>5}_url.html'.format(i)
        with open(dir_path + '/' + file_path, 'w') as f:
            f.write(r)
    # return last shop number
    return len(shop_urls)


start_url = 'https://www.hotpepper.jp/yoyaku/SA11/'
response = requests.get(start_url).text
soup = BeautifulSoup(response, 'html.parser')
tags = soup.find_all('h3', {'class': 'detailShopNameTitle'})

# get last page number
last_page = soup.find('li', {'class': 'lh27'}).text.replace('1/', '').replace('ページ', '')
last_page = int(last_page)
print('last page num:{}'.format(last_page))

# get the number of shops before crawling
get_num(soup)

# first page crawling
start_shop_urls = get_shop_urls(tags)

# from 2nd page
shop_urls = []
# last page(test)
last_page = 10  # test
for p in range(last_page-1):
    time.sleep(1)
    url = start_url + 'bgn' + str(p+2) + '/'
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    tags = soup.find_all('h3', {'class': 'detailShopNameTitle'})
    shop_urls.extend(get_shop_urls(tags))
    # how speed
    if p % 100 == 0:
        percent = p/last_page*100
        print('{:.2f}% Done'.format(percent))

start_shop_urls.extend(shop_urls)
shop_urls = start_shop_urls

t2 = time.time()
elapsed_time = t2 - t1
print('time(get_page):{:.2f}s'.format(elapsed_time))
print('num(shop_num):{}'.format(len(shop_urls)))

# get the url of shop
last_num = save_shop_urls(shop_urls)  # html_dir

# get the number of shops after crawling
get_num(soup)

t3 = time.time()
elapsed_time = t3 - t1
print('time(get_html):{:.2f}s'.format(elapsed_time))
print('num(shop_num):{}'.format(last_num))
