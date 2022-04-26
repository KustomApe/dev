class Spam:
    def __init__(self, amount):
        self.salt = 2.2

    def bmi(self):
        result = 1

    def manufacture(self):
        print('Hormel Foods Corporation')

    def echo(self, message):
        print(message)

# Spamクラスの中の関数manufacture = インスタンス・メソッド
# インスタンス生成 -> Spamクラスを使えるようにlunch変数に機能を代入する
lunch = Spam()
lunch.manufacture()
lunch.echo()