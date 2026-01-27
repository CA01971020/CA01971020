import os
import requests
from datetime import date

TOKEN = os.environ.get("PROFILE_GH_TOKEN")
USER = "CA01971020"

if not TOKEN:
    raise EnvironmentError("PROFILE_GH_TOKEN が設定されていません。")

today = date.today()
from_date = date(today.year, 1, 1)
to_date = today

query = """
query {
  user(login: "%s") {
    contributionsCollection(from: "%sT00:00:00Z", to: "%sT23:59:59Z") {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
""" % (USER, from_date.isoformat(), to_date.isoformat())

res = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"query": query}
)
res.raise_for_status()
json_data = res.json()

if "errors" in json_data:
    raise RuntimeError(json_data["errors"])

weeks = json_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
monthly_commits = [0] * 12

for week in weeks:
    for day in week["contributionDays"]:
        dt = date.fromisoformat(day["date"])
        month_index = dt.month - 1
        monthly_commits[month_index] += day["contributionCount"]

# ===== レイアウト =====
WIDTH = 440
HEIGHT = 260
LEFT = 32
RIGHT = 24
TOP = 40
BOTTOM = 40

GRAPH_WIDTH = WIDTH - LEFT - RIGHT
GRAPH_HEIGHT = HEIGHT - TOP - BOTTOM
BAR_GAP = 10
BAR_WIDTH = GRAPH_WIDTH // 12 - BAR_GAP

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MAX_COMMITS = max(monthly_commits) or 1

bars = ""
labels = ""
for i, (month, value) in enumerate(zip(months, monthly_commits)):
    x = LEFT + i * (BAR_WIDTH + BAR_GAP)
    bar_height = int((value / MAX_COMMITS) * GRAPH_HEIGHT)
    y = TOP + GRAPH_HEIGHT - bar_height

    bars += f"""
    <rect x="{x}" y="{y}" width="{BAR_WIDTH}" height="{bar_height}"
          rx="3" fill="#111827"/>
    """
    labels += f"""
    <text x="{x + BAR_WIDTH/2}" y="{TOP + GRAPH_HEIGHT + 16}"
          text-anchor="middle" class="label">{month}</text>
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
      font-size: 10px;
      fill: #6b7280;
    }}
  </style>

  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" class="card"/>
  <text x="{LEFT}" y="26" class="title">Commits in {today.year}</text>
  {bars}
  {labels}
</svg>
"""

os.makedirs("public", exist_ok=True)
with open("public/commits_monthly.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("public/commits_monthly.svg を生成しました")
