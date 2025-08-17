# 年齢を月と日に換算する
age = int(input('あなたの年齢を入力してください'))
month = age * 12
day = age * 365
print(f'あなたは{age}歳で、月でいうと{month}ヶ月、日でいうと{day}日です。')

# BMIを求める
# 身長と体重を入力してもらう
height = int(input('身長を入力してください'))
weight = int(input('体重を入力してください'))
# BMIを求めるために身長をメートル記法からセンチメートル記法に変換する
height_float = height / 100
bmi = weight / height_float / height_float
print(f'あなたのBMIは{bmi}です。')

bmi = weight / height_float // height_float
print(f'あなたのBMIは{bmi}です。')
