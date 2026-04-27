# Schedule-Management-Tool

[![iOS Build & Test](https://github.com/ntdrill/Schedule-Management-Tool/actions/workflows/ios-build.yml/badge.svg?branch=sdk-migration)](https://github.com/ntdrill/Schedule-Management-Tool/actions/workflows/ios-build.yml)

iOS / watchOS 向けの「測定と介入の記録」に特化したロガーアプリ。未来のスケジューリングは行わず、「今」の状態測定と「今」の対処行動の記録・評価に集中する v1 MVP を開発中。

## ドキュメント

仕様の真正典は `docs/readme/` 配下です。読む順番:

| # | 内容 |
|---|---|
| [01_プロジェクト概要](docs/readme/01_プロジェクト概要.md) | プロダクトコンセプト、技術スタック、対象 OS |
| [02_開発体制・エージェント構成](docs/readme/02_開発体制・エージェント構成.md) | 自動開発エージェントの責務分担 |
| [03_バージョン別機能スコープ](docs/readme/03_バージョン別機能スコープ.md) | v1 MVP / v2 / v3 の機能境界 |
| [04_開発ワークフロー](docs/readme/04_開発ワークフロー.md) | Agent Workflow Phase と Loop の運用 |
| [05_ドメイン知識・理論基盤](docs/readme/05_ドメイン知識・理論基盤.md) | 対象領域の前提知識 |
| [06_ディレクトリ構造ガイド](docs/readme/06_ディレクトリ構造ガイド.md) | リポジトリ構成・ビルド方法 |
| [07_進捗・履歴](docs/readme/07_進捗・履歴.md) | 直近の実装スナップショット |

## ビルド

ローカルビルドは Xcode 15+ / macOS 13+ 必須（SwiftData が iOS 17+ を要求）。実機検証はレンタル MacBook Pro 2020 到着後を予定。詳細: [docs/RENTAL_MAC_ONBOARDING.md](docs/RENTAL_MAC_ONBOARDING.md)。

```bash
brew install xcodegen
xcodegen generate
open ScheduleManagementTool.xcodeproj
```

それまでは GitHub Actions の `iOS Build & Test` workflow（上記 badge）が SwiftLint・iPhone/Watch ビルド・SharedTests・WatchAppTests・iPhoneAppUITests・カバレッジを毎 push で自動検証する。

## ブランチ

現在の作業ブランチは `sdk-migration`。`main` への取り込みは v1 MVP の主要機能が安定してから。
