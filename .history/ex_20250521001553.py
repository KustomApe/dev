# 年齢を月と日に換算する
age = int(input('あなたの年齢を入力してください'))
month = age * 12
day = age * 365
print(f'あなたは{age}歳で、月でいうと{month}ヶ月、日でいうと{day}日です。')

# BMIを求める
height = int(input('身長を入力してください'))
height_float = height / 100
weight = int(input('体重を入力してください'))
bmi = weight / height / height
print('あなたのBMIは{}です。')
