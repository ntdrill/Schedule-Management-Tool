# レンタル MacBook Pro 2020 オンボーディング手順書

レンタル機（MacBook Pro 2020 / Xcode 16+ が動作する macOS 14+ 想定）が到着した日に **30 分で iPhone Simulator と Apple Watch Simulator の両方でアプリが起動するところまで** 到達するためのチェックリスト。

各項目には「期待結果」を 1 行併記してある。期待結果が得られなかった時点で立ち止まり、原因を切り分けてから次へ進むこと。

---

## 1. Xcode 16+ インストール

- [ ] App Store を開き「Xcode」を検索 → インストール（10〜20 GB のダウンロードが入るので Wi-Fi 接続必須）。
  - 期待結果: 「Open」ボタンが表示される（完了サイン）。
- [ ] Xcode を初回起動し、ライセンス同意 + 追加コンポーネントのインストールを完了させる。
  - 期待結果: Welcome ウィンドウが表示される。
- [ ] ターミナルで `xcode-select --install` を実行（既にインストール済みなら「already installed」エラーが出るが問題なし）。
  - 期待結果: Command Line Tools が利用可能。
- [ ] `xcodebuild -version` でバージョン確認。
  - 期待結果: `Xcode 16.x` 以降が表示される。Xcode 15 以下なら App Store から最新版に更新。

## 2. リポジトリ取得 + プロジェクト生成

本リポジトリは XcodeGen による project 生成方式を採用しており、`*.xcodeproj/` は git 管理されていない。`project.yml` から都度生成する。

- [ ] Homebrew が無い場合はインストール: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  - 期待結果: `brew --version` が表示される。
- [ ] 任意の作業ディレクトリに `git clone` する（HTTPS でも SSH でも可）。
  - 期待結果: `Schedule-Management-Tool/` ディレクトリが生成される。
- [ ] `cd Schedule-Management-Tool` でリポジトリルートに移動。
- [ ] XcodeGen を導入: `brew install xcodegen`
  - 期待結果: `xcodegen --version` が表示される。
- [ ] プロジェクト生成: `xcodegen generate`
  - 期待結果: リポジトリルートに `ScheduleManagementTool.xcodeproj/` が生成される。warning は出るが error なく完了。
- [ ] Xcode で開く: `open ScheduleManagementTool.xcodeproj`
  - 期待結果: Xcode が起動し、左ペインに `iPhoneApp` / `WatchApp` / `SharedTests` の 3 ターゲットが見える。

`project.yml` を変更したら必ず `xcodegen generate` を再実行する。生成された `*.xcodeproj/` は `.gitignore` 対象なので git にコミットしないこと。

## 3. iPhone Simulator + Apple Watch Simulator のペアリング設定確認

`WatchApp` は `iPhoneApp` に embed される構成のため、watchOS Simulator は paired iPhone Simulator が必要。

- [ ] Xcode メニュー → Window → Devices and Simulators → Simulators タブを開く。
  - 期待結果: 既存の iPhone / Apple Watch Simulator 一覧が表示される。
- [ ] iPhone 15（または 17.0+ runtime のもの）と Apple Watch Series 9 (45mm)（10.0+ runtime）が並んでいることを確認。無ければ「+」で追加。
  - 期待結果: 両方の Simulator がリストにある。
- [ ] iPhone Simulator を選択し、右ペインの「Paired Apple Watch」項目に Apple Watch Series 9 が紐付いていることを確認。未ペアリングなら「Pair Apple Watch」で関連付け。
  - 期待結果: ペアリング済みステータス。
- [ ] ターミナルで `xcrun simctl list pairs` を実行。
  - 期待結果: 該当 iPhone と Apple Watch のペアが 1 行表示される（`(active, ...)`）。

## 4. ビルド & ラン（iPhone / Watch 両方）

- [ ] Xcode 上部の Scheme セレクタで `iPhoneApp` を選び、Destination に「iPhone 15」を指定。
- [ ] ⌘R で Run。
  - 期待結果: ビルドが緑（数分かかる初回）→ iPhone Simulator が起動 → ScheduleManagementTool のダッシュボード画面が表示される。
- [ ] ペアリングされた Apple Watch Simulator も自動で起動し、Watch 側の `ScheduleManagementTool` アプリも自動配信される。Watch Simulator のホーム画面でアプリアイコンを探してタップ。
  - 期待結果: Watch 側でメイン画面（測定モード ON/OFF トグル + 期待状態プリセット）が表示される。
- [ ] iPhone 側で「ダッシュボード」「ログ」「設定」の 3 タブが見えることを確認。
  - 期待結果: タブ切り替えで遷移できる。
