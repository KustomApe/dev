import tweepy
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


def geocode():
   # geocodeをseleniumを使って検索し、取得する
   driver = webdriver.Chrome("./chromedriver")
   driver.get("https://www.geocoding.jp/")
   driver.implicitly_wait(20)
   search_word = driver.find_element_by_xpath('//*[@id="q"]')
   search_word.send_keys(word)
   search_word.send_keys(Keys.ENTER)
   latitude = driver.find_element_by_xpath('/html/body/span[1]/b[1]').text
   longitude = driver.find_element_by_xpath('/html/body/span[1]/b[2]').text
   return latitude,longitude

query = '応募方法'
query2 = 'プレゼントキャンペーン'


def get_oauth():
   consumer_key = "3bp6koptyzYkHPho7uSqGTnfr"
   consumer_secret = "tnzUkyOGHprmYqlzAdBDDpALIfMIwAlyOR3Dfo9ZMbjRtNYdaZ"
   access_key = "87425177-Byj0gBSpuyvABM9onpfyvSCTHuSCJ9vjPrxEnwkyr"
   access_secret = "WWjn4QbZu7QaM7ptvxg0vzjDYE1knusk5MkY9WAzLjZpN"
   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_key, access_secret)
   return auth

def submit(api):
   n = 0
   search_word = [query,query2,query3]
   for status in api.search(q = search_word, lang='ja'):
      tweet_id = status.id
      user_id = status.user.id
      print(tweet_id)
      try:
         api.retweet(tweet_id)
         api.create_friendship(user_id)
         n += 1
      except:
         print('error')


def main():
   auth = get_oauth()
   api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
   submit(api)
   print("done")


if __name__ == '__main__':
   main()