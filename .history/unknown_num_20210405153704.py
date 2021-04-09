print('数字を入れてください')
n = int(input())
i = 0

while True:
    if i > n:
        t = t + 1
        i += 1
        continue
    else:
        print(n)
        break