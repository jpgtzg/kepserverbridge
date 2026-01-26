# KepServer Bridge

OPC UA client for connecting to KepServer with certificate-based security.

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed

### Building the Container

```bash
docker-compose build
```

### Usage

#### Step 1: Generate Certificate

First, generate the OPC UA client certificate:

```bash
docker-compose run app cert
```

This will create the certificate files in the `certs/` directory:
- `certs/client_cert.pem`
- `certs/client_key.pem`

#### Step 2: Connect Client

After generating the certificate, connect to the KepServer:

```bash
docker-compose run app client
```

The client will automatically generate a certificate if one doesn't exist.

### Alternative: Direct Python Execution

You can also run Python scripts directly in the container:

```bash
# Generate certificate
docker-compose run app python cert.py

# Connect client
docker-compose run app python test_client.py
```

### Network Configuration

The container uses `host` network mode to connect to `localhost:4840`. If your KepServer is running on a different host, you may need to:

1. Update `test_client.py` with the correct server URL
2. Change `network_mode: host` in `docker-compose.yml` to a bridge network if needed

## Local Development

If you prefer to run locally without Docker:

```bash
# Install dependencies (using uv or pip)
uv sync
# or
pip install -r pyproject.toml

# Generate certificate
python cert.py

# Connect client
python test_client.py
```

