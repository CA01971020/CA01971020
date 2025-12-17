# scripts/fetch_stats.py
import os
import requests
from datetime import datetime

TOKEN = os.environ["PROFILE_GH_TOKEN"]
USER = "CA01971020"

query = """
query {
  user(login: "%s") {
    contributionsCollection {
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
""" % USER

res = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"query": query}
)

data = res.json()
