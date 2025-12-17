import os
import requests

GITHUB_API = "https://api.github.com/graphql"

token = os.environ.get("PROFILE_GH_TOKEN")
if not token:
    raise RuntimeError("PROFILE_GH_TOKEN is not set")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

query = """
{
  viewer {
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""

res = requests.post(
    GITHUB_API,
    headers=headers,
    json={"query": query},
)

if res.status_code != 200:
    raise RuntimeError(f"GitHub API error: {res.status_code} {res.text}")

data = res.json()

total = data["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

with open("total_contributions.txt", "w") as f:
    f.write(str(total))

print(f"Total contributions: {total}")
