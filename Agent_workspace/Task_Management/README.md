# Task Management Center

プロジェクトの実装タスクを管理するディレクトリです。
各エージェントはここを通じて自律的にタスクを提案・実行します。

## ディレクトリ構成

### 1. 01_Proposals (提案)
各エージェントが自律的に発見した課題や必要な実装を提案する場所。
- **作成ルール**:
  - 誰でも作成可能。
  - ファイル名: `proposal_by_[AgentName]_[Subject].txt`
  - 内容: 現状の課題、提案内容、期待される効果。

### 2. 02_Active (進行中)
Agent_Managerによって承認され、現在実行中のタスク。
- **運用ルール**:
  - Agent_Managerが `01_Proposals` から移動させる。
  - ファイル内に `## Assignment` セクションを追記し、担当者(Assignee)と期限などを明記する。
  - 担当者は進捗をこのファイルに追記する。

### 3. 03_Completed (完了)
完了したタスクのアーカイブ。
- **完了ルール**:
  - 実装とテストが終了したら成果物をまとめる。
  - **進捗管理agentへの報告を行う**（報告ファイルを提出）。
  - ファイルを `03_Completed` へ移動させる。
  - 完了報告（成果物へのリンク、進捗報告ファイル名など）をファイル末尾に追記する。

## 運用フロー
Propose -> (Manager Review) -> Active -> (Execute) -> **Report to Progress Agent** -> Complete
