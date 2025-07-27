import pytest
from src.yt_dlp_server.userproxy import get_cookies


@pytest.mark.asyncio
async def test_get_cookies(cache):
    cookies = await get_cookies("test_user", ".baidu.com")
    cache.set("test_user", cookies.model_dump(mode="json"))
