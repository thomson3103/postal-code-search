"""
検索用JSONチャンクを都道府県別に生成する
クライアントサイドJSから遅延読み込みして検索に使用

出力: dist/data/search/{code}-{slug}.json
"""
import json
import os

from prefectures import PREFECTURES

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DIST_DIR = os.path.join(BASE_DIR, "dist")


def generate_search_json(data: dict):
    """都道府県別の検索用JSONを生成"""
    out_dir = os.path.join(DIST_DIR, "data", "search")
    os.makedirs(out_dir, exist_ok=True)

    total_entries = 0

    for pref_name, pref_data in data.items():
        info = PREFECTURES.get(pref_name)
        if not info:
            continue

        code = info["code"]
        slug = info["slug"]

        entries = []
        for city_name, city_data in pref_data["cities"].items():
            for zc in city_data["zipcodes"]:
                address = f"{pref_name}{city_name}{zc['neighborhood']}"
                kana = " ".join(filter(None, [
                    city_data["kana"],
                    zc["neighborhood_kana"],
                ]))
                entries.append({
                    "z": zc["code"],
                    "a": address,
                    "k": kana,
                })

        # 郵便番号順にソート
        entries.sort(key=lambda x: x["z"])

        filename = f"{code}-{slug}.json"
        filepath = os.path.join(out_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))

        total_entries += len(entries)

    print(f"  検索JSON生成完了: 47ファイル, {total_entries:,}エントリ")
    # ファイルサイズ合計
    total_size = sum(
        os.path.getsize(os.path.join(out_dir, fn))
        for fn in os.listdir(out_dir)
        if fn.endswith(".json")
    )
    print(f"  合計サイズ: {total_size / 1024 / 1024:.1f} MB")
