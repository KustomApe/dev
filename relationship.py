class Person:
    def __init__(self, name, intimacy, barrier):
        self.name = name
        # 0.0〜1.0: 親密度
        self.intimacy = intimacy
        # 0.0〜1.0: 恥ずかしさや社会的な壁
        self.barrier = barrier

    def __repr__(self):
        return self.name

def check_relationship_status(person):
    # 「友達以上恋人未満」の定義:
    # 1. 親密度が0.7を超えている (ただの友達ではない)
    # 2. かつ、二人の間に「壁」が存在する (恋人ではない)
    
    is_more_than_friend = person.intimacy > 0.7
    is_less_than_lover = person.barrier > 0.3
    
    if is_more_than_friend and is_less_than_lover:
        return "❤️ 友達以上恋人未満 (The Friendzone Zone)"
    elif person.intimacy > 0.9 and person.barrier < 0.1:
        return "💑 恋人"
    else:
        return "👋 ただの友達"

# 全員（友達リスト）を対象に判定する
friends_list = [
    Person("幼馴染", intimacy=0.8, barrier=0.5), # 典型例
    Person("飲み仲間", intimacy=0.4, barrier=0.8),
    Person("片思いの人", intimacy=0.9, barrier=0.9), # これはただの片思い
    Person("完璧なパートナー", intimacy=1.0, barrier=0.0),
]

print("--- 友達全員を対象とした残酷な判定結果 ---")
for p in friends_list:
    print(f"{p.name}: {check_relationship_status(p)}")
