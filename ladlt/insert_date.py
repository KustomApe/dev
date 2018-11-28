# --- insert Date type information --- #
# 文字列型の日付に加えてDatetime型のTweet日の属性追加
for d in tweetdata.find({'created_datetime':{ "$exists": False }},{'_id':1, 'created_at':1}):
    #print str_to_date_jp(d['created_at'])
    tweetdata.update({'_id' : d['_id']}, 
                     {'$set' : {'created_datetime' : str_to_date_jp(d['created_at'])}})