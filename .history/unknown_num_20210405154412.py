print('数字を入れてください')
# n = int(input())
n = 5
t = 0
i = 0

while True:
    if i > n:
        t = i + 1
        num = i += 1
        print(t)
        continue
    else:
        print(t)
        break