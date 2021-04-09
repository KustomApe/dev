print('数字を入れてください')
n = int(input())

while True:
    print('数字を入れてください')
    answer = int(input())
    if answer == n:
        print('正解です！答えは' + str(n) + 'です！')
        break
    else:
        print('違います')
        continue