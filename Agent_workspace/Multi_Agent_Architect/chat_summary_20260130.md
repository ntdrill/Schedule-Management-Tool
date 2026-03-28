# codex移植 議論まとめ（Multi_Agent_Architect向け）
日付: 2026-01-30  
範囲: 「codex-smoke（CAO + Codex CLI）を現在の**実装システム**へ移植・統合する」議論のみ  
方針: 資料準拠/提案/未整備を区別。引用は最小限。  

---

## 1. 対象と前提（資料準拠）
- **主題**: 本チャットの目的は、`codex-smoke` という自律エージェント基盤（CAO + Codex CLI）を、現在ファイルシステムベースで運用されている**実装システム**（開発体制そのもの）に移植・統合する設計を行うこと。スケジュール管理ツール（対象システム）の実装ではない。
- **クロック受付の場所**: `Agent_Manager` フォルダ配下に存在する。これはエージェントの稼働時間を管理するためのポストである。

---

## 2. codex-smoke の確認結果（資料準拠）
### 2.1 動作構成（アーキテクチャ）
- **CAO (Orchestrator)**: 複数の `tmux` セッションを管理し、外部からエージェントを操作するための REST API を提供するサーバ。
- **Codex CLI**: OpenAIのコーディングエージェント。`--no-alt-screen` オプションで起動することで、TUI（テキストUI）ではなく標準入出力で制御可能な状態で常駐する。
- **Driver**: `communication_log.jsonl` というログファイルを監視し、書き込まれたメッセージを適切なエージェントの `tmux` セッションに配送する Python スクリプト。
- **send_message.sh**: エージェントが他者へメッセージを送る際に実行するツール。実際には直接通信するのではなく、ログファイルへの書き込みを行うトリガーとして機能する。
- **`>>> [CALL: ...]`**: エージェントの思考過程（Thinking）と実際の行動（Action）を区別するために導入された、厳格な行頭ルール。これにより誤作動を防いでいる。

### 2.2 実証された動作
- `codex-smoke` 環境内において、**Manager**（管理者）と **Architect**（設計者）という2つのエージェントが、人間の介入なしに自律的に対話し、Todoアプリの設計案を作成することに成功している。

### 2.3 解決済み課題
- **TUI誤検知**: Codexの装飾的な画面出力が原因で起動判定に失敗していた問題を解決。
- **出力パース不安定**: 正規表現による抽出から、明確なプレフィックス判定へ移行。
- **プロンプト誤検知**: システムプロンプト内の「例示」を実行してしまう問題を、ファイル書き込み方式で解決。
- **権限待ち**: コマンド実行時の確認ダイアログで止まる問題を、`Assume yes` 設定で解決。

---

## 3. 既存運用の前提（資料準拠 + ユーザー提示）
### 3.1 基本フロー（資料準拠）
- `Task_Management` ディレクトリを用いたタスク管理フロー：
  1. **Propose**: 提案ファイルを作成
  2. **Active**: Managerが承認・移動・割当
  3. **Execute**: 担当者が作業・進捗追記
  4. **Complete**: 完了報告・移動

### 3.2 基本ループ（ユーザー提示）
- 開発サイクルの基本単位は **「Active発行 → タスク処理 → クロック → Active発行」** である。
- 開発フェーズやワークフローは最初に定義されるものであり、途中で新しいワークを差し込むのは**例外的な処理**として扱う。

### 3.3 クロック判断の位置（ユーザー提示）
- タスク処理の流れにおける判断ポイント：
  1. Task_Management の変化を監視
  2. 進捗報告受付へ通知
  3. **進捗管理エージェント** が状況を見て「クロック（作業区切り）」を判断
  4. その後、**Agent_Manager** が次の Active タスクを発行する

---

## 4. ユーザー要件（資料準拠）
### 4.1 監視対象の分離（スケーラビリティと質）
- **実体**: 実装エージェントの実体は「ターミナル（プロセス）」である。
- **稼働数**: 現在の状況から予想すると常時稼働するのは Manager と 進捗管理 の2つに加え、必要に応じて 1〜5 つの専門家/設計エージェントが立ち上がる。
- **Agent_Manager**: 「クロック受付」を監視する。
- **進捗管理エージェント**: 「進捗報告受付」と「対象ファイルの更新」を監視する。
  - **理由**: 進捗管理は頻度が多すぎるため、Manager から分離して Manager の負荷を下げ、アサインの質を向上させたい。
