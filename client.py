from asyncua import Client, ua, crypto
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
import asyncio

CERT_PATH = "certs/client_cert.pem"
KEY_PATH  = "certs/client_key.pem"

async def main():
    async with Client(url="opc.tcp://192.168.1.160:4840/freeopcua/server/") as client:
        await client.set_security(
            SecurityPolicyBasic256Sha256(),
            CERT_PATH,  
            KEY_PATH,
            mode=ua.MessageSecurityMode.SignAndEncrypt,
        )

        client.set_user("admin")
        client.set_password("admin")

        async with client:
            print("✅ Connected to KepServer")

            root = client.nodes.root
            objects = client.nodes.objects

            print("Root:", root)
            print("Objects:", objects)

            # Example browse
            for child in await objects.get_children():
                print(await child.read_browse_name())

if __name__ == "__main__":
    asyncio.run(main())