# Copyright (C) 2023 Zuoqiu Yingyi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from pathlib import Path
import typing as T
import uuid

from httpx._types import (
    FileTypes,
    HeaderTypes,
)
import httpx

from . import (
    audios_dir,
    images_dir,
    siyuan_config,
    videos_dir,
)
from .data import AccountModel


class BaseResponse(T.TypedDict):
    """API 响应体"""

    code: int
    msg: str
    data: T.Any


class CloudUploadData(T.TypedDict):
    """API /apis/siyuan/upload 数据"""

    succMap: dict[str, str]  # 上传成功的文件列表 (文件名: 文件 URL)
    errFiles: list[str]  # 上传失败的文件列表


class CloudUploadResponse(BaseResponse):
    """API /apis/siyuan/upload 响应体"""

    data: CloudUploadData


class Client(object):
    __clients: T.ClassVar[dict[str, "Client"]] = {}

    @classmethod
    def new(
        cls,
        account: AccountModel,
    ) -> "Client":
        client = cls.__clients.get(account.id)
        if client:
            client.account = account
        else:
            client = cls(account)
            cls.__clients[account.id] = client
        return client

    account: AccountModel
    __cloud_add_url: httpx.URL
    __cloud_upload_url: httpx.URL

    def __init__(
        self,
        account: AccountModel,
    ):
        self.account = account
        self.__cloud_add_url = httpx.URL(siyuan_config.siyuan_assets_add_url)
        self.__cloud_upload_url = httpx.URL(siyuan_config.siyuan_assets_upload_url)

    @property
    def __cloud_headers(self) -> HeaderTypes:
        """云收集箱 HTTP 请求头"""
        return {
            "Authorization": f"token {self.account.cloud.token}",
        }

    @property
    def __cloud_add_headers(self) -> HeaderTypes:
        """云收集箱 HTTP 请求头"""
        return {
            **self.__cloud_headers,
            siyuan_config.siyuan_assets_upload_user_agent_key: siyuan_config.siyuan_assets_upload_user_agent_value,
        }

    @property
    def __cloud_upload_headers(self) -> HeaderTypes:
        """云收集箱文件上传 HTTP 请求头"""
        return {
            **self.__cloud_headers,
            siyuan_config.siyuan_assets_upload_user_agent_key: siyuan_config.siyuan_assets_upload_user_agent_value,
            siyuan_config.siyuan_assets_upload_biz_type_key: siyuan_config.siyuan_assets_upload_biz_type_value,
            siyuan_config.siyuan_assets_upload_meta_type_key: siyuan_config.siyuan_assets_upload_meta_type_value,
        }

    @property
    def __service_headers(self) -> HeaderTypes:
        """思源服务收集箱 HTTP 请求头"""
        return {
            "Authorization": f"Token {self.account.service.token}",
        }

    async def __handle_response(
        self,
        response: httpx.Response,
    ):
        """处理 HTTP 响应

        Args:
            response: HTTP 响应

        Raises:
            HTTPStatusError: HTTP 状态码错误
            AssertionError: HTTP 响应错误
        """
        # 请求出错时抛出异常
        response.raise_for_status()
        response_body: dict[str, str | int] = response.json()
        code = response_body.get("code", 0)
        msg = response_body.get("msg", "Unknown error")
        assert code == 0, f"code {code}: {msg}"

    async def download(
        self,
        url: str | httpx.URL,
        type: T.Literal["image", "audio", "video"],
        name: str | None = None,
    ) -> (Path, str):
        """下载文件

        Args:
            url: 文件 URL
            dir: 下载目录
            name: 文件名

        Returns:
            Path: 下载文件路径
            str: 文件名
        """
        # 下载文件
        if not name:
            name = f"{uuid.uuid4()}.{type}"
        file_path: Path
        match type:
            case "image":
                file_path = images_dir / name
            case "audio":
                file_path = audios_dir / name
            case "video":
                file_path = videos_dir / name

        # REF: https://www.python-httpx.org/advanced/#monitoring-download-progress
        with file_path.open("wb") as f:
            # REF: https://www.python-httpx.org/async/#streaming-responses
            client = httpx.AsyncClient()
            async with client.stream("GET", url) as response:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

        return file_path, name

    async def cloudUpload(
        self,
        files: list[FileTypes],
    ) -> CloudUploadResponse:
        """上传文件到云收集箱

        Args:
            file: 文件对象
        """
        # 上传资源文件至云收集箱
        async with httpx.AsyncClient(headers=self.__cloud_upload_headers) as client:
            # 发起请求
            response = await client.post(
                url=self.__cloud_upload_url,
                files=[("file[]", file) for file in files],
            )

            # 请求出错时抛出异常
            await self.__handle_response(response)

            return response.json()

    async def addCloudShorthand(
        self,
        content: str,
        title: T.Optional[str] = None,
    ) -> httpx.Response:
        """添加一项云收集箱内容

        Args:
            content: 内容 (Markdown 格式)
            title: 标题 (若为 `YYYY-MM-DD` 格式, 则追加到今日的收集箱项, 否则新建一项)
        """

        # 设置收集箱项默认
        if title is None:
            title = datetime.now().strftime("%Y-%m-%d")

        # 添加一项云收集箱内容
        async with httpx.AsyncClient(headers=self.__cloud_add_headers) as client:
            # 发起请求
            response = await client.post(
                url=self.__cloud_add_url,
                json={
                    "title": title,
                    "content": content,
                },
            )

            # 请求出错时抛出异常
            await self.__handle_response(response)

            return response.json()
