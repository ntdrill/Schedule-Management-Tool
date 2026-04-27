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
- [x] docs/readme/03_バージョン別機能スコープ.md と docs/readme/04_開発ワークフロー.md の間で用語・フェーズ番号がズレていないかを照合し、ズレがあれば 04 側を 03 に合わせて修正する。ズレが無ければ PROGRESS にその旨だけ記録して done — 2026-04-27 20:25 JST commit:022725c
- [x] docs/readme/01_プロジェクト概要.md の「対象プラットフォーム」「主要機能」記述を、`ScheduleManagementTool/` 配下の Xcode プロジェクト実態（iPhone / Watch / Shared 構成）と突き合わせて齟齬があれば修正する — 2026-04-27 20:38 JST commit:37d998e

<!-- ↓↓ ここから CI 基盤構築タスク。MacBook 2016 では Xcode が動かないため、GitHub Actions の macos-latest ランナーで xcodegen → xcodebuild を回す。public repo 化前提（無料で macOS 無制限）。-->

- [x] chore(repo): リポジトリ ルートに `.gitignore` を作成。Xcode 系（`*.xcodeproj/`, `*.xcworkspace/`, `xcuserdata/`, `DerivedData/`, `build/`, `*.xcuserstate`）、macOS（`.DS_Store`）、Swift Package Manager（`.swiftpm/`, `Packages/`, `Package.resolved` は残す）、Python venv（`.venv/`）、Node（`node_modules/`）、IDE（`.idea/`, `.vscode/`）、ローカルログ（`*.log`）、半自動開発のロック/ログ（`半自動開発/tool/*.lock`, `半自動開発/codex_observe/`, `半自動開発/スクリーンショット/`）を網羅。GitHub の Swift `.gitignore` テンプレートを参考に、本リポジトリ実体に合わせて整える — 2026-04-27 20:42 JST commit:bb99f19
- [x] chore(build): リポジトリルートに `project.yml`（XcodeGen 入力）を作成。targets は `iPhoneApp`（iOS 17+, SwiftUI, SwiftData, sources: `ScheduleManagementTool/iPhoneApp/` + `ScheduleManagementTool/Shared/`）、`WatchApp`（watchOS 10+, sources: `ScheduleManagementTool/WatchApp/` + `ScheduleManagementTool/Shared/`）の 2 つ。bundle id は `com.ntdrill.schedulemanagementtool` / `.watchkitapp`、deployment target は iOS 17.0 / watchOS 10.0、Swift version 5.9、`Info.plist` は XcodeGen の自動生成に任せる。WatchApp は iPhoneApp の embed target として `dependencies` で連結。XcodeGen の YAML 仕様は https://github.com/yonaskolb/XcodeGen/blob/master/Docs/ProjectSpec.md を参照 — 2026-04-27 20:55 JST commit:3e3438a
- [x] chore(ci): `.github/workflows/ios-build.yml` を新規作成。トリガーは `push`（ブランチ全部）と `pull_request`。job は `runs-on: macos-latest` 1 本のみ。手順は (a) checkout (b) `brew install xcodegen` (c) `xcodegen generate` (d) `xcodebuild -project ScheduleManagementTool.xcodeproj -scheme iPhoneApp -destination 'generic/platform=iOS' build` (e) Watch 用にもう 1 ステップ `xcodebuild ... -scheme WatchApp -destination 'generic/platform=watchOS' build`。失敗ログがそのまま Actions UI に出るよう `set -o pipefail` 等は付けず素直に。キャッシュは導入せず最初は素朴に — 2026-04-27 21:07 JST commit:0cd2b5a
- [x] chore(docs): `docs/readme/06_ディレクトリ構造ガイド.md` の末尾に「ビルド方法」セクションを 1 つ追加。XcodeGen が必須・`brew install xcodegen` → `xcodegen generate` → `open ScheduleManagementTool.xcodeproj` の手順を記述。MacBook 2016 / macOS 12 環境ではローカルビルド不可で GitHub Actions に依存する旨も明記 — 2026-04-27 21:19 JST commit:d2e50e0

<!-- ↓↓ ここから ScheduleManagementTool/ v1 MVP 実装タスク。仕様の真正典は docs/readme/03_バージョン別機能スコープ.md。CI が緑になってから着手。1 tick 1 タスク、Swift コード変更は型・構文レベルで自己レビュー必須。 -->

