#!/bin/bash
set -e

docker build -t kepserverbridge .

docker save kepserverbridge:latest -o kepserverbridge.tar
echo "Tar file generated successfully!"