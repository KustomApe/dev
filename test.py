friend = 0
you_are_friend = 5
in_relationship = 10
you_are_my_gf_bf = 15
in_marriage = 20
you_are_my_wife_husband = 25

import numpy as np

def calculate_relationship_state(intimacy, distance):
    """
    友達以上恋人未満の関係を数値化する関数
    Intimacy: 0.0 - 1.0 (0はただの友達, 1は恋人)
    Distance: 0.0 - 1.0 (1は赤の他人, 0は完全に統合された状態)
    """
    
    # 友達以上恋人未満の判定領域
    # 親密度は高いが、心理的境界線が一定以上残っている状態
    is_more_than_friend = intimacy > 0.5
    is_less_than_lover = distance > 0.1
    
    if is_more_than_friend and is_less_than_lover:
        return "Friends with Benefits / Something More"
    elif intimacy >= 0.8 and distance <= 0.1:
        return "Lovers"
    else:
        return "Just Friends"

# シミュレーション
# 二人の距離が縮まっていく過程
intimacy_levels = np.linspace(0.4, 0.9, 5)
distance_levels = np.linspace(0.5, 0.05, 5)

for i, d in zip(intimacy_levels, distance_levels):
    state = calculate_relationship_state(i, d)
    print(f"Intimacy: {i:.1f}, Distance: {d:.1f} -> {state}")
