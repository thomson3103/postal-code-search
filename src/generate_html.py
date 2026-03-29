"""
Jinja2テンプレートを使って全HTMLページを生成する

生成するページ:
- トップページ (1)
- 都道府県ページ (47)
- 市区町村ページ (~1,900)
- 個別郵便番号ページ (~124,000)
- 検索ページ (1)
"""
import os
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from prefectures import PREFECTURES, REGIONS

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DIST_DIR = os.path.join(BASE_DIR, "dist")

SITE_URL = "https://yubin-code.com"


def _format_number(value):
    """数値をカンマ区切りにするJinja2フィルター"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


def _format_zip(code: str) -> str:
    """7桁コードをXXX-XXXX形式に"""
    if len(code) == 7:
        return f"{code[:3]}-{code[3:]}"
    return code


def setup_jinja_env():
    """Jinja2環境をセットアップ"""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=True,
    )
    env.filters["format_number"] = _format_number
    return env


def _build_regions_context(data: dict, slug_map: dict) -> list:
    """テンプレートに渡す地方・都道府県データを構築"""
    from collections import OrderedDict
    regions = OrderedDict()
    for region_name, pref_names in REGIONS:
        prefs = []
        for pref_name in pref_names:
            info = PREFECTURES[pref_name]
            zipcode_count = sum(
                len(c["zipcodes"])
                for c in data.get(pref_name, {}).get("cities", {}).values()
            )
            prefs.append({
                "name": pref_name,
                "short_name": info["short"],
                "slug": info["slug"],
                "zipcode_count": zipcode_count,
            })
        regions[region_name] = prefs
    return regions


def _write_file(path: str, content: str):
    """ファイルを書き出す（ディレクトリ自動作成）"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_html(data: dict, slug_map: dict):
    """全HTMLを生成"""
    env = setup_jinja_env()
    regions = _build_regions_context(data, slug_map)
    current_year = datetime.now().year

    # 全郵便番号をソートしたリスト（前後ナビ用）
    all_zipcodes_sorted = []
    for pref_name, pref_data in data.items():
        pref_slug = PREFECTURES[pref_name]["slug"]
        for city_name, city_data in pref_data["cities"].items():
            city_slug = slug_map.get((pref_name, city_name), "unknown")
            for zc in city_data["zipcodes"]:
                all_zipcodes_sorted.append({
                    "code": zc["code"],
                    "formatted": _format_zip(zc["code"]),
                    "pref_name": pref_name,
                    "pref_slug": pref_slug,
                    "city_name": city_name,
                    "city_slug": city_slug,
                    "neighborhood": zc["neighborhood"],
                    "full_address_short": f"{pref_name}{city_name}{zc['neighborhood']}",
                })
    all_zipcodes_sorted.sort(key=lambda x: x["code"])

    # コード→インデックスのマップ（前後ナビ高速化）
    code_to_idx = {}
    for i, zc in enumerate(all_zipcodes_sorted):
        # 同じコードが複数ある場合は最初のものを採用
        if zc["code"] not in code_to_idx:
            code_to_idx[zc["code"]] = i

    # --- 静的ファイルコピー ---
    dist_static = os.path.join(DIST_DIR, "css")
    if os.path.exists(os.path.join(STATIC_DIR, "css")):
        shutil.copytree(
            os.path.join(STATIC_DIR, "css"),
            dist_static,
            dirs_exist_ok=True,
        )
    dist_js = os.path.join(DIST_DIR, "js")
    if os.path.exists(os.path.join(STATIC_DIR, "js")):
        shutil.copytree(
            os.path.join(STATIC_DIR, "js"),
            dist_js,
            dirs_exist_ok=True,
        )

    total_zipcode_count = len(all_zipcodes_sorted)
    common_ctx = {
        "regions": regions,
        "current_year": current_year,
        "site_url": SITE_URL,
    }

    # === 1. トップページ ===
    print("  トップページ生成中...")
    tpl = env.get_template("top.html")
    html = tpl.render(
        **common_ctx,
        total_zipcode_count=total_zipcode_count,
        canonical_url=f"{SITE_URL}/",
    )
    _write_file(os.path.join(DIST_DIR, "index.html"), html)

    # === 2. 検索ページ ===
    print("  検索ページ生成中...")
    tpl = env.get_template("search.html")
    html = tpl.render(
        **common_ctx,
        query="",
        canonical_url=f"{SITE_URL}/search/",
    )
    _write_file(os.path.join(DIST_DIR, "search", "index.html"), html)

    # === 3. 都道府県ページ (47) ===
    print("  都道府県ページ生成中...")
    tpl = env.get_template("prefecture.html")
    for pref_name, pref_data in data.items():
        info = PREFECTURES[pref_name]
        pref_slug = info["slug"]

        # 市区町村リスト
        cities = []
        for city_name, city_data in pref_data["cities"].items():
            city_slug = slug_map.get((pref_name, city_name), "unknown")
            cities.append({
                "name": city_name,
                "slug": city_slug,
                "kana": city_data["kana"],
                "zipcode_count": len(city_data["zipcodes"]),
            })
        cities.sort(key=lambda x: x["kana"])

        zipcode_count = sum(c["zipcode_count"] for c in cities)

        html = tpl.render(
            **common_ctx,
            prefecture={
                "name": pref_name,
                "slug": pref_slug,
                "zipcode_count": zipcode_count,
                "info": {"capital": info["capital"]},
            },
            cities=cities,
            canonical_url=f"{SITE_URL}/{pref_slug}/",
        )
        _write_file(os.path.join(DIST_DIR, pref_slug, "index.html"), html)
    print(f"    → 47 ページ")

    # === 4. 市区町村ページ (~1,900) ===
    print("  市区町村ページ生成中...")
    tpl = env.get_template("city.html")
    city_count = 0
    for pref_name, pref_data in data.items():
        info = PREFECTURES[pref_name]
        pref_slug = info["slug"]

        # 同都道府県の他市区町村（nearby用）
        all_cities_in_pref = []
        for cn, cd in pref_data["cities"].items():
            cs = slug_map.get((pref_name, cn), "unknown")
            all_cities_in_pref.append({
                "name": cn,
                "slug": cs,
                "zipcode_count": len(cd["zipcodes"]),
            })

        for city_name, city_data in pref_data["cities"].items():
            city_slug = slug_map.get((pref_name, city_name), "unknown")

            # 郵便番号リスト
            zipcodes = []
            for zc in city_data["zipcodes"]:
                zipcodes.append({
                    "code": zc["code"],
                    "formatted": _format_zip(zc["code"]),
                    "neighborhood": zc["neighborhood"],
                    "neighborhood_kana": zc["neighborhood_kana"],
                    "note": zc["note"],
                })
            zipcodes.sort(key=lambda x: x["code"])

            # 近隣市区町村（自分を除く、最大10件）
            nearby = [c for c in all_cities_in_pref if c["name"] != city_name][:10]

            html = tpl.render(
                **common_ctx,
                prefecture={"name": pref_name, "slug": pref_slug},
                city={
                    "name": city_name,
                    "slug": city_slug,
                    "zipcode_count": len(zipcodes),
                },
                zipcodes=zipcodes,
                nearby_cities=nearby,
                canonical_url=f"{SITE_URL}/{pref_slug}/{city_slug}/",
            )
            _write_file(
                os.path.join(DIST_DIR, pref_slug, city_slug, "index.html"),
                html,
            )
            city_count += 1
    print(f"    → {city_count:,} ページ")

    # === 5. 個別郵便番号ページ (~124,000) ===
    print("  個別郵便番号ページ生成中...")
    tpl = env.get_template("zipcode.html")
    zip_count = 0
    for pref_name, pref_data in data.items():
        info = PREFECTURES[pref_name]
        pref_slug = info["slug"]

        for city_name, city_data in pref_data["cities"].items():
            city_slug = slug_map.get((pref_name, city_name), "unknown")

            # 同市区町村の郵便番号一覧（サイドナビ用、最大20件）
            same_city_zcs = []
            for zc in city_data["zipcodes"]:
                same_city_zcs.append({
                    "code": zc["code"],
                    "formatted": _format_zip(zc["code"]),
                    "neighborhood": zc["neighborhood"],
                })
            same_city_zcs.sort(key=lambda x: x["code"])
            same_city_has_more = len(same_city_zcs) > 20

            for zc in city_data["zipcodes"]:
                code = zc["code"]
                formatted = _format_zip(code)
                full_kana = " ".join(
                    filter(None, [
                        PREFECTURES[pref_name].get("slug", ""),  # ダミー
                        city_data["kana"],
                        zc["neighborhood_kana"],
                    ])
                )
                # カナの都道府県部分を正しく構築
                # CSVにはpref_kanaがあるが、ここではcity_kanaとneighborhood_kanaのみ
                # parse_csv側でpref_kanaを保存していないので、簡易的にカナ表記
                pref_kana_map = {
                    "北海道": "ホッカイドウ", "青森県": "アオモリケン",
                    "岩手県": "イワテケン", "宮城県": "ミヤギケン",
                    "秋田県": "アキタケン", "山形県": "ヤマガタケン",
                    "福島県": "フクシマケン", "茨城県": "イバラキケン",
                    "栃木県": "トチギケン", "群馬県": "グンマケン",
                    "埼玉県": "サイタマケン", "千葉県": "チバケン",
                    "東京都": "トウキョウト", "神奈川県": "カナガワケン",
                    "新潟県": "ニイガタケン", "富山県": "トヤマケン",
                    "石川県": "イシカワケン", "福井県": "フクイケン",
                    "山梨県": "ヤマナシケン", "長野県": "ナガノケン",
                    "岐阜県": "ギフケン", "静岡県": "シズオカケン",
                    "愛知県": "アイチケン", "三重県": "ミエケン",
                    "滋賀県": "シガケン", "京都府": "キョウトフ",
                    "大阪府": "オオサカフ", "兵庫県": "ヒョウゴケン",
                    "奈良県": "ナラケン", "和歌山県": "ワカヤマケン",
                    "鳥取県": "トットリケン", "島根県": "シマネケン",
                    "岡山県": "オカヤマケン", "広島県": "ヒロシマケン",
                    "山口県": "ヤマグチケン", "徳島県": "トクシマケン",
                    "香川県": "カガワケン", "愛媛県": "エヒメケン",
                    "高知県": "コウチケン", "福岡県": "フクオカケン",
                    "佐賀県": "サガケン", "長崎県": "ナガサキケン",
                    "熊本県": "クマモトケン", "大分県": "オオイタケン",
                    "宮崎県": "ミヤザキケン", "鹿児島県": "カゴシマケン",
                    "沖縄県": "オキナワケン",
                }
                full_kana = " ".join(filter(None, [
                    pref_kana_map.get(pref_name, ""),
                    city_data["kana"],
                    zc["neighborhood_kana"],
                ]))

                # 前後の郵便番号
                idx = code_to_idx.get(code)
                prev_zc = all_zipcodes_sorted[idx - 1] if idx and idx > 0 else None
                next_zc = all_zipcodes_sorted[idx + 1] if idx is not None and idx < len(all_zipcodes_sorted) - 1 else None

                html = tpl.render(
                    **common_ctx,
                    prefecture={"name": pref_name, "slug": pref_slug},
                    city={
                        "name": city_name,
                        "slug": city_slug,
                        "zipcode_count": len(city_data["zipcodes"]),
                    },
                    zipcode={
                        "code": code,
                        "formatted": formatted,
                        "neighborhood": zc["neighborhood"],
                        "neighborhood_kana": zc["neighborhood_kana"],
                        "note": zc["note"],
                        "old_code": zc["old_code"],
                        "jis_code": zc["jis_code"],
                        "full_kana": full_kana,
                    },
                    alternates=[],  # Phase2で対応
                    same_city_zipcodes=same_city_zcs[:20],
                    same_city_has_more=same_city_has_more,
                    prev_zipcode=prev_zc,
                    next_zipcode=next_zc,
                    canonical_url=f"{SITE_URL}/zipcode/{code}/",
                )
                _write_file(
                    os.path.join(DIST_DIR, "zipcode", code, "index.html"),
                    html,
                )
                zip_count += 1

                if zip_count % 10000 == 0:
                    print(f"    ... {zip_count:,} ページ生成済み")

    print(f"    → {zip_count:,} ページ")
    print(f"  合計: {1 + 1 + 47 + city_count + zip_count:,} ページ生成完了")
