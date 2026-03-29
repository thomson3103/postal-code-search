# 郵便番号検索サイト — Claude Code 引き継ぎ書

## これは何？

79サイト群プロジェクトの #11「郵便番号検索サイト」。
日本郵便の公式CSVデータ（著作権フリー・12万件）から、
全郵便番号の個別ページを静的HTMLとして自動生成するサイト。

---

## 完成しているもの

チャットで以下を全て作成済み。ZIPファイル `postal-code-search.zip` に同梱。

### 設計書
- `CLAUDE.md` — サイト全体の設計書（データソース、URL設計、SEO設計、Phase分け等）

### テンプレート（Jinja2）6ファイル
- `templates/base.html` — 共通レイアウト（ヘッダー・パンくず・フッター）
- `templates/top.html` — トップページ（都道府県グリッド＋検索窓）
- `templates/prefecture.html` — 都道府県ページ（市区町村テーブル＋絞り込み）
- `templates/city.html` — 市区町村ページ（郵便番号テーブル＋絞り込み）
- `templates/zipcode.html` — 個別番号ページ（詳細カード＋コピーボタン＋前後ナビ＋JSON-LD）
- `templates/search.html` — 検索結果ページ

### CSS / JS
- `static/css/style.css` — モバイルファースト。日本郵便の赤(#cc0000)アクセント
- `static/js/search.js` — 都道府県別JSON遅延読み込み＋インクリメンタルサーチ

### Pythonビルドスクリプト 8ファイル
- `src/build.py` — 統合ビルド（これ1つで全工程実行）
- `src/download_data.py` — 日本郵便CSVダウンロード＆解凍
- `src/parse_csv.py` — CSV解析（複数行結合・注記分離・特殊ケース処理）
- `src/prefectures.py` — 47都道府県メタデータ
- `src/generate_slugs.py` — 市区町村名→ローマ字スラッグ変換（pykakasi）
- `src/generate_html.py` — 全HTMLページ生成（12万ページ超）
- `src/generate_search_json.py` — 検索用JSONチャンク生成（47ファイル）
- `src/generate_sitemap.py` — サイトマップ＋robots.txt生成

### その他
- `requirements.txt` — jinja2, pykakasi, requests

---

## Claude Code にやってほしいこと

### Step 1: ビルド実行＆動作確認

```bash
cd postal-code-search
pip install -r requirements.txt
python src/build.py
```

生成された `dist/` をローカルサーバーで確認：
```bash
cd dist && python -m http.server 8000
```

### Step 2: バグ修正・調整

ビルドスクリプトはチャットで書いたもので未テスト。
実行時にエラーが出たら直してほしい。特に注意点：

- `parse_csv.py` のCSV複数行結合ロジック
- `generate_slugs.py` のpykakasi変換（政令指定都市の区名が正しくスラッグ化されるか）
- `generate_html.py` の12万ページ生成（メモリ・速度）

### Step 3: SITE_URL の設定

ドメインが決まったら以下2ファイルの `SITE_URL` を更新：
- `src/generate_html.py`
- `src/generate_sitemap.py`

### Step 4: デプロイ

Cloudflare Pages（GitHub連携）にデプロイ。
`dist/` ディレクトリがデプロイ対象。

---

## まだやっていないこと

- ドメイン名の確定（候補: yubin-bango.jp 等）
- 実データでのビルドテスト
- 広告コード（忍者AdMax）の実タグ埋め込み
- Cloudflare Pagesの設定
- Phase 2（事業所データ追加・地図表示・アドセンス）

---

## ページ生成数の目安

| ページ種別 | 件数 |
|---|---|
| トップ | 1 |
| 検索 | 1 |
| 都道府県 | 47 |
| 市区町村 | 約1,900 |
| 個別郵便番号 | 約124,000 |
| **合計** | **約126,000** |
