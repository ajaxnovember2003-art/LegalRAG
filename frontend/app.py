import streamlit as st
import requests


st.title("⚖️ LegalRAG")

st.write(
    "Temporally-Aware Multi-Hop Retrieval-Augmented Generation "
    "Framework for Indian Legal Question Answering"
)


question = st.text_input(
    "Enter your legal question:"
)


if st.button("Ask"):

    if question:

        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={
                "question": question
            }
        )

        if response.status_code == 200:

            result = response.json()

            st.success("Response Generated")

            st.write("### Question")
            st.write(result["question"])

            st.write("### Answer")
            st.write(result["answer"])

            st.write("### Status")
            st.write(result["status"])

        else:
            st.error("Backend Error")

    else:
        st.warning("Please enter a question")