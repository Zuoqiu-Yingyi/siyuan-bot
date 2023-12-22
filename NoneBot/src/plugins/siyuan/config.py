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


from pydantic import BaseModel


class SiyuanConfig(BaseModel):
    siyuan_pgp_primary_passphrase: str = ""  # PGP 主密钥保护口令
    siyuan_pgp_primary_file_name: str = "pgp-primary.pem"  # PGP 主密钥文件名

    siyuan_pgp_name: str = "思源小助手"  # PGP 密钥用户名
    siyuan_pgp_comment: str = "SiYuan Bot"  # PGP 密钥用户备注
    siyuan_pgp_email: str = ""  # PGP 密钥用户邮箱

    siyuan_assets_add_url: str = "https://ld246.com/apis/siyuan/inbox/addCloudShorthand"  # 云收集箱-内容添加地址
    siyuan_assets_upload_url: str = "https://ld246.com/apis/siyuan/upload"  # 云收集箱-资源文件上传地址

    # 业务类型
    siyuan_assets_upload_biz_type_key: str = "Biz-Type"
    siyuan_assets_upload_biz_type_value: str = "upload-assets"

    # 资源来源
    siyuan_assets_upload_meta_type_key: str = "Meta-Type"
    siyuan_assets_upload_meta_type_value: str = "5"  # SiYuan

    # 用户代理
    siyuan_assets_upload_user_agent_key: str = "User-Agent"
    siyuan_assets_upload_user_agent_value: str = "SiYuan/0.0.0"

    siyuan_data_file_name: str = "data.json"  # 数据文件名
