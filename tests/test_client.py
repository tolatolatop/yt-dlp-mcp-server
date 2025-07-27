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
        assert "标题: Download YouTube Video with YT-DLP Fastest Method\n" in result.data


@pytest.mark.asyncio
async def test_download_video():
    # Pass the server directly to the Client constructor
    url = "https://www.youtube.com/watch?v=9K6wM-P5Jao"
    async with Client(mcp) as client:
        output_path = "./.pytest_cache/temp"
        result = await client.call_tool("download_video", {"url": url})
        assert result.data == "视频 'Download YouTube Video with YT-DLP Fastest Method' 下载完成，保存在 ./.pytest_cache/temp 目录"


@pytest.mark.asyncio
async def test_download_video_with_cookies():
    # Pass the server directly to the Client constructor
    url = "https://www.youtube.com/watch?v=g0C4CsititQ"
    async with Client(mcp) as client:
        result = await client.call_tool("download_video", {"url": url})
        assert result.data == "视频 'Download YouTube Video with YT-DLP Fastest Method' 下载完成，保存在 ./.pytest_cache/temp 目录"
