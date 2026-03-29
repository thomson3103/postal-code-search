"""
サイトマップを生成する
12万ページ超のためインデックス方式で都道府県別に分割

出力:
  dist/sitemap_index.xml
  dist/sitemap-{slug}.xml (47ファイル)
"""
import os
from datetime import datetime

from prefectures import PREFECTURES

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DIST_DIR = os.path.join(BASE_DIR, "dist")

SITE_URL = "https://yubin-code.com"


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_sitemap(data: dict, slug_map: dict):
    """サイトマップを生成"""
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_files = []

    for pref_name, pref_data in data.items():
        info = PREFECTURES.get(pref_name)
        if not info:
            continue
        pref_slug = info["slug"]

        urls = []

        # 都道府県ページ
        urls.append({
            "loc": f"{SITE_URL}/{pref_slug}/",
            "changefreq": "monthly",
            "priority": "0.8",
        })

        # 市区町村ページ + 個別郵便番号ページ
        for city_name, city_data in pref_data["cities"].items():
            city_slug = slug_map.get((pref_name, city_name), "unknown")

            urls.append({
                "loc": f"{SITE_URL}/{pref_slug}/{city_slug}/",
                "changefreq": "monthly",
                "priority": "0.6",
            })

            for zc in city_data["zipcodes"]:
                urls.append({
                    "loc": f"{SITE_URL}/zipcode/{zc['code']}/",
                    "changefreq": "yearly",
                    "priority": "0.4",
                })

        # 都道府県別サイトマップ出力
        filename = f"sitemap-{pref_slug}.xml"
        filepath = os.path.join(DIST_DIR, filename)

        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for url in urls:
            lines.append("  <url>")
            lines.append(f"    <loc>{_xml_escape(url['loc'])}</loc>")
            lines.append(f"    <lastmod>{today}</lastmod>")
            lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
            lines.append(f"    <priority>{url['priority']}</priority>")
            lines.append("  </url>")
        lines.append("</urlset>")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        sitemap_files.append({
            "loc": f"{SITE_URL}/{filename}",
            "count": len(urls),
        })

    # サイトマップインデックス
    index_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    index_lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for sm in sitemap_files:
        index_lines.append("  <sitemap>")
        index_lines.append(f"    <loc>{_xml_escape(sm['loc'])}</loc>")
        index_lines.append(f"    <lastmod>{today}</lastmod>")
        index_lines.append("  </sitemap>")

    index_lines.append("</sitemapindex>")

    index_path = os.path.join(DIST_DIR, "sitemap_index.xml")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))

    # robots.txt
    robots_path = os.path.join(DIST_DIR, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap_index.xml\n")

    total_urls = sum(sm["count"] for sm in sitemap_files)
    print(f"  サイトマップ生成完了: {len(sitemap_files)}ファイル, {total_urls:,} URL")
