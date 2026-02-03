# -*- coding: utf-8 -*-
"""
Dieses Skript liest die Steam-ID aus einer CSV-Dateien, ruft basierend auf den IDs Informationen von der SteamDB ab
und indexiert alles mit Tantivy, um eine durchsuchbare Volltext-Indizestruktur zu erstellen.

Hauptschritte:
1) Schema für den Tantivy-Index definieren.
2) Index-Verzeichnis erstellen und Writer initialisieren.
3) CSV‑Daten (steamID) einlesen.
4) Für jedes Spiel: SteamDB-Daten ergänzen, Dokument zusammenstellen und in den Index schreiben.
5) Änderungen committen und Merge-Threads abwarten.
"""

import pandas as pd
from tantivy import SchemaBuilder, Index, Document
import pathlib
import json
import requests
import os
from itertools import islice
from dotenv import load_dotenv
import traceback


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
schema_builder.add_integer_field("steamId", stored=True, indexed=True)
schema_builder.add_text_field("title", stored=True, tokenizer_name='en_stem')
schema_builder.add_text_field("description", stored=True, tokenizer_name='en_stem')
schema_builder.add_text_field("description_short", stored=True, tokenizer_name='en_stem')
schema_builder.add_text_field("genres", stored=True)
schema_builder.add_text_field("publisher", stored=True)
schema_builder.add_text_field("platforms", stored=True)
schema_builder.add_text_field("url", stored=True)
schema_builder.add_text_field("image", stored=True)
schema_builder.add_text_field("trailer", stored=True)
schema_builder.add_date_field("release_date", stored=True)
schema = schema_builder.build()

# === 2) Index anlegen/öffnen ===S
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
# file = 'steamID.csv'  # Pfad zur SteamID-Liste (muss existieren)
# data = pd.read_csv(file)

# Nach dem indizieren werden IDs vermerkt, damit nichts doppelt indiziert wird
processed_steamIDs = set()

# === 4) Dokumente aufbauen und in den Index schreiben ===
# for index, row in data[:].iterrows():
with open("data.txt", "r", encoding="UTF-8") as f:
    for idx, line in enumerate(f):
        # Neues Tantivy-Dokument
        doc = Document()

        # === STEAM_DB-Abfragen (auf Basis der STEAM-ID) ===
        try:
            steam_json = json.loads(line)
            steam_ID = list(steam_json.keys())[0]

            if not steam_json[steam_ID]["success"]:
                print("ID existiert nicht!")
                continue

            if steam_ID in processed_steamIDs:
                print("haben wir schon.")
                continue

            data = steam_json[steam_ID]["data"]

            #id
            doc.add_integer("id", idx)
            print("ID:" + str(idx))

            #SteamId
            doc.add_integer("steamId", steam_ID)
            print("ID:" + str(steam_ID))

            #title
            title = data.get("name")
            if title is not None:
                doc.add_text("title", title)

            #description
            description = data.get("detailed_description")
            if description is not None:
                doc.add_text("description", description)

            # description - short
            short_description = data.get("short_description")
            if short_description is not None:
                doc.add_text("description_short", short_description)
            
            # genres
            # genres sieht so aus:
            # [{'id': '1', 'description': 'Action'}, {'id': '9', 'description': 'Racing'}]
            genres = data.get("genres")
            if genres is not None:
                for genre in genres:
                    doc.add_text("genres", genre["description"])

            # publisher
            publishers = data.get("publishers")
            if publishers is not None:
                for publisher in publishers:
                    doc.add_text("publisher", publisher)

            # platform
            platforms = data.get("platforms")
            if platforms is not None:
                for platform, b in platforms.items():
                    if b is True:
                        doc.add_text("platforms", platform)
                
            # image
            image = data.get("header_image")
            if image is not None:
                doc.add_text("image", image)

            # url
            url = data.get("website")
            if url is not None:
                doc.add_text("url", url)

            # release_date
            release_date = data.get("release_date")
            if release_date is not None:
                doc.add_text("release_date", release_date["date"])

            # trailer
            trailers:list[dict] = data.get("movies")
            if trailers is not None:
                trailers = [t for t in trailers if t["highlight"]]
                if len(trailers)>0:
                    doc.add_text("trailer", trailers[0]["hls_h264"])
            
            print("--> wurde eingelesen")

            processed_steamIDs.add(steam_ID)        #IDs als verarbeitet markieren
                        
        except Exception as e:
            # Fehler in der STEAM_DB-Abfrage protokollieren, Indexierung dennoch fortsetzen
            print(traceback.format_exc())

        # Fertiges Dokument in den Index schreiben
        writer.add_document(doc)

# === 5) Index-Änderungen finalisieren ===
writer.commit()                 # Schreibvorgänge bestätigen
writer.wait_merging_threads()   # Hintergrund-Mergeprozesse abwarten