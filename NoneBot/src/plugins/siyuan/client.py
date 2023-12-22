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
import typing as T

from httpx._types import (
    FileTypes,
    HeaderTypes,
)
import httpx

from . import siyuan_config
from .data import AccountModel

__clients: dict[str, "Client"] = {}


class Client(object):
    @classmethod
    def new(
        cls,
        account: AccountModel,
    ) -> "Client":
        client = __clients.get(account.id)
        if client:
            client.account = account
        else:
            client = cls(account)
            __clients[account.id] = client
        return client

    account: AccountModel
    __cloud_url: httpx.URL

    def __init__(
        self,
        account: AccountModel,
    ):
        self.account = account
        self.__cloud_url = httpx.URL(siyuan_config.siyuan_assets_upload_url)

    @property
    def __cloud_headers(self) -> HeaderTypes:
        """云收集箱 HTTP 请求头"""
        return {
            "Authorization": f"token {self.account.cloud.token}",
        }

    @property
    def __cloud_upload_headers(self) -> HeaderTypes:
        """云收集箱文件上传 HTTP 请求头"""
        return {
            **self.__cloud_headers,
            siyuan_config.siyuan_assets_upload_biz_type_key: siyuan_config.siyuan_assets_upload_biz_type_value,
            siyuan_config.siyuan_assets_upload_meta_type_key: siyuan_config.siyuan_assets_upload_meta_type_value,
            siyuan_config.siyuan_assets_upload_user_agent_key: siyuan_config.siyuan_assets_upload_user_agent_value,
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

    async def cloudUpload(
        self,
        files: list[FileTypes],
    ):
        """上传文件到云收集箱

        Args:
            file: 文件对象
        """
        # 上传资源文件至云收集箱
        async with httpx.AsyncClient(headers=self.__cloud_headers) as client:
            # 发起请求
            response = await client.post(
                url=self.__cloud_url,
                headers=self.__cloud_upload_headers,
                files=[("file[]", file) for file in files],
            )

            # 请求出错时抛出异常
            self.__handle_response(response)

            return response

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
        async with httpx.AsyncClient(headers=self.__cloud_headers) as client:
            # 发起请求
            response = await client.post(
                url=self.__cloud_url,
                headers=self.__cloud_headers,
                json={
                    "title": title,
                    "content": content,
                },
            )

            # 请求出错时抛出异常
            self.__handle_response(response)

            return response
