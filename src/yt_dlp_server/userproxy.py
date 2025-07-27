import os
from dotenv import load_dotenv
from websockets import connect
from .schemas import CommandMessage, CommandResultMessage, ClientIdMessage, MessageType

load_dotenv('.env.prod')

USER_PROXY_URL = os.getenv("USER_PROXY_URL")


async def get_cookies(user_proxy_id: str, domain: str):
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
    return CommandResultMessage.model_validate_json(response)
