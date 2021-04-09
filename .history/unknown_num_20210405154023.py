print('数字を入れてください')
n = int(input())
t = 0
i = 0

while True:
    if i > n:
        t = i + 1
        i += 1
        continue
    else:
        print()
        break