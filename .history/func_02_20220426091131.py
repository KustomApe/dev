# 請求書を例に考えてみよう





# 体重70kg, 身長160cm(1.6m)
# 体重75kg, 身長180cm(1.8m)

def bmi(weight, height):
    bmi_result = weight / (height ** 2)
    return bmi_result

# nakanishi_bmi = bmi(weight, height) #体重70, 身長1.7
nakanishi_bmi = bmi(70, 1.7) #体重70, 身長1.7
konishiki_bmi = bmi(100,1.8)
