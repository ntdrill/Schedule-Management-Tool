
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 部屋全体の定義
ROOM_W = 348
ROOM_D = 258

# データの定義 (単位: cm)
# 形式: {'id': ID, 'w': 幅, 'd': 奥行(y), 'h': 高さ, 'desc': 説明, 'pos': (x, y)}
# pos (x, y) は左下座標を想定。Noneの場合は推測ロジックで決定。

objects = [
    {'id': 'a', 'w': 29.5, 'd': 43.5, 'h': 39.5, 'desc': '食器入れ', 'pos': None},
    {'id': 'b', 'w': 75.0, 'd': 45.0, 'h': 18.0, 'desc': 'コンロ台', 'pos': None},
    {'id': 'c', 'w': 100.0, 'd': 45.0, 'h': 80.0, 'desc': 'シンク・調理台', 'pos': None},
    # d は c に内包されるため、別途描画するか考慮
    {'id': 'e', 'w': 60.0, 'd': 45.0, 'h': 80.0, 'desc': '手作り机', 'pos': None},
    {'id': 'f', 'w': 42.0, 'd': 39.0, 'h': 88.0, 'desc': '棚', 'pos': None},
    {'id': 'g', 'w': 50.0, 'd': 52.0, 'h': 120.0, 'desc': '冷蔵庫', 'pos': None},
    {'id': 'h', 'w': 45.0, 'd': 29.5, 'h': 69.0, 'desc': 'キャスター机', 'pos': None},
    {'id': 'j', 'w': 42.0, 'd': 27.0, 'h': 57.5, 'desc': 'ゴミ箱', 'pos': None},
    {'id': 'm', 'w': 49.0, 'd': 19.0, 'h': 45.0, 'desc': 'PC', 'pos': None},
    {'id': 'n', 'w': 31.0, 'd': 31.5, 'h': 41.0, 'desc': '食洗機', 'pos': None},
    {'id': 'r', 'w': 100.0, 'd': 60.0, 'h': 0, 'desc': '昇降机(サイズ不明仮定)', 'pos': None}, # サイズ不明、Gエリアに配置
]

areas = [
    # 座標は推測ロジックにより動的に設定するが、ここでは仮置き計算用の辞書
    {'id': 'B', 'w': 52, 'd': 121, 'desc': '冷蔵庫エリア'},
    {'id': 'G', 'w': 120, 'd': 172, 'desc': 'PCエリア'}, # 258 * 2/3
    {'id': 'D', 'w': 296, 'd': 86, 'desc': '6畳の一部(1/3)'}, # 348 - 52
    {'id': 'E', 'w': 228, 'd': 86, 'desc': '6畳の一部(2/3)'}, # 348 - 120
    {'id': 'F', 'w': 228, 'd': 86, 'desc': '6畳の一部(3/3)'}, # 348 - 120
    {'id': 'A', 'w': 220, 'd': 79, 'desc': '通路'},
    {'id': 'C', 'w': 100, 'd': 42, 'desc': 'エリアC'},
    {'id': 'I', 'w': 68, 'd': 79, 'desc': '玄関'},
]

# 描画の準備
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(-20, ROOM_W + 20)
ax.set_ylim(-20, ROOM_D + 20)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)

# --- 座標推測と配置ロジック ---

# 1. ゾーン分割 (Y軸)
# Zone 1: 0 - 86
# Zone 2: 86 - 172
# Zone 3: 172 - 258
y_z1 = 0
y_z2 = 86
y_z3 = 172

# 2. エリアの配置 (背景)

# エリアB: 左下隅と仮定 (x=0, y=0)
pos_B = (0, 0)
# エリアD: Bの右、Zone 1 (x=52, y=0)
pos_D = (52, 0)

# エリアG: 左側、Zone 2,3 (x=0, y=86)
pos_G = (0, 86)
# エリアE: Gの右、Zone 2 (x=120, y=86)
pos_E = (120, 86)
# エリアF: Gの右、Zone 3 (x=120, y=172)
pos_F = (120, 172)