- [x] feat(Watch): `ScheduleManagementTool/WatchApp/Views/MainView.swift` の `selectedPresetId` が `@State` ローカル変数のため、アプリ再起動で期待状態の選択が失われる。`UserState` か アクティブな `MeasurementSession` に保存し、起動時に復元するよう修正。docs/readme/03 §B「期待状態・状態入力」を満たす最小実装。Shared/Models/ の既存フィールド（`UserState.expectedStateId` 等）を優先利用し、無ければモデル拡張は最小限で行う — 2026-04-27 21:32 JST commit:005e13d
- [x] feat(iPhone): `ScheduleManagementTool/iPhoneApp/Views/DashboardView.swift` は現状ステータス表示のみで、docs/readme/03 §A「Watch/iOS共にメイン画面に大きなトグルボタンを配置」の iOS 側要件を満たしていない。Watch `MainView.startMeasurement` / `stopMeasurement` 相当のロジックを iPhone 側にも実装し、`measurementStatusCard` の上に大きなトグルボタンを追加する。SwiftData 経由で `MeasurementSession` を作成/終了する点は Watch と同じ作法に揃える — 2026-04-27 21:45 JST commit:e526dcb
- [x] feat(iPhone): `ScheduleManagementTool/iPhoneApp/Services/SwitchBotService.swift` の現状実装を読み、docs/readme/03 §D「客観データ: 室温・湿度（センサー連携）」を満たすための呼び出し動線が欠けていれば配線する。少なくとも測定モード ON 中に周期的に SwitchBot から温湿度を取得し `EnvironmentState` に保存する最小ループを iPhone 側に追加（タイマー間隔は 60 秒既定、定数は `Shared/AppConstants.swift` に置く）。API クレデンシャル等は `Info.plist` か環境変数前提で、ハードコードしない — 2026-04-27 22:00 JST commit:0b3a91a

<!-- ↓↓ レンタル MacBook Pro 2020 到着までに価値を出すタスク -->

- [x] test(Shared): `ScheduleManagementTool/Tests/SharedTests/` を新設し、Shared/Models/ と Shared/Types/ の純ロジック（`@Model` のデフォルト値・Enum raw 値整合性・`Timestamped` プロトコル準拠・`StateSnapshotConvertible` の往復変換等）を XCTest で覆う。狙いは「CI で意味のある検証ができる範囲を広げる」。SwiftData 永続化を要するテストは避け、純粋な Swift 単体テストに絞る。`project.yml` に `Tests` ターゲット（platform: iOS）を追加し、`.github/workflows/ios-build.yml` に `xcodebuild test -scheme Tests -destination 'platform=iOS Simulator,name=iPhone 15'` ステップを追加する。テスト本体は最小 5 ケース程度から — 2026-04-27 22:14 JST commit:b2df903
- [x] docs(handoff): `docs/RENTAL_MAC_ONBOARDING.md` を新規作成。レンタル MacBook Pro 2020 が到着した日に 30 分で動作確認まで持っていける手順書。内容: (1) Xcode 16+ インストール（App Store） (2) `git clone` → `brew install xcodegen` → `xcodegen generate` → `open ScheduleManagementTool.xcodeproj` (3) iPhone Simulator + Apple Watch Simulator のペアリング設定確認 (4) ビルド & ラン（iPhone と Watch 両方） (5) 実機接続する場合の手順（Apple ID で署名、Capabilities で HealthKit を有効化、実機を信頼、Personal Team で開発者証明書発行） (6) 既知の制約（SwitchBot 実 API key 未設定なら温湿度は表示されない 等）。チェックリスト形式で、各項目に「期待結果」を 1 行ずつ書く — 2026-04-27 22:28 JST commit:c88c317

<!-- ↓↓ CI で検証範囲を最大化するタスク群（GitHub Actions macOS runner で実機なしに到達可能な最大）-->

