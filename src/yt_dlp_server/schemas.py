from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """消息类型枚举"""
    COMMAND = "command"
    CLIENT_ID = "client_id"


class ClientIdMessage(BaseModel):
    """客户端ID分配消息"""
    type: MessageType = Field(MessageType.CLIENT_ID, description="消息类型")
    client_id: str = Field(..., description="分配的客户端ID")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="时间戳")


class CommandMessage(BaseModel):
    """适用于执行远程命令的消息"""
    type: MessageType = Field(MessageType.COMMAND, description="消息类型")
    client_id: str = Field(..., description="客户端ID")
    receiver: str = Field(..., description="接收命令的目标对象")
    command: str = Field(..., description="要执行的命令")
    data: Optional[Dict] = Field(None, description="命令相关的数据")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID，用于追踪")


class CommandResultMessage(BaseModel):
    """命令执行结果回传消息"""
    type: MessageType = Field(MessageType.COMMAND, description="消息类型")
    client_id: str = Field(..., description="客户端ID")
    receiver: str = Field(..., description="接收结果的目标对象")
    request_id: str = Field(..., description="对应的请求ID")
    success: bool = Field(..., description="命令执行是否成功")
    result: Optional[Dict] = Field(None, description="命令执行结果")
    error: Optional[str] = Field(None, description="错误信息（如果执行失败）")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="时间戳")


# 联合类型，用于处理所有类型的WebSocket消息
WebSocketMessage = CommandMessage | CommandResultMessage


class Cookie(BaseModel):
    """cookies"""
    name: str = Field(..., description="cookie名称")
    value: str = Field(..., description="cookie值")
    domain: str = Field(default="", description="域名")
    httpOnly: bool = Field(default=False, description="是否为httpOnly")
    secure: bool = Field(default=False, description="是否为secure")
    # 将float转换为int
    expirationDate: float = Field(default=0, description="过期时间")


class Cookies(BaseModel):
    """cookies"""
    cookies: List[Cookie] = Field(..., description="cookies")

    def to_netscape_formatcookies_txt(self):
        """转换为cookies.txt格式"""
        bodys = "#domain\tHTTP/Secure\tExpires\tName\tValue"
        for cookie in self.cookies:
            http_only = "TRUE" if cookie.httpOnly else "FALSE"
            secure = "TRUE" if cookie.secure else "FALSE"
            expiration_date = int(cookie.expirationDate)
            bodys += f"\n{cookie.domain}\t{http_only}\t{secure}\t{expiration_date}\t{cookie.name}\t{cookie.value}"
        return bodys
