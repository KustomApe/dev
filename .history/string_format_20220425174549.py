age = input('あなたの年齢を入れてください')
year = 2012
print('私の年齢は{}歳です。'.format(age))
print('今年は西暦{0}年です。私の年齢は{1}歳で、来年は{2}歳になります。'.format(year))

while True:
    if year < 2023:
        break
    else:
        year += 1