import random

cnt = 1
group_num = [1, 2, 3, 4, 5, 6]

print(group_num)
random.shuffle(group_num)
for i in group_num:
    print(str(cnt) + '番目の発表はグループ' + str(i))
    cnt += 1

