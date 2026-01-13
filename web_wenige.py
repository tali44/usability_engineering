import urllib.parse as up
from typing import Any
import streamlit as st
from tantivy import Query, Index, SchemaBuilder

import utils

# Konstanten
INDEX_PATH = "neu"  # bestehendes Tantivy-Index-Verzeichnis
TOP_K = 20          # wie viele Ergebnisse angezeigt werden sollen
CARDS_PER_PAGE = 3 # Cards, die in der zufälligen Anzeige auftauchen



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

index_path = "neu"
index = Index(schema, path=str(index_path))
searcher = index.searcher()

with open("styles.html", "r") as f:
    css = f.read()

st.markdown(css, unsafe_allow_html=True)

# Hilfsfunktion für Seitenrouting mit Anfrageparametern.
# Gibt die Query-Parameter der aktuellen Seite als Dictionary zurück.
# Falls `st.query_params` nicht verfügbar ist, wird ein leeres Dictionary zurückgegeben.
def get_qp() -> dict[str, Any]:
    return getattr(st, "query_params", {})


# (Letzte) Nutzeranfrage, die in den Session-Parametern gespeichert ist
q = get_qp().get("q", "")
view = get_qp().get("view")
selected_id = get_qp().get("id")

if view == "detail" and selected_id:
    q_t = index.parse_query(selected_id, default_field_names=["id"])
    hits = searcher.search(q_t, limit= 1).hits
    score, address = hits[0]
    doc = searcher.doc(address)
    #title= doc["title"][0]
    description_short = doc["description_short"][0] if doc["description_short"] else ""
    st.text(description_short)
    #overview_src = doc["tmdb_overview"] or doc["description"] or ""
    #overview = overview_src[0]
    #trailer = doc["trailer"]
    #genres = doc["genres"]
    #video_key = trailer[0] if trailer else ""
    
    #if genres is not None:
    #    tags_html = "<div>"
    #    for tag in genres:
    #        tags_html += f'<span class="tag">{tag}</span>'
    #    tags_html += "</div>"
    
    

    #st.title(title)
    #st.markdown(tags_html, unsafe_allow_html=True)
    #st.text(overview)
    #if video_key != "":
    #    st.video(f"https://www.youtube.com/watch?v={video_key}")

    if st.button("Zurück zur Übersicht"):
        st.query_params.update({view: "grid"})
        st.query_params.pop("id", None)
        st.rerun()
    st.stop()

# Hauptseite
st.title("Video Spiele")

# items = [10,25,33,42,102,111,124,298]
# random_cards_html = []
# for item in items:
#     q_t = index.parse_query(str(item), ["id"])
#     random_hits = searcher.search(q_t, 1).hits
#     if random_hits:
#         random_score, random_address = random_hits[0]
#         random_doc = searcher.doc(random_address)
#         print(random_doc, type(random_doc))
#         random_title = random_doc["title"][0] if random_doc["title"] else "" # Leeren String speichern, falls das Feld nicht befüllt ist.
#         random_poster = random_doc["tmdb_poster_path"]
#         if random_poster:
#             random_href = f"?view=detail&id={str(item)}&q={up.quote(q, safe='')}"
#             #random_img_url = TMDB_PATH + random_poster[0]
#             #random_img_tag = f'<img src="{random_img_url}" loading="lazy" alt="poster">'
#             #random_cards_html.append(f"""<a class="card" href="{random_href}" target="_self">{random_img_tag}<div class="t">{random_title}</div></a>""")
# utils.display_random_items(random_cards_html)

# Verarbeitet die aktuelle Anfrage (Query);
query_text = st.text_input("Suchbegriff eingeben", value=q, placeholder="z. B. Sea of Thieves, The Witcher, etc. ...")
if st.button("Suchen", type="primary"):
    if not query_text:
        st.info("Bitte gib einen Suchbegriff ein.")
    else:
        # Speichert die Anfrageparameter und lädt die Seite erneut
        st.query_params.update({"q": up.quote(query_text, safe=''), "view": "grid"})
        st.rerun()

# Raster (Grid) darstellen, wenn q existiert
if q:
    #query = Query.term_query(schema, "title", q)
    #query = Query.term_query(schema, "title", q)
    query = Query.term_query(schema, "description", q)
    hits = searcher.search(query, TOP_K).hits

    if not hits:
        st.warning("Keine Ergebnisse gefunden.")
    else:
        st.subheader("Ergebnisse")
        # Erstelle das Grid mit klickbaren Thumbnails
        cards_html = ['<div class="grid">']

        for score, addr in hits:
            doc = searcher.doc(addr)
            doc_id = doc["id"][0]
            #title = doc["title"][0]
            #poster = doc["tmdb_poster_path"]
            #poster_url = (TMDB_PATH_SMALL + poster[0]) if poster else ""
            description_short = doc["description_short"][0] if doc["description_short"] else ""
            href = f"?view=detail&id={doc_id}&q={q}"
            #img_tag = f'<img src="{poster_url}" loading="lazy" alt="poster">' if poster_url else ""
            cards_html.append(f'<a class="card" href="{href}"><div class="t">{description_short }</div></a>')
        cards_html.append("</div>")
        st.markdown("".join(cards_html), unsafe_allow_html=True)
else:
    st.info("Gib einen Suchbegriff ein und klicke auf **Suchen** (oder drücke Enter).")