# 解答例 : 1
# str = 'パタトクカシーー'
# result = str[::2]
# print(result)

# 解答例 : 2
str = 'パタトクカシーー'
result = ''
for i in range(0, len(str), 2):
    result += str[i]
print(result)

# Sample input
# パタトクカシーー

# Sample output
パトカー
