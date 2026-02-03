import streamlit as st
import urllib.parse as up
from typing import Any
from tantivy import Query, Index, SchemaBuilder
from streamlit.components.v1 import html

# Konstanten
INDEX_PATH = "neu"  # bestehendes Tantivy-Index-Verzeichnis
TOP_K = 60          # wie viele Ergebnisse angezeigt werden sollen


schema_builder = SchemaBuilder()
schema_builder.add_integer_field("id", stored=True, indexed=True)
schema_builder.add_integer_field("steamId", stored=True, indexed=True)
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


#Unterseiten
if view == "detail" and selected_id:
    q_t = index.parse_query(selected_id, default_field_names=["id"])
    hits = searcher.search(q_t, limit= 1).hits
    score, address = hits[0]
    doc = searcher.doc(address)


    title= doc["title"][0]
    description = doc["description"][0] if doc["description"] else "keine Angabe"
    genres = doc["genres"] if doc["genres"] else "keine Angabe"
    publisher = doc["publisher"] if doc["publisher"] else "keine Agabe"
    platforms = doc["platforms"] if doc["platforms"] else "keine Angabe"
    img = doc["image"]
    image_url = (img[0]) if img else ""
    url = doc["url"][0] if doc["url"] else "keine Angabe"
    trailer = doc["trailer"][0] if doc["trailer"] else None
    date = doc["release_date"][0] if doc["release_date"] else "keine Angabe"

    if publisher is not None:
       publisher_html = "<div>"
       for tag in publisher:
           publisher_html += f'<span class="tag">{tag}</span>'
       publisher_html += "</div>"
    
    if genres is not None:
       genre_html = "<div>"
       for tag in genres:
           genre_html += f'<span class="tag">{tag}</span>'
       genre_html += "</div>"
    
    if platforms is not None:
       platform_html = "<div>"
       for tag in platforms:
           platform_html += f'<span class="tag">{tag}</span>'
       platform_html += "</div>"


    if st.button("Zurück zur Übersicht"):
        st.query_params.update({view: "grid"})
        st.query_params.pop("id", None)
        st.rerun()
    


    st.title(title)
    st.image(image_url)

    if trailer is not None:
        html(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embedded Video Player</title>
    <link href="https://vjs.zencdn.net/8.5.2/video-js.css" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 800px;
            height: 400px;
            background: #000;
        }}

        .video-js {{
            width: 100%;
            height: 100%;
            max-height: 400px;
        }}
    </style>
</head>
<body>
<script src="https://vjs.zencdn.net/8.5.2/video.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<video id="video-player" class="video-js vjs-default-skin" controls preload="auto">
        <track id="subtitle-track" kind="subtitles" label="English" srclang="en" default>
</video>
<script>
const player = videojs('video-player', {{
            autoplay: true,
            muted: false,
            controls: true,
            preload: 'auto',
            playbackRates: [0.5, 1, 1.5, 2],
            fluid: false,
            crossOrigin: 'anonymous',
        }});
if (Hls.isSupported()) {{
            player.src({{
                src: "{trailer}",
                type: 'application/x-mpegURL'
            }});
        }} else {{
            alert('Your browser does not support HLS playback.');
        }}
</script>
</body>
</html>""", height=400, width=800)
    
    st.set_page_config(layout="wide")

    col1, col2 = st.columns(2)
    st.session_state["optionen"] = None
    st.session_state["slider"] = None
    st.session_state["checkbox"] = None
    st.session_state["text"] = None

    with col1:
        st.markdown(description, unsafe_allow_html=True)
        

    with col2:
        st.text("Genres:")
        st.markdown(genre_html, unsafe_allow_html=True)

        st.text("Publisher:")
        st.markdown(publisher_html, unsafe_allow_html=True)
        
        st.text("Für Platformen verfügbar:")
        st.markdown(platform_html, unsafe_allow_html=True)

        st.text("Link zur Website:")
        st.write(url)

        st.text("Erscheinungsdatum:")
        st.text(date)
    st.stop()


# Hauptseite
st.title("Video Spiele")

# Verarbeitet die aktuelle Anfrage (Query);
query_text = st.text_input("", value=q, placeholder="z. B. Sea of Thieves, The Witcher, etc. ...")
if st.button("Suchen", type="primary"):
    if not query_text:
        st.info("Bitte gib einen Suchbegriff ein.")
    else:
        # Speichert die Anfrageparameter und lädt die Seite erneut
        st.query_params.update({"q": up.quote(query_text, safe=''), "view": "grid"})
        st.rerun()

# Raster (Grid) darstellen, wenn q existiert
if q:
    query = Query.term_query(schema, "title", q)
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
            title = doc["title"][0]
            img = doc["image"]
            image_url = (img[0]) if img else ""
            description_short = doc["description_short"][0] if doc["description_short"] else ""
            href = f"?view=detail&id={doc_id}&q={q}"
            img_tag = f'<img src="{image_url}" loading="lazy" alt="poster">' if image_url else ""
            cards_html.append(f'<a class="card" href="{href}"target="_self">{img_tag}<div class="t">{title}</div></a>')
        cards_html.append("</div>")
        st.markdown("".join(cards_html), unsafe_allow_html=True)
else:
    st.info("Gib einen Suchbegriff ein und klicke auf **Suchen**.")