from fastmcp import FastMCP

mcp = FastMCP(name="YoutubeDLPServer")


@mcp.tool(name="download_video")
async def download_video(url: str) -> str:
    """Download a video from a given URL."""
    return f"Downloading video from {url}"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=58000)
