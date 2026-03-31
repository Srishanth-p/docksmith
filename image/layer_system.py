import os
import tarfile
import hashlib
import json
from datetime import datetime


# Docksmith storage paths


BASE_DIR = os.path.expanduser("~/.docksmith")

LAYERS_DIR = os.path.join(BASE_DIR, "layers")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
CACHE_DIR = os.path.join(BASE_DIR, "cache")



# Initialize storage


def init_storage():

    os.makedirs(LAYERS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)



# Generate SHA256 for file


def sha256_file(path):

    sha = hashlib.sha256()

    with open(path, "rb") as f:

        while True:
            chunk = f.read(8192)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()



# Creating layer (tar archive)

def create_layer(files, output_tar, rootfs):
    import os
    import tarfile

    with tarfile.open(output_tar, "w") as tar:
        for file in sorted(files):

            # ALWAYS relative to rootfs
            arcname = os.path.relpath(file, start=rootfs)

            info = tar.gettarinfo(file, arcname=arcname)
            info.mtime = 0

            with open(file, "rb") as f:
                tar.addfile(info, f)



# Store layer in docksmith


def store_layer(temp_tar):

    digest = sha256_file(temp_tar)

    filename = "sha256_" + digest + ".tar"
    final_path = os.path.join(LAYERS_DIR, filename)

    if not os.path.exists(final_path):
        os.rename(temp_tar, final_path)
    else:
        os.remove(temp_tar)

    return digest, final_path



# Get layer size


def get_layer_size(path):

    return os.path.getsize(path)



# Create image manifest


def create_manifest(name, tag):

    manifest = {

        "name": name,
        "tag": tag,
        "digest": "",
        "created": datetime.utcnow().isoformat(),

        "config": {
            "Env": [],
            "Cmd": [],
            "WorkingDir": "/"
        },

        "layers": []
    }

    return manifest



# Add layer to manifest


def add_layer(manifest, digest, size, instruction):

    manifest["layers"].append({

        "digest": "sha256:" + digest,
        "size": size,
        "createdBy": instruction

    })


# Compute manifest hash


def compute_manifest_digest(manifest):

    manifest["digest"] = ""

    data = json.dumps(manifest, sort_keys=True).encode()

    digest = hashlib.sha256(data).hexdigest()

    manifest["digest"] = "sha256:" + digest


# Save manifest


def save_manifest(manifest):

    name = manifest["name"]
    tag = manifest["tag"]

    filename = name + "_" + tag + ".json"

    path = os.path.join(IMAGES_DIR, filename)

    with open(path, "w") as f:

        json.dump(manifest, f, indent=2)



# Load image manifest

def load_manifest(name, tag):

    filename = name + "_" + tag + ".json"

    path = os.path.join(IMAGES_DIR, filename)

    with open(path) as f:

        return json.load(f)



# List images


def list_images():

    if not os.path.exists(IMAGES_DIR):
        return

    for file in os.listdir(IMAGES_DIR):

        path = os.path.join(IMAGES_DIR, file)

        with open(path) as f:

            data = json.load(f)

        image_id = data["digest"][7:19]

        print(data["name"], data["tag"], image_id, data["created"])

# Remove image


def remove_image(name, tag):

    manifest = load_manifest(name, tag)

    for layer in manifest["layers"]:

        digest = layer["digest"].replace("sha256:", "")

        path = os.path.join(LAYERS_DIR, "sha256_" + digest + ".tar")

        if os.path.exists(path):
            os.remove(path)

    image_file = os.path.join(IMAGES_DIR, name + "_" + tag + ".json")

    if os.path.exists(image_file):
        os.remove(image_file)

