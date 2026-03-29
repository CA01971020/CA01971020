import os
import requests
from datetime import datetime

TOKEN = os.environ["PROFILE_GH_TOKEN"]
USER = "Hii-Dev"

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
