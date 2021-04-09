print('数字を入れてください')
i = int(input())
t = 0
n = 0

while True:
    if i > n:
        t = n
        t = i + 1
        i += 1
        print(t)
        continue
    else:
        print(t)
        break