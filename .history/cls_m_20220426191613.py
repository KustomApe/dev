class Spam:
    def __init__(self, amount):
        self.salt = 2.2

    def manufacture(self):
        bmi = 1
        print('Hormel Foods Corporation')
        return bmi

    def echo(self, message):
        print(message)

# Spamクラスの中の関数manufacture = インスタンス・メソッド
# インスタンス生成 -> Spamクラスを使えるようにlunch変数に機能を代入する
lunch = Spam()
lunch.manufacture()
lunch.echo()