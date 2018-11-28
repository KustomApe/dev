# １時間の間にlimitに指定した数以上にリツイートされたアカウントを表示する
def select_outlier_retweet_num_per_hour(from_str_datetime_jp, limit=120):
    '''
    from_str_datetime_jp: １時間枠の開始時刻
    limit: この数を超えてリツイートされたものを検出する
    e.g. select_outlier_tweet_num_per_hour("2015-03-18 22:00:00")
    '''
    result_list = []
    from_date = str_to_date_jp_utc(from_str_datetime_jp)
    to_date = str_to_date_jp_utc(from_str_datetime_jp) + datetime.timedelta(hours=1) 
    
    for d in tweetdata.find({'retweeted_status':{"$ne": None},'created_datetime':{"$gte":from_date, "$lt":to_date}},\
                            {'user':1,'text':1,'entities':1, 'created_at':1, 'id':1}):
        mensioned_username = ""
        if len(d['entities']['user_mentions'])!=0:
            mensioned_username = d['entities']['user_mentions'][0]['screen_name']
                
        result_list.append({"created_at":utc_str_to_jp_str(d['created_at']),\
                            "screen_name":d['user']['screen_name'],\
                            "referred_name":mensioned_username,\
                            "text":d['text'].replace('\n',' ')\
                            })

    name_dict = defaultdict(int)
    for r in result_list:
        name_dict[r['referred_name']] += 1  

    s = sorted(name_dict.iteritems(),key=lambda (k,v): v,reverse=True) # リツイート回数でソート
    return s[0:int(np.sum(map(lambda (k,v): 1 if v>limit else 0 ,s)))] # リツイート元ユーザー名, リツイート回数(limitを超えたもの)
    

start_date = str_to_date_jp_utc("2015-03-10 19:00:00")
to_date    = str_to_date_jp_utc("2015-03-22 22:00:00")
d_diff = (to_date - start_date)
d_hours = d_diff.days * 24 + d_diff.seconds/float(3600)

for i in range(int(d_hours)):
    d = (start_date + datetime.timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
    result = select_outlier_retweet_num_per_hour(d, limit=540)
    if len(result) > 0:
        print d, result