- [ ] 大きなトグルボタンを押して測定モード ON。
  - 期待結果: ボタンが赤系（停止）に切り替わり、ステータスカードが「測定中」表記に変わる。

## 5. 実機接続する場合の手順（任意）

レンタル機のため Apple Developer Program 加入は通常無し。Personal Team（無料 Apple ID 署名）で 7 日間有効の開発者証明書を発行して実機にインストールする運用になる。

- [ ] Xcode → Settings → Accounts に Apple ID を追加（個人 Apple ID で OK）。
  - 期待結果: Account 一覧に Apple ID が表示され、Team 欄に「(Personal Team)」が見える。
- [ ] iPhone をライトニング/USB-C ケーブルで Mac に接続し、デバイス側で「このコンピュータを信頼」を選択。
  - 期待結果: Xcode の Devices and Simulators の「Devices」タブに iPhone が「Connected」として現れる。
- [ ] Xcode の Project ナビゲータで `iPhoneApp` ターゲットを選択 → Signing & Capabilities タブを開く。
  - 「Automatically manage signing」を有効化、Team を Personal Team に設定。
  - Bundle Identifier `com.ntdrill.schedulemanagementtool` がチームで未使用ならそのまま、衝突するなら末尾に個人タグを追記して回避。
  - 期待結果: 「Signing Certificate: Apple Development」が緑表示される。
- [ ] 同タブで「+ Capability」→ 「HealthKit」を追加（Watch 側は実機で心拍 / HRV を読むため必須）。
  - 期待結果: HealthKit の項目が Capabilities リストに加わる。
- [ ] WatchApp ターゲットでも同様に Team / Capabilities (HealthKit) を設定。Bundle Identifier は `com.ntdrill.schedulemanagementtool.watchkitapp`。
  - 期待結果: WatchApp 側も Signing Certificate が緑。
- [ ] iPhone で「設定 → 一般 → VPN とデバイス管理」で開発者証明書を「信頼」する（初回のみ）。
  - 期待結果: アプリが起動可能になる。
- [ ] Destination を実機 iPhone に切り替え ⌘R。
  - 期待結果: 実機にインストールされ、ペアリング済み Apple Watch にも Watch アプリが配信される。

実機での HealthKit 動作確認は、Watch アプリ起動 → HealthKit 認可ダイアログ → 心拍数 / HRV の読み取り許可 → 測定モード ON で `latestHeartRate` が更新されることを確認する。

## 6. 既知の制約

実機・Simulator 双方で発生しうる現状の制約：

- **SwitchBot 実 API key 未設定なら温湿度は表示されない**: iPhone 側の「設定」タブで `switchBotToken` / `switchBotDeviceId` を入力していない場合、ダッシュボードの environmentCard は `--` のまま。SwitchBot Cloud API のトークンとデバイス ID を別途取得して設定すること（`@AppStorage` に保存される）。
- **Simulator は HealthKit データを返さない**: Watch Simulator では `HKAnchoredObjectQuery` が空配列を返すため `latestHeartRate` / `latestHRV` は更新されない。実機での確認が必須。
- **Personal Team の証明書は 7 日で失効**: 1 週間ごとに Xcode から再ビルド & 再インストールが必要。プロビジョニング切れで実機側ではアプリ起動しなくなる。
- **WatchApp は iPhoneApp に embed される単独配信不可構成**: Watch 単独で App Store / TestFlight 配信はできず、必ず iPhone 経由で配信。Independent Watch App には現状していない。
- **macOS 12 以前の開発機ではローカルビルド不可**: 既存の MacBook 2016（macOS 12）では Xcode 16 が動かないため、ローカルでは `xcodebuild` を打てず、コード変更後は GitHub Actions（`.github/workflows/ios-build.yml`）の緑/赤を見て判断するフロー。レンタル機が手元にある間は、レンタル機を「ローカル CI 兼実機検証用」に使うのが効率的。
- **`SharedTests` のみ CI で実行されている**: `WatchAppTests` / `iPhoneAppUITests` はまだ `project.yml` に追加されておらず、ローカル / CI どちらでも走らない（backlog で順次追加予定）。

---

## 困ったときの確認順序

1. `xcodegen generate` を再実行したか → `project.yml` 編集後は必須。
2. `*.xcodeproj/` を一度削除して `xcodegen generate` をやり直す → 古い参照が残っているケースに有効。
3. Xcode の Product → Clean Build Folder（⇧⌘K）→ Run。
4. Simulator がフリーズしたら Device → Erase All Content and Settings。
5. `xcrun simctl list pairs` でペアリング状態確認。崩れていたら `xcrun simctl pair` で再構築。
6. それでも解決しない場合は GitHub Actions の最新 `iOS Build` ジョブが緑かを確認。緑ならローカル環境固有の問題、赤なら共通のコード破損。
