import urllib.parse as up
from typing import Any
import streamlit as st
from tantivy import Query, Index, SchemaBuilder


st.set_page_config(layout="wide")
st.session_state["slider"] = None
st.session_state["pill"] = None
st.session_state["checkbox"] = False
st.session_state["text"] = None
st.session_state["optionen"] = None
col1, col2, col3 = st.columns(3)

# Seiten festlegen
page1 = st.Page("pages/home.py", title="Home")
page2 = st.Page("pages/favs.py", title="Favoriten")
page3 = st.Page("pages/wishlist.py", title="Wunschliste")

# Navigationsstruktur festlegen
pages_config = {
    "": [page1, page2, page3]
}

# CSS einlesen
with open("styles.html", "r") as f:
    css = f.read()
st.set_page_config(layout="wide")
st.markdown(css, unsafe_allow_html=True)

# Navigationsstruktur erstellen
navigation = st.navigation(pages_config, position="top")
navigation.run()
