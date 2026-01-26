#!/bin/bash
set -e

# Default command if none provided
CMD="${1:-help}"

case "$CMD" in
    cert|certificate)
        echo "🔐 Generating certificate..."
        python cert.py
        ;;
    client|connect)
        echo "🔌 Connecting client..."
        # Check if certificate exists
        if [ ! -f "certs/client_cert.pem" ] || [ ! -f "certs/client_key.pem" ]; then
            echo "⚠️  Certificate not found. Generating certificate first..."
            python cert.py
        fi
        python test_client.py
        ;;
    help)
        echo "Usage: docker-compose run app [command]"
        echo ""
        echo "Commands:"
        echo "  cert, certificate  - Generate OPC UA client certificate"
        echo "  client, connect     - Connect to KepServer (generates cert if needed)"
        echo "  help                - Show this help message"
        echo ""
        echo "Examples:"
        echo "  docker-compose run app cert"
        echo "  docker-compose run app client"
        ;;
    *)
        # Execute any other command directly
        exec "$@"
        ;;
esac

