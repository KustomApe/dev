sum = 0
for number in range(1, 11): # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 -> 55
    print('number変数：' + str(number)) # 1 -> 2
    sum += number # sum = sum + number -> sum=1, sum3
    print('途中経過：' + str(sum))
print('合計値：' + str(sum))
