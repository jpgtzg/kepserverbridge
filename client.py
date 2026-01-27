from asyncua import Client, ua, crypto
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

CLIENT_USERNAME = os.getenv("CLIENT_USERNAME")
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD")
APP_URI = os.getenv("APP_URI")
SERVER_URL = os.getenv("SERVER_URL")

CERT_PATH = "certs/client_cert.pem"
KEY_PATH  = "certs/client_key.pem"

async def main():
    client = Client(url=SERVER_URL)

    client.application_uri = APP_URI
    client.name = "kepserverbridge"

    await client.set_security(
        SecurityPolicyBasic256Sha256,
        CERT_PATH,
        KEY_PATH,
        mode=ua.MessageSecurityMode.SignAndEncrypt,
    )

    client.set_user(CLIENT_USERNAME)
    client.set_password(CLIENT_PASSWORD)

    async with client:
        print("✅ Connected to KepServer")

        root = client.nodes.root
        objects = client.nodes.objects

        print("Root:", root)
        print("Objects:", objects)

        for child in await objects.get_children():
            print(await child.read_browse_name())

if __name__ == "__main__":
    asyncio.run(main())