- **Task_Management監視**: エージェントではなく、単なるスクリプトとして `Task_Management` フォルダ自体を監視する。
  - **動作**: 一定以上の変化量、または時間経過があった場合に、進捗報告受付へレポートを投げる。
- **専門家エージェント**: `Task_Management` 全体ではなく、自分専用の **「専用タスク受付（Task_Inbox）」** を監視する。
  - 起動中はここだけを見ていれば良い状態にする。
- **ボトムアップの課題**: 現状は上層→下層の指令はスムーズだが、下層からの意見吸い上げが弱い。
  - **理想**: 専門家に対し適切なタイミングで進捗を共有し、意見を収集 → Proposal 起案 → 必要なら例外的にワークフローへワークを割り込み、という流れを作りたい。

### 4.2 キャッシュ / プロンプトフロー（コストと文脈）
- **事前キャッシュ**: エージェントごとに、起動コストを下げるためのキャッシュを事前に作成し再利用する。
- **事前資料の定義**: 「共通の `readme`」＋「エージェント専用の `docs`」の組み合わせ。
- **プロンプトフロー**: 事前資料に含まれない動的な情報（新規Proposal、現在の進捗など）は、特定のプロンプト手順で適宜注入する。
- **APIの使い分け**: OpenAI (prompt caching), Gemini (context caching), Claude (cache_control) など、プロバイダごとの機能を活用。
- **Assistants API thread**: コスト削減効果はないが、同じ文脈でやり取りを続ける場合の「プロンプトフロー（再入力）の省略」に有効。
- **繰り返し業務**: 定型業務はシステムプロンプトに組み込んで新たにキャッシュ化することでコストカットを図る。
- **繰り返し業務の検知と予想**:
  - 繰り返し検知: 進捗管理 + 各エージェント
  - 予想: Agent_Manager + 各エージェント
- **タイミング**: 業務が発行された時点でキャッシュを保持すべき。検知や予想処理は頻繁に行うものではない。

### 4.3 ツール方針（拡張性）
- **優先度**: ツール開発はコストとスピード改善において**最優先**事項。
- **言語**: シェルスクリプトだけでなく Python スクリプトも許容する。
- **管理**: 「共有ツール」と「専用ツール」を分ける。
- **運用**: `Shared_Tools` フォルダを作成し、必要に応じて各エージェントのワークスペースにコピーして（改変可能にして）使う。

### 4.4 権限ポリシー（セキュリティ）
- **基本原則**: 各エージェントは自分のワークスペース内は自由に操作できる。
- **編集/削除**: 原則として「そのファイルを作成したエージェント」か「開発者本人」だけが可能。
- **Role別権限**:
  - **Agent_Manager**: `Task_Management` フォルダを自由に編集可。
  - **専門家**: `01_Proposals` への追加（起案）のみ可。
  - **Agent_Manager / 進捗管理**: プロジェクト全体を参照できるが、編集権限は限定的。
  - **進捗報告受付 / ツールオリジン**: 誰でも追加して良い。
  - **進捗管理**: `進捗報告受付` 内のファイルを移動可。`クロック受付` には追加のみ可。
  - **Symbol_Agent**: シンボル用データベースの操作権限を持つ唯一の存在。
  - **進捗管理**: Git 操作権限を持つ唯一の存在。
  - **Data_Model_Agent**: プロジェクト直下の `data` と `data_backup` を編集できる唯一の存在。
  - **全エージェント**: プロジェクト直下の `docs` は編集禁止（読み取り専用）。
  - **Multi_Agent_Architect**: `Agent Workflow Queue` への追加が可能。

### 4.5 コミュニティ共有（情報共有）
- 特定のエージェント間でのみコミュニケーションファイルを共有する仕組み（チャネル）が必要。
  - **Community A**: Multi_Agent_Architect, Agent_Manager
  - **Community B**: 専門家同士
  - **Community C**: Data_Model_Agent, Symbol_Agent

---

## 5. codex-smoke 移植の設計案（提案/ドラフト）
### 5.1 統合イメージ
- **コンセプト**: 静的なディレクトリ構造（身体）に対し、`codex-smoke` の実行基盤（魂）を組み込む。
- **役割マッピング**: `docs/redme`や`Agent_workspace/{Agent}/docs` の内容を `agent_profiles`（システムプロンプト）に変換しキャッシュ化する。（そのまま流用するのもよい）
- **通信方式**: `codex-smoke` の設計に従い、ファイル（ログやタスクファイル）を介した非同期通信を基本とする。

