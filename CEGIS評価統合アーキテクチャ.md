# CEGIS + エレガンス/認知能力評価 統合アーキテクチャ

## 1. 全体フロー（評価レイヤー統合版）

```mermaid
flowchart TD
    subgraph input [入力]
        Problem["数学問題\n(自然言語)"]
    end

    subgraph formalization [形式化フェーズ]
        DSFormalize["P0: DeepSeek-Prover-V2-7B\n問題の形式化・テンプレ選択"]
    end

    subgraph cegisLoop [CEGISループ]
        Synthesizer["P1: 合成器\nLean4証明候補の生成\nエンコード生成"]
        FOLCheck["P2: FOL検証器\nZ3/cvc5\n高速枝刈り"]
        HOLCheck["P3: HOL検証器\nLean4 Type Checker / Leo-III\n精密検証"]
        CEGISEngine["P4: CEGISエンジン\nテンプレ・文法・反例反映"]
        FinalCheck["P5: 最終チェッカ\nLean4独立検証"]
    end

    subgraph observation [観測レイヤー（実行中）]
        TraceLog["実行トレースログ\n・探索経路の分岐数\n・方針転換の発火\n・仮説候補の多様性\n・制約使用タイミング"]
        DenseReward["Dense Reward\n(認知指標)\n・抑制制御スコア\n・柔軟性スコア\n・メタ認知スコア"]
    end

    subgraph evaluation [P6: ポートフォリオ評価器]
        EleganceEval["エレガンス評価\n(6軸)\n短さ・局所性・道具の軽さ\n本質性・必然性・再利用性"]
        CognitiveEval["認知能力評価\n方針転換の質\n仮説多様性\n問題再表象化\n制約保持"]
        ProcessEval["プロセス評価\nバックトラック率\n条件カバレッジ\n補題再利用率\n依存距離"]
    end

    subgraph feedback [フィードバック生成]
        FeedbackGen["構造化フィードバック\nスコア + 改善ヒント\n→ LLMプロンプトへ"]
    end

    subgraph output [出力]
        Answer["最終回答"]
    end

    Problem --> DSFormalize
    DSFormalize --> Synthesizer

    Synthesizer --> FOLCheck
    FOLCheck -->|"Pass"| HOLCheck
    FOLCheck -->|"Fail + 反例"| CEGISEngine
    HOLCheck -->|"Pass(証明完了)"| FinalCheck
    HOLCheck -->|"Fail + エラー"| CEGISEngine
    CEGISEngine -->|"次イテレーション"| Synthesizer

    Synthesizer -.->|"候補ログ"| TraceLog
    FOLCheck -.->|"判定ログ"| TraceLog
    HOLCheck -.->|"判定ログ"| TraceLog
    CEGISEngine -.->|"遷移ログ"| TraceLog
    TraceLog -.->|"各ステップ"| DenseReward

    FinalCheck -->|"CHECKED"| EleganceEval
    FinalCheck -->|"CHECKED"| CognitiveEval
    FinalCheck -->|"CHECKED"| ProcessEval
    FinalCheck -->|"CHECKED"| Answer

    TraceLog --> CognitiveEval
    TraceLog --> ProcessEval

    EleganceEval --> FeedbackGen
    CognitiveEval --> FeedbackGen
    ProcessEval --> FeedbackGen

    DenseReward -->|"実行中報酬"| CEGISEngine

    FeedbackGen -->|"次問題の\nプロンプト改善"| DSFormalize
```

## 2. 評価タイミングと3層分離

```mermaid
flowchart LR
    subgraph runtime ["実行中（各イテレーション）"]
        direction TB
        R1["認知指標の観測"]
        R2["Dense Reward計算"]
        R3["CEGISエンジンへ\nフィードバック"]
        R1 --> R2 --> R3
    end

    subgraph post_success ["実行後（成功時）"]
        direction TB
        S1["① 正しさ\nLean4 CHECKED\n(自動判定)"]
        S2["② エレガンス\n6軸スコア\n(ランキング学習)"]
        S3["③ 説明品質\n可読性・答案らしさ\n(スタイル評価)"]
        S1 --> S2 --> S3
    end

    subgraph post_fail ["実行後（失敗時）"]
        direction TB
        F1["認知指標の\n事後分析"]
        F2["「どこで詰まったか」\n構造分析"]
        F3["次回の\n戦略選択改善"]
        F1 --> F2 --> F3
    end

    runtime ---|"成功"| post_success
    runtime ---|"予算切れ"| post_fail
```

