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
    siyuan_pgp_encrypt_passphrase: str = ""  # PGP 加密密钥保护口令
    siyuan_pgp_primary_file_name: str = "pgp-primary.pem"  # PGP 主密钥文件名
    siyuan_pgp_encrypt_file_name: str = "pgp-encrypt.pem"  # PGP 加密密钥文件名

    siyuan_data_file_name: str = "data.json"  # 数据文件名
