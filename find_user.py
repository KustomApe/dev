import tweepy
import json
auth = tweepy.OAuthHandler('PhmPFIDjTcbaxeRmqXqK0KZVR', 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR')
auth.set_access_token('87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQ', '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7')
api = tweepy.API(auth)
jsonarray = api.statuses_lookup([1064438982837059585])
print(jsonarray)
