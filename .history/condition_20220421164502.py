# 年齢変数
age = 65
# 曜日変数
day = 'Monday'
# 平日配列
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
# 週末配列
weekend = ['Saturday', 'Sunday']

if age >= 65 and day is weekdays[0]:
    print('年齢が65歳以上なので割引適応')
else:
    print('年齢が65歳未満なので定額販売')
