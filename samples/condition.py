# 年齢変数
age = 70
# 曜日変数
day = 'Monday'
# 平日配列
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
# 週末配列
weekend = ['Saturday', 'Sunday']

# 65歳以上かつ平日であれば割引適応
if age >= 65 and day is weekdays[0]:
    print('年齢が65歳以上なので割引適応')
else:
    print('年齢が65歳未満なので定額販売')
