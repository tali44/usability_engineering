import json
import pandas as pd
import requests 
from tqdm.auto import tqdm
import time

# Basis-URLs für SteamDB-Requests
STEAM_API = "https://store.steampowered.com/api/appdetails?appids="
VON_STEAM_ID = 88001       # Anfangsnummer eingeben --> beim nächsten indizieren wäre das 4582
BIS_STEAM_ID = 92000    # Endnummer eingeben, i guess in so 4000 Abständen wäre ganz ok

# HTTP-Header inkl. Bearer-Token für SteamDB
headers = {
    "accept": "application/json"
}

file = 'steamID.csv'  # Pfad zur SteamID-Liste (muss existieren)
data = pd.read_csv(file)

outputpath = "88001-92000.txt"
with open(outputpath,"a", encoding = "UTF-8") as f:     #"a" --> öffnet Datei im apend mode   
    for idx,row in tqdm(data[VON_STEAM_ID:BIS_STEAM_ID].iterrows(),total = len(data[VON_STEAM_ID:BIS_STEAM_ID]),desc="Fetche alle Antworten von der Steam API."):
        if row.get("steamid") is None:
            print("Die SteamID in Zeile {idx} ist nicht vorhanden. Skippen")
            continue
        response = requests.get(STEAM_API + str(row.get("steamid")), headers=headers)
        if response.status_code != 200:
            print(f"Hier ist etwas schiefgelaufen. Die Steam ID war {row.get("steamid")}")
            time.sleep(5*60)
            continue
        f.write(response.text+"\n")
        time.sleep(1.5) #"schläft" für 1,5 sekunden, um das steam-anfragen-limit nicht zu überschreiten