class Spam:
    def manufacture(self):
        print('Hormel Foods Corporation')

    def echo(self, message='hoge', num=20):
        print(message)
        print(num)
# Spamクラスの中の関数manufacture = インスタンス・メソッド
# インスタンス生成 -> Spamクラスを使えるようにlunch変数に機能を代入する
lunch = Spam()
lunch.manufacture()
lunch.echo('中西', 12)