# エリアA, C, I の配置 (かなり推測)
# A (通路): 220x79. 「a~f (y~45) より遠い」。
# 仮説: Zone 1 の上部、または Zone 2 にかかっている。
# エリアC: AとBに隣接。
# ここでは D, E の中にある「論理的なエリア」として描画するか、オーバーレイするか。
# Cを B(x=0..52) の隣、a,b,c の奥 (y=45~) に配置してみる。
pos_C = (52, 45) # x=52, y=45。 e, f がここにある。

# Aを C の隣 (x=152) に配置してみる？
# A(220) + C(100) + B(52) = 372 > 348。はみ出る。
# A は C の「奥」かもしれないし、並列かもしれない。
# 記述「玄関前の通路... a~fはx軸に近い方に置かれておりAエリアはそれより遠い」
# -> Aは y 軸方向で奥 (yが大きい) 可能性が高い。
# 仮置き: A を E のエリアにオーバーレイさせる (x=120, y=86)。
pos_A = (120, 86) 

# I (玄関): Aの隣。
pos_I = (120 + 220, 86) # はみ出るが一旦置く

# 辞書に反映
area_map = {
    'B': pos_B, 'D': pos_D, 'G': pos_G, 'E': pos_E, 'F': pos_F,
    'C': pos_C, 'A': pos_A, 'I': pos_I
}

# 3. 家具の配置 (前景)

# 冷蔵庫 g -> エリアB内
pos_g = (1, 1) # B(0,0)基準

# キッチン列 a, b, c -> エリアDの下辺 (y=0) 沿い、B(x=52)の右から開始
current_x = 52
pos_a = (current_x, 0); current_x += 29.5
pos_b = (current_x, 0); current_x += 75
pos_c = (current_x, 0); current_x += 100

# エリアCにある家具 e, f
# C は (52, 45) と仮定
pos_e = (52, 45)
pos_f = (52 + 60, 45)

# エリアGにある r (昇降机)
pos_r = (10, 86 + 10)

# ゴミ箱 j -> どこ？ キッチン付近？ 仮に c の横
pos_j = (current_x + 5, 0)

# 辞書に反映
obj_map = {
    'g': pos_g, 'a': pos_a, 'b': pos_b, 'c': pos_c, 
    'e': pos_e, 'f': pos_f, 'r': pos_r, 'j': pos_j
}

# --- 描画実行 ---

# エリアを描画
colors = {'B': '#ffcccc', 'D': '#ccffcc', 'G': '#ccccff', 'E': '#eeffcc', 'F': '#ccffee', 
          'C': '#ffffcc', 'A': '#eeeeee', 'I': '#dddddd'}

for area in areas:
    aid = area['id']
    if aid in area_map:
        x, y = area_map[aid]
        w, d = area['w'], area['d']
        rect = patches.Rectangle((x, y), w, d, linewidth=1, edgecolor='black', facecolor=colors.get(aid, '#f0f0f0'), alpha=0.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + d/2, f"Area {aid}\n{area['desc']}", ha='center', va='center', fontsize=9, color='black', alpha=0.7)

# 家具を描画
for obj in objects:
    oid = obj['id']
    pos = obj_map.get(oid)
    if pos:
        x, y = pos
        w, d = obj['w'], obj['d']
        rect = patches.Rectangle((x, y), w, d, linewidth=2, edgecolor='blue', facecolor='none')
        ax.add_patch(rect)
        ax.text(x + w/2, y + d/2, f"{oid}", ha='center', va='center', fontsize=10, color='blue', weight='bold')

# 壁P (x軸上の壁)
plt.plot([0, 172], [0, 0], color='red', linewidth=3, label='Wall P')
# 換気扇壁 O (玄関よりx軸に近い) -> 推測で左壁?
plt.plot([0, 0], [0, 43], color='green', linewidth=3, label='Wall O?')

plt.title("Room Layout Visualization (Draft)")
plt.xlabel("Width (cm)")
plt.ylabel("Depth (cm)")
plt.legend()
plt.savefig('room_layout_v1.svg') # ベクター形式で保存
plt.close()

print("Layout generated: room_layout_v1.svg")
