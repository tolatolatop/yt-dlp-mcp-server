from fastmcp import FastMCP
from yt_dlp import YoutubeDL

mcp = FastMCP(name="YoutubeDLPServer")


@mcp.tool(name="download_video")
async def download_video(url: str) -> str:
    """Download a video from a given URL."""
    with YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict["title"]


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=58000)
