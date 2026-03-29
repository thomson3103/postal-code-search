"""
日本郵便の郵便番号CSVデータをダウンロード・解凍する
UTF-8版（1レコード1行）を使用
"""
import os
import io
import zipfile
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
CSV_URL = "https://www.post.japanpost.jp/zipcode/dl/utf/zip/utf_ken_all.zip"
CSV_FILENAME = "utf_ken_all.csv"


def download_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    dest = os.path.join(DATA_DIR, CSV_FILENAME)

    print(f"ダウンロード中: {CSV_URL}")
    resp = requests.get(CSV_URL, timeout=60)
    resp.raise_for_status()
    print(f"  サイズ: {len(resp.content):,} bytes")

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        # ZIP内のCSVファイルを探す
        csv_name = None
        for n in names:
            if n.lower().endswith(".csv"):
                csv_name = n
                break
        if not csv_name:
            raise FileNotFoundError(f"ZIP内にCSVファイルが見つかりません: {names}")

        print(f"  解凍: {csv_name} → {dest}")
        with zf.open(csv_name) as src, open(dest, "wb") as dst:
            dst.write(src.read())

    # 行数確認
    with open(dest, "r", encoding="utf-8") as f:
        count = sum(1 for _ in f)
    print(f"  完了: {count:,} 行")
    return dest


if __name__ == "__main__":
    download_data()
