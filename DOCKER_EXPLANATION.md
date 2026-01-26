# Docker Setup Explanation

This document explains the Docker setup for beginners.

## What is Docker?

Docker packages your application and its dependencies into a **container** - a lightweight, portable environment that runs the same way everywhere. Think of it like a shipping container: your code, dependencies, and settings are all packaged together.

---

## File-by-File Explanation

### 1. Dockerfile (The Recipe)

The `Dockerfile` is like a recipe that tells Docker how to build your container image.

```dockerfile
FROM python:3.13-slim
```
**What it does:** Starts with a base image - a pre-built Linux system with Python 3.13 installed.
- `python:3.13-slim` = Official Python image, slim version (smaller size)
- This is your starting point

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```
**What it does:** Installs system-level tools needed to compile Python packages.
- `apt-get update` = Updates package list (like refreshing an app store)
- `build-essential` = C compiler and tools needed for some Python packages
- `rm -rf /var/lib/apt/lists/*` = Cleans up cache to make image smaller

```dockerfile
WORKDIR /app
```
**What it does:** Sets `/app` as the working directory (like `cd /app`).
- All commands after this run from `/app`
- Files copied go into `/app`

```dockerfile
COPY pyproject.toml ./
```
**What it does:** Copies your dependency file into the container.
- `pyproject.toml` → `/app/pyproject.toml`
- We copy this first (before code) for Docker caching optimization

```dockerfile
RUN pip install --no-cache-dir asyncua>=1.1.8 cryptography
```
**What it does:** Installs Python packages your app needs.
- `asyncua` = OPC UA library
- `cryptography` = For certificate generation
- `--no-cache-dir` = Don't save pip cache (smaller image)

```dockerfile
COPY *.py ./
```
**What it does:** Copies all Python files into the container.
- `*.py` matches all `.py` files in your project
- They go into `/app/`

```dockerfile
RUN mkdir -p certs
```
**What it does:** Creates the `certs` directory inside the container.
- `-p` = Create parent directories if needed, don't error if exists

```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
```
**What it does:** Copies and makes the entrypoint script executable.
- `chmod +x` = Makes it runnable (like making a file executable)

```dockerfile
ENTRYPOINT ["/entrypoint.sh"]
```
**What it does:** Sets the default command that runs when container starts.
- Every time the container runs, it starts with this script
- You can still pass arguments to it

---

### 2. docker-compose.yml (The Orchestrator)

Docker Compose makes it easier to run containers with configuration.

```yaml
version: '3.8'
```
**What it does:** Specifies the Docker Compose file format version.

```yaml
services:
  app:
```
**What it does:** Defines a service named "app" (your container).

```yaml
build: .
```
**What it does:** Tells Docker to build the image using the Dockerfile in current directory (`.`).

```yaml
container_name: keepserverbridge
```
**What it does:** Gives your container a friendly name instead of a random one.

```yaml
volumes:
  - ./certs:/app/certs
```
**What it does:** **This is important!** Creates a shared folder between your computer and the container.
- `./certs` = Directory on your computer
- `:/app/certs` = Directory inside the container
- **Why?** So certificates persist even after container stops/deletes
- Think of it like a shared drive or network folder

```yaml
network_mode: host
```
**What it does:** Makes the container use your computer's network directly.
- Container can access `localhost:4840` (your KepServer)
- Without this, `localhost` inside container ≠ `localhost` on your computer

```yaml
entrypoint: ["/entrypoint.sh"]
command: ["help"]
```
**What it does:** Sets what runs when container starts.
- `entrypoint` = The script that always runs
- `command` = Default argument passed to entrypoint ("help")

---

### 3. entrypoint.sh (The Command Router)

This script decides what to do based on what command you give it.

```bash
#!/bin/bash
set -e
```
**What it does:** 
- `#!/bin/bash` = Tells system to use bash to run this
- `set -e` = Exit immediately if any command fails (safety)

```bash
CMD="${1:-help}"
```
**What it does:** Gets the first argument, or defaults to "help" if none provided.
- `$1` = First command-line argument
- `${1:-help}` = Use "help" if `$1` is empty

```bash
case "$CMD" in
    cert|certificate)
        echo "🔐 Generating certificate..."
        python cert.py
        ;;
```
**What it does:** If you run `docker-compose run app cert`, it runs `python cert.py`.

```bash
    client|connect)
        echo "🔌 Connecting client..."
        if [ ! -f "certs/client_cert.pem" ] || [ ! -f "certs/client_key.pem" ]; then
            echo "⚠️  Certificate not found. Generating certificate first..."
            python cert.py
        fi
        python test_client.py
        ;;
```
**What it does:** 
- If you run `docker-compose run app client`, it:
  1. Checks if certificates exist
  2. If not, generates them first
  3. Then runs the client

```bash
    *)
        exec "$@"
        ;;
esac
```
**What it does:** If you pass any other command, it runs it directly.
- Allows you to run custom commands like `python main.py`

---

### 4. .dockerignore (The Filter)

This file tells Docker what **NOT** to copy into the container.

**Why?** 
- Makes builds faster (less to copy)
- Makes images smaller
- Prevents copying unnecessary files

**What's ignored:**
- `__pycache__/` = Python cache files
- `.venv/` = Virtual environment (not needed in container)
- `.git/` = Git history (not needed)
- `*.md` = Documentation files (not needed to run)

---

## How It All Works Together

### Building the Image

When you run `docker-compose build`:

1. Docker reads `Dockerfile`
2. Starts with Python 3.13 base image
3. Installs system packages
4. Copies your files
5. Installs Python dependencies
6. Creates a snapshot (image) of this environment

### Running the Container

When you run `docker-compose run app cert`:

1. Docker Compose reads `docker-compose.yml`
2. Starts a container from the image
3. Mounts `./certs` folder (shared between host and container)
4. Runs `/entrypoint.sh cert`
5. Entrypoint script sees "cert" command
6. Runs `python cert.py` inside the container
7. Certificate is saved to `/app/certs` (which is your `./certs` folder)

### The Flow

```
Your Computer          Docker Container
─────────────          ────────────────
./certs/      ←────→    /app/certs/     (shared via volume)
./cert.py     ─────→    /app/cert.py    (copied during build)
./test_client.py ───→   /app/test_client.py (copied during build)
```

---

## Common Commands Explained

```bash
docker-compose build
```
- Builds the image from Dockerfile
- Only needed when you change Dockerfile or dependencies

```bash
docker-compose run app cert
```
- Creates and runs a new container
- Passes "cert" to entrypoint script
- Container stops after command completes

```bash
docker-compose run app client
```
- Creates and runs a new container
- Passes "client" to entrypoint script
- Automatically generates cert if needed, then connects

```bash
docker-compose run app python main.py
```
- Runs any custom Python script
- Uses the `*)` case in entrypoint.sh

---

## Key Concepts

### Image vs Container
- **Image** = The blueprint/template (like a class in programming)
- **Container** = A running instance of an image (like an object instance)
- You build an image once, but can run many containers from it

### Volumes
- **Volume** = Shared folder between host and container
- Changes in volume persist after container stops
- Your `certs/` folder is a volume, so certificates survive container restarts

### Network Modes
- **host** = Container uses your computer's network directly
- **bridge** (default) = Container has its own isolated network
- We use `host` so container can reach `localhost:4840` on your machine

---

## Troubleshooting Tips

1. **"Certificate not found"** → Run `docker-compose run app cert` first
2. **"Can't connect to localhost"** → Make sure KepServer is running on your host
3. **"Permission denied"** → Check that entrypoint.sh is executable (should be handled by Dockerfile)
4. **Changes not appearing** → Rebuild with `docker-compose build` if you changed Dockerfile or dependencies

