# KepServer Bridge

Dockerized OPC UA client that connects securely to KepServerEX using
certificate-based security and username/password authentication.

The container automatically generates and persists OPC UA client certificates and is designed to be built locally and run on a remote (even offline) machine.

## Docker Setup

### Prerequisites
- Docker installed

## Build the Image (Development Machine)

From the project root:

```bash
docker build -t kepserverbridge .
```

## Export the Image for a Remote Machine

Save the built image to a .tar file:

This can be done running the following script:

```bash
./generate_tar.sh
```

Or manually:

```bash
docker build -t kepserverbridge .
docker save kepserverbridge:latest -o kepserverbridge.tar
```

## Import the Image on a Remote Machine

Transfer the following files to the remote machine:
- ```kepserverbridge.tar```
- ```docker-compose.yml```


## Load and Run the Container on a Remote Machine

From the remote machine, load the image from the tar file:

```bash
docker load -i kepserverbridge.tar
```

Then run the container with docker compose:

```bash
docker compose up
```

The docker compose file will mount the certs volume to the container, so you don't need to generate the certificates again.
It iwll generate the certificates if they don't exist.

## Certificates and First Run Behavior

- Client certificates are stored in a named Docker volume
- On first startup, the container:
    - Automatically generates a client certificate if none exists
    - Reuses the same certificate on subsequent runs and restarts
- On first connection, KepServerEX will reject the client certificate

## KepServerEX (one-time step)

- Open OPC UA Configuration on the KepServerEX machine
- Set the client certificate to Trusted
- Retry the connection to KepServerEX