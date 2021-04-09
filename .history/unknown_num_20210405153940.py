print('数字を入れてください')
t = int(input())
i = 0

while True:
    if t > i:
        t = i + 1
        i += 1
        continue
    else:
        print()
        break