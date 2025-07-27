import asyncio
import pytest
from fastmcp.client import Client
from src.yt_dlp_server.main import mcp


@pytest.mark.asyncio
async def test_tool_functionality():
    # Pass the server directly to the Client constructor
    url = "https://www.youtube.com/watch?v=9K6wM-P5Jao"
    async with Client(mcp) as client:
        result = await client.call_tool("extract_video_info", {"url": url})
        assert result.data == "Download YouTube Video with YT-DLP Fastest Method"
