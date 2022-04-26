# 請求書を例に考えてみよう
'''
宛先名：中西株式会社 -> これ
項目名：関数構築開発費用
単価：10,000円 -> これ
個数：1個 -> これ
金額：10,000円 -> これ
合計金額(金額*1.1)：11,000円
'''
def seikyuusyo(name, item_num, price): #仮引数
    kekka = name + str(item_num) + str(price)
    return kekka #返り値

nakanishi_inc = seikyuusyo('中西株式会社', 1, 10000) #引数*3
print(nakanishi_inc)
miyata_inc = seikyuusyo('宮田株会社', 3, 500000)
print(miyata_inc)












# 体重70kg, 身長160cm(1.6m)
# 体重75kg, 身長180cm(1.8m)

def bmi(weight, height):
    bmi_result = weight / (height ** 2)
    return bmi_result

# nakanishi_bmi = bmi(weight, height) #体重70, 身長1.7
nakanishi_bmi = bmi(70, 1.7) #体重70, 身長1.7
konishiki_bmi = bmi(100,1.8)
