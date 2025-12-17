import os
import requests
from datetime import date

TOKEN = os.environ.get("PROFILE_GH_TOKEN")
USER = "CA01971020"

if not TOKEN:
    raise EnvironmentError("PROFILE_GH_TOKEN が設定されていません。")

YEARS_BACK = 5
total_contributions = 0
today = date.today()

for i in range(YEARS_BACK):
    year = today.year - i
    from_date = date(year, 1, 1)
    to_date = date(year, 12, 31)
    if year == today.year:
        to_date = today  # 今年の場合は今日まで

    # ここで期間が 1 年を超えないことを確認
    # GraphQL API は UTC で時刻を指定
    query = """
    query {
      user(login: "%s") {
        contributionsCollection(from: "%sT00:00:00Z", to: "%sT23:59:59Z") {
          contributionCalendar {
            totalContributions
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

    year_contributions = json_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    total_contributions += year_contributions

print(f"合計貢献数: {total_contributions}")

# ===== SVG レイアウト =====
WIDTH = 440
HEIGHT = 150
LEFT = 24
today_str = today.isoformat()

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
      font-weight: 600;
      fill: #111827;
    }}
    .value {{
      font-size: 36px;
      font-weight: 700;
      fill: #111827;
      text-anchor: middle;
    }}
    .footer {{
      font-size: 10px;
      fill: #6b7280;
      text-anchor: middle;
    }}
  </style>

  <!-- Card -->
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" class="card"/>

  <!-- Title -->
  <text x="{LEFT}" y="28" class="title">
    Total Contributions
  </text>

  <!-- Value -->
  <text x="{WIDTH / 2}" y="86" class="value">
    {total_contributions:,}
  </text>

  <!-- Footer -->
  <text x="{WIDTH / 2}" y="{HEIGHT - 14}" class="footer">
    All time · Updated {today_str}
  </text>

</svg>
"""

# public ディレクトリ作成 & SVG 保存
os.makedirs("public", exist_ok=True)
with open("public/total_contributions.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("public/total_contributions.svg を生成しました")
