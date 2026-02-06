import streamlit as st
import urllib.parse as up
from typing import Any
from tantivy import Index
from streamlit.components.v1 import html

index = Index.open("neu")
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


def load_doc_by_id(doc_id: str | int):
    """Lädt ein Dokument über das Feld 'id' und gibt Tantivy-Doc oder None zurück."""
    try:
        doc_id_int = int(doc_id)
    except (TypeError, ValueError):
        return None

    # Explizites Feld im Query-String hilft bei Numeric-Fields
    q_id = index.parse_query(f"id:{doc_id_int}", default_field_names=["id"])
    res = searcher.search(q_id, limit=1)
    if not res.hits:
        return None

    _, address = res.hits[0]
    return searcher.doc(address)


def render_tags(values):
    """Erzeugt Tag-HTML oder 'keine Angabe'."""
    if not values:
        return '<span class="muted">keine Angabe</span>'
    return "<div>" + "".join(f'<span class="tag">{v}</span>' for v in values) + "</div>"


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

    video_html = f"""<!DOCTYPE html>
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
            width: 100vw;
            height: 99vh;
            background: #000;
        }}
        .video-js {{
            width: 100%;
            height: 100%;
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
</html>""".replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;').replace("'","&#039;")
   
    html = ['<div class="layout">']

    if trailer is not None:
        iframe = f'<iframe class="trailer" srcdoc="{video_html}" allow="accelerometer; ambient-light-sensor; autoplay; battery; camera; clipboard-write; document-domain; encrypted-media; fullscreen; geolocation; gyroscope; layout-animations; legacy-image-formats; magnetometer; microphone; midi; oversized-images; payment; picture-in-picture; publickey-credentials-get; sync-xhr; usb; vr ; wake-lock; xr-spatial-tracking"></iframe>'

    html.append(f'<div class="column_l">{iframe}<p>{description}</p></div>')
    html.append(f'<div class="column_r"><p>Genres:</p><p>{genre_html}</p><p>Publisher:</p><p>{publisher_html}</p><p>Für Platformen verfügbar:</p><p>{platform_html}</p><p>Link zur Website:</p><a class="link" href="{url}"><p>{url}</p></a><p>Erscheinungsdatum:</p><p>{date}</p></div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    st.stop()

# Hauptseite
st.title("Favoriten der Redaktion")

ids = [5497, 7027, 5667, 8296, 6641, 127025, 58365, 60799, 9969, 10107]
# Titel: SteamID (id)
# SoT: 1172620 (5497)
# Raft: 648800 (7027)
# Stardew: 413150 (5667)
# CK3: 1158310 (8296)
# Overcooked 2: 728880 (6641)
# SotF: 1326470 (127025)
# Chained Together: 2567870 (58365)
# A&T Tavern: 2683150 (60799)
# Medieval Dynasty: 1129580 (9969)
# It takes Two: 1426210 (10107)

cards_html = ['<div class="grid_favs">']

num = 0

for fav_id in ids:
    doc = load_doc_by_id(fav_id)
    if doc is None:
        continue

    doc_id = doc["id"][0]
    title = doc["title"][0] 
    img = doc["image"]
    image_url = img[0] if img else ""
    description_short = doc["description_short"][0] if doc["description_short"] else ""
    href = f"?view=detail&id={doc_id}&q={up.quote_plus(str(q))}"
    img_tag = f'<img src="{image_url}" loading="lazy" alt="poster">' if image_url else ""

    num += 1
    place = f'<div class="platz">#{str(num)}</div>'
    card = f'<div class="hover"><a class="card" href="{href}" target="_self">{img_tag}<div class="t">{title}</div></a></div>'
    extra = f'<div class="extra"><p>{description_short}</p></div>'

    cards_html.append(f'<div class="num">{place}{card}{extra}</div>')
cards_html.append("</div>")
st.markdown("".join(cards_html), unsafe_allow_html=True)