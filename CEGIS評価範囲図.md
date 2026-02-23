# CEGIS フローに対する評価範囲の注釈図

CEGISのプロセスの線はそのまま維持し、外側の範囲指定（subgraph）で「どこからどこまでが何の評価対象か」を示す。

## 1. 全体俯瞰: 評価範囲とCEGISフロー

```mermaid
flowchart TD

    subgraph scope_cognitive ["🧠 認知能力評価の範囲\n方針転換の質 / 仮説多様性 / 問題再表象化 / 抑制制御 / 作動記憶"]

        subgraph scope_process ["📐 プロセス評価の範囲\nバックトラック率 / 条件カバレッジ / 補題再利用率 / 依存距離"]

            subgraph scope_elegance ["✨ エレガンス評価の範囲\n短さ / 局所性 / 道具の軽さ / 本質性 / 必然性 / 再利用性"]
                FinalCheck["P5: 最終チェッカ\nLean4独立検証"]
                Answer["最終回答"]
                FinalCheck -->|"CHECKED"| Answer
            end

            P0["P0: 問題解釈\nテンプレ選択"]
            P1["P1: 合成器\nLean4証明候補生成"]
            FOL["P2: FOL検証器\nZ3/cvc5"]
            HOL["P3: HOL検証器\nLean4/Leo-III"]
            CEGIS["P4: CEGISエンジン\nテンプレ・反例反映"]

            P0 --> P1
            P1 --> FOL
            FOL -->|"Pass"| HOL
            FOL -->|"Fail + 反例"| CEGIS
            HOL -->|"Pass"| FinalCheck
            HOL -->|"Fail + エラー"| CEGIS
            CEGIS -->|"次イテレーション"| P1

        end

    end

    Problem["数学問題"] --> P0
    Answer --> Feedback["P6: ポートフォリオ評価器\n全軸スコア算出 → フィードバック"]
    Feedback -->|"次問題の改善"| P0
```

## 2. 各評価軸の範囲を個別に示す

### 2-1. エレガンス評価の範囲（成功した証明の事後評価）

```mermaid
flowchart TD

    subgraph elegance_scope ["✨ エレガンス評価対象\n証明が CHECKED になった後、完成した証明の構造を評価"]
        P5["P5: CHECKED\n証明完了"]
        proof_tree["完成した証明木"]
        P5 --> proof_tree
    end

    P0["P0: 問題解釈"] --> P1["P1: 合成器"]
    P1 --> P2["P2: FOL"]
    P2 -->|"Pass"| P3["P3: HOL"]
    P2 -->|"Fail"| P4["P4: CEGIS"]
    P3 -->|"Pass"| P5
    P3 -->|"Fail"| P4
    P4 --> P1

    proof_tree --> E1["短さ: ステップ数・補助対象数"]
    proof_tree --> E2["局所性: 依存距離"]
    proof_tree --> E3["道具の軽さ: Mathlib定理深度"]
    proof_tree --> E4["本質性: 条件使用カバレッジ"]
    proof_tree --> E5["必然性: 最終証明の分岐の少なさ"]
    proof_tree --> E6["再利用性: 補題再利用率"]
```

### 2-2. プロセス評価の範囲（CEGISループ全体の探索過程）

```mermaid
flowchart TD

    P0["P0: 問題解釈"] --> P1

    subgraph process_scope ["📐 プロセス評価対象\nP1→P2→P3→P4 のループ全体の探索振る舞い"]
        P1["P1: 合成器"]
        P2["P2: FOL"]
        P3["P3: HOL"]
        P4["P4: CEGIS"]
        P5["P5: 最終チェッカ"]

        P1 --> P2
        P2 -->|"Pass"| P3
        P2 -->|"Fail"| P4
        P3 -->|"Pass"| P5
        P3 -->|"Fail"| P4
        P4 --> P1
    end

    process_scope -.-> Pr1["バックトラック率\n= CEGIS→P1 の回数 / 全ステップ数"]
    process_scope -.-> Pr2["条件カバレッジ\n= P2 unsat core で使われた前提の割合"]
    process_scope -.-> Pr3["補題再利用率\n= P3で採用された部品の再参照回数"]
    process_scope -.-> Pr4["依存距離\n= 証明DAG上の平均ステップ間距離"]
    process_scope -.-> Pr5["道具の軽さ\n= 使用したMathlib定理の最大深度"]
```

### 2-3. 認知能力評価の範囲（P0を含む最広域）

```mermaid
flowchart TD

    subgraph cognitive_scope ["🧠 認知能力評価対象\nP0の問題解釈からP4の戦略変更まで、思考過程全体"]

        P0["P0: 問題解釈\nテンプレ選択"]
        P1["P1: 合成器"]
        P2["P2: FOL"]
        P3["P3: HOL"]
        P4["P4: CEGIS"]
        P5["P5: 最終チェッカ"]

        P0 --> P1
        P1 --> P2
        P2 -->|"Pass"| P3
        P2 -->|"Fail"| P4
        P3 -->|"Pass"| P5
        P3 -->|"Fail"| P4
        P4 --> P1
    end

    Problem["数学問題"] --> P0

    cognitive_scope -.-> C1["認知的柔軟性\n= P4での戦略変更・テンプレ変更のうち\n有効だった割合"]
    cognitive_scope -.-> C2["拡散的思考\n= P1で生成されたbeam候補間の\n構造的距離"]
    cognitive_scope -.-> C3["問題再表象化\n= CEGIS→P0 に戻った回数と\n前提集合の変化量"]
    cognitive_scope -.-> C4["メタ認知\n= 自己修正（P4経由の修正成功）/\n全エラー数"]
    cognitive_scope -.-> C5["抑制制御\n= P1で問題文にない前提を\n追加しなかった度合い"]
    cognitive_scope -.-> C6["作動記憶\n= 推論後半で前半の制約を\n忘れていない度合い"]
```

