import os
import contextlib
from urllib.parse import urlparse
from pathlib import Path
from tempfile import TemporaryFile
from dotenv import load_dotenv
from websockets import connect
from .schemas import CommandMessage, CommandResultMessage, ClientIdMessage, MessageType
from .schemas import Cookies

load_dotenv('.env.prod')

USER_PROXY_URL = os.getenv("USER_PROXY_URL")


async def get_cookies(user_proxy_id: str, domain: str) -> Cookies:
    """
    获取指定域名的cookies
    Args:
        user_proxy_id: 用户代理ID
        domain: 域名 example: .baidu.com
    Returns:
        CommandResultMessage: 命令执行结果
    """
    async with connect(USER_PROXY_URL) as ws:
        client_id = await ws.recv()
        client_id = ClientIdMessage.model_validate_json(client_id)
        await ws.send(CommandMessage(
            type=MessageType.COMMAND,
            client_id=client_id.client_id,
            receiver=user_proxy_id,
            command="sendCookies",
            data={"domain": domain}
        ).model_dump_json())
        response = await ws.recv()
    message = CommandResultMessage.model_validate_json(response)
    cookies = Cookies.model_validate(message.result)
    return cookies


@contextlib.asynccontextmanager
async def get_cookies_file(user_proxy_id: str, domain: str):
    """
    获取指定域名的cookies
    """
    with TemporaryFile(prefix="cookies_", suffix=".txt") as temp_file:
        cookies = await get_cookies(user_proxy_id, domain)
        temp_file.write(cookies.to_netscape_formatcookies_txt().encode())
        temp_file.seek(0)
        yield Path(temp_file.name)


def get_domain(url: str) -> str:
    """
    获取url的域名
    """
    return "." + ".".join(urlparse(url).netloc.split(".")[-2:])
