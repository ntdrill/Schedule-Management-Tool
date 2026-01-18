# 対処行動と場面データの管理

## ファイル構成

- `05_対処行動と場面の管理.md` - 対処行動と場面の管理に関する詳細資料
- `coping_actions.txt` - 対処行動データファイル（78項目）
- `coping_scenarios.txt` - 場面データファイル（239項目）

## データソース

これらのデータは、開発者の実体験に基づいて整理されたものです。

**元データ:**
- `docs/開発者の実体験.txt` - リワークプログラム修了レポート

**データベース:**
- Supabase: `coping_actions`テーブル、`coping_scenarios`テーブル
- 登録日: 2026年1月（推定）

## データファイルの形式

### coping_actions.txt
```
name|category|effectiveness|ease_of_use|recommendation|description
```

### coping_scenarios.txt
```
name|category|severity_level|description
```

## 更新方法

データを更新する場合は、以下の手順を実行してください：

1. `data/coping_actions.txt` または `data/coping_scenarios.txt` を編集
2. `migrate_coping_data_to_supabase.py` を実行してデータベースを更新
3. 本フォルダのデータファイルも同期（必要に応じて）

## 関連ファイル

- プロジェクトルート: `data/coping_actions.txt`, `data/coping_scenarios.txt`
- 登録スクリプト: `migrate_coping_data_to_supabase.py`
- ドキュメント: `docs/coping_data_migration_README.md`

