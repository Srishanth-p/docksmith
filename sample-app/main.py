import streamlit as st
import os

st.title("Hello from Docksmith Container")

st.write("This app is running inside a container! v2")
st.write("ENV VALUE:", os.getenv("KEY", "not set"))

name = st.text_input("Enter your name:")

if name:
    st.success(f"Hello {name}, welcome to Docksmith!")

with open("test.txt", "w") as f:
    f.write("created inside container")

st.write("File created!")