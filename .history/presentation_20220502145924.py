import random

cnt = 1
group_num = [1, 2, 3, 4, 5, 6]
print(group_num)
shuffle_group = random.shuffle(group_num)
print(shuffle_group)
for i in iter(shuffle_group):
    print(str(cnt) + '番目の発表はグループ' + str(i))
    cnt += 1