### 5.2 監視の分離（実装案）
単一の Driver ではなく、役割ごとに軽量な監視プロセス（Watcher）を立てる。
- **ClockWatcher**: `Agent_Manager/Clock_Inbox` を監視し、Agent_Manager に通知。
- **ProgressWatcher**: `進捗報告受付` と対象ファイルを監視し、進捗管理エージェントに通知。
- **TaskFolderWatcher**: `Task_Management` 全体を監視し、変化があれば進捗報告受付へ自動レポート（非エージェント）。
- **InboxWatcher**: 各専門家の `Task_Inbox` を監視し、タスクが来たらその専門家を起動/通知。

### 5.3 最小フロー（クロック判断込み）
1. `Task_Management` に変化発生（TaskFolderWatcher検知）
2. `進捗報告受付` へ通知
3. **進捗管理エージェント** が内容を確認し、クロック（作業区切り）を判断
4. Goサインなら **Agent_Manager** へ通知
5. Agent_Manager が `02_Active` を発行し、担当の `Task_Inbox` へ配布
6. 担当エージェントが作業 → 完了報告
7. 次の Active 発行へ

### 5.4 設定手段（例）
- `agents.yaml`: エージェントの定義（役割、端末名、監視対象パス、受信フォルダ）。
- `permissions.yaml`: 権限ルール（誰がどこを read/write/exec できるか）。
- `tools_registry.yaml`: 利用可能なツールの一覧と、共有/専用の区分。
- `cache/manifest.yaml`: 事前資料パックの構成と、取得済みキャッシュIDの管理。
- `prompt_flow/`: 状況に応じたプロンプトのテンプレート集。
- `thresholds.yaml`: 監視時の「変化量」や「時間経過」の閾値設定。

### 5.5 共有ツール/専用ツール（例）
- `read_task`: 指定されたタスクファイルを読む。
- `assign_task`: タスクに担当者を追記し、フォルダを移動させる。
- `report_progress`: 進捗報告受付にレポートを書く。
- `clock_in`: クロック受付にタイムスタンプを打つ。
- `safe_write`: 権限チェックを行った上でファイルに書き込む。

### 5.6 Driver 改修
- 既存の `run_file_orchestrator.py` を、単一ファイル監視から**ディレクトリ監視**へ改造する。
- 監視対象を `Task_Management/01_Proposals`, `02_Active` などに設定。
- 検知時のメッセージを `>>> [INSTRUCTION: <ファイルパス>]` 形式にすることで、エージェントにファイルを見るよう促す。  

---

## 6. 権限制御（ユーザー提示 + 提案/ドラフト）
### 6.1 ユーザー提示（codex側権限モデル）
- **別セッション（別プロセス/別スレッド）**で分離するのが最も確実。  
- Codex CLI の安全制御は **Sandbox mode / Approval policy**。  
- 作業ディレクトリ境界は `--cd`、追加許可は `--add-dir`。  
- Agents SDK なら MCP サーバ共有/分離の2択。  
- App Server なら thread 単位で `cwd/approvalPolicy/sandbox` 固定。  
- rules/execpolicy や profiles の運用が可能。  
- どの方式で組むか（Agents SDK / app-server / CLIサブエージェント）は未回答。  

### 6.2 提案/ドラフト（強度別の現実解）
- **レベル0**: ツール層ガード（safe_* 経由に統一）  
- **レベル1**: OSユーザー分離（chmod/ACL）  
- **レベル2**: コンテナ/VM分離（厳格だが運用負荷）  

---

## 7. 未整備（要検証）
- Codex CLI キャッシュの実効性（codex-smoke側で検証したい）  
- クロック判断ルールの具体化  
- 監視プロセスの起動/停止ポリシー  
- Codex側権限機能が現環境で使えるか  
- 方式選択（Agents SDK / app-server / CLIサブエージェント）  
# チャット内容まとめ（Multi_Agent_Architect向け）
日付: 2026-01-30  
範囲: このチャット内で行われた依頼・回答・調査・提案・修正の記録  
方針: 内容は省略せず、重複は整理。チャット外の情報は含めない。  