## 3. 範囲の入れ子関係

```mermaid
flowchart TD
    subgraph nest_cognitive ["🧠 認知能力評価 ── 最広域: P0〜P5 全域"]
        direction TB

        subgraph nest_process ["📐 プロセス評価 ── 中域: P1〜P5 ループ"]
            direction TB

            subgraph nest_elegance ["✨ エレガンス評価 ── 最狭域: P5 証明完了後"]
                direction TB
                inner_P5["P5: CHECKED → 完成証明木の静的分析"]
            end

            inner_P1["P1: 合成器"]
            inner_P2["P2: FOL検証"]
            inner_P3["P3: HOL検証"]
            inner_P4["P4: CEGISエンジン"]

            inner_P1 --> inner_P2
            inner_P2 --> inner_P3
            inner_P3 --> inner_P5
            inner_P2 -.->|"Fail"| inner_P4
            inner_P3 -.->|"Fail"| inner_P4
            inner_P4 --> inner_P1
        end

        inner_P0["P0: 問題解釈・テンプレ選択"]
        inner_P0 --> inner_P1
    end

    note_e["✨ 何を評価: 完成した証明の構造的品質\n短さ・局所性・道具の軽さ・本質性・必然性・再利用性"]
    note_p["📐 何を評価: 解にたどり着く過程の効率\nバックトラック率・条件カバレッジ・補題再利用率・依存距離"]
    note_c["🧠 何を評価: 推論主体としての認知的振る舞い\n柔軟性・多様性・再表象化・メタ認知・抑制制御・作動記憶"]

    nest_elegance -..- note_e
    nest_process -..- note_p
    nest_cognitive -..- note_c
```

## 4. 評価タイミングと範囲の対応

```mermaid
flowchart LR
    subgraph timing ["評価タイミング"]
        direction TB
        T1["毎イテレーション\n(Dense Reward)"]
        T2["証明成功時\n(CHECKED)"]
        T3["予算切れ時\n(Fail)"]
    end

    subgraph scope ["対応する評価範囲"]
        direction TB
        S1["🧠 認知能力\n(P0〜P4 全域)"]
        S2["📐 プロセス\n(P1〜P5 ループ)"]
        S3["✨ エレガンス\n(P5 証明完了後)"]
    end

    subgraph usage ["用途"]
        direction TB
        U1["CEGISエンジンへの\nDense報酬"]
        U2["GRPO学習の\n報酬シグナル"]
        U3["次問題への\nプロンプト改善"]
    end

    T1 --> S1
    T1 --> S2

    T2 --> S1
    T2 --> S2
    T2 --> S3

    T3 --> S1
    T3 --> S2

    S1 --> U1
    S1 --> U2
    S2 --> U2
    S2 --> U3
    S3 --> U2
    S3 --> U3
```

## 5. フィードバックの流れ（範囲別）

```mermaid
flowchart TD
    subgraph cegis_flow ["CEGISフロー"]
        direction LR
        fP0["P0"] --> fP1["P1"] --> fP2["P2"] --> fP3["P3"] --> fP5["P5"]
        fP2 -.->|"Fail"| fP4["P4"]
        fP3 -.->|"Fail"| fP4
        fP4 --> fP1
    end

    subgraph eval_layer ["評価レイヤー"]
        direction TB
        ev_cog["🧠 認知能力\n(P0〜P4)"]
        ev_proc["📐 プロセス\n(P1〜P5)"]
        ev_eleg["✨ エレガンス\n(P5)"]
    end

    subgraph feedback_targets ["フィードバック先"]
        direction TB
        fb_dense["Dense Reward\n→ P4 CEGISエンジン\n（実行中に即時反映）"]
        fb_grpo["GRPO報酬\n→ DeepSeek-Prover重み更新\n（学習時に反映）"]
        fb_prompt["プロンプト改善\n→ P0 問題解釈\n（次問題に反映）"]
        fb_memory["パターンDB\n→ Construction Memory\n（長期蓄積）"]
    end

    cegis_flow -.-> eval_layer

    ev_cog -->|"毎ステップ"| fb_dense
    ev_cog -->|"事後"| fb_grpo
    ev_proc -->|"事後"| fb_grpo
    ev_proc -->|"事後"| fb_prompt
    ev_eleg -->|"成功時のみ"| fb_grpo
    ev_eleg -->|"成功時のみ"| fb_prompt
    ev_cog -->|"失敗時"| fb_memory
```

---

## 資料準拠/提案の区別

### 資料準拠（事実）
- エレガンス6指標の定義と近似方法（エレガンスの評価方法.md）
- 認知能力指標の階層と定義（仮説推論の評価方法.md）
- CEGISのP0〜P5ポートとルール表（ソルバの出力パターン2.md）
- 3層分離の原則（正しさ → エレガンス → 説明品質）

### 提案/ドラフト
- 3つの評価範囲（エレガンス/プロセス/認知）の入れ子構造の定義
- 各評価範囲がCEGISフローのどこからどこまでを対象とするかの設計
- 範囲別のフィードバック先の振り分け
- 上記全てのMermaid図
