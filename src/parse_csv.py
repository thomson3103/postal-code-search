"""
日本郵便CSVを解析して構造化データに変換する

対処する「悪名高い」問題:
1. 町域名の複数行分割（カッコが閉じていない行は次行に続く）
2. 「以下に掲載がない場合」の処理
3. カッコ内の注記の分離
4. 一つの郵便番号で複数町域
"""
import csv
import os
import re
from collections import OrderedDict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
CSV_FILE = os.path.join(DATA_DIR, "utf_ken_all.csv")


def _extract_note(neighborhood: str) -> tuple[str, str]:
    """町域名からカッコ内の注記を分離する"""
    if "（" not in neighborhood:
        return neighborhood, ""

    # 「大宮町（今出川通河原町西入、...）」→ 「大宮町」と注記に分離
    match = re.match(r"^(.+?)（(.+)）$", neighborhood)
    if match:
        return match.group(1), match.group(2)

    # カッコが閉じていないケース（複数行結合済みの場合に起こりうる）
    idx = neighborhood.index("（")
    main = neighborhood[:idx]
    note = neighborhood[idx + 1:].rstrip("）")
    return main, note


def _is_special_neighborhood(name: str) -> bool:
    """特殊な町域名かどうか"""
    specials = [
        "以下に掲載がない場合",
        "の次に番地がくる場合",
    ]
    return any(s in name for s in specials)


def parse_csv(csv_path: str = None) -> dict:
    """
    CSVを解析して以下の構造を返す:
    {
        "都道府県名": {
            "cities": {
                "市区町村名": {
                    "kana": "カナ",
                    "jis_code": "13101",
                    "zipcodes": [
                        {
                            "code": "1000001",
                            "old_code": "100",
                            "neighborhood": "千代田",
                            "neighborhood_kana": "チヨダ",
                            "note": "",
                            "jis_code": "13101",
                            "is_multi": False,
                        },
                        ...
                    ]
                }
            }
        }
    }
    """
    if csv_path is None:
        csv_path = CSV_FILE

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSVファイルが見つかりません: {csv_path}\n"
            "先に python src/download_data.py を実行してください"
        )

    # --- Pass 1: CSVを読み込み、複数行分割を結合 ---
    raw_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        pending = None  # 未完了の行（カッコが閉じていない）

        for row in reader:
            if len(row) < 15:
                continue

            jis_code = row[0]
            old_code = row[1]
            zipcode = row[2]
            pref_kana = row[3]
            city_kana = row[4]
            neighborhood_kana = row[5]
            pref = row[6]
            city = row[7]
            neighborhood = row[8]
            flag_multi_zip = row[9]    # 一町域が二以上の郵便番号
            flag_banchi = row[10]
            flag_choume = row[11]
            flag_multi_area = row[12]  # 一つの郵便番号で二以上の町域
            flag_update = row[13]
            flag_reason = row[14]

            if pending is not None:
                # 前の行の続き: 町域名とカナを結合
                pending[8] += neighborhood
                pending[5] += neighborhood_kana

                # カッコが閉じたか確認
                open_count = pending[8].count("（")
                close_count = pending[8].count("）")
                if open_count <= close_count:
                    raw_rows.append(pending)
                    pending = None
                continue

            # カッコが開いて閉じていない → 次行に続く
            open_count = neighborhood.count("（")
            close_count = neighborhood.count("）")
            if open_count > close_count:
                pending = list(row)
                continue

            raw_rows.append(list(row))

        # 最終行が未完了の場合
        if pending is not None:
            raw_rows.append(pending)

    print(f"  CSV解析: {len(raw_rows):,} 行（結合後）")

    # --- Pass 2: 構造化 ---
    data = OrderedDict()

    for row in raw_rows:
        jis_code = row[0]
        old_code = row[1]
        zipcode = row[2]
        pref_kana = row[3]
        city_kana = row[4]
        neighborhood_kana = row[5]
        pref = row[6]
        city = row[7]
        neighborhood = row[8]
        flag_multi_area = row[12] == "1"

        # 「以下に掲載がない場合」→ 町域なし
        if _is_special_neighborhood(neighborhood):
            neighborhood = ""
            neighborhood_kana = ""
            note = ""
        else:
            # カッコ内注記を分離
            neighborhood, note = _extract_note(neighborhood)
            # カナからもカッコ内を除去
            if "（" in neighborhood_kana:
                neighborhood_kana = neighborhood_kana.split("（")[0]
            elif "(" in neighborhood_kana:
                neighborhood_kana = neighborhood_kana.split("(")[0]

        # 都道府県
        if pref not in data:
            data[pref] = {"cities": OrderedDict()}

        # 市区町村
        cities = data[pref]["cities"]
        if city not in cities:
            cities[city] = {
                "kana": city_kana,
                "jis_code": jis_code,
                "zipcodes": [],
            }

        # 重複チェック（同じ郵便番号+町域の組み合わせ）
        existing = None
        for zc in cities[city]["zipcodes"]:
            if zc["code"] == zipcode and zc["neighborhood"] == neighborhood:
                existing = zc
                break

        if existing is None:
            cities[city]["zipcodes"].append({
                "code": zipcode,
                "old_code": old_code,
                "neighborhood": neighborhood,
                "neighborhood_kana": neighborhood_kana,
                "note": note,
                "jis_code": jis_code,
                "is_multi": flag_multi_area,
            })

    # --- 統計 ---
    total_prefs = len(data)
    total_cities = sum(len(d["cities"]) for d in data.values())
    total_zipcodes = sum(
        len(c["zipcodes"])
        for d in data.values()
        for c in d["cities"].values()
    )
    print(f"  構造化完了: {total_prefs}都道府県, {total_cities:,}市区町村, {total_zipcodes:,}郵便番号")

    return data


if __name__ == "__main__":
    data = parse_csv()
    # サンプル出力
    tokyo = data.get("東京都")
    if tokyo:
        chiyoda = tokyo["cities"].get("千代田区")
        if chiyoda:
            print(f"\n千代田区: {len(chiyoda['zipcodes'])}件")
            for zc in chiyoda["zipcodes"][:5]:
                print(f"  〒{zc['code'][:3]}-{zc['code'][3:]} {zc['neighborhood']} ({zc['neighborhood_kana']})")
