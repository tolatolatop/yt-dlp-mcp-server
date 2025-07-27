import os
import asyncio

from yt_dlp_server.logs import logger

from fastmcp import FastMCP
from yt_dlp import YoutubeDL
from yt_dlp_server.userproxy import get_cookies_file
from yt_dlp_server.userproxy import get_domain

mcp = FastMCP(name="YoutubeDLPServer")


@mcp.tool(name="download_video")
async def download_video(url: str) -> str:
    """Download a video from a given URL."""
    output_path: str = os.getenv("OUTPUT_PATH")
    user_proxy_id: str = os.getenv("USER_PROXY_ID")
    logger.info(f"开始下载视频: {url}")
    os.makedirs(output_path, exist_ok=True)

    progress_queue: asyncio.Queue = asyncio.Queue()

    # ⏳ 启动后台任务异步处理进度日志
    progress_task = asyncio.create_task(progress_consumer(progress_queue))

    # 配置下载选项
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [make_progress_hook(progress_queue)],
        'format': 'bestvideo+bestaudio/best',
    }

    ydl_args = {
        "url": url,
        "output_path": output_path,
        "ydl_opts": ydl_opts,
    }

    try:
        if user_proxy_id:
            domain = get_domain(url)
            async with get_cookies_file(user_proxy_id, domain) as cookies_file:
                ydl_opts["cookiefile"] = cookies_file.absolute().as_posix()
                result = await asyncio.to_thread(download_video_with_cookies, ydl_args)
        else:
            result = await asyncio.to_thread(download_video_with_cookies, ydl_args)
    finally:
        # ✅ 通知 consumer 退出
        await progress_queue.put(None)
        await progress_task  # 等待后台处理完毕

    return result


def make_progress_hook(queue: asyncio.Queue):
    """返回一个闭包，将 yt_dlp 的下载事件转发到 async queue"""

    def hook(d: dict):
        try:
            queue.put_nowait(d)
        except Exception as e:
            logger.warning(f"无法推送进度: {e}")

    return hook


async def progress_consumer(queue: asyncio.Queue):
    """异步处理下载进度，适合输出日志或上报状态"""

    while True:
        d = await queue.get()
        if d is None:
            break  # 终止信号

        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                if speed and speed > 0:
                    speed_mb = speed / 1024 / 1024
                    logger.info(
                        f"下载进度: {percent:.1f}% - 速度: {speed_mb:.2f} MB/s - 剩余时间: {eta}秒")
                else:
                    logger.info(f"下载进度: {percent:.1f}% - 剩余时间: {eta}秒")
            else:
                downloaded = d.get('downloaded_bytes', 0) / 1024 / 1024
                logger.info(f"已下载: {downloaded:.2f} MB")
        elif d['status'] == 'finished':
            logger.info(f"下载完成: {d['filename']}")
        elif d['status'] == 'error':
            logger.error(f"下载错误: {d.get('error', '未知错误')}")


def download_video_with_cookies(ydl_args: dict):
    url = ydl_args["url"]
    output_path = ydl_args["output_path"]
    ydl_opts = ydl_args["ydl_opts"]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # 先获取视频信息
            logger.info("正在获取视频信息...")
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Unknown Title')
            logger.info(f"视频标题: {title}")

            # 开始下载
            logger.info("开始下载视频文件...")
            ydl.download([url])

            logger.info(f"视频下载完成: {title}")
            return f"视频 '{title}' 下载完成，保存在 {output_path} 目录"

    except Exception as e:
        error_msg = f"下载失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(name="extract_video_info")
async def extract_video_info(url: str) -> str:
    """Extract video information from a given URL."""
    logger.info(f"正在获取视频信息: {url}")

    try:
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Unknown Title')
            duration = info_dict.get('duration', 0)
            uploader = info_dict.get('uploader', 'Unknown')
            view_count = info_dict.get('view_count', 0)

            info = f"标题: {title}\n上传者: {uploader}\n时长: {duration}秒\n观看次数: {view_count}"
            logger.info(f"视频信息获取成功: {title}")
            return info

    except Exception as e:
        error_msg = f"获取视频信息失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=58000)
