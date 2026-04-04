import os
import tarfile
import tempfile
import shutil
import subprocess
import sys

from image.layer_system import load_manifest, LAYERS_DIR
from runtime.container_manager import add_container, stop_container


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

    cid = add_container(image)
    print(f"Container ID: {cid}")

    # -----------------------------
    # ISOLATED EXECUTION
    # -----------------------------
    pid = os.fork()

    if pid == 0:
        try:
            print("Running inside isolated environment...\n")

            # Fix command paths
            fixed_cmd = []
            for part in cmd:
                if part.endswith(".py"):
                    fixed_cmd.append(os.path.join(rootfs, workdir.lstrip("/"), part))
                else:
                    fixed_cmd.append(part)

            subprocess.run(
                fixed_cmd,
                cwd=abs_workdir,
                env=env
            )

            os._exit(0)

        except Exception as e:
            print("Error in container:", e)
            os._exit(1)

    else:
        os.wait()
        stop_container(cid)

    # Cleanup
    shutil.rmtree(rootfs)