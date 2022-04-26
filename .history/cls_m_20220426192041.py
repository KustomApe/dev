class Spam:
    def __init__(self, x):
        self.salt = 2.2
        self.y = x

    def bmi(self):
        self.result = 1
        return self.result

    def manufacture(self):
        print('Hormel Foods Corporation')

    def echo(self, message):
        print(message)

# Spamクラスの中の関数manufacture = インスタンス・メソッド
# インスタンス生成 -> Spamクラスを使えるようにlunch変数に機能を代入する
lunch = Spam()
lunch.manufacture()
lunch.echo()