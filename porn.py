import pandas as pd 
import requests
from bs4 import beautifulsoup4  # BeautifulSoupのインポート

# データフレームの作成

columns = ["title", "likes", "tag_name"]
df = pd.DataFrame(columns = columns)
df
base_url = "http://loveh.org/?paged="
page_num = 1
max_page_num = 183

# 最後のページまで実行する

if __name__ == '__main__':
  while page_num < max_page_num:
    res = requests.get(base_url+ str(page_num))
    soup = BeautifulSoup(res.text, 'html.parser') # BeautifulSoupの初期化
    tags = soup.select("div#entrybox")
    for tag in tags:
        try:
          title = tag.select("h2.entrytitle")[0]. get_text() # タイトル
          like = tag.select("div.likenumberin")[0].get_text().replace("Like", "").rstrip() # いいね数
          # タグ名を取得する。複数ある場合はリスト化して、文字列を結合する
          tag_name = ""
          tmp_tags = tag.select("span.tagdesign")
          for tmp_tag in tmp_tags:
            tag_name += tmp_tag.get_text() + " "
          print(tag_name)
          se = pd.Series([title, like, tag_name],columns)
          df = df.append(se, ignore_index=True)
          print(se)
        except Exception as e:
          print ()
    page_num +=1
    print("{} th page DONE".format(page_num))
    df.to_csv("all_videos.csv")