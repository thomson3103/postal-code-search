#!/usr/bin/env python3
"""
全HTMLファイルに Search Console 検証メタタグ と GA4 計測タグを一括挿入するスクリプト。
既に挿入済みのファイルはスキップする。
"""
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SITE_DIR = Path(__file__).parent

# Search Console 検証メタタグ（<head>内に挿入）
SC_META = '  <meta name="google-site-verification" content="AZUpg5megM5jk80M0AfrIL3XjoSBPaf8kZUbmgCtSfs" />'

# GA4 計測タグ（</head>の直前に挿入）
GA4_TAG = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-N9GEKKEEFD"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-N9GEKKEEFD');
  </script>"""

# スキップするディレクトリ
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'src', 'data'}


def collect_html_files(root: Path) -> list[Path]:
    """HTMLファイルを収集"""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # スキップ対象を除外
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith('.html'):
                files.append(Path(dirpath) / f)
    return files


def inject_tags(filepath: Path) -> str:
    """1ファイルにタグを挿入。戻り値: 'injected', 'skipped', 'error:...'"""
    try:
        content = filepath.read_text(encoding='utf-8')

        # 既に挿入済みかチェック
        if 'G-N9GEKKEEFD' in content:
            return 'skipped'

        modified = False

        # 1. Search Console メタタグを <meta charset="UTF-8"> の直後に挿入
        if 'google-site-verification' not in content:
            marker = '<meta charset="UTF-8">'
            if marker in content:
                content = content.replace(
                    marker,
                    marker + '\n' + SC_META,
                    1
                )
                modified = True

        # 2. GA4タグを </head> の直前に挿入
        if '</head>' in content:
            content = content.replace(
                '</head>',
                GA4_TAG + '\n</head>',
                1
            )
            modified = True

        if modified:
            filepath.write_text(content, encoding='utf-8')
            return 'injected'
        else:
            return 'skipped'

    except Exception as e:
        return f'error:{e}'


def main():
    print("HTMLファイルを収集中...")
    html_files = collect_html_files(SITE_DIR)
    total = len(html_files)
    print(f"対象ファイル数: {total:,}")

    injected = 0
    skipped = 0
    errors = 0

    # マルチスレッドで高速処理
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(inject_tags, f): f for f in html_files}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result == 'injected':
                injected += 1
            elif result == 'skipped':
                skipped += 1
            else:
                errors += 1
                print(f"  ERROR: {futures[future]} -> {result}")

            if i % 10000 == 0:
                print(f"  進捗: {i:,}/{total:,} ({i*100//total}%)")

    print(f"\n完了!")
    print(f"  挿入: {injected:,}")
    print(f"  スキップ（既存）: {skipped:,}")
    print(f"  エラー: {errors:,}")

    # 検証: index.htmlの<head>を表示
    index = SITE_DIR / 'index.html'
    if index.exists():
        head = index.read_text(encoding='utf-8')
        head_end = head.find('</head>')
        if head_end > 0:
            print(f"\n--- index.html <head> 確認 ---")
            print(head[:head_end + 7])


if __name__ == '__main__':
    main()
