print('数字を入れてください')
n = int(input())
t = 0



# if t <= n:
#     for i in range(0, n):
#         t = t + n
#         print(t)
#         n =+ 1
#     print('計算終了' + str(t))

sum = 0
for i in range(0,n):
    sum += i
    print(sum)