# 位置情報を持っているツイートの割合
num_not_geo = tweetdata.find({'coordinates':None},{'_id':1, 'coordinates':1}).count()
num_geo = tweetdata.find({'coordinates':{"$ne":None}},{'_id':1, 'coordinates':1}).count()

print "num_not_geo",num_not_geo
print "num_geo", num_geo
print "%.3f"%(num_geo / float(num_geo+num_not_geo) * 100),"%"

# 緯度経度表示
for d in tweetdata.find({'coordinates':{"$ne":None}},{'_id':1, 'coordinates':1}):
    co = d['coordinates']['coordinates']
    print co[1], co[0]