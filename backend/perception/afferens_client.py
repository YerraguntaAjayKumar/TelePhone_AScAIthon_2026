import json
import os

from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class AfferensClient:

    def __init__(self):

        self.server = StdioServerParameters(
            command="npx",
            args=["-y", "@afferens/mcp-server"],
            env={
                "AFFERENS_API_KEY": os.getenv("AFFERENS_API_KEY")
            }
        )

    async def get_vision(self):

        async with stdio_client(self.server) as (read, write):

            async with ClientSession(read, write) as session:

                await session.initialize()

                result = await session.call_tool(
                    "afferens_perceive",
                    arguments={
                        "modality": "VISION",
                        "limit": 1
                    }
                )

                return json.loads(result.content[0].text)