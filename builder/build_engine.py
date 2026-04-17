import os
import shutil
import tempfile
import subprocess
import uuid
import hashlib
import json
import tempfile

from image.layer_system import (
    create_layer,
    store_layer,
    get_layer_size,
    create_manifest,
    add_layer,
    compute_manifest_digest,
    save_manifest,
    init_storage
)

CACHE_FILE = os.path.expanduser("~/.docksmith/cache/index.json")


# -------------------------
# Docksmithfile Parser
# -------------------------

def hash_directory(path):
    import hashlib
    sha = hashlib.sha256()

    for root, _, files in os.walk(path):
        for f in sorted(files):
            file_path = os.path.join(root, f)

            with open(file_path, "rb") as file:
                sha.update(file.read())

    return sha.hexdigest()

def parse_docksmithfile(path):
    instructions = []

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(" ", 1)
            cmd = parts[0]
            value = parts[1] if len(parts) > 1 else ""

            instructions.append((cmd, value))

    return instructions


# -------------------------
# Cache Functions
# -------------------------
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE) as f:
        return json.load(f)


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def compute_cache_key(prev_digest, instruction):
    data = prev_digest + instruction
    return hashlib.sha256(data.encode()).hexdigest()


# -------------------------
# File Snapshot
# -------------------------
def get_all_files(root):
    files = []
    for r, _, filenames in os.walk(root):
        for f in filenames:
            files.append(os.path.join(r, f))
    return files


# -------------------------
# COPY Instruction
# -------------------------
def handle_copy(value, context, rootfs, manifest, cache, prev_digest):
    import os
    import shutil
    import uuid
    import tempfile

    from image.layer_system import (
        create_layer,
        store_layer,
        get_layer_size,
        add_layer
    )

    # -------------------------
    # Parse instruction
    # -------------------------
    # -------------------------
# COPY LOGIC (FINAL FIX)
# -------------------------

    src, dest = value.split()

    abs_src = os.path.join(context, src)

    # destination inside container
    container_dest = dest.lstrip("/")   # "app"
    abs_dest = os.path.join(rootfs, container_dest)

    # ensure destination exists
    os.makedirs(abs_dest, exist_ok=True)

    # 🔴 FIX: copy INTO /app, not rootfs
    if os.path.isdir(abs_src):
        for item in os.listdir(abs_src):
            s = os.path.join(abs_src, item)
            d = os.path.join(abs_dest, item)

            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    else:
        shutil.copy2(abs_src, abs_dest)

    # -------------------------
    # Create layer
    # -------------------------
    instruction = f"COPY {value}"

    dir_hash = hash_directory(abs_src)
    cache_key = prev_digest + instruction + dir_hash

    if cache_key in cache:
        print(f"{instruction} [CACHE HIT]")
        digest = cache[cache_key]
        size = 0
    else:
        print(f"{instruction} [CACHE MISS]")

        temp_tar = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.tar")

        # collect all files in rootfs
        files = []
        for root, _, filenames in os.walk(rootfs):
            for f in filenames:
                files.append(os.path.join(root, f))

        create_layer(files, temp_tar, rootfs)

        digest, path = store_layer(temp_tar)

        size = get_layer_size(path)

        cache[cache_key] = digest

    add_layer(manifest, digest, size, instruction)

    return digest


# -------------------------
# RUN Instruction
# -------------------------
def handle_run(command, rootfs, manifest, cache, prev_digest):

    instruction = f"RUN {command}"
    cache_key = compute_cache_key(prev_digest, instruction)

    if cache_key in cache:
        print(f"{instruction} [CACHE HIT]")
        digest = cache[cache_key]
        size = 0
    else:
        print(f"{instruction} [CACHE MISS]")

        subprocess.run(command, shell=True, cwd=rootfs)

        temp_tar = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.tar")

        files = get_all_files(rootfs)

        create_layer(files, temp_tar, rootfs)

        digest, path = store_layer(temp_tar)

        size = get_layer_size(path)

        cache[cache_key] = digest

    add_layer(manifest, digest, size, instruction)

    return digest


# -------------------------
# MAIN BUILD FUNCTION
# -------------------------
def build_image(tag, context):

    init_storage()

    name, tag = tag.split(":")

    manifest = create_manifest(name, tag)

    docksmithfile_path = os.path.join(context, "Docksmithfile")
    instructions = parse_docksmithfile(docksmithfile_path)

    rootfs = tempfile.mkdtemp()

    cache = load_cache()
    prev_digest = ""

    for inst, value in instructions:

        if inst == "COPY":
            prev_digest = handle_copy(value, context, rootfs, manifest, cache, prev_digest)

        elif inst == "RUN":
            prev_digest = handle_run(value, rootfs, manifest, cache, prev_digest)

        elif inst == "WORKDIR":
            manifest["config"]["WorkingDir"] = value

        elif inst == "ENV":
            manifest["config"]["Env"].append(value)

        elif inst == "CMD":
            manifest["config"]["Cmd"] = eval(value)

        else:
            print(f"Unknown instruction: {inst}")

    save_cache(cache)

    compute_manifest_digest(manifest)
    save_manifest(manifest)

    print(f"\nSuccessfully built {name}:{tag}")