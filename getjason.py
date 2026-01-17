import json
import pandas as pd
import requests 
from tqdm.auto import tqdm

# Basis-URLs für SteamDB-Requests
STEAM_API = "https://store.steampowered.com/api/appdetails?appids="

# HTTP-Header inkl. Bearer-Token für SteamDB
headers = {
    "accept": "application/json"
}

file = 'steamID.csv'  # Pfad zur SteamID-Liste (muss existieren)
data = pd.read_csv(file)

outputpath = "allrequests.txt"
with open(outputpath,"a", encoding = "UTF-8") as f:     #"a" --> öffnet Datei im apend mode   
    for idx,row in tqdm(data[:].iterrows(),total = len(data),desc="Fetche alle Antworten von der Steam API."):
        if row.get("steamid") is None:
            print("Die SteamID in Zeile {idx} ist nicht vorhanden. Skippen")
            continue
        response = requests.get(STEAM_API + str(row.get("steamid")), headers=headers)
        f.write(response.text+"\n")