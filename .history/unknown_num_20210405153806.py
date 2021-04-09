print('数字を入れてください')
n = int(input())
i = 0

while True:
    if n > i:
        t = i + 1
        print(t)
        t += 1
        print(t)
        continue
    else:
        print(n)
        break