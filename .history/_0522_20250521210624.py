# 問題を解いていると、どの段階でfor文を使ったらいいのかわからなくなってきます。
lst = ['red', 'blue', 'green']
for i in lst:
    print(i)

# 反復（while文)・(for文)の使い分けについて
# sample codeを使いながら説明する
# メルカリの検索
# twitterのリサーチ
'''
CSVデータを読み込んで分析を行う際はfor文を使う
ウェブページからページの枚数分実行するものはwhileを使う
'''

# for文とrange文について
for i in range(1, 11, 2):
    print(i)

# while文やfor文の中で、先にprint関数を使うのかcountをするのかなど順番がまだあやふやです。
cnt = 0
for i in range(1, 11):
    print(i)
    if i % 3 == 0:
        print('3の倍数')
        cnt += 1
print('done')

cnt_02 = 0
range_var = 1
while True:
    if cnt_02 == 10:
        print('done')
        break
    print(range_var)
    range_var += 1
    cnt_02 += 1

# 演習問題において、問題を見た際にどの方法を使って解くべきが思いつきません。自力で解くことができた問題がほぼありませんでした。。。
# for文に関して、
# 　for 変数　in リストの「変数」には何を入れてもいいですか？
# 　例えば、for color in colors:の場合、「color」を「a」にしても問題ないのでしょうか。
#  問題ないです。
lst = [1, 2, 3]

for i in lst:
    print(i)

# 演習問題　６章　exercise4
# sum = 0
# for num in range (1,50):
#     if num % 5 == 0:
#         sum += num
#     num += 1
# print(""1から50までの数字の中で、5の倍数の合計は"" + str(sum) + ""です。"")
# 上記のように解答と違う求め方で解きましたが、答えが225になってしまいます。解答にある求め方も含め、解説していただきたいです。
sum = 0
for num in range (1,50): # 1, 51に変更する
    if num % 5 == 0:
        sum += num
    num += 1
print("1から50までの数字の中で、5の倍数の合計は" + str(sum) + "です。")

# 第7章の演習5と、in演算子の使い方が分からなかった。
lst1 = [1, 2, 3, 4, 5, 6]
lst2 = [4, 5, 6, 7, 8, 9]
lst3 = []

for i in lst1:

# "演習問題7章のexercise2が、何となく理解しましたが、あやふやです。
# max_value=number[0]は、for関数によって、max_value=number[1] →　max_value=number[2]・・・　と変化していくということでしょうか。
numbers = [16, 42, 54, 8, 38, 96, 23]
max_value = numbers[0]

for number in numbers:
    if number > max_value:
        max_value = number

print('最大値は' + str(max_value) + 'です。')
# "7章exercise2:最大値の表し方
# 条件分岐全般



# 何を使ってどの順番で書くのかを思い出して、頭の中で整理してから手を動かすまでに時間がかかるのでついていくのが難しかったです。
# "説明が難しいのですが、リスト1とリスト2の中の共通の値を導き出したいときは直訳するとリスト1 in リスト2のようなニュアンスで覚えれば良いのでしょうか
# 伝わりづらい内容で申し訳ありません"

# 演習７の５に関して、どうすれば共通の数字を表示させるのかがわからなかった。


# 演習課題全般、頭がパンクしそうです

# "演習問題の、7-2のif以降の部分が答えを見たが、なぜそのようになるのかが分からなかった。
# また、教科書の6-6のfor分のfor以降の変数は、自分で突然定義するということでしょうか。
# 伝わりづらくて申し訳ないです。"
