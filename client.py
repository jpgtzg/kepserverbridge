from asyncua.common.node import Node


from asyncua import Client, ua, crypto
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from asyncua.common.node import Node
from dotenv import load_dotenv
import os
import asyncio
import sys

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

        await print_tree(objects)

async def print_tree(node : Node, indent=0):
    children = await node.get_children()
    for index, child in enumerate(children):
        print(f"{'  ' * indent}{index}. {await child.read_browse_name()}")

    index = input("Enter the index of the node to print the tree (q to quit): ")

    if index == "q":
        return

    child = children[int(index)]

    await print_tree(child, indent+1)

if __name__ == "__main__":
    asyncio.run(main())