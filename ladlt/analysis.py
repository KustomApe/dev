import MeCab
tagger = MeCab.Tagger("-Ochasen")
text = u"私は横浜に住んでいます。"
text_encode = text.encode('utf-8')
result = tagger.parse(text_encode)
result = result.decode('utf-8')  # 必ずdecode
print(result)
