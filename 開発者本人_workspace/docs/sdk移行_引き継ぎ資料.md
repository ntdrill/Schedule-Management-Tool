# SDK移行に関する引き継ぎ資料

**To**: Multi_Agent_Architect
**From**: Implementation Agent Manager (Context Holder)
**Date**: 2026-01-30

本資料は、現在のファイルシステムベースのエージェント運用および `codex-smoke` (CAO + Codex CLI) の検証結果を踏まえ、**OpenAI SDK ベースの新しい実装システム**へ移行するための設計・運用方針をまとめたものである。

---

## 1. 移行の背景と目的

### 1.1 背景
これまで「実装システム（エージェントが開発を行う基盤）」として、以下の2つのアプローチが検証されてきた。
1.  **ファイルシステムベース運用**: `Task_Management` フォルダ等を介した手動に近い運用。柔軟だが、監視や自動化がスクリプト頼みで分散している。
2.  **codex-smoke (CAO + Codex CLI)**: `tmux` セッションとログファイルを介した自律運用。自律性は高いが、監視の粒度やツールの拡張性、権限管理の統合に課題があった。

### 1.2 目的
これら既存の知見を統合し、**OpenAI SDK** を用いて以下の要件を満たす堅牢な実装システムを構築する。

*   **監視の分離と強化**: エージェントマネージャー、進捗管理、各専門家が、それぞれの責務に応じた対象（Clock Inbox, Progress Report, Task Inbox）のみを監視する構造を作る。
*   **ボトムアップ提案の実現**: 下層エージェントからの意見吸い上げ（Proposal）と、それに基づくワークフローへの動的な割り込み（例外処理）をシステム化する。
*   **権限の明確な分離**: エージェントごとに独立したセッション（プロセス/スレッド）を持ち、`sandbox` や `approval-policy` を固定することで、役割に応じた権限（Read-only, Workspace-write等）を強制する。
*   **コストとコンテキストの最適化**: 「事前資料（キャッシュ）」と「プロンプトフロー（動的注入）」を明確に分離し、運用コストを最適化する。

---

## 2. 移行ステータス

*   **判定**: **Ready for Implementation**（実装開始可能）
*   **現状**: アーキテクチャ設計、要件定義、既存資産の棚卸しは完了している。
*   **次のステップ**: `sdk_runtime` ディレクトリの構築と、OrchestratorおよびWatcherの実装。

---

## 3. 関連資料

本資料と合わせて、以下の整理済み資料を参照すること。

1.  **`開発者本人_workspace/docs/sdkでりようできるファイル.txt`**
    *   既存プロジェクト内のファイルについて、「そのまま流用」「編集して利用」「新規作成」の分類をまとめたもの。
2.  **`開発者本人_workspace/docs/sdkに必要な情報.txt`**
    *   プロジェクト固有の業務ルール（タスク運用、クロック定義、シンボル管理など）や、SDK実装時に決定すべき未整備事項（閾値設定など）を網羅したもの。

---

## 4. SDK実行時の運用フロー (Operational Flow)

`sdk_runtime` 環境におけるエージェントとシステムの連携フローは以下の通り定義する。

### Phase 1: 起動と監視
1.  **Bootstrap**: `sdk_runtime/orchestrator/` が起動し、設定ファイル（`agents.yaml`, `permissions.yaml`）をロード。
2.  **Watcher起動**: 役割別の監視プロセスが常駐（または定期起動）を開始。
    *   `TaskFolderWatcher`: `Agent_workspace/Task_Management/` を監視（全体俯瞰）
    *   `ProgressWatcher`: `進捗管理agent/進捗報告受付/` を監視（進捗検知）
    *   `ClockWatcher`: `Agent_workspace/Agent_maneger/クロック受付/` を監視（クロック検知）
    *   `InboxWatcher`: 各 `Agent_workspace/<agent>/Task_Inbox/` を監視（個別指令）

### Phase 2: タスク検知と配布
3.  **Event Dispatch**:
    *   Watcherが変化を検知すると Orchestrator へ通知。
    *   Orchestrator は内容を解析し、適切なエージェントの `Task_Inbox` へタスク（または通知）を配布。
    *   必要なエージェントプロセス（またはスレッド）のみを起動/再開。

### Phase 3: 実行と進捗
4.  **Agent Execution**:
    *   エージェントは `Task_Inbox` の指示に従い作業を開始。
    *   成果物は `Task_Management` 内の対象ファイルへ直接反映（権限範囲内で）。
    *   進捗状況は `進捗管理agent/進捗報告受付/` へレポートとして提出（**必須**）。

### Phase 4: クロックと判定 (Closed Loop)
5.  **Clock Cycle**:
    *   `ProgressWatcher` がレポート提出を検知し、進捗管理エージェントへ通知。
    *   進捗管理エージェントが内容を確認し、作業区切り（クロック）と判断すれば `Agent_workspace/Agent_maneger/クロック受付/` へ事実報告を作成。
    *   `ClockWatcher` がこれを検知し、Agent_Manager へ通知 → Agent_Manager が次の `Active` タスク発行を判断。

### Phase 5: 完了と共有
6.  **Completion**:
    *   タスク完了時、担当エージェントは完了報告を行い、`03_Completed` へ移動。
    *   Orchestrator（または定期バッチ）が `Shared_Tools` や `.channels` を介してコミュニティ間へ情報を同期。

---

## 5. 既存スクリプトの統合戦略

`Agent_workspace/Agent_maneger/scripts/` 等に存在するPythonスクリプト群は、以下の戦略でSDK環境へ統合する。

### A. Watcher/Orchestrator に組み込むもの（常駐・自動化）
ツールとして呼ぶのではなく、システム機能（ロジック）として移植する。
*   `task_monitor.py` → `TaskFolderWatcher` の監視ロジックへ
*   `clock_diff.py` → `ClockWatcher` の検知ロジックへ
*   `clock_digest.py` → `ClockWatcher` 検知後の要約処理へ
*   `daily_check.py` → Orchestrator の定期タスク（Cron的実行）へ

### B. エージェント用ツールとしてラップするもの（On-Demand）
エージェントが必要なタイミングで呼び出す `sdk_runtime/tools/` として整備する。
*   `task_mover.py` → `assign_task` / `complete_task` ツールへ
*   `auto_proposal_processor.py` → `read_proposal` 系ツールへ
*   `weekly_summary_generator.py` → 進捗管理エージェント専用ツールへ
*   `unresolved_to_proposal.py` → Agent_Manager専用ツールへ
*   `update_agent_list.py` → Agent_Manager専用ツールへ

### C. 外部連携・データ同期（Batch/Admin）
特定のタイミングで実行する独立スクリプトとして維持、または管理者用ツールとする。
*   `migrate_symbols_to_supabase.py` 等のDB系 → `Symbol_Agent` 専用ツール、または管理者が手動実行する管理コマンド。
