import pytest
from src.yt_dlp_server.main import download_video_with_cookies
from src.yt_dlp_server.userproxy import get_domain, get_cookies_file
import asyncio


@pytest.mark.asyncio
async def test_download_with_cookies():
    # 配置下载选项
    output_path = "./.pytest_cache/temp"
    url = "https://www.bilibili.com/video/BV1s2pLeTED6"
    user_proxy_id = "test_user"

    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'prefer_ffmpeg': True,
        'postprocessor_args': ['-strict', 'experimental'],  # 容许 FLAC 等实验性音频格式
    }
    ydl_args = {
        "url": url,
        "output_path": output_path,
        "ydl_opts": ydl_opts,
    }

    domain = get_domain(url)
    async with get_cookies_file(user_proxy_id, domain) as cookies_file:
        ydl_opts["cookiefile"] = cookies_file.absolute().as_posix()
        result = download_video_with_cookies(ydl_args)
    if isinstance(result, Exception):
        raise result
    else:
        assert result == "视频 'Download YouTube Video with YT-DLP Fastest Method' 下载完成，保存在 ./.pytest_cache/temp 目录"
