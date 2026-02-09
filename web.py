import urllib.parse as up
from typing import Any
import streamlit as st
from tantivy import Query, Index, SchemaBuilder


st.set_page_config(
    page_title="Videogames",
    layout="wide"
)

if "slider" not in st.session_state:
    st.session_state["slider"] = None
if "pill" not in st.session_state:
    st.session_state["pill"] = None
if "checkbox" not in st.session_state:
    st.session_state["checkbox"] = False
if "text" not in st.session_state:
    st.session_state["text"] = None
if "optionen" not in st.session_state:
    st.session_state["optionen"] = None


# Seiten festlegen
page1 = st.Page("pages/home.py", title="Home")
page2 = st.Page("pages/favs.py", title="Editor's picks")

# Navigationsstruktur festlegen
pages_config = {
    "": [page1, page2]
}

# CSS einlesen
with open("styles.html", "r") as f:
    css = f.read()
st.set_page_config(layout="wide")
st.markdown(css, unsafe_allow_html=True)

st.markdown("""<div class="header_title">Videogames</div>""", unsafe_allow_html=True)

# Navigationsstruktur erstellen
navigation = st.navigation(pages_config, position="top")
navigation.run()

st.markdown("""<div class="footer">Wintersemster 2025/26 - Usability Engineering - Talena Thielecke, Smilla Hill</div>""", unsafe_allow_html=True)