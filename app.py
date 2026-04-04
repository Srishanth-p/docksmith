import streamlit as st
import subprocess
import json
import os

from builder.build_engine import build_image
from runtime.container import run_container
from image.layer_system import list_images
from runtime.container_manager import list_containers

st.set_page_config(page_title="Docksmith UI", layout="wide")

st.title("Docksmith Container System")

# Sidebar
st.sidebar.header("Actions")
option = st.sidebar.selectbox(
    "Choose Action",
    ["Build Image", "Run Container", "View Images", "View Containers"]
)

# -----------------------
# BUILD IMAGE
# -----------------------
if option == "Build Image":
    st.header("Build Image")

    tag = st.text_input("Image Tag (name:tag)", "myapp:latest")
    context = st.text_input("Build Context", "sample-app")

    if st.button("Build"):
        st.write("Building image...")
        build_image(tag, context)
        st.success("Build complete")

# -----------------------
# RUN CONTAINER
# -----------------------
elif option == "Run Container":
    st.header("Run Container")

    image = st.text_input("Image name:tag", "myapp:latest")

    if st.button("Run"):
        st.write("Running container...")
        run_container(image)
        st.success("Container finished")

# -----------------------
# VIEW IMAGES
# -----------------------
elif option == "View Images":
    st.header("Images")

    images_dir = os.path.expanduser("~/.docksmith/images")

    if os.path.exists(images_dir):
        for file in os.listdir(images_dir):
            path = os.path.join(images_dir, file)
            with open(path) as f:
                data = json.load(f)

            st.write({
                "name": data["name"],
                "tag": data["tag"],
                "created": data["created"]
            })
    else:
        st.write("No images found")

# -----------------------
# VIEW CONTAINERS
# -----------------------
elif option == "View Containers":
    st.header("Containers")

    container_file = os.path.expanduser("~/.docksmith/containers.json")

    if os.path.exists(container_file):
        with open(container_file) as f:
            data = json.load(f)

        st.table(data)
    else:
        st.write("No containers found")