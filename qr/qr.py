# QRコードを作成するURLの一覧 --- (*1)
from IPython.display import Image, display_png
import qrcode
urls = [
    "https://eisukenakanishi.com",
    "https://google.com",
]


# 一気にQRコードを生成 --- (*2)
for url in urls:
     img = qrcode.make(url, box_size=3)
     display_png(img)
     img.save(str(img) + '.png')
