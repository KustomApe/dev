# 請求書を例に考えてみよう
'''
宛先名：中西株式会社
項目名：関数構築開発費用
単価：10,000円
個数：1個
金額：10,000円
合計金額(金額*1.1)：11,000円
'''















# 体重70kg, 身長160cm(1.6m)
# 体重75kg, 身長180cm(1.8m)

def bmi(weight, height):
    bmi_result = weight / (height ** 2)
    return bmi_result

# nakanishi_bmi = bmi(weight, height) #体重70, 身長1.7
nakanishi_bmi = bmi(70, 1.7) #体重70, 身長1.7
konishiki_bmi = bmi(100,1.8)
