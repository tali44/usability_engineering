# -*- coding: utf-8 -*-
"""
Dieses Skript liest die Steam-ID aus einer CSV-Dateien, ruft basierend auf
den IDs Informationen von der SteamDB ab und indexiert alles mit Tantivy,
um eine durchsuchbare Volltext-Indizestruktur zu erstellen.

Hauptschritte:
1) Schema für den Tantivy-Index definieren.
2) Index-Verzeichnis erstellen und Writer initialisieren.
3) CSV‑Daten (steamID) einlesen.
4) Für jede Serie: SteamDB-Daten ergänzen, Dokument zusammenstellen und in den Index schreiben.
5) Änderungen committen und Merge-Threads abwarten.
"""

import pandas as pd
from urllib.parse import urlparse, unquote
from tantivy import SchemaBuilder, Index, Document, Query, Occur
import pathlib
import json
import requests
import os
from itertools import islice
from dotenv import load_dotenv


# Basis-URLs für SteamDB-Requests
STEAM_API = "https://store.steampowered.com/api/appdetails?appids="

#Umgebungsvariablen laden
load_dotenv()

# HTTP-Header inkl. Bearer-Token für SteamDB
headers = {
    "accept": "application/json"
}

# === 1) Schema für den Index definieren ===
schema_builder = SchemaBuilder()
schema_builder.add_integer_field("id", stored=True, indexed=True)
schema_builder.add_text_field("title", stored=True, tokenizer_name='en_stem')
schema_builder.add_text_field("description", stored=True, tokenizer_name='en_stem')  # Mehrwertiges Textfeld
schema_builder.add_text_field("description_short", stored=True, tokenizer_name='en_stem')  # Mehrwertiges Textfeld
schema_builder.add_text_field("genres", stored=True)
schema_builder.add_text_field("publisher", stored=True)
schema_builder.add_text_field("platforms", stored=True)
schema_builder.add_text_field("url", stored=True)
schema_builder.add_text_field("image", stored=True)
schema_builder.add_text_field("trailer", stored=True)
schema_builder.add_date_field("release_date", stored=True)
schema = schema_builder.build()

# === 2) Index anlegen/öffnen ===
index_path = "neu"  # Relativer Pfad für das Index-Verzeichnis
if not os.path.exists(index_path):
    os.makedirs(index_path)
    print(f"Der {index_path}-Ordner wurde angelegt.")
else:
    print(f"Ordner {index_path} existiert bereits.")

index_path = pathlib.Path(index_path)
index = Index(schema, path=str(index_path))
writer = index.writer()  # Writer für Batch-Schreibvorgänge

# === 3) CSVs einlesen ===
file = 'steamID.csv'  # Pfad zur SteamID-Liste (muss existieren)
data = pd.read_csv(file)


# === 4) Dokumente aufbauen und in den Index schreiben ===
# islice(..., 10) beschränkt auf die ersten 10 Einträge – bei Bedarf anpassen/entfernen

#for index, row in islice data.iterrows(): # für alle zeilen (kann nen bissl dauern)
for index, row in islice(data.iterrows(), 2):
    # Neues Tantivy-Dokument
    doc = Document()
    # === STEAM_DB-Abfragen (auf Basis der STEAM-ID) ===
    try:
        print(row.get("steamid"))
        response = requests.get(STEAM_API + str(row.get("steamid")), headers=headers)
        #print(response.text)

        steam_json = json.loads(response.text)
        data = steam_json[str(row.get("steamid"))]["data"]
        #print(data)

        #id
        doc.add_integer("id", index)
        print("ID:" + str(index))

        #title
        title = data["name"]
        doc.add_text("title", title)
        print("Name:" + title)
        t = doc.get_all("title")
        print("Dokument:", t)

        #description
        description = data["detailed_description"]
        doc.add_text("description", description)
        print("Beschreibung:" + description)

        # description - short
        short_description = data["short_description"]
        doc.add_text("description_short", short_description)
        print("Short:" + short_description)
        
        # genres
        # genres sieht so aus:
        # [{'id': '1', 'description': 'Action'}, {'id': '9', 'description': 'Racing'}]
        genres = data["genres"]
        for genre in genres:
            doc.add_text("genres", genre["description"])
            print("Genres:" + genre["description"])

        # publisher
        publishers = data["publishers"]
        for publisher in publishers:
            doc.add_text("publisher", publisher)
            print("Publisher:" + publisher)

        # platform
        platforms = data["platforms"]
        print(platforms)
        for platform, b in platforms.items():
            if b is True:
                doc.add_text("platforms", platform)   # ich bekomme alle 3 plattformen (windows, linux, mac) - aber nicht den true/false wert
            

        # url
        url = data["website"]
        doc.add_text("url", url) 
        print("URL:" + url)

        # image
        image = data["header_image"]
        doc.add_text("image", image)
        print("Bild:" + image)

        # trailer
        trailers = data["movies"]
        for trailer in trailers:
            doc.add_text("trailer", trailer["dash_av1"])
            print("Trailer:" + trailer["dash_av1"])             # keine Ahnung ist ne mpd datei, ich kann sie nicht öffnen weiß nicht ob die angezeigt werden kann

        # release_date
        release_date = data["release_date"]
        doc.add_text("release_date", release_date["date"])
        print("Datum:" + release_date["date"])                  # unterschiedliche schreibweisen "17. Nov. 2018"; "17. Nov, 2018" --> zweites wird angezeit das erste nicht
        
    except Exception as e:
        # Fehler in der STEAM_DB-Abfrage protokollieren, Indexierung dennoch fortsetzen
        print(str(e))

    # Fertiges Dokument in den Index schreiben
    writer.add_document(doc)

# === 5) Index-Änderungen finalisieren ===
writer.commit()                 # Schreibvorgänge bestätigen
writer.wait_merging_threads()   # Hintergrund-Mergeprozesse abwarten



# index_path = "neu"
# index = Index(schema, path=str(index_path))
# searcher = index.searcher()

# text_q = Query.term_query(schema, "title", "team")

# q = Query.boolean_query([
#     (Occur.Must, text_q)
# ])

# q_hits = searcher.search(q, limit=10).hits
# for score, addr in q_hits:
#     hit = searcher.doc(addr)
#     print(hit['title'][0])