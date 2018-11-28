# 検索ワードを指定して100件のTweetデータをTwitter REST APIsから取得する
def getTweetData(search_word, max_id, since_id):
    global twitter
    url = 'https://api.twitter.com/1.1/search/tweets.json'
    params = {'q': search_word,
              'count': '100',
              }
    # max_idの指定があれば設定する
    if max_id != -1:
        params['max_id'] = max_id
    # since_idの指定があれば設定する
    if since_id != -1:
        params['since_id'] = since_id

    req = twitter.get(url, params=params)   # Tweetデータの取得

    # 取得したデータの分解
    if req.status_code == 200:  # 成功した場合
        timeline = json.loads(req.text)
        metadata = timeline['search_metadata']
        statuses = timeline['statuses']
        limit = req.headers['x-rate-limit-remaining'] if 'x-rate-limit-remaining' in req.headers else 0
        reset = req.headers['x-rate-limit-reset'] if 'x-rate-limit-reset' in req.headers else 0
        return {"result": True, "metadata": metadata, "statuses": statuses, "limit": limit, "reset_time": datetime.datetime.fromtimestamp(float(reset)), "reset_time_unix": reset}
    else:  # 失敗した場合
        print("Error: %d" % req.status_code)
        return{"result": False, "status_code": req.status_code}


def obj_nullcheck(string):  # Y if X else Z
    return False if string is None else True


def is_exist_id(id_str):
    return tweetdata.find({'id': long(id_str)}, {'id': 1}).count() > 0