## 1. 依頼・指示（資料準拠）
- `@docs/readme` の内容理解
- `@Agent_workspace/Multi_Agent_Architect/メモ.txt` と `形式的記述について２.md` の内容理解
- `codex-smoke` フォルダのレポート読了
- 「現在の実装システム（対象システムと区別）」との組み合わせ設計（ファイル編集なし）
- 「どのように実装するか」提案（ファイル編集なし）
- その提案への修正点提示と、設定手段・フォルダ構成の再検討
- codex-smoke前提での実装像の説明
- 「クロック受付」位置の修正と、ウォッチャー/通信/キャッシュ/ループ/権限についての再確認
- 基本ループの定義（Active→作業→クロック→Active）と、差し込みは例外という前提の再考
- 権限制御の具体的な仕組みへの質問
- 最終的に「ここまでのチャット内容を資料化し、Multi_Agent_Architectに作成」

---

## 2. 読み取ったファイル（資料準拠）
### docs/readme
- `docs/readme/01_プロジェクト概要.md`
- `docs/readme/02_開発体制・エージェント構成.md`
- `docs/readme/03_バージョン別機能スコープ.md`
- `docs/readme/04_開発ワークフロー.md`
- `docs/readme/05_ドメイン知識・理論基盤.md`
- `docs/readme/06_ディレクトリ構造ガイド.md`
- `docs/readme/07_進捗・履歴.md`

### Multi_Agent_Architect
- `Agent_workspace/Multi_Agent_Architect/メモ.txt`
- `Agent_workspace/Multi_Agent_Architect/形式的記述について２.md`

### codex-smoke
- `/Users/numaoryuutarou/codex-smoke/final_report.md`
- `/Users/numaoryuutarou/codex-smoke/report_v5.md`

### ワークフロー/運用
- `Agent_workspace/Agent_maneger/data/Agent Workflow Queue/v1_phase1.txt`
- `Agent_workspace/Agent_maneger/data/Agent Workflow Queue/v1_phase2.txt`
- `Agent_workspace/Agent_maneger/data/Agent Workflow Queue/v1_phase3.txt`
- `Agent_workspace/Task_Management/README.md`
- `Agent_workspace/Agent_maneger/docs/README.md`


## 6. codex-smoke レポート理解（資料準拠）
### 6.1 final_report.md
- Codex CLI をマルチエージェントとして稼働させた検証
- CAO（Orchestrator）+ Driver + Codex CLI + communication_log.jsonl
- codex-smoke内のManagerとArchitectが対話して設計案作成
- 解決課題: TUI誤検知、出力パース不安定、プロンプト誤検知、権限待ち
- 次のステップ案: エージェント増員、ツール拡充、長期記憶

### 6.2 report_v5.md
- Driverの誤検知対策（`>>> [CALL: ...]`）
- manager/architectプロファイル整備
- CAO + Codex CLI + Driver構成が稼働可能

---


