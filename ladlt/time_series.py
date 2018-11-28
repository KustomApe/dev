# 時系列ツイート数データの表示
date_dict = defaultdict(int)
ret_date_dict = defaultdict(int)
norm_date_dict = defaultdict(int)
spam_dict = defaultdict(int)
not_spam_norm_dict = defaultdict(int)
not_spam_ret_dict = defaultdict(int)

for d in tweetdata.find({},{'_id':1, 'created_datetime':1,'retweeted_status':1,'spam':1}):
    str_date = date_to_Japan_time(d['created_datetime']).strftime('%Y\t%m/%d %H %a') 
    date_dict[str_date] += 1
    
    # spamの除去
    if ('spam' in d) and (d['spam'] == True):
        spam_dict[str_date] += 1
    else:
        spam_dict[str_date] += 0
        # spamでないもののRetweet数のカウント
        if 'retweeted_status' not in d:
            not_spam_ret_dict[str_date]  += 0
            not_spam_norm_dict[str_date] += 1
        elif obj_nullcheck(d['retweeted_status']):
            not_spam_ret_dict[str_date]  += 1
            not_spam_norm_dict[str_date] += 0
        else:
            not_spam_ret_dict[str_date]  += 0
            not_spam_norm_dict[str_date] += 1
    
    # Retweet数のカウント
    if 'retweeted_status' not in d:
        ret_date_dict[str_date]  += 0
        norm_date_dict[str_date] += 1
    elif obj_nullcheck(d['retweeted_status']):
        ret_date_dict[str_date]  += 1
        norm_date_dict[str_date] += 0
    else:
        ret_date_dict[str_date]  += 0
        norm_date_dict[str_date] += 1


print "日付" + "\t\t\t" + "#ALL" + "\t" + "#NotRT" + "\t" + "#RT" + "\t" "#spam" + "\t" "#NotRT(exclude spam)" + "\t" + "#RT(exclude spam)"
keys = date_dict.keys()
keys.sort()
for k in keys:
    print k  + "\t" +  str(date_dict[k]) + "\t" +  str(norm_date_dict[k]) + "\t" +  str(ret_date_dict[k]) \
                    + "\t" +  str(spam_dict[k])+ "\t" +  str(not_spam_norm_dict[k]) + "\t" +  str(not_spam_ret_dict[k])