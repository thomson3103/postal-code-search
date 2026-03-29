"""
市区町村名からURLスラッグを生成する
カナ読み → ローマ字変換 → ハイフン区切り

例:
  千代田区 → chiyoda-ku
  札幌市中央区 → sapporo-shi-chuo-ku
  西多摩郡奥多摩町 → nishitama-gun-okutama-machi
"""
import re
from pykakasi import kakasi


_kakasi = kakasi()


def _to_romaji(text: str) -> str:
    """日本語テキストをローマ字に変換"""
    result = _kakasi.convert(text)
    parts = []
    for item in result:
        parts.append(item["hepburn"])
    return "".join(parts)


def generate_city_slug(city_name: str) -> str:
    """
    市区町村名からスラッグを生成

    戦略:
    1. 「市」「区」「町」「村」「郡」の区切りでハイフンを入れる
    2. 各パーツをローマ字変換
    """
    # 政令指定都市の区: 「札幌市中央区」→「sapporo-shi-chuo-ku」
    # 郡の町村: 「西多摩郡奥多摩町」→「nishitama-gun-okutama-machi」

    # 区切りパターン
    # 「市」「郡」「区」「町」「村」の前後で分割
    # ただし「四日市市」のような「市市」パターンに注意

    # 行政区分サフィックスのマッピング
    suffixes = {
        "市": "shi",
        "区": "ku",
        "町": "cho",  # 後で machi に変換する場合あり
        "村": "mura",  # son の場合もあるが mura で統一
        "郡": "gun",
    }

    # 分割パターン: 行政区分文字で区切る
    # 「札幌市中央区」→ [「札幌」,「市」,「中央」,「区」]
    pattern = r"(市|郡|区|町|村)"
    parts = re.split(pattern, city_name)

    slug_parts = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if part in suffixes:
            slug_parts.append(suffixes[part])
        else:
            romaji = _to_romaji(part).lower()
            # 不要な文字を除去
            romaji = re.sub(r"[^a-z0-9]", "", romaji)
            if romaji:
                slug_parts.append(romaji)

    slug = "-".join(slug_parts)

    # 空の場合のフォールバック
    if not slug:
        slug = _to_romaji(city_name).lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")

    return slug


def generate_all_slugs(data: dict) -> dict:
    """
    全市区町村のスラッグを生成し、重複を解決する

    Args:
        data: parse_csv() の出力

    Returns:
        {(都道府県名, 市区町村名): slug} のdict
    """
    slug_map = {}
    slug_counts = {}  # slug → 出現回数（重複検出用）

    # 第1パス: スラッグ生成
    for pref_name, pref_data in data.items():
        for city_name in pref_data["cities"]:
            slug = generate_city_slug(city_name)
            key = (pref_name, city_name)
            slug_map[key] = slug

            if slug not in slug_counts:
                slug_counts[slug] = []
            slug_counts[slug].append(key)

    # 第2パス: 同一都道府県内の重複を解決
    # （異なる都道府県の同名市区町村は都道府県スラッグで分離されるので問題なし）
    for slug, keys in slug_counts.items():
        # 同一都道府県内の重複を探す
        by_pref = {}
        for key in keys:
            pref = key[0]
            if pref not in by_pref:
                by_pref[pref] = []
            by_pref[pref].append(key)

        for pref, pref_keys in by_pref.items():
            if len(pref_keys) > 1:
                # JISコード下3桁を付加して重複解決
                for key in pref_keys:
                    city_name = key[1]
                    city_data = data[pref]["cities"][city_name]
                    jis_suffix = city_data["jis_code"][-3:]
                    slug_map[key] = f"{slug}-{jis_suffix}"

    return slug_map


if __name__ == "__main__":
    # テスト
    tests = [
        "千代田区",
        "中央区",
        "港区",
        "札幌市中央区",
        "西多摩郡奥多摩町",
        "北群馬郡榛東村",
        "四日市市",
    ]
    for name in tests:
        print(f"  {name} → {generate_city_slug(name)}")
