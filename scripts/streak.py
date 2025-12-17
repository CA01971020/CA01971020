import os
import requests
from datetime import date, datetime, timedelta

TOKEN = os.environ.get("PROFILE_GH_TOKEN")
USER = "CA01971020"

if not TOKEN:
    raise EnvironmentError("PROFILE_GH_TOKEN が設定されていません。")

today = date.today()
from_date = today - timedelta(days=365)

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
""" % (USER, from_date.isoformat(), today.isoformat())

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

days = []
for week in weeks:
    for day in week["contributionDays"]:
        dt = datetime.strptime(day["date"], "%Y-%m-%d").date()
        days.append((dt, day["contributionCount"]))

days.sort()

# ===== ストリーク計算 =====
current_streak = 0
longest_streak = 0
temp_streak = 0
streak_start_date = None

for dt, count in days:
    if count > 0:
        temp_streak += 1
        if temp_streak == 1:
            temp_start = dt
        if temp_streak > longest_streak:
            longest_streak = temp_streak
            streak_start_date = temp_start
    else:
        temp_streak = 0

current_streak = 0
for dt, count in reversed(days):
    if count > 0:
        current_streak += 1
    else:
        break

streak_start = streak_start_date.isoformat() if streak_start_date else "N/A"

# ===== レイアウト =====
WIDTH = 440
HEIGHT = 150
LEFT = 24
CENTER_X = WIDTH / 2

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
      font-size: 13px;
      fill: #374151;
      font-weight: 500;
    }}
    .label {{
      font-size: 11px;
      fill: #6b7280;
    }}
    .value {{
      font-size: 26px;
      fill: #111827;
      font-weight: 700;
    }}
    .unit {{
      font-size: 12px;
      fill: #6b7280;
      font-weight: 400;
    }}
    .footer {{
      font-size: 10px;
      fill: #6b7280;
    }}
  </style>

  <!-- Card -->
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" class="card"/>

  <!-- Title -->
  <text x="{LEFT}" y="28" class="title">
    Commit Streak
  </text>

  <!-- Current -->
  <text x="{LEFT}" y="62" class="label">Current</text>
  <text x="{LEFT}" y="96" class="value">
    {current_streak}
    <tspan class="unit"> days</tspan>
  </text>

  <!-- Longest -->
  <text x="{CENTER_X + 12}" y="62" class="label">Longest</text>
  <text x="{CENTER_X + 12}" y="96" class="value">
    {longest_streak}
    <tspan class="unit"> days</tspan>
  </text>

  <!-- Divider -->
  <line x1="{CENTER_X}" y1="48" x2="{CENTER_X}" y2="116"
        stroke="#e5e7eb"/>

  <!-- Footer -->
  <text x="{LEFT}" y="{HEIGHT-18}" class="footer">
    Since: {streak_start}
  </text>
</svg>
"""

os.makedirs("public", exist_ok=True)
with open("public/streak.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("public/streak.svg を生成しました")
