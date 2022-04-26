age = 20
year = 2022
next_age = 21
print('私の年齢は{}歳です。'.format(age))
print('今年は西暦{0}年です。私の年齢は{1}歳で、来年は{2}歳になります。'.format(year, age, next_age))

while True:
    if year < 2023:
        break
    else:
        year += 1