## 3. 観測項目と観測箇所の対応

```mermaid
flowchart TD
    subgraph sources ["観測ソース（CEGISパイプライン内）"]
        P0Log["P0: 問題解釈ログ\n再解釈の有無"]
        P1Log["P1: 候補生成ログ\nbeam内の構造距離"]
        P2Log["P2: FOL判定ログ\nunsat core履歴"]
        P3Log["P3: HOL判定ログ\nMathlib定理深度"]
        P4Log["P4: CEGIS遷移ログ\nルール発火履歴"]
        HistLog["history\n全探索経路"]
    end

    subgraph elegance ["エレガンス6軸"]
        E_len["短さ\nステップ数\n補助対象数"]
        E_loc["局所性\n推論DAGの\n依存距離"]
        E_tool["道具の軽さ\nMathlib\n定理深度"]
        E_const["本質性\n条件使用\nカバレッジ"]
        E_inev["必然性\n分岐数\nバックトラック量"]
        E_reuse["再利用性\n補題\n再利用率"]
    end

    subgraph cognitive ["認知能力指標"]
        C_flex["認知的柔軟性\n方針転換の\n回数と質"]
        C_div["拡散的思考\n候補間の\n構造距離"]
        C_refr["問題再表象化\nP0再帰回数\n前提変化量"]
        C_meta["メタ認知\n自己修正率\nエラー率"]
        C_inhib["抑制制御\n不要前提の\n追加有無"]
        C_wm["作動記憶\n制約保持\n一貫性"]
    end

    HistLog --> E_len
    HistLog --> E_loc
    P3Log --> E_tool
    P2Log --> E_const
    P4Log --> E_inev
    P3Log --> E_reuse

    P4Log --> C_flex
    P1Log --> C_div
    P0Log --> C_refr
    P4Log --> C_meta
    P1Log --> C_inhib
    HistLog --> C_wm
```

## 4. 損失関数の構造

```mermaid
flowchart TD
    subgraph existing ["既存の損失関数"]
        L_valid["L_valid\n正しさ\n(形式検証通過)"]
        L_rank["L_rank\nエレガンス順位\n(ペア比較)"]
        L_style["L_style\n読みやすさ\n答案らしさ"]
        L_len["L_length_reg\n冗長性抑制"]
    end

    subgraph new ["追加する損失関数"]
        L_proc["L_process\nプロセス報酬"]
        L_cog["L_cognitive\n認知能力報酬"]
    end

    subgraph proc_detail ["L_process の内訳"]
        Pr1["(1-バックトラック率)\n× w_inevitability"]
        Pr2["条件カバレッジ\n× w_constraint"]
        Pr3["補題再利用率\n× w_reuse"]
        Pr4["1/Mathlib深度\n× w_tool_min"]
        Pr5["1/平均依存距離\n× w_locality"]
    end

    subgraph cog_detail ["L_cognitive の内訳"]
        Co1["有効転換/全転換\n× w_flexibility"]
        Co2["候補構造距離\n× w_diversity"]
        Co3["再表象化成功率\n× w_reframing"]
        Co4["自己修正/エラー数\n× w_metacog"]
    end

    L_valid --> Loss
    L_rank --> Loss
    L_style --> Loss
    L_len --> Loss
    L_proc --> Loss
    L_cog --> Loss

    Pr1 --> L_proc
    Pr2 --> L_proc
    Pr3 --> L_proc
    Pr4 --> L_proc
    Pr5 --> L_proc

    Co1 --> L_cog
    Co2 --> L_cog
    Co3 --> L_cog
    Co4 --> L_cog

    Loss["L = a·L_valid + b·L_rank\n+ c·L_style + d·L_length_reg\n+ e·L_process + f·L_cognitive"]
```

## 5. ルール表への統合（P6 Portfolio Evaluator）

