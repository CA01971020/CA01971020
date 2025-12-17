import os
import requests
from datetime import date

TOKEN = os.environ["PROFILE_GH_TOKEN"]
USER = "CA01971020"

query = """
query {
  user(login: "%s") {
    followers {
      totalCount
    }
    repositories(privacy: PUBLIC) {
      totalCount
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
    email
    createdAt
    location
    starredRepositories {
      totalCount
    }
  }
}
""" % USER

res = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"query": query}
)
data = res.json()["data"]["user"]

stars = data.get("starredRepositories", {}).get("totalCount", 0)
followers = data.get("followers", {}).get("totalCount", 0)
public_repos = data.get("repositories", {}).get("totalCount", 0)
commits = data.get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions", 0)

account_created = data.get("createdAt", "").split("T")[0]
email = data.get("email") or "N/A"
email = "CA01971020@st.kawahara.ac.jp"
location = data.get("location") or "N/A"

MAX_STARS = 10
MAX_FOLLOWERS = 30
MAX_REPOS = 40
MAX_COMMITS = 1200

# ===== レイアウト =====
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
INFO_GAP = 18  # Account info の行間

today = date.today().isoformat()

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
    .footer {{
      font-size: 10px;
      fill: #6b7280;
    }}
  </style>

  <!-- Card -->
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" class="card"/>

  <!-- Title -->
  <text x="{LEFT}" y="28" class="title">GitHub Summary</text>

  <!-- Stats -->
  {rows}

  <!-- Divider -->
  <line x1="{LEFT}" y1="{INFO_START_Y - 24}"
        x2="{WIDTH - LEFT}" y2="{INFO_START_Y - 24}"
        stroke="#e5e7eb"/>

  <!-- Account info -->
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

with open("public/summary.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("public/summary.svg を生成しました")