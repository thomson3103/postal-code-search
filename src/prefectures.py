"""
都道府県メタデータ
47都道府県の情報を一元管理
"""

REGIONS = [
    ("北海道・東北", ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"]),
    ("関東", ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県"]),
    ("中部", ["新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県"]),
    ("近畿", ["三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"]),
    ("中国・四国", ["鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県"]),
    ("九州・沖縄", ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]),
]

PREFECTURES = {
    "北海道":   {"code": "01", "slug": "hokkaido",   "capital": "札幌市",   "short": "北海道"},
    "青森県":   {"code": "02", "slug": "aomori",     "capital": "青森市",   "short": "青森"},
    "岩手県":   {"code": "03", "slug": "iwate",      "capital": "盛岡市",   "short": "岩手"},
    "宮城県":   {"code": "04", "slug": "miyagi",     "capital": "仙台市",   "short": "宮城"},
    "秋田県":   {"code": "05", "slug": "akita",      "capital": "秋田市",   "short": "秋田"},
    "山形県":   {"code": "06", "slug": "yamagata",   "capital": "山形市",   "short": "山形"},
    "福島県":   {"code": "07", "slug": "fukushima",  "capital": "福島市",   "short": "福島"},
    "茨城県":   {"code": "08", "slug": "ibaraki",    "capital": "水戸市",   "short": "茨城"},
    "栃木県":   {"code": "09", "slug": "tochigi",    "capital": "宇都宮市", "short": "栃木"},
    "群馬県":   {"code": "10", "slug": "gunma",      "capital": "前橋市",   "short": "群馬"},
    "埼玉県":   {"code": "11", "slug": "saitama",    "capital": "さいたま市", "short": "埼玉"},
    "千葉県":   {"code": "12", "slug": "chiba",      "capital": "千葉市",   "short": "千葉"},
    "東京都":   {"code": "13", "slug": "tokyo",      "capital": "新宿区",   "short": "東京"},
    "神奈川県": {"code": "14", "slug": "kanagawa",   "capital": "横浜市",   "short": "神奈川"},
    "新潟県":   {"code": "15", "slug": "niigata",    "capital": "新潟市",   "short": "新潟"},
    "富山県":   {"code": "16", "slug": "toyama",     "capital": "富山市",   "short": "富山"},
    "石川県":   {"code": "17", "slug": "ishikawa",   "capital": "金沢市",   "short": "石川"},
    "福井県":   {"code": "18", "slug": "fukui",      "capital": "福井市",   "short": "福井"},
    "山梨県":   {"code": "19", "slug": "yamanashi",  "capital": "甲府市",   "short": "山梨"},
    "長野県":   {"code": "20", "slug": "nagano",     "capital": "長野市",   "short": "長野"},
    "岐阜県":   {"code": "21", "slug": "gifu",       "capital": "岐阜市",   "short": "岐阜"},
    "静岡県":   {"code": "22", "slug": "shizuoka",   "capital": "静岡市",   "short": "静岡"},
    "愛知県":   {"code": "23", "slug": "aichi",      "capital": "名古屋市", "short": "愛知"},
    "三重県":   {"code": "24", "slug": "mie",        "capital": "津市",     "short": "三重"},
    "滋賀県":   {"code": "25", "slug": "shiga",      "capital": "大津市",   "short": "滋賀"},
    "京都府":   {"code": "26", "slug": "kyoto",      "capital": "京都市",   "short": "京都"},
    "大阪府":   {"code": "27", "slug": "osaka",      "capital": "大阪市",   "short": "大阪"},
    "兵庫県":   {"code": "28", "slug": "hyogo",      "capital": "神戸市",   "short": "兵庫"},
    "奈良県":   {"code": "29", "slug": "nara",       "capital": "奈良市",   "short": "奈良"},
    "和歌山県": {"code": "30", "slug": "wakayama",   "capital": "和歌山市", "short": "和歌山"},
    "鳥取県":   {"code": "31", "slug": "tottori",    "capital": "鳥取市",   "short": "鳥取"},
    "島根県":   {"code": "32", "slug": "shimane",    "capital": "松江市",   "short": "島根"},
    "岡山県":   {"code": "33", "slug": "okayama",    "capital": "岡山市",   "short": "岡山"},
    "広島県":   {"code": "34", "slug": "hiroshima",  "capital": "広島市",   "short": "広島"},
    "山口県":   {"code": "35", "slug": "yamaguchi",  "capital": "山口市",   "short": "山口"},
    "徳島県":   {"code": "36", "slug": "tokushima",  "capital": "徳島市",   "short": "徳島"},
    "香川県":   {"code": "37", "slug": "kagawa",     "capital": "高松市",   "short": "香川"},
    "愛媛県":   {"code": "38", "slug": "ehime",      "capital": "松山市",   "short": "愛媛"},
    "高知県":   {"code": "39", "slug": "kochi",      "capital": "高知市",   "short": "高知"},
    "福岡県":   {"code": "40", "slug": "fukuoka",    "capital": "福岡市",   "short": "福岡"},
    "佐賀県":   {"code": "41", "slug": "saga",       "capital": "佐賀市",   "short": "佐賀"},
    "長崎県":   {"code": "42", "slug": "nagasaki",   "capital": "長崎市",   "short": "長崎"},
    "熊本県":   {"code": "43", "slug": "kumamoto",   "capital": "熊本市",   "short": "熊本"},
    "大分県":   {"code": "44", "slug": "oita",       "capital": "大分市",   "short": "大分"},
    "宮崎県":   {"code": "45", "slug": "miyazaki",   "capital": "宮崎市",   "short": "宮崎"},
    "鹿児島県": {"code": "46", "slug": "kagoshima",  "capital": "鹿児島市", "short": "鹿児島"},
    "沖縄県":   {"code": "47", "slug": "okinawa",    "capital": "那覇市",   "short": "沖縄"},
}

# JISコード上2桁 → 都道府県名
JIS_TO_PREF = {}
for name, info in PREFECTURES.items():
    JIS_TO_PREF[info["code"]] = name