- [x] test(Watch): `ScheduleManagementTool/Tests/WatchAppTests/` を新設。`MeasurementService` の状態遷移（start/stop で isActive が切り替わる、`HealthKitService` の `@Published` プロパティを直接書き換えて `updateUserState` が呼ばれること）を XCTest で覆う。Real HealthKit 呼出は避け、`HealthKitService` をモック可能なプロトコル抽出 → テストで偽実装を注入。`project.yml` に `WatchAppTests` ターゲット（platform: watchOS, hostTarget: WatchApp）を追加。CI workflow に `xcodebuild test -scheme WatchAppTests -destination 'platform=watchOS Simulator,name=Apple Watch Series 9 (45mm)'` ステップを追加。watchOS Simulator は paired iPhone Simulator が必要なので Series 9 + iPhone 15 のペアを `xcrun simctl create` でセットアップするステップも前置 — 2026-04-27 22:51 JST commit:ef2de06
- [x] test(iPhone-UI): `ScheduleManagementTool/Tests/iPhoneAppUITests/` を新設し最小スモーク 1 件: アプリ起動 → 「ダッシュボード」タブが表示される → タブ「ログ」「設定」が存在する → 「ログ」タップで遷移できる、を XCUITest で書く。`project.yml` に `iPhoneAppUITests` ターゲット（type: bundle.ui-testing, hostTarget: iPhoneApp）を追加。CI workflow に `xcodebuild test -scheme iPhoneAppUITests -destination 'platform=iOS Simulator,name=iPhone 15'` ステップを追加 — 2026-04-27 23:06 JST commit:804a24b
- [x] chore(quality): SwiftLint をプロジェクトに導入。リポジトリルートに `.swiftlint.yml`（`disabled_rules: [trailing_whitespace, line_length]` で出発、`included: [ScheduleManagementTool]`、`excluded: [Tests, .build]`）。`.github/workflows/ios-build.yml` の build ジョブの先頭に `brew install swiftlint && swiftlint --strict` ステップを追加。最初の実行で出る既存違反は **タスク内では直さず**、`disabled_rules` か `excluded` で抑制し、別タスクで段階的に直す方針を `.swiftlint.yml` のコメントに明記 — 2026-04-27 23:18 JST commit:62c8e9d
- [x] chore(coverage): CI workflow の test ステップに `-enableCodeCoverage YES -resultBundlePath TestResults.xcresult` を付与。後続ステップで `xcrun xccov view --report --json TestResults.xcresult > coverage.json` を生成し、`actions/upload-artifact` で `TestResults.xcresult` と `coverage.json` を CI 成果物として残す。閾値判定は導入しない（最初は可視化のみ） — 2026-04-27 23:31 JST commit:c047220
- [x] chore(ci-hardening): `.github/workflows/ios-build.yml` を仕上げる。(a) `concurrency` で同一ブランチ重複ジョブをキャンセル (b) `xcodebuild` の前に `xcrun simctl list runtimes` でランナー上の SDK バージョンを stdout に出して切り分けやすく (c) ジョブ失敗時に `*.xcresult` を必ずアップロード (d) PR コメント自動投稿 (`actions/github-script` で coverage 1 行サマリ) (e) badge URL を README に貼れるよう workflow 名を `iOS Build & Test` に整える — 2026-04-27 23:44 JST commit:7ab44ac

<!-- ↓↓ CI 緑化（commit ed30b1e で達成）後の継続タスク。/loop ベース cron で駆動中。 -->

- [x] docs(handoff): `半自動開発/CLAUDE_SESSION_HANDOFF.md` を最新化。com.user.claude-dev LaunchAgent が 2026-04-27 23:55 に自己 unload（全タスク消化）したこと、その後 `/loop 7m loop_instruction.txt` ベースの cron 駆動に切り替えたこと、CI 緑化までの修正履歴（SwiftLint 緩和 → 不足 Swift ファイル commit → 署名無効化 → iPhone 15→16 → TEST_HOST 補正 → host scheme + only-testing） commit `ed30b1e` 緑化までを「7. 直近の出来事タイムライン」に追記。「2 つの LaunchAgent」表は claude-dev も unload 済として更新する — 2026-04-28 00:50 JST commit:405db61
- [x] chore(quality): SwiftLint の `identifier_name` を再有効化（`min_length: { warning: 2, error: 1 }`, `max_length: { warning: 50, error: 80 }` 程度に緩和）し、`HealthKitService.swift` の `let ms = ...` を `let milliseconds = ...` にリネーム。`.swiftlint.yml` の disabled_rules から `identifier_name` を外す。CI が緑のまま維持されることを確認（push 後 `/loop` cron が CI 結果を確認する） — 2026-04-28 01:30 JST commit:(本 push)
- [ ] docs(readme): リポジトリルートの README（または無ければ `docs/readme/00_README索引.md`）に `iOS Build & Test` workflow の status badge を追加。マークダウン形式で `https://github.com/ntdrill/Schedule-Management-Tool/actions/workflows/ios-build.yml/badge.svg?branch=sdk-migration` を埋め込み、Actions 一覧へのリンクも併記する
