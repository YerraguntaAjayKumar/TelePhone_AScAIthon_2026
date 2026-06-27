import asyncio

from perception.afferens_client import AfferensClient


async def main():

    client = AfferensClient()

    data = await client.get_vision()

    print(data)


asyncio.run(main())