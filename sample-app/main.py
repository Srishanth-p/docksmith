import streamlit as st

st.title("Hello from Docksmith Container")

st.write("This app is running inside a container!")

name = st.text_input("Enter your name:")

if name:
    st.success(f"Hello {name}, welcome to Docksmith!")