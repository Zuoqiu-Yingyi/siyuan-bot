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

from enum import Enum
import typing as T
from pathlib import Path
from pydantic import BaseModel

T_account = T.Dict[str, T.Any]
T_accounts = T.Dict[str, T_account]


class CloudModel(BaseModel):
    """ 推送至云收集箱

    POST 请求 https://ld246.com/apis/siyuan/inbox/addCloudShorthand
    ```json
    {
        "title": "A simple text title",
        "content": "Content with **Markdown**."
    }
    ```
    - `title` 格式为 `YYYY-MM-DD` 时间戳时 `content` 内容可以追加到末尾
    - 鉴权方案为 `Authorization: token <token>`
    """

    enable: bool  # 是否启用
    token: str


class ServiceModel(BaseModel):
    """ 推送至思源内核服务 """

    enable: bool  # 是否启用
    baseURI: str  # 思源内核服务地址
    token: str  # 思源内核服务 token
    notebook: str  # 指定作为收集箱的思源笔记本, 文档使用 API `/api/filetree/createDailyNote` 创建


class InboxMode(Enum):
    """ 收集箱默认模式 """
    none: int = 0  # 未启用收集箱
    cloud: int = 1  # 云收集箱
    service: int = 2  # 思源内核服务收集箱


class AccountModel(BaseModel):
    id: int | str
    mode: InboxMode
    cloud: CloudModel
    service: ServiceModel


class SiyuanModel(BaseModel):
    accounts: T.Dict[int | str, AccountModel]
    

class Data:
    data_file: Path
    model: SiyuanModel

    def __init__(
        self,
        data_file: Path,
    ):
        self.data_file = data_file
        if data_file.exists() and data_file.is_file():
            self.model = SiyuanModel.parse_file(data_file)
        else:
            self.model = SiyuanModel(accounts=dict())
    
    def save(self):
        self.data_file.write_text(self.model.json(indent=4, ensure_ascii=False))
