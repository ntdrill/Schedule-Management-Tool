#!/usr/bin/env python3
import os
import argparse


TEMPLATE = """# ワークフロー草案

## 入力
- 目的:
- 対象フェーズ:
- 参照資料:

## ステップ
1. (担当) 行為 → 出力
2. (担当) 行為 → 出力

## 備考
- 依存関係:
- 例外:
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="workflow_draft.txt")
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    manager_dir = os.path.dirname(scripts_dir)
    out_path = os.path.join(manager_dir, "data", args.out)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(TEMPLATE)

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
