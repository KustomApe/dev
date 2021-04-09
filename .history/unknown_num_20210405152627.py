print('数字を入れてください')
n = int(input())

while True:
    answer = int(input())
    if answer == n:
        print(n)
        break
    else:
        print('違います')
        continue