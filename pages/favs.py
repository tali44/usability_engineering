import streamlit as st
import urllib.parse as up
from typing import Any
from tantivy import Index
from detail import render_detail_page

index = Index.open("neu")
searcher = index.searcher()

with open("styles.html", "r") as f:
    css = f.read()
st.markdown(css, unsafe_allow_html=True)

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
    """Erzeugt Tag-HTML oder 'no data'."""
    if not values:
        return '<span class="muted">no data</span>'
    return "<div>" + "".join(f'<span class="tag">{v}</span>' for v in values) + "</div>"


# Unterseite
if view == "detail" and selected_id:
    q_t = index.parse_query(f"id:{selected_id}", default_field_names=["id"])
    hits = searcher.search(q_t, limit=1).hits

    if not hits:
        st.error("Game not found.")
        st.stop()

    score, address = hits[0]
    doc = searcher.doc(address)

    render_detail_page(doc, q)
    st.stop()



# Hauptseite
st.title("Editor's picks")

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