import streamlit as st


st.set_page_config(
    page_title="Steamerino",
    page_icon="",
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


page1 = st.Page("pages/home.py", title="Home")
page2 = st.Page("pages/favs.py", title="Editor's Favorites")


pages_config = {
    "": [page1, page2]
}

with open("styles.html", "r") as f:
    css = f.read()
st.set_page_config(layout="wide")
st.markdown(css, unsafe_allow_html=True)

st.markdown("""<div class="header_title">Steamerino</div>""", unsafe_allow_html=True)

with st.popover("Evaluation", width="content"):
    st.markdown("""
        <div style="width: 35vw; height: 80vh">
            <iframe 
                src="https://docs.google.com/forms/d/e/1FAIpQLSfqjkIZ-trBClutW2ZNTn4-Hn0CqJJtIZMZCbuRV7BlHE9p1g/viewform?embedded=true"
                width="100%" 
                height="100%" 
                frameborder="0"
                style="overflow:hidden;">
            </iframe>
        </div>
    """, unsafe_allow_html=True)

navigation = st.navigation(pages_config, position="top")
navigation.run()

st.markdown("""<footer>Wintersemster 2025/26 - Usability Engineering - Talena Thielecke, Smilla Hill</footer>""", unsafe_allow_html=True)