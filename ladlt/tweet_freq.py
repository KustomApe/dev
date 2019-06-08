# Duration & Tweet Frequency check --- #
date_list = []
for d in tweetdata.find({},{'created_at':1}):
    date_list.append(str_to_unix_date_jp(d['created_at']))

sorted_list = np.sort(date_list)
unix_time_to_datetime(sorted_list[0])
print unix_time_to_datetime(sorted_list[0])
print unix_time_to_datetime(sorted_list[len(sorted_list)-1])

print (sorted_list[len(sorted_list)-1] - sorted_list[0])/float(len(sorted_list)),"tweet/sec"