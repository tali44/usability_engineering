import streamlit as st
import urllib.parse as up
from typing import Any
from tantivy import Query, Index, SchemaBuilder

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
#schema_builder.add_text_field("trailer", stored=True)
schema_builder.add_date_field("release_date", stored=True)
schema = schema_builder.build()

index_path = "neu"
index = Index(schema, path=str(index_path))
searcher = index.searcher()

with open("styles.html", "r") as f:
    css = f.read()

st.markdown(css, unsafe_allow_html=True)

st.title("Favoriten der Redaktion")

index=[1, 2, 3, 4]

cards_html = ['<div class="grid">']

for i in index:
    doc = searcher.doc(i)
    doc_id = doc["id"][0]
    title = doc["title"][0]
    img = doc["image"]
    image_url = (img[0]) if img else ""
    description_short = doc["description_short"][0] if doc["description_short"] else ""
    href = f"?view=detail&id={doc_id}&q={q}"
    img_tag = f'<img src="{image_url}" loading="lazy" alt="poster">' if image_url else ""
    cards_html.append(f'<a class="card" href="{href}"target="_self">{img_tag}<div class="t">{title }</div></a>')
cards_html.append("</div>")
st.markdown("".join(cards_html), unsafe_allow_html=True)