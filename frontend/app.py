import streamlit as st
import requests


st.title("⚖️ LegalRAG")

st.write(
    "Temporally-Aware Multi-Hop Retrieval-Augmented Generation "
    "for Indian Legal Question Answering"
)


query = st.text_input(
    "Ask your legal question:"
)


if st.button("Submit"):

    if query:
        response = requests.get(
            "http://127.0.0.1:8000"
        )

        if response.status_code == 200:
            data = response.json()

            st.success("Backend Connected Successfully")

            st.json(data)

        else:
            st.error("Backend connection failed")

    else:
        st.warning("Please enter a question")