import random

# 男性と女性の名前を作成
men = [f"男{str(i+1).zfill(2)}" for i in range(25)]
women = [f"女{str(i+1).zfill(2)}" for i in range(11)]

# シャッフルしておく（ランダム性）
random.shuffle(men)
random.shuffle(women)

# 空のグループを6つ作成
groups = [[] for _ in range(6)]

# 1人ずつ男女交互にグループに追加（できるだけ均等に）
# 女性から先に各グループに順に配置（分散するため）
for i, woman in enumerate(women):
    groups[i % 6].append(woman)

# 次に男性を順に配置
for i, man in enumerate(men):
    groups[i % 6].append(man)

# 最終シャッフル（グループ内の順番もランダムに）
for group in groups:
    random.shuffle(group)

# 結果出力
for i, group in enumerate(groups):
    print(f"グループ {i + 1}:")
    for person in group:
        print(f"  - {person}")
    print()
