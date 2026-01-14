import streamlit as st

st.set_page_config(layout="wide")
st.session_state["slider"] = None
st.session_state["pill"] = None
st.session_state["checkbox"] = False
st.session_state["text"] = None
st.session_state["optionen"] = None
col1, col2, col3 = st.columns(3)

with col1:
    st.title("Spalte 1")
    st.color_picker("Farbe auswählen", "#044c38")
    optionen = st.multiselect(
        "Was magst du?",
        [
            "Pizza", "Pasta", "Döner", "Sushi", "Veggie"
        ],
        default=["Veggie"]
    )
    st.session_state["optionen"] = optionen

with col2:
    st.title("Spalte 2")
    with st.form("mein_formular"):
        st.write("Das ist mein Formular!")
        slider_val = st.slider("Temperatur", 0.0, 2.0, (0.4))
        checkbox_val = st.checkbox("Checkbox")
        text_val = st.text_input(label="Ihre Eingabe", placeholder="Bitte schreiebn Sie hier Ihren Kommentar!")
        pill = st.pills("Genre",
                        [
                            "Action", "Shooter", "Adventure"
                        ],
                        selection_mode="multi")
        submitted = st.form_submit_button("Submit")
        # Der Nutzer hat auf den Button geklickt
        if submitted:
            st.session_state["slider"] = slider_val
            st.session_state["pill"] = pill
            st.session_state["checkbox"] = checkbox_val
            st.session_state["text"] = text_val

with col3:
    st.title("Spalte 3")
    st.write("Slider-Wert:", st.session_state["slider"])
    st.write("Optionen", st.session_state["optionen"])
    st.write("Genre", st.session_state["pill"])
    st.write("Checkbox", st.session_state["checkbox"])
    with st.expander("Hier derKommentar!:"):
        st.write("Text", st.session_state["text"])