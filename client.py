from asyncua.common.node import Node
from asyncua import Client, ua
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from dotenv import load_dotenv
import os
import asyncio
from typing import Any, Awaitable, Callable, Optional

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

    node = None

    async with client:
        print("✅ Connected to KepServer")

        root = client.nodes.root
        objects = client.nodes.objects

        print("Root:", root)
        print("Objects:", objects)

        if node is None:
            node = await find_node(objects)

        if node is not None:
            print(f"Selected node: {await node.read_browse_name()}")
            while True:
                value = await node.read_value()
                print(f"Value: {value}")
                await asyncio.sleep(1)
                
async def find_node(node: Node, indent=0) -> Node:
    children = await node.get_children()

    # If len(children) is 0, we know that it is a data channel, so we need to print its values
    if len(children) == 0:
        # await dump_node_details(node, indent=indent)
        return node

    for index, child in enumerate(children):
        print(f"{'  ' * indent}{index}. {await child.read_browse_name()}")

    index = input("Enter the index of the node to print the tree (q to quit): ")

    if index == "q":
        return None 

    child = children[int(index)]

    return await find_node(child, indent+1)

if __name__ == "__main__":
    asyncio.run(main())