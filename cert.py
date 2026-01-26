import asyncio
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import ExtendedKeyUsageOID
from cryptography.hazmat.primitives.serialization import Encoding

from asyncua.crypto.cert_gen import (
    generate_private_key,
    dump_private_key_as_pem,
    generate_self_signed_app_certificate,
    load_private_key,
    load_certificate,
    check_certificate
)

async def main():
    key_file = Path("certs/client_key.pem")
    cert_file = Path("certs/client_cert.pem")
    app_uri = "urn:python:opcua:client"
    host_name = "localhost"
    
    # Create certs directory if it doesn't exist
    key_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate or load private key
    if key_file.exists():
        key = await load_private_key(key_file)
        generate_cert = not cert_file.exists()
        if cert_file.exists():
            cert = await load_certificate(cert_file)
            generate_cert = not check_certificate(cert, app_uri, host_name)
    else:
        key = generate_private_key()
        key_file.write_bytes(dump_private_key_as_pem(key))
        generate_cert = True
    
    # Generate certificate if needed
    if generate_cert:
        subject_alt_names = [
            x509.UniformResourceIdentifier(app_uri),
            x509.DNSName(host_name),
        ]
        
        cert = generate_self_signed_app_certificate(
            key,
            app_uri,
            {"commonName": "Python OPC UA Client"},
            subject_alt_names,
            extended=[ExtendedKeyUsageOID.CLIENT_AUTH],
            days=365
        )
        
        # Write certificate in PEM format
        cert_file.write_bytes(cert.public_bytes(encoding=Encoding.PEM))
        print("Certificate generated successfully!")
    else:
        print("Certificate already exists and is valid.")

if __name__ == "__main__":
    asyncio.run(main())
