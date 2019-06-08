# spamアカウントのツイートにspamフラグを付与する

#  08_spam_detector.pyであぶり出したスパムアカウントのリスト
spam_list = ['**********', '**********', '**********', '**********', '**********']

count = 0
retweeted_name = ""

for d in tweetdata.find({'retweeted_status':{"$ne": None}}):
    try:
        retweeted_name = d['entities']['user_mentions'][0]['screen_name']
    except:
        count += 1
        pattern = r".*@([0-9a-zA-Z_]*).*"
        ite = re.finditer(pattern, d['text'])
        for it in ite:
            retweeted_name = it.group(1)
            break

    if retweeted_name in spam_list:
        # スパムアカウントへのリツイートにspamフラグを付与
        tweetdata.update({'_id' : d['_id']},{'$set': {'spam':True}})
        # スパムツイートをしたアカウントもブラックリスト入り
        spam_twitter.add(d['user']['screen_name'])
        
print '%d件のリツイートをスパムに分類しました'%count

# ブラックリスト入りのユーザーのツイートをスパムに分類
count = 0
for d in tweetdata.find({},{'user.screen_name':1}):
    sc_name = d['user']['screen_name'] 
    if sc_name in spam_twitter:
        count += 1
        tweetdata.update({'_id' : d['_id']},{'$set': {'spam':True}})

print "%d件のツイートをスパムに分類しました"