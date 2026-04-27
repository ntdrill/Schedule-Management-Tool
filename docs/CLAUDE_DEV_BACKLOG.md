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
- [x] docs/readme/07_進捗・履歴.md を現状に合わせて更新する。現行 sdk-migration ブランチの進捗・最近の Phase 6/Phase 7 完了クロック・半自動開発移植完了など、`Agent_workspace/Agent_maneger/クロック受付/` と `進捗管理agent/進捗報告受付/` の実ファイルを根拠として参照し、何が今最新かを 1 セクション追記する（既存セクションは温存、追記のみ） — 2026-04-27 20:11 JST commit:f082a85
- [x] docs/readme/03_バージョン別機能スコープ.md と docs/readme/04_開発ワークフロー.md の間で用語・フェーズ番号がズレていないかを照合し、ズレがあれば 04 側を 03 に合わせて修正する。ズレが無ければ PROGRESS にその旨だけ記録して done — 2026-04-27 20:25 JST commit:pending
- [ ] docs/readme/01_プロジェクト概要.md の「対象プラットフォーム」「主要機能」記述を、`ScheduleManagementTool/` 配下の Xcode プロジェクト実態（iPhone / Watch / Shared 構成）と突き合わせて齟齬があれば修正する

<!-- ↓↓ ここから ScheduleManagementTool/ v1 MVP 実装タスク。仕様の真正典は docs/readme/03_バージョン別機能スコープ.md。Xcode が無いためビルド検証はユーザーが手動で行う前提。1 tick 1 タスク、Swift コード変更は型・構文レベルで自己レビュー必須。 -->

- [ ] feat(Watch): `ScheduleManagementTool/WatchApp/Views/MainView.swift` の `selectedPresetId` が `@State` ローカル変数のため、アプリ再起動で期待状態の選択が失われる。`UserState` か アクティブな `MeasurementSession` に保存し、起動時に復元するよう修正。docs/readme/03 §B「期待状態・状態入力」を満たす最小実装。Shared/Models/ の既存フィールド（`UserState.expectedStateId` 等）を優先利用し、無ければモデル拡張は最小限で行う
- [ ] feat(iPhone): `ScheduleManagementTool/iPhoneApp/Views/DashboardView.swift` は現状ステータス表示のみで、docs/readme/03 §A「Watch/iOS共にメイン画面に大きなトグルボタンを配置」の iOS 側要件を満たしていない。Watch `MainView.startMeasurement` / `stopMeasurement` 相当のロジックを iPhone 側にも実装し、`measurementStatusCard` の上に大きなトグルボタンを追加する。SwiftData 経由で `MeasurementSession` を作成/終了する点は Watch と同じ作法に揃える
- [ ] feat(iPhone): `ScheduleManagementTool/iPhoneApp/Services/SwitchBotService.swift` の現状実装を読み、docs/readme/03 §D「客観データ: 室温・湿度（センサー連携）」を満たすための呼び出し動線が欠けていれば配線する。少なくとも測定モード ON 中に周期的に SwitchBot から温湿度を取得し `EnvironmentState` に保存する最小ループを iPhone 側に追加（タイマー間隔は 60 秒既定、定数は `Shared/AppConstants.swift` に置く）。API クレデンシャル等は `Info.plist` か環境変数前提で、ハードコードしない
