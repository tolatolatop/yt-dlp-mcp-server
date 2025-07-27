import asyncio
import pytest
from fastmcp.client import Client
from src.yt_dlp_server.main import mcp


@pytest.mark.asyncio
async def test_tool_functionality():
    # Pass the server directly to the Client constructor
    async with Client(mcp) as client:
        result = await client.call_tool("download_video", {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        assert result.data == "Downloading video from https://www.youtube.com/watch?v=dQw4w9WgXcQ"