```mermaid
flowchart TD
    subgraph triggers ["評価トリガー"]
        T_success["P5: CHECKED\n(証明成功)"]
        T_budget["予算切れ\n(search_remaining < 1)"]
        T_iteration["各イテレーション\n完了時"]
    end

    subgraph eval_actions ["P6: 評価アクション"]
        direction TB
        A1["evaluate_portfolio\n全軸スコア計算"]
        A2["generate_feedback_prompt\nスコア + 改善ヒント"]
        A3["save_artifacts\n評価結果保存"]
    end

    subgraph feedback_content ["フィードバック内容"]
        FB_score["スコア\nProcess: 0.72\nElegance: 0.58\nCognitive: 0.65"]
        FB_hints["改善ヒント\n・h3を早期使用すべき\n・定理を軽量に置換可能\n・依存距離を短縮可能"]
        FB_fail["失敗分析\n・詰まった箇所\n・無効な方針転換の特定\n・テンプレ不足の診断"]
    end

    subgraph destinations ["フィードバック先"]
        D_prompt["次問題の\nLLMプロンプト"]
        D_grpo["GRPO学習の\n報酬シグナル"]
        D_memory["Construction Memory\nパターンDB更新"]
    end

    T_success --> A1
    T_budget --> A1
    T_iteration -.->|"Dense"| A1

    A1 --> A2
    A2 --> A3

    A2 -->|"成功時"| FB_score
    A2 -->|"成功時"| FB_hints
    A2 -->|"失敗時"| FB_fail

    FB_score --> D_prompt
    FB_score --> D_grpo
    FB_hints --> D_prompt
    FB_fail --> D_prompt
    FB_fail --> D_memory
```

## 6. 報酬シグナルの種類と対応

```mermaid
flowchart LR
    subgraph result_rewards ["結果報酬（成功時のみ）"]
        RR1["最終解答の正確性\n← Lean4 CHECKED"]
        RR2["エレガンス順位\n← ペア比較"]
        RR3["説明品質\n← スタイル評価"]
    end

    subgraph process_rewards ["プロセス報酬（毎ステップ）"]
        PR1["暗黙前提の列挙\n← 抑制制御"]
        PR2["方針転換の実行\n← 認知的柔軟性"]
        PR3["仮説の多様性\n← 拡散的思考"]
        PR4["仮説への反例提示\n← メタ認知的監視"]
        PR5["問題の再定義\n← 問題再表象化"]
    end

    subgraph elegance_rewards ["エレガンス報酬（成功時のみ）"]
        ER1["短さ\n← ステップ数"]
        ER2["局所性\n← 依存距離"]
        ER3["道具の軽さ\n← 定理深度"]
        ER4["本質性\n← 条件カバレッジ"]
        ER5["必然性\n← 分岐数"]
        ER6["再利用性\n← 補題再利用率"]
    end

    result_rewards -->|"a · L_valid\nb · L_rank\nc · L_style"| TOTAL["統合報酬\nL_total"]
    process_rewards -->|"f · L_cognitive"| TOTAL
    elegance_rewards -->|"e · L_process"| TOTAL

    TOTAL -->|"GRPO"| LLM["DeepSeek-Prover-V2-7B\n次イテレーション/\n次問題の改善"]
```

---

## 資料準拠/提案の区別

### 資料準拠（事実）
- エレガンス6指標の定義と近似方法（エレガンスの評価方法.md）
- 認知能力の階層と報酬シグナル候補（仮説推論の評価方法.md）
- 損失関数 `L = a*L_valid + b*L_rank + c*L_style + d*L_length_reg`
- 3層分離の原則（正しさ → エレガンス → 説明品質）
- CEGISのP0〜P5ポートとルール表（ソルバの出力パターン2.md）

### 提案/ドラフト
- P6（Portfolio Evaluator）の新設
- L_process / L_cognitive の損失関数追加
- 観測項目8種と観測箇所の対応設計
- Dense Reward（実行中報酬）の仕組み
- フィードバックフォーマットの具体形
- 上記全てのMermaid図

### 未整備
- 各重みのチューニング方法
- ペア比較データの収集パイプライン
- ドメイン別評価器（幾何 vs 整数論）の分離反映方法
- 推論DAGをCEGIS historyから再構成する具体手順
