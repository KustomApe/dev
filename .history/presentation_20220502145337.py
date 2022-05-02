import random

cnt = 1
group_num = [1, 2, 3, 4, 5, 6]
for i in group_num:
    result = random.choice(i)
    print(str(cnt) + '番目の発表はグループ' + i)
    cnt += 1
