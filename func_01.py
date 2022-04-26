# 関数=プログラムのまとまり(パック)
# アメリカ旅行(ホテル・飛行機・ガイドさん)
def travel(hotel, jet, guide):
    # 処理
    content = hotel + jet + guide
    return content

nakanishi = travel('ANAHotel', 'JAL', 'Satake')
hirosawa = travel('JALHotel', 'AirFrance', 'Hara')
satake = travel('東京ホテル', '中西航空', '宮田さん')
print(nakanishi)
print(hirosawa)
print(satake)
