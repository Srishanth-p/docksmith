import os
import tarfile
import tempfile
import shutil
import subprocess

from image.layer_system import load_manifest, LAYERS_DIR


def extract_layer(layer_digest, rootfs):
    digest = layer_digest.replace("sha256:", "")
    tar_path = os.path.join(LAYERS_DIR, f"sha256_{digest}.tar")

    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(rootfs)


def build_rootfs(manifest):
    rootfs = tempfile.mkdtemp()

    for layer in manifest["layers"]:
        extract_layer(layer["digest"], rootfs)

    return rootfs


def run_container(image):

    name, tag = image.split(":")

    manifest = load_manifest(name, tag)

    # Build filesystem
    rootfs = build_rootfs(manifest)

    # Config
    workdir = manifest["config"]["WorkingDir"]
    env_list = manifest["config"]["Env"]
    cmd = manifest["config"]["Cmd"]

    # Setup working directory
    abs_workdir = os.path.join(rootfs, workdir.lstrip("/"))
    os.makedirs(abs_workdir, exist_ok=True)

    # Setup environment
    env = os.environ.copy()
    for e in env_list:
        key, value = e.split("=", 1)
        env[key] = value

    print(f"\nRunning container: {image}\n")

    # 🔴 ADD THIS DEBUG BLOCK HERE
    print("\n--- DEBUG: rootfs contents ---")
    for root, dirs, files in os.walk(rootfs):
        print(root)
        for f in files:
            print("   ", f)

    print("\n--- END DEBUG ---\n")

    # Run command
    subprocess.run(cmd, cwd=abs_workdir, env=env)

    # Cleanup
    shutil.rmtree(rootfs)