## 7. 統合・実装に関する議論
### 7.1 提案/ドラフト（初期の統合像）
- 「静的な身体に動的な魂」: 既存のAgent_workspaceにcodex-smokeを統合
- 役割マッピング:
  - 役割定義: `Agent_workspace/{Agent}/docs` ↔ `agent_profiles/*.md`
  - 通信: Task_Management ↔ communication_log.jsonl
  - 思考: Codex CLI 常駐
  - 行動: tools/*.sh
- 例フロー: Proposal作成→Manager監視→Active→専門家実行→Completed

### 7.2 提案/ドラフト（実装ロードマップ）
**Phase 1: 共有ツール + 権限基盤**
- `Shared_Tools` と `.system/permissions` 追加
- `permissions.json` 例による役割ごとの許可制

**Phase 2: キャッシュとプロンプトフロー**
- 事前資料（readme + agent docs）
- プロンプトフロー（動的情報再入力）

**Phase 3: 分散監視 + チャネル**
- ClockWatcher / ReportWatcher / TaskFolderWatcher / InboxWatcher
- `.channels/community_a/b/c` による共有

### 7.3 提案/ドラフト（導入ステップ）
1. Agent_Manager の自動化（タスク割当のみ）
2. Tooling の整備（共有/専用ツール）
3. Specialist の段階的自動化

### 7.4 提案/ドラフト（codex-smoke移植先）
- `Agent_workspace/.system/automation/` に codex-smoke の主要部品を移植（仮）

---

## 8. ユーザー修正・要件（資料準拠）
### 8.0 前提評価
- 「1は大丈夫。後から今の環境に合わせられる」

### 8.1 監視対象の分離
- エージェントごとに監視対象を分ける
- 実装エージェントの実体はターミナル
- 常時稼働は「2 + 1〜5端末」
- Agent_Manager: クロック受付監視
- 進捗管理エージェント: 進捗報告受付 + 対象ファイル更新監視  
  （進捗管理は頻度が多すぎるため、Managerから分離してアサインの質を上げたい）
- Task_Management自体を監視する非エージェントプロセスを置く
- Task_Management自身は「一定以上の変化量 or 時間経過」で進捗報告受付に報告
- 専門家はTask_Managementではなく専用タスク受付を監視
- 上層→下層はスムーズだが、下層→上層の意見回収ができない問題がある  
  進捗共有→意見収集→proposal→フェーズのワークフローへ新規ワーク割り込みが理想

### 8.2 キャッシュ/プロンプトフロー
- エージェントごとに事前キャッシュを作成し再利用
- 事前資料 = readme共通 + エージェント専用docs
- 事前資料に含められない情報はプロンプトフローで注入
- OpenAI: prompt caching / Gemini: context caching / Claude: cache_control
- スレッド保存（Assistants API thread）はコスト削減ではないが、  
  同一状況でのプロンプトフロー省略に有効
- 繰り返し業務はシステムプロンプトに含めてキャッシュ化
- 繰り返し業務検知は進捗管理エージェント+各エージェント
- 予想はAgent_Manager+各エージェント
- 業務発行時点でキャッシュ保持が望ましい
- 業務繰り返しの検知/予想は頻繁に行うべきではない

### 8.3 ツール方針
- ツール拡張は最優先級
- シェルだけでなくPythonスクリプトも許容
- 共有ツール/専用ツールを分離
- 共有ツールフォルダを作成し、必要に応じてコピー

### 8.4 権限ポリシー
- 各エージェントは自分のワークスペースは自由に操作
- 編集/削除は「作成者 or 開発者」
- Agent_Manager: Task_Management自由編集
- 専門家: Proposalsへの追加のみ
- Agent_Manager/進捗管理: 全体参照可、編集は限定
- 進捗報告受付/ツールオリジン: 誰でも追加可
- 進捗管理: 進捗報告受付の移動可、クロック受付は追加のみ
- Symbol DB操作はSymbol_Agentのみ
- Git操作は進捗管理のみ
- `data`/`data_backup` はData_Model_Agentのみ編集
- プロジェクト直下の`docs`は編集禁止
- Multi_Agent_ArchitectはAgent Workflow Queueに追加可

### 8.5 コミュニティ共有
- community_a: Multi_Agent_Architect + Agent_Manager
- community_b: 専門家同士
- community_c: Data_Model + Symbol

---

## 9. 追加の再考・修正（資料準拠）
### 9.1 基本ループの明確化
- 基本ループ: **Active発行 → タスク処理 → クロック → Active発行**
- フェーズとワークフローは初期定義
- ワーク差し込みは特殊ケース

### 9.2 クロック判断の位置
- TaskManagement監視→進捗報告受付通知
- 進捗管理エージェントがクロック判断を挟む
- その後 Agent_Manager が Active 発行

---

## 10. codex-smoke前提での再整理
### 10.1 資料準拠（codex-smoke）
- **CAO (Orchestrator)**: `tmux` セッションを管理し、外部から操作するための REST API を提供する。これにより、エージェントの実体となるターミナルプロセスを維持・制御する。
- **Codex CLI**: OpenAIのコーディングエージェント。`--no-alt-screen` オプションで起動することで、TUIではなく標準入出力で対話可能な状態にする。
- **Driver**: `communication_log.jsonl` を監視し、新しいメッセージが書き込まれると、それを適切なエージェントの `tmux` セッションに送信（入力）する役割を担う Python スクリプト。
- **send_message.sh**: エージェントが他者にメッセージを送る際に使用するツール。実際には直接通信するのではなく、共通のログファイルにメッセージを追記する処理を行う。
- **`>>> [CALL: ...]`**: エージェントの出力を監視する際、思考（Thinking）と行動（Action）を区別するための行頭ルール。このプレフィックスがある行だけをツール実行として処理することで、誤検知を防ぐ。

### 10.2 未整備（要検証/未確定）
- **Codex CLI キャッシュの実効性**: プロンプトキャッシュ機能が CLI で有効に機能するか、コスト削減効果があるかについては、`codex-smoke` 環境での実証データが存在しないため検証が必要。
- **クロック判断の具体的ルール**: 進捗管理エージェントがどのような基準（時間帯、変化量、タスク滞留数など）で「クロック（作業区切り）」を判断するかのロジックが未定義。
- **監視プロセスの起動/停止ポリシー**: 複数の Watcher プロセスをいつ起動し、エラー時にどう再起動するかという運用ポリシーが未定。

### 10.3 提案/ドラフト（codex-smoke適合）
- **常駐プロセス**: 「端末 ＝ エージェント」として `tmux` セッションを常駐させ、CAO で管理する構成とする。
- **Driverの分割**: 単一の巨大な監視スクリプトではなく、`ClockWatcher`, `ProgressWatcher` など、監視対象ディレクトリごとに特化した軽量な監視プロセスに分割する。
- **Task_Inbox監視**: 専門家エージェントは全体共有の `Task_Management` ではなく、自分宛てのタスクだけが届く `Task_Inbox` を監視することで、無駄な起動やコンテキスト消費を防ぐ。
- **事前資料＋プロンプトフロー**: 起動時に共通資料（キャッシュ）を読み込ませ、タスク発生時に動的な状況（プロンプトフロー）を追加注入する運用を行う。
- **意見回収ループ**: `.channels` ディレクトリを活用し、専門家からの意見を吸い上げて `01_Proposals` に起案するボトムアップのフローを確立する。

---

## 11. 権限制御の議論（ユーザー提示）
### 11.1 提案/ドラフト（ユーザー提示・外部資料参照あり）
**主張**: 「エージェントごとに編集範囲/実行範囲を変える」なら、  
**Codex側の権限モデルを “別セッション（別プロセス/別スレッド）” に分けるのが最も確実**。

#### Codex CLI の安全制御の2軸
- **Sandbox mode**: 技術的に「どこへ書けるか／ネットワークに出られるか」などの範囲を制限する機能。  
  例: `read-only`（読み取り専用） / `workspace-write`（ワークスペース内のみ書き込み可）
- **Approval policy**: コマンド実行などの前に「いつ承認を求めるか」を制御するポリシー。  
  例: `untrusted`（信頼できない操作は承認が必要） / `on-request`（都度承認） / `never`（承認なしで実行/拒否）

#### 作業ディレクトリ境界
- `--cd`: エージェントの作業ディレクトリ（カレントディレクトリ）を指定するオプション。これにより、そのディレクトリ以下を作業範囲として限定できる。
- `--add-dir`: Sandbox外の特定のディレクトリに対して、例外的に書き込み許可を与えるオプション。

#### A. Agents SDK（おすすめ）
- Codex を **MCP server** として利用する構成。
- 各エージェントの codex 呼び出し時に `cwd`（作業ディレクトリ）、`sandbox`、`approval-policy`、`profile`、`config` を渡すことができる。
- 公式ガイドにも、マルチエージェントで「各役割が成果物フォルダを持つ（例: /design）」構成が紹介されており、このプロジェクトの構造に適している。

**2択提案**:
1. **（簡単）**: 同じMCPサーバを共有しつつ、各エージェントの呼び出し時に毎回 `sandbox/cwd/approval-policy` をパラメータとして指定する。
2. **（堅牢）**: 権限セットごとに Codex MCP サーバ自体を別プロセスとして起動し、完全に分離する。

#### B. Codex App Server
- `thread/start` でスレッドを開始する際に、**スレッドごとに `cwd` / `approvalPolicy` / `sandbox` を指定して固定**できる。
- 「エージェント = thread」として扱う運用であれば、スレッド単位で権限を固定することが可能。

#### ファイル編集の制御（具体例）
- **編集禁止**: `--sandbox read-only` を指定する。
- **特定フォルダのみ編集**: `--cd ./backend` のようにディレクトリを指定し、`--sandbox workspace-write` を組み合わせることで、そのディレクトリ以下のみ編集可能にする。
- **例外的な追加許可**: 共有ドキュメントなどへの書き込みが必要な場合、`--add-dir path/to/shared` で許可を与える。

#### 実行の制御（approval-policyの具体例）
- **安全に閲覧**: `read-only` + `on-request`（編集不可、かつコマンド実行等は都度承認が必要）
- **CI的に読むだけ**: `read-only` + `never`（編集不可、承認ダイアログも出さず自動進行/拒否）
- **編集自動/怪しい実行は承認**: `workspace-write` + `untrusted`（ワークスペース内は自由に編集、危険なコマンドは承認）

#### ルール（execpolicy）
- `.rules` ファイルを使用して、Sandbox外でのコマンド実行を細かく制御する機能。
- `decision = "allow" | "prompt" | "forbidden"` で、コマンドごとに許可/都度承認/禁止を設定できる。
- 設定したルールは `codex execpolicy check` コマンドでテスト可能。

#### プロファイル運用
- `config.toml` に `profiles.*` として設定セット（SandboxモードやApproval policyの組み合わせ）を定義できる。
- エージェント起動時に `--profile dev_edit` のように指定することで、役割に応じた設定を一括で適用できる。

#### 動作検証
- `codex sandbox macos ...` / `codex sandbox linux ...` コマンドを使用して、特定のコマンドが現在のSandbox設定でブロックされるかどうかをローカルで検証できる。

#### 最短実装手順（ユーザー提示）
1. **役割を決める**: Planner（閲覧のみ）、Dev（特定ディレクトリ編集）、Tester（実行中心）など。
2. **作業ディレクトリを分ける**: 各エージェントに `--cd` で異なるディレクトリを割り当てる。
3. **sandbox を割り当てる**: 役割に応じて `read-only` か `workspace-write` かを決める。
4. **approval-policy を決める**: 実行の自由度に応じて `untrusted` / `on-request` / `never` を設定する。
5. **Rulesを設定**: Sandbox外のコマンドが必要な場合、`.rules`ファイルで許可/禁止を定義しテストする。
6. **別セッションに固定**: 可能であれば、Agents SDKやApp Serverの機能を使って、エージェント（プロセス/スレッド）ごとにこれらの設定を固定する。

#### 質問（ユーザー）
- 「Agents SDK / app-server / CLIのコラボ（サブエージェント）のどれで組んでいるか？」への回答が必要。

**参照リンク（ユーザー提示）**
- [Security](https://developers.openai.com/codex/security/)
- [Command line options](https://developers.openai.com/codex/cli/reference/)
- [Use Codex with the Agents SDK](https://developers.openai.com/codex/guides/agents-sdk/)
- [Codex App Server](https://developers.openai.com/codex/app-server)
- [Rules](https://developers.openai.com/codex/rules/)

---

## 12. 提案/ドラフト（設定手段とフォルダ構成）
### 12.1 設定ファイル案
- `Agent_workspace/.system/agents.yaml`  
  役割/端末名/監視対象/受信フォルダの定義
- `Agent_workspace/.system/permissions.yaml`  
  役割ごとの read/write/append/delete/exec
- `Agent_workspace/.system/tools_registry.yaml`  
  共有ツール/専用ツールの可視化
- `Agent_workspace/.system/cache/manifest.yaml`  
  事前資料パックとキャッシュID管理
- `Agent_workspace/.system/prompt_flow/`  
  ワーク別プロンプトテンプレ
- `Agent_workspace/.system/thresholds.yaml`  
  Task_Management監視の変化量/時間閾値

### 12.2 フォルダ構成案（最小）
```
Agent_workspace/
  .system/
    agents.yaml
    permissions.yaml
    tools_registry.yaml
    thresholds.yaml
    watchers/
    cache/
    prompt_flow/
  Shared_Tools/
    shell/
    python/
  Task_Management/
  Agent_maneger/
    Clock_Inbox/
  進捗管理agent/
    進捗報告受付/
  .channels/
    community_a/
    community_b/
    community_c/
  <agent_name>/
    docs/
    Task_Inbox/
    tools/
    work/
```

### 12.3 監視割当案
- Agent_Manager: `Clock_Inbox` 監視
- 進捗管理: 進捗報告受付 + 対象ファイル更新
- Task_Management監視（非エージェント）: 変化量/時間で進捗報告受付へ報告
- 専門家: 自分の `Task_Inbox` のみ監視

### 12.4 下層→上層の意見回収案
- 進捗管理が定期サマリーを `.channels` に配布
- 専門家/設計が `.channels` から提案→`01_Proposals` 投入
- Multi_Agent_Architect が `Agent Workflow Queue` に差し込み要求

### 12.5 優先順位案
1. 共有ツール + 権限基盤
2. 監視デーモン分離（Clock/Progress/Task/Inbox）
3. 事前キャッシュ + プロンプトフロー
4. コミュニティ共有チャネル

---

## 13. 提案/ドラフト（ツール拡張の具体例）
- `read_task.sh` / `read_task.py`: タスク内容の読み出し
- `assign_task.sh`: Assignment追記と `02_Active` への移動
- `report_progress.sh`: 進捗報告受付への報告
- `clock_in.sh`: クロック受付への追加
- `safe_write.py`: 権限チェック付き書き込み
- 共有ツールと専用ツールを分離し、共有ツールはコピー運用

---

## 14. 提案/ドラフト（Driver改修の詳細）
- `run_file_orchestrator.py` をディレクトリ監視型に改造
- 監視対象: `Task_Management/01_Proposals`, `02_Active`
- 新規作成/移動検知で該当エージェントに通知
- ファイル内容を `>>> [INSTRUCTION: <path>]` として渡す案

---

## 15. 追加の質疑・補足（資料準拠）
- クロック受付は Agent_Manager 配下にある
- InboxWatcherはアシスタント提案（専門家のTask_Inbox監視用）
- codex-smokeは send_message.sh → ファイル書き込み → Driver配信の流れ
- Codex CLI キャッシュは未検証、codex-smoke側で検証したい
- 最小フローは「進捗管理のクロック判断」を挟む
- ワーク差し込みは例外ケースで、無限ループは避けるべき
- 権限制御の具体的仕組み/道具が分からず、考えを求めた

---

## 16. 未整備（要検証/未確定）
- Codex CLI キャッシュ機能の実効性
- クロック判断の具体的ルール
- 監視プロセスの起動/停止ポリシー
- 権限強制の具体手段（Codex CLI側機能が環境で使えるか）

---

## 17. 提案/ドラフト（権限制御の層別）
### レベル0: ツール層ガード（導入容易・強制力低）
- **仕組み**: すべてのファイル操作（書き込み、移動、削除）やコマンド実行を、専用のラッパーツール（例: `safe_write.py`, `safe_exec.sh`）経由で行うように運用ルール化する。
- **実装**: `permissions.yaml` に「誰が・どこを・どう操作できるか」を定義し、ツール実行時にこのファイルを参照して許可/拒否を判定する。
- **メリット**: OSやCodex自体の設定を変更せずに導入でき、既存のワークフローに組み込みやすい。
- **デメリット**: エージェント（またはその背後のLLM）がツールを使わずに直接コマンド（`rm`, `echo >`）を実行した場合は防げない。あくまで「行儀の良いエージェント」を前提としたガードレール。

### レベル1: OSユーザー分離（中強度・運用負荷中）
- **仕組み**: 各エージェント（または役割グループ）ごとに、OS（macOS/Linux）上のユーザーアカウントを作成する。
- **実装**:
  - `user_manager`, `user_symbol`, `user_dev` などのアカウントを作成。
  - プロジェクトディレクトリ内の各フォルダに対し、`chown` / `chmod` または ACL（Access Control List）を使用して、所有者と権限（rwx）を厳密に設定する。
  - CAO（Orchestrator）が各エージェントのtmuxセッションを起動する際、`sudo -u user_symbol ...` のように指定ユーザー権限でプロセスを立ち上げる。
- **メリット**: エージェントがOSの権限を越えてファイルを読み書きすることをシステムレベルで阻止できる。ツールを介さない直接操作も防げる。
- **デメリット**: ユーザー作成や権限管理の初期設定が複雑。開発者本人がファイルを触る際にも権限エラーが起きる可能性があり、運用に慣れが必要。

### レベル2: コンテナ/VM分離（最高強度・運用負荷高）
- **仕組み**: 各エージェントを独立した Docker コンテナや仮想マシン（VM）の中で実行する。
- **実装**:
  - エージェントごとに Dockerfile を用意し、必要なツールと依存関係のみをインストール。
  - ホスト（開発機）のプロジェクトディレクトリのうち、そのエージェントが編集すべきサブディレクトリだけを `docker run -v ...` でマウントする。
  - 読み取り専用で良い部分は `:ro` オプションでマウントする。
- **メリット**: ファイルシステムだけでなく、プロセス空間、ネットワーク、環境変数なども完全に隔離できる。エージェントが暴走してもホスト環境への影響を最小限に抑えられる。
- **デメリット**: コンテナごとのリソース消費（メモリ・CPU）が増える。Mac環境ではファイルマウントのパフォーマンスや、ホスト側ツールとの連携（クリップボード、通知など）に課題が出やすい。構築・維持コストが最も高い。

---

## 18. 進行上の合意点（資料準拠）
- **ファイル編集の方針**: 現段階では設計議論に集中し、実際のコードや設定ファイルの編集は行わない。
- **基本ループの定義**: 開発のメインサイクルは「**Active発行**（タスク割当）→ **タスク処理**（エージェント作業）→ **クロック**（完了報告・時間記録）→ **Active発行**」の繰り返しであると合意。
- **ワーク差し込みの位置づけ**: 進行中のフェーズやワークフローに対し、予定外のタスクを割り込ませる「ワーク差し込み」は、標準的なフローではなく**特殊ケース（例外処理）**として扱う。無限ループを防ぐための制御が必要。
