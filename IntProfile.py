import streamlit as st
def intTab(tab):
    with tab:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)