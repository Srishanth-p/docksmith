# Docksmith – A Lightweight Docker-like Container Engine

Docksmith is a simplified containerization system inspired by Docker.  
It allows users to build images from a Docksmithfile, store them using a layered filesystem, and run them as containers.

This project demonstrates core containerization concepts such as image building, layer management, caching, and runtime execution.

---

## Overview

Docksmith implements the fundamental ideas behind container systems:

- Parsing a build file (Docksmithfile)
- Creating layered filesystem snapshots
- Using content-addressable storage (SHA256)
- Reconstructing filesystems at runtime
- Executing container commands

---

## Features

- Build images from a Docksmithfile  
- Layered filesystem using tar archives  
- SHA256-based layer hashing and deduplication  
- Build cache support (CACHE HIT / MISS)  
- Image manifest system  
- Command Line Interface (CLI)
  - build
  - run
  - images
  - rmi
  - ps (container tracking)
- Container runtime with basic process isolation (Linux/WSL)

---

## Tech Stack

- Python 3
- OS File System APIs
- tarfile module
- hashlib (SHA256)
- subprocess
- Linux process control (fork)

---

## Project Structure

docksmith/
├── builder/           # Build engine (parsing + instructions)
├── image/             # Layer storage + manifest system
├── runtime/           # Container runtime + manager
├── sample-app/        # Example application (Streamlit)
├── docksmith.py       # CLI entry point

---

## Requirements

- Python 3.8+
- Linux or WSL (recommended)
- pip installed

---

## Setup Instructions

### 1. Clone the repository

git clone https://github.com/your-username/docksmith.git  
cd docksmith

---

### 2. Create a virtual environment

python3 -m venv ~/.docksmith-venv  
source ~/.docksmith-venv/bin/activate

---

### 3. Install dependencies

pip install streamlit

---

## How to Run Docksmith

### Start CLI

python3 docksmith.py

---

### Build an image

docksmith> build -t myapp:latest sample-app

---

### Run a container

docksmith> run myapp:latest

If using the sample Streamlit app, open:

http://localhost:8501

---

### List images

docksmith> images

---

### Remove image

docksmith> rmi myapp:latest

---

### List containers

docksmith> ps

---

## Example Docksmithfile

WORKDIR /app  
COPY . /app  
RUN echo "Hello from Docksmith"  
CMD ["python3", "-m", "streamlit", "run", "main.py"]

---

## Notes & Limitations

- Dependencies are installed on the host system (not fully isolated)
- Requires Linux/WSL for process isolation (fork)
- Not a full replacement for Docker, but demonstrates core concepts

---

## Future Improvements

- Full dependency isolation (virtual environments per container)
- Better filesystem isolation (chroot + namespaces)
- Networking support
- Volume mounting
- Web UI for container management

---

## Conclusion

Docksmith successfully replicates the fundamental workflow of container systems:

Build → Store → Run

It serves as an educational implementation of how container engines like Docker work internally.