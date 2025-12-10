import requests
import json

headers = {
    "accept": "application/json",
}

STEAM_API="https://store.steampowered.com/api/appdetails?appids="
steam_ids=[440, 1672970]

for steam_id in steam_ids:
    id_str = str(steam_id)
    response = requests.get(STEAM_API + id_str, headers=headers)
    steam_json = json.loads(response.text)
    data = steam_json[id_str]["data"]
    name = data["name"]
    print(name)