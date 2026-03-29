#!/usr/bin/env python3
"""
郵便番号検索サイト ビルドスクリプト

使い方:
  python src/build.py              # フルビルド（データDL含む）
  python src/build.py --skip-dl    # データDLをスキップ（CSV既存時）
  python src/build.py --only-html  # HTML生成のみ（テンプレ修正確認用）

ビルドフロー:
  1. CSVダウンロード（--skip-dl で省略可）
  2. CSV解析 → 構造化データ
  3. スラッグ生成
  4. HTML生成（12万ページ超）
  5. 検索用JSON生成
  6. サイトマップ生成
"""
import os
import sys
import time
import argparse
import shutil

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

from download_data import download_data
from parse_csv import parse_csv
from generate_slugs import generate_all_slugs
from generate_html import generate_html
from generate_search_json import generate_search_json
from generate_sitemap import generate_sitemap

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DIST_DIR = os.path.join(BASE_DIR, "dist")
CSV_FILE = os.path.join(BASE_DIR, "data", "raw", "utf_ken_all.csv")


def main():
    parser = argparse.ArgumentParser(description="郵便番号検索サイト ビルド")
    parser.add_argument("--skip-dl", action="store_true", help="データDLをスキップ")
    parser.add_argument("--only-html", action="store_true", help="HTML生成のみ")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("郵便番号検索サイト ビルド開始")
    print("=" * 60)

    # --- Step 0: dist/ をクリーン ---
    if os.path.exists(DIST_DIR):
        print("\n[0/5] dist/ をクリーン中...")
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)

    # --- Step 1: データダウンロード ---
    if not args.skip_dl and not args.only_html:
        print("\n[1/5] データダウンロード...")
        download_data()
    else:
        if not os.path.exists(CSV_FILE):
            print(f"エラー: CSVファイルが見つかりません: {CSV_FILE}")
            print("  --skip-dl を外して実行するか、先に python src/download_data.py を実行してください")
            sys.exit(1)
        print("\n[1/5] データダウンロード → スキップ")

    # --- Step 2: CSV解析 ---
    print("\n[2/5] CSV解析...")
    data = parse_csv(CSV_FILE)

    # --- Step 3: スラッグ生成 ---
    print("\n[3/5] スラッグ生成...")
    slug_map = generate_all_slugs(data)
    print(f"  {len(slug_map):,} 市区町村のスラッグ生成完了")

    # --- Step 4: HTML生成 ---
    print("\n[4/5] HTML生成...")
    generate_html(data, slug_map)

    if not args.only_html:
        # --- Step 5: 検索JSON + サイトマップ ---
        print("\n[5/5] 検索JSON + サイトマップ生成...")
        generate_search_json(data)
        generate_sitemap(data, slug_map)
    else:
        print("\n[5/5] 検索JSON + サイトマップ → スキップ")

    # --- 完了 ---
    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"ビルド完了! ({elapsed:.1f}秒)")
    print(f"出力先: {os.path.abspath(DIST_DIR)}")
    print()

    # ファイル数カウント
    file_count = 0
    total_size = 0
    for root, dirs, files in os.walk(DIST_DIR):
        for f in files:
            file_count += 1
            total_size += os.path.getsize(os.path.join(root, f))
    print(f"  ファイル数: {file_count:,}")
    print(f"  合計サイズ: {total_size / 1024 / 1024:.1f} MB")
    print()
    print("ローカル確認:")
    print(f"  cd {os.path.abspath(DIST_DIR)} && python -m http.server 8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
