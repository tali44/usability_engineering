import streamlit as st
from typing import Any
from tantivy import Index
from detail import render_detail_page

# Konstanten
TOP_K = 100          # Anzahl der Ergebnisse, die angezeigt werden sollen

#Tokenisierung um in der Suche auch nach Wortteilen suchen zu können
def ngrams(word, n=3):
    word = word.lower()
    return [word[i:i+n] for i in range(len(word)-n+1)]

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

if st.session_state.get("reset_all"):
    st.session_state["search_input"] = ""
    st.query_params.clear()
    q = ""
    st.session_state["genres_pills"] = []
    st.session_state["modus_pills"] = []

    st.session_state["reset_all"] = False



# Unterseite
if view == "detail" and selected_id:
    q_t = index.parse_query(selected_id, default_field_names=["id"])
    hits = searcher.search(q_t, limit=1).hits

    if not hits:
        st.error("Game not found.")
        st.stop()

    score, address = hits[0]
    doc = searcher.doc(address)
    render_detail_page(doc, q)


# Hauptseite
st.title("Videogames")

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:

    col_input, col_button, col_clear= st.columns([5, 1, 1])

    with col_input:
        query_text = st.text_input("", value=q, placeholder="Search a game e. g. Sea of Thieves, The Witcher, etc. ...", label_visibility="collapsed", key="search_input")

    with col_button:
        button_triggered = st.button("Search", type="primary", key="search_button", width="stretch")

    with col_clear:
        clear_triggered = st.button("Clear", key="clear_button", width="stretch")

    if clear_triggered:
        st.session_state["reset_all"] = True
        st.rerun()

    genre_opt = ["Action", "Adventure", "Casual", "Indie", "Racing", "RPG", "Simulation", "Strategy"]
    modus_opt = ["Multiplayer", "Free to play"]
    selected_genres = st.pills("Genres", genre_opt, selection_mode="multi", label_visibility="collapsed", width="stretch", key="genres_pills")
    selected_modus = st.pills("Modus", modus_opt, selection_mode="multi", label_visibility="collapsed", width="stretch", key="modus_pills")


enter_triggered = query_text != q and query_text != ""

if enter_triggered or button_triggered:
    st.query_params.update({"q": query_text, "view": "grid"})
    st.rerun()


if q or selected_genres or selected_modus:
    # Titel-Suche
    words = q.lower().split() if q else []
    query_parts = []

    for w in words:
        if len(w) < 3:
            query_parts.append(f"title_ngrams:{w}")
        else:
            grams = ngrams(w, 3)
            part = " AND ".join([f"title_ngrams:{g}" for g in grams])
            query_parts.append(f"({part})")

    # Genre-Suche
    genre_filters = []
    if selected_genres:
        for g in selected_genres:
            genre_filters.append(f'genres:"{g}"')

    # Modus-Suche
    modus_filters = []
    if selected_modus:
        for m in selected_modus:
            modus_filters.append(f'genres:"{m}"')

    # Suchen kombinieren
    all_filters = []

    if query_parts:
        all_filters.append("(" + " AND ".join(query_parts) + ")")

    if genre_filters:
        all_filters.append("(" + " AND ".join(genre_filters) + ")")

    if modus_filters:
        all_filters.append("(" + " AND ".join(modus_filters) + ")")

    final_query = " AND ".join(all_filters)
    query = index.parse_query(final_query)
    hits = searcher.search(query, TOP_K).hits

    if not hits:
        st.markdown("<div class='keineTitel'><p>No games found!</p></div>", unsafe_allow_html=True)
    else:
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
            genres = doc["genres"] if doc["genres"] else "no data"

            if genres is not None:
                genre_html = "<div>"
                for tag in genres:
                    genre_html += f'<span class="tag">{tag}</span>'
                genre_html += "</div>"

            extra = f'<div class="extra"><p>{description_short}{genre_html}</p></div>'       
            card = f'<div class="hover"><a href="{href}" target="_self">{img_tag}<div class="text"><div class="t">{title}</div>{extra}</div></a></div>'

            cards_html.append(f'<div class="suche card">{card}</div>')
        cards_html.append("</div>")
        st.markdown("".join(cards_html), unsafe_allow_html=True)