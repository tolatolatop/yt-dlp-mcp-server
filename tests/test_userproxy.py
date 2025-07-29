import pytest
import asyncio
import json
from .conftest import USER_PROXY_URL
from src.yt_dlp_server.userproxy import get_cookies
from src.yt_dlp_server.schemas import CommandMessage, MessageType, ClientIdMessage
from websockets import connect


@pytest.mark.asyncio
async def test_get_cookies(cache):
    cookies = await get_cookies("test_user", ".youtube.com")
    cache.set("test_user-cookies-json", cookies.model_dump(mode="json"))


@pytest.mark.asyncio
async def test_common_fetch(cache):
    command = CommandMessage(
        type=MessageType.COMMAND,
        client_id="test_user",
        receiver="test_user",
        command="commonFetch",
        data={
            "url": "https://www.youtube.com/watch?v=9K6wM-P5Jao",
            "method": "GET",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
        },
    )

    cache_lines = []
    async with connect(USER_PROXY_URL) as ws:
        hello = await ws.recv()
        client_message = ClientIdMessage.model_validate_json(hello)
        cache_lines.append(json.loads(hello))
        command.client_id = client_message.client_id
        await ws.send(command.model_dump_json())
        response = await asyncio.wait_for(ws.recv(), timeout=10)
        cache_lines.append(json.loads(response))
    cache.set("test_user-common_fetch-json", cache_lines)
