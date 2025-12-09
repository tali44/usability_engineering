# -*- coding: utf-8 -*-
"""
Dieses Skript liest Videospieldaten aus CSV-Dateien, ruft basierend auf
den Steam-IDs von Wikipedia und weitere Informationen von Steam ab und
indexiert alles mit Tantivy, um eine durchsuchbare Volltext-Indizestruktur
zu erstellen.

Hauptschritte:
1) Schema für den Tantivy-Index definieren.
2) Index-Verzeichnis erstellen und Writer initialisieren.
3) Wikipedia‑Client mit benutzerdefiniertem User‑Agent aufsetzen.
4) CSV‑Daten (Serien + IMDb) einlesen und mergen.
5) Für jede Serie: Wikipedia-Seite laden, TMDB-Daten per API ergänzen,
   Dokument zusammenstellen und in den Index schreiben.
6) Änderungen committen und Merge-Threads abwarten.
"""

import pandas as pd
import wikipediaapi
import re
from urllib.parse import urlparse, unquote
from tantivy import Facet, SchemaBuilder, Index, Document
import pathlib
import json
import requests
import os
from itertools import islice
from dotenv import load_dotenv


# Basis-URLs für TMDB-Requests
STEAM_API = "https://store.steampowered.com/api/appdetails?appids="

#Umgebungsvariablen laden
load_dotenv()

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

# === 3) Wikipedia-Client mit Session und User-Agent ===
custom_user_agent = "MyWikipediaBot/1.0 (https://example.com; myemail@example.com)"
session = requests.Session()
session.headers.update({'User-Agent': custom_user_agent})

# Wikipedia-API-Objekt; Session explizit zuweisen, um Rate Limits zu respektieren
wiki = wikipediaapi.Wikipedia(language='en', user_agent=custom_user_agent)
wiki.session = session

# === 4) CSVs einlesen ===
file = 'steamID.csv'  # Pfad zur SteamID-Liste (muss existieren)
data = pd.read_csv(file)

# === 5) Dokumente aufbauen und in den Index schreiben ===
# islice(..., 10) beschränkt auf die ersten 10 Einträge – bei Bedarf anpassen/entfernen

# for index, row in islice data.iterrows(): # für alle zeilen (kann nen bissl dauern)
for index, row in islice(data.iterrows(), 10):
    # Neues Tantivy-Dokument
    doc = Document()
    print(index)
    
    doc.add_integer("id", index)

    # === STEAM_DB-Abfragen (auf Basis der STEAM-ID) ===
    try:
        response = requests.get(STEAM_API + row["SteamID"], headers=headers)
        steamdb_json = json.loads(response.text)

        # Prüfen, ob Spiel-Ergebnisse vorhanden sind (wir nehmen das erste)
        if steamdb_json.get("game_results"):
            steamdb = steamdb_json["game_results"][0]

            # titel
            if steamdb.get("name"):
                name = steamdb.get("name")
                doc.add_text("titel", name)

            # description
            if steamdb.get("detailed_description"):
                description = steamdb.get("detailed_description")
                doc.add_text("description", description)

            # description - short
            if steamdb.get("short_description"):
                short_description = steamdb.get("short_description")
                doc.add_text("description_short", short_description)
            
            # genres
            if steamdb.get("genres"):
                genres = steamdb.get("genres")
                doc.add_text("genres", genres)

            # publisher
            if steamdb.get("publishers"):
                publisher = steamdb.get("publishers")
                doc.add_text("publisher", publisher)

            # platform
            if steamdb.get("platforms"):
                platforms = steamdb.get("platforms")
                doc.add_text("platforms", platforms)      

            # url
            if steamdb.get("website"):
                url = steamdb.get("website")
                doc.add_text("url", url) 

            # image
            if steamdb.get("publishers"):
                publisher = steamdb.get("publishers")
                doc.add_text("publisher", publisher) 

            # trailer
            if steamdb.get("movies"):
                trailer = steamdb.get("movies")
                doc.add_text("trailer", trailer) 

            # release_date
            if steamdb.get("release_date"):
                release_date = steamdb.get("release_date")
                doc.add_date("release_date", release_date) 

        else:
            print("No game results found.")
    except Exception as e:
        # Fehler in der STEAM_DB-Abfrage protokollieren, Indexierung dennoch fortsetzen
        print("STEAM_DB Error")

    # Fertiges Dokument in den Index schreiben
    writer.add_document(doc)

# === 6) Index-Änderungen finalisieren ===
writer.commit()                 # Schreibvorgänge bestätigen
writer.wait_merging_threads()   # Hintergrund-Mergeprozesse abwarten