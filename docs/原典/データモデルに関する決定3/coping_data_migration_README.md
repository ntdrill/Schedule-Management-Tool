# 対処行動・場面データのデータベース登録

## 概要

開発者の実体験に基づく対処行動（78項目）と対処が必要な場面（221項目）をSupabaseデータベースに登録するためのスクリプトです。

## テーブル構造

### coping_actions テーブル
- `id` (SERIAL PRIMARY KEY)
- `name` (TEXT NOT NULL UNIQUE) - 対処行動の名前
- `description` (TEXT) - 詳細説明
- `category` (TEXT) - 分類（measurement, physical, nutrition, psychological, audio, tool, other等）
- `effectiveness_rating` (INTEGER) - 効果評価（1-5）
- `ease_of_use_rating` (INTEGER) - 手軽さ評価（1-5）
- `recommendation_rating` (INTEGER) - おすすめ度（1-5）
- `is_active` (BOOLEAN DEFAULT TRUE)
- `created_at` (TIMESTAMPTZ DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ DEFAULT NOW())

### coping_scenarios テーブル
- `id` (SERIAL PRIMARY KEY)
- `name` (TEXT NOT NULL UNIQUE) - 場面の名前
- `description` (TEXT) - 詳細説明
- `category` (TEXT) - 分類（physical, mental, cognitive, behavioral等）
- `severity_level` (TEXT) - 軽度/中度/重度（mild/moderate/severe）
- `is_active` (BOOLEAN DEFAULT TRUE)
- `created_at` (TIMESTAMPTZ DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ DEFAULT NOW())

## データファイル

### data/coping_actions.txt
フォーマット: `name|category|effectiveness|ease_of_use|recommendation|description`

例:
```
SpO2測定|measurement|4|3|3|動けない感覚を数値で把握できる測定方法
太極拳|physical|5|4|2|時間のサンプリング間隔を短くする効果がある
```

### data/coping_scenarios.txt
フォーマット: `name|category|severity_level|description`

例:
```
体重(筋肉量)の減少|physical|moderate|高強度運動が少ない期間が3ヶ月以上続く状態
過集中・覚醒|mental|mild|タスク遂行中に脈拍上昇など興奮の症状が現れる状態
```

## 実行方法

1. Supabase接続情報の確認
   - `Agent_workspace/symbol_agent/key/supabase_1.txt` に接続情報があることを確認

2. テーブルの作成確認
   - Supabase管理画面で `coping_actions` と `coping_scenarios` テーブルが作成されていることを確認

3. スクリプトの実行
   ```bash
   python migrate_coping_data_to_supabase.py
   ```

4. 実行結果の確認
   - 各テーブルへの登録件数が表示されます
   - エラーが発生した場合は、エラーメッセージを確認してください

## 注意事項

- `name` フィールドがUNIQUE制約のため、同名のレコードは更新されます（upsert）
- データファイルのフォーマットが正しいことを確認してください
- `#` で始まる行はコメントとして無視されます
- 評価値が数値でない場合は `NULL` が設定されます

## トラブルシューティング

### テーブルが存在しないエラー
- Supabase管理画面でテーブルが作成されているか確認してください
- SQLエディタでテーブル作成SQLを実行してください

### 接続エラー
- `Agent_workspace/symbol_agent/key/supabase_1.txt` の内容を確認してください
- SupabaseのプロジェクトURLとAPIキーが正しいか確認してください

### パースエラー
- データファイルのフォーマットを確認してください
- `|` で区切られているか確認してください
- 必要なフィールドがすべて含まれているか確認してください

