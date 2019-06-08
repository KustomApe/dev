# Tweepyライブラリをインポート
import tweepy
# 各種キーをセット
CONSUMER_KEY = 'PhmPFIDjTcbaxeRmqXqK0KZVR'
CONSUMER_SECRET = 'TLIWUadER3B5zySncWwHT7aG1Vyg8evWelvfT9Z9wXXznqQ6uR'
ACCESS_TOKEN = 'xxxxx87425177-4dkwezCSg5Ux58X2NId3WE2XilzzSX9K7hv2KG9KQxxx'
ACCESS_SECRET = '6htnT5yE0zgGC67lfHZ4y9DU21jGwufRtDkfXgQZoJKW7'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
#APIインスタンスを作成
api = tweepy.API(auth)

q = "エボラニ" # ここに検索キーワードを設定
count = 100
search_results = api.search(q=q, count=count)

for result in search_results:
    username = result.user._json['screen_name']
    user_id = result.id  # ツイートのstatusオブジェクトから、ツイートidを取得
    print(user_id)
    user = result.user.name  # ツイートのstatusオブジェクトから、userオブジェクトを取り出し、名前を取得する
    print(user)
    tweet = result.text
    print(tweet)
    time = result.created_at
    print(time)
    try:
        api.create_favorite(user_id)  # ファヴォる
        print(user)
        print("をライクしました")
        api.create_friendship(user_id)
        print("をフォローしました")
    except:
        print("もうすでにふぁぼかフォローしてますわ")
    print("##################")
