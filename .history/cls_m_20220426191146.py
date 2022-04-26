class Spam:
    def manufacture(self):
        print('Hormel Foods Corporation')

    def echo(self, message):
        print(message)

# Spamクラスの中の関数manufacture = インスタンス・メソッド
# インスタンス生成 -> Spamクラスを使えるようにlunch変数に機能を代入する
lunch = Spam()
lunch.fuga = 1
lunch.manufacture()
lunch.echo()