import os
import requests
from datetime import date

# ======================
# GitHub 設定
# ======================
TOKEN = os.environ["PROFILE_GH_TOKEN"]
USER = "CA01971020"

# ======================
# 今年の期間を作成
# ======================
today = date.today()
year_start = date(today.year, 1, 1)

FROM = year_start.isoformat() + "T00:00:00Z"
TO = today.isoformat() + "T23:59:59Z"

# ======================
# GraphQL クエリ
# ======================
query = f"""
query {{
  user(login: "{USER}") {{
    followers {{
      totalCount
    }}
    repositories(privacy: PUBLIC) {{
      totalCount
    }}
    contributionsCollection(from: "{FROM}", to: "{TO}") {{
      contributionCalendar {{
        totalContributions
      }}
    }}
    email
    createdAt
    location
    starredRepositories {{
      totalCount
    }}
  }}
}}
"""

# ======================
# API リクエスト
# ======================
res = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"query": query},
)

res.raise_for_status()
data = res.json()["data"]["user"]

# ======================
# データ取得
# ======================
stars = data.get("starredRepositories", {}).get("totalCount", 0)
followers = data.get("followers", {}).get("totalCount", 0)
public_repos = data.get("repositories", {}).get("totalCount", 0)
commits = (
    data.get("contributionsCollection", {})
        .get("contributionCalendar", {})
        .get("totalContributions", 0)
)

account_created = data.get("createdAt", "").split("T")[0]
email = data.get("email") or "N/A"
email = "CA01971020@st.kawahara.ac.jp"
location = data.get("location") or "N/A"

# ======================
# 最大値（バー表示用）
# ======================
MAX_STARS = 10
MAX_FOLLOWERS = 30
MAX_REPOS = 40
MAX_COMMITS = 1200

# ======================
# SVG レイアウト
# ======================
WIDTH = 440
HEIGHT = 260

LEFT = 24
LABEL_X = LEFT
VALUE_X = 160
BAR_X = 210

BAR_WIDTH = 170
BAR_HEIGHT = 8
ROW_GAP = 30
START_Y = 58

def bar_len(value, max_value):
    return int(BAR_WIDTH * min(value / max_value, 1))

items = [
    ("Stars", stars, MAX_STARS),
    ("Followers", followers, MAX_FOLLOWERS),
    ("Public repos", public_repos, MAX_REPOS),
    ("Commits this year", commits, MAX_COMMITS),
]

INFO_START_Y = START_Y + ROW_GAP * len(items) + 28
INFO_GAP = 18

# ======================
# SVG 行生成
# ======================
rows = ""
for i, (label, value, max_val) in enumerate(items):
    y = START_Y + i * ROW_GAP
    length = bar_len(value, max_val)

    rows += f"""
    <text x="{LABEL_X}" y="{y}" class="label">{label}</text>
    <text x="{VALUE_X}" y="{y}" class="value">{value}</text>
    <rect x="{BAR_X}" y="{y-7}" width="{BAR_WIDTH}" height="{BAR_HEIGHT}"
          rx="4" fill="#e5e7eb"/>
    <rect x="{BAR_X}" y="{y-7}" width="{length}" height="{BAR_HEIGHT}"
          rx="4" fill="#111827"/>
    """

# ======================
# SVG 本体
# ======================
svg = f"""<svg width="{WIDTH}" height="{HEIGHT}"
  viewBox="0 0 {WIDTH} {HEIGHT}"
  xmlns="http://www.w3.org/2000/svg">

  <style>
    .card {{
      fill: #ffffff;
      stroke: #e5e7eb;
      stroke-width: 1;
      rx: 14;
    }}
    .title {{
      font-size: 14px;
      font-weight: 600;
      fill: #111827;
    }}
    .label {{
      font-size: 12px;
      fill: #374151;
    }}
    .value {{
      font-size: 12px;
      fill: #111827;
      text-anchor: end;
      font-weight: 500;
    }}
    .info-label {{
      font-size: 11px;
      fill: #6b7280;
    }}
    .info-value {{
      font-size: 11px;
      fill: #111827;
    }}
  </style>

  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" class="card"/>

  <text x="{LEFT}" y="28" class="title">GitHub Summary</text>

  {rows}

  <line x1="{LEFT}" y1="{INFO_START_Y - 24}"
        x2="{WIDTH - LEFT}" y2="{INFO_START_Y - 24}"
        stroke="#e5e7eb"/>

  <text x="{LEFT}" y="{INFO_START_Y}" class="info-label">
    Account created
  </text>
  <text x="{VALUE_X}" y="{INFO_START_Y}" class="info-value">
    {account_created}
  </text>

  <text x="{LEFT}" y="{INFO_START_Y + INFO_GAP}" class="info-label">
    Email
  </text>
  <text x="{VALUE_X}" y="{INFO_START_Y + INFO_GAP}" class="info-value">
    {email}
  </text>

  <text x="{LEFT}" y="{INFO_START_Y + INFO_GAP * 2}" class="info-label">
    Location
  </text>
  <text x="{VALUE_X}" y="{INFO_START_Y + INFO_GAP * 2}" class="info-value">
    {location}
  </text>

</svg>
"""

# ======================
# ファイル出力
# ======================
os.makedirs("public", exist_ok=True)
with open("public/summary.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("public/summary.svg を生成しました")
