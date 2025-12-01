# UI Data Contract v1.0

## 概要
Environment State Module (Backend) から Persuasive Interface (Frontend) へ受け渡されるデータ構造の定義。
本インターフェースは、単なるタスク情報の伝達ではなく、ユーザーの行動変容を促すための「説得メタデータ」を含む。

## 1. ルート構造
```json
{
  "suggested_tasks": [ ... ], // 今すぐ実行すべきタスクのリスト
  "postponed_tasks": [ ... ]  // 戦略的に延期されたタスクのリスト
}
```

## 2. Suggested Task Object
介入推奨タスクの定義。ユーザーに対し「なぜ今やるべきか」を数学的に証明するデータを持つ。

| Field | Type | Description |
| :--- | :--- | :--- |
| `task_id` | String | 一意のタスクID (e.g., "task_MoldRisk") |
| `title` | String | タスク名 (e.g., "MoldRiskへの介入") |
| `description` | String | 詳細説明 |
| `required_time` | Float | 所要時間 (分/単位時間) |
| `required_energy` | Float | 消費エネルギー (0-100) |
| `urgency_score` | Float | 0.0 - 1.0 の緊急度。UIでの強調表示（赤色など）に使用。 |
| `roi_value` | Float | 投資対効果。正の値が大きいほど「今やると得」。 |
| `persuasion_message` | String | LLMやルールベースで生成された、ユーザーへの短い説得メッセージ。 |
| `projected_cost_series` | Array | 未来のコスト推移データ（後述）。グラフ描画用。 |

### 2.1. Projected Cost Point Object
`projected_cost_series` の各要素。

| Field | Type | Description |
| :--- | :--- | :--- |
| `time_offset` | Int | 現在からの経過時間ステップ (0=現在, 1=次回...) |
| `predicted_penalty` | Float | その時点で放置した場合のペナルティ（不快度など） |
| `predicted_action_cost` | Float | その時点で介入した場合のコスト（労力） |

**Usage:** フロントエンドは `time_offset` をX軸、`predicted_action_cost` をY軸とした折れ線グラフを描画し、右肩上がりの急勾配（指数関数的増加）を可視化することで恐怖/危機感を喚起する。

## 3. Postponed Task Object
却下（延期）されたタスクの定義。ユーザーの罪悪感を軽減し、賢明な判断であることを伝える。

| Field | Type | Description |
| :--- | :--- | :--- |
| `task_id` | String | 一意のID |
| `title` | String | タスク名 |
| `reason` | Enum | `ResourceShortage` (リソース不足), `LowROI` (時期尚早), `Deprioritized` (他優先), `NotApplicable` (不要) |
| `justification_message` | String | ユーザーへの慰め・正当化メッセージ (e.g., "今はリソースが不足しています...") |

## 4. Enum Definitions

### RejectionReason
*   `ResourceShortage`: 時間や体力が足りないため、物理的に不可能。
*   `LowROI`: まだ汚れが溜まっておらず、今やると効率が悪い（規模の経済待ち）。
*   `Deprioritized`: リソースはあるが、より緊急性の高いタスク（Moldなど）に割り当てられた。
