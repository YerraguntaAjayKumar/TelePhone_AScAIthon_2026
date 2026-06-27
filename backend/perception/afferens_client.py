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
            env={"AFFERENS_API_KEY": os.getenv("AFFERENS_API_KEY")}
        )
        self.session = None
        self._ctx = None

    async def __aenter__(self):
        self._ctx = stdio_client(self.server)
        read, write = await self._ctx.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._ctx:
            await self._ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def get_vision(self):
        """Queries your live active node feed via MCP protocol parameters."""
        if not self.session:
            raise RuntimeError("Client not initialized.")
            
        result = await self.session.call_tool(
            "afferens_perceive",
            arguments={
                "modality": "VISION",
                "limit": 1
            }
        )
        return json.loads(result.content[0].text)