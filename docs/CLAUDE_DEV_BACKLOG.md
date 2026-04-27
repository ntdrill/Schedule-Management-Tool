# Claude 自動開発 バックログ

このファイルは launchd から 10 分ごとに走る `claude -p` ワーカーが読むタスクリストです。
ユーザーがタスクを追加し、Claude が **先頭の未完了 (- [ ]) タスクを 1 件だけ** 進めて完了 (- [x]) に書き換えます。

## 運用ルール

- **作業対象**: `/Users/numaoryuutarou/cursor/Schedule-Management-Tool/` 配下のリポジトリ全体（コード・ドキュメント・テスト・設定 すべて）
- **触らない**: 自分自身の運用基盤（`半自動開発/tool/claude_dev_*`, `com.user.claude-dev.plist`）、旧運用基盤（`半自動開発/tool/cron_tick.*`, `com.user.halfauto-scheduler.plist`）、`.venv/`, `node_modules/`, `.git/`, `~/Library/LaunchAgents/`
- **粒度**: 1 タスクは 9 分以内に収まるサイズに分割。大きすぎるタスクはここで小タスクに割って書く
- **commit**: 各タスク完了時に Claude が自動で `git commit`（明示パス指定、`-A` は使わない）。push はしない（ユーザー手動）。`.env` 等の secret が working tree にある場合は commit せず blocked に
- **完了印**: `- [x] <task> — <YYYY-MM-DD HH:MM JST> commit:<short-sha>` の形式で書き換え
- **詰まったら**: `- [!] <task> — blocked: <理由>` に変更して次へ進まず終了。次回 tick で人間が判断

## タスク

<!-- タスクは「- [ ] <内容>」の形で1行ずつ追記してください。先頭から順に処理されます。 -->

- [x] docs/readme/06_ディレクトリ構造ガイド.md を、現在のリポジトリ実態（`半自動開発/`, `Agent_workspace/`, `ScheduleManagementTool/` 等）と突き合わせて更新する。実態と差分があれば全箇所を直す — 2026-04-27 19:35 JST commit:a08114a
- [x] docs/readme/07_進捗・履歴.md を現状に合わせて更新する。現行 sdk-migration ブランチの進捗・最近の Phase 6/Phase 7 完了クロック・半自動開発移植完了など、`Agent_workspace/Agent_maneger/クロック受付/` と `進捗管理agent/進捗報告受付/` の実ファイルを根拠として参照し、何が今最新かを 1 セクション追記する（既存セクションは温存、追記のみ） — 2026-04-27 20:11 JST commit:後で更新
- [ ] docs/readme/03_バージョン別機能スコープ.md と docs/readme/04_開発ワークフロー.md の間で用語・フェーズ番号がズレていないかを照合し、ズレがあれば 04 側を 03 に合わせて修正する。ズレが無ければ PROGRESS にその旨だけ記録して done
- [ ] docs/readme/01_プロジェクト概要.md の「対象プラットフォーム」「主要機能」記述を、`ScheduleManagementTool/` 配下の Xcode プロジェクト実態（iPhone / Watch / Shared 構成）と突き合わせて齟齬があれば修正する
