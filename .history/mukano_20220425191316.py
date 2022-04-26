def nakanishi():
    answer = 'Pythonに関して何でも応えます'
    return answer
    # 返り値
# def add():
#     kekka = 1 + 1
# 体重70kg, 身長160cm(1.6m)
# 体重75kg, 身長180cm(1.8m)
def bmiA():
    return 70 / (1.6 ** 2)
# bmi(70, 1.7)
def bmi(weight, height):
    bmi_result = weight / (height ** 2)
    return bmi_result
# テンプレート
# nakanishi_bmi = bmi(weight, height) #体重70, 身長1.7
nakanishi_bmi = bmi(70, 1.7) #体重70, 身長1.7
konishiki_bmi = bmi(100,1.8)



def tashizan():
    #足し算代わりにやってやるよ
    # kekka = 1 + 1
    # 結果はreturn = これ(kekka)だよ、受け取れ！
    # と投げられる変数「返り値」
    return 1 + 1
#俺(kore)が受け取るよ！ = tashizan()受け取れ！
kore = 1 + 1
print(kore)
