# 解答例 : 1
# str = 'パタトクカシーー'
# result = str[::2]
# print(result)

# 解答例 : 2
# str = 'パタトクカシーー'
# result = ''
# for i in range(0, len(str), 2):
#     result += str[i]
# print(result)

# Sample input
# パタトクカシーー

# Sample output
# パトカー

# str1 = input()
# str2 = input()
# sorted_str1 = sorted(str1)
# sorted_str2 = sorted(str2)
# result = sorted_str1 == sorted_str2
# print(result)

engineers = {'中島さん':'ビギナー', '田中さん':'プロフェッショナル', '村松さん':'ビギナー', '新井さん':'プロフェッショナル', '上田さん':'プロフェッショナル'}
result = []
for i in engineers:
    if engineers[i].values == 'プロフェッショナル':
        result.append(engineers[i].keys)
print(result)
