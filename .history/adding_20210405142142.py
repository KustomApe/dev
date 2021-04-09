n = 1
t = 0

# 1から5までの足し算をループを使って実装する
# while True:
#     if n == 6:
#         print(t)
#         break
#     else:
#         t = t + n
#         n = n + 1

# 1から10までの足し算をループを使って実装する
# while True:
#     if n >= 11:
#         print(t)
#         break
#     else:
#         t = t + n
#         n = n + 1

# 1から10までの奇数の合計値を計算する
# n = 1
# t = 0
# while True:
#     if n <= 11:
#         t = t + n
#         n = n + 2
#         print(t)
#     else:
#         break


# テキスト - アルゴリズム14/23
n = 0
counter = 0
l = []
while True:
    if n == 100:
        break
    else:
        n += 1
        l[counter] = n
        n + 1
        counter += 1
        continue