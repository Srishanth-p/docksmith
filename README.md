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
- Container runtime (basic execution)

---

## Tech Stack

- Python 3
- OS File System APIs
- tarfile module
- hashlib (SHA256)
- subprocess

---

## Project Structure
