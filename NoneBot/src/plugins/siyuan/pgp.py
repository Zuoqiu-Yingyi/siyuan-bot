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

from pathlib import Path
import pgpy
from pgpy.constants import (
    PubKeyAlgorithm,
    EllipticCurveOID,
    KeyFlags,
    HashAlgorithm,
    SymmetricKeyAlgorithm,
    CompressionAlgorithm,
)

from .config import SiyuanConfig


class PGP:
    primary_key: pgpy.PGPKey = None
    encrypt_key: pgpy.PGPKey = None
    primary_file: Path
    encrypt_file: Path

    _config: SiyuanConfig

    def __init__(
        self,
        config: SiyuanConfig,
        pgp_primary_file: Path,
        pgp_encrypt_file: Path,
    ):
        self._config = config
        self.primary_file = pgp_primary_file
        self.encrypt_file = pgp_encrypt_file

        if not self.primary_file.exists():
            self.init_pgp_primary_key()
            self.init_pgp_encrypt_key()
            self.primary_file.write_text(str(self.primary_key))
        elif not self.primary_file.is_file():
            raise RuntimeError(f"{self.primary_file} is not a file")
        else:
            # REF: https://pgpy.readthedocs.io/en/latest/examples.html#loading-keys
            self.primary_key, _ = pgpy.PGPKey.from_file(self.primary_file)
            if len(self.primary_key.subkeys) < 1:
                self.init_pgp_encrypt_key()
            else:
                sub_key: pgpy.PGPKey
                for sub_key_id, sub_key in self.primary_key.subkeys.items():
                    if not sub_key.is_public:
                        self.encrypt_key = sub_key
                        break
                if self.encrypt_key is None:
                    self.init_pgp_encrypt_key()

    def init_pgp_primary_key(
        self,
        name: str = "思源小助手",
        comment: str = "SiYuan Bot",
        email: str = "",
    ) -> None:
        """初始化 PGP 密钥对

        若密钥不存在，则生成密钥对并保存

        Args:
            name: PGP 密钥用户名
            comment: PGP 密钥用户备注
            email: PGP 密钥用户邮箱
        """

        # 生成主密钥
        self.primary_key = pgpy.PGPKey.new(
            key_algorithm=PubKeyAlgorithm.ECDSA,
            key_size=EllipticCurveOID.Brainpool_P512,
        )
        uid = pgpy.PGPUID.new(
            pn=name,
            comment=comment,
            email=email,
        )
        self.primary_key.add_uid(
            uid,
            usage={
                KeyFlags.Sign,
                KeyFlags.EncryptCommunications,
                KeyFlags.EncryptStorage,
                KeyFlags.Authentication,
            },
            hashes=[
                HashAlgorithm.SHA224,
                HashAlgorithm.SHA256,
                HashAlgorithm.SHA384,
                HashAlgorithm.SHA512,
            ],
            ciphers=[
                SymmetricKeyAlgorithm.AES128,
                SymmetricKeyAlgorithm.AES192,
                SymmetricKeyAlgorithm.AES256,
                SymmetricKeyAlgorithm.Camellia128,
                SymmetricKeyAlgorithm.Camellia192,
                SymmetricKeyAlgorithm.Camellia256,
            ],
            compression=[
                CompressionAlgorithm.ZLIB,
                CompressionAlgorithm.BZ2,
                CompressionAlgorithm.ZIP,
                CompressionAlgorithm.Uncompressed,
            ],
        )

        # 使用口令保护密钥
        self.primary_key.protect(
            self._config.siyuan_pgp_primary_passphrase,
            SymmetricKeyAlgorithm.AES256,
            HashAlgorithm.SHA256,
        )

    def init_pgp_encrypt_key(self):
        # 生成加密密钥
        self.encrypt_key = pgpy.PGPKey.new(
            key_algorithm=PubKeyAlgorithm.ECDSA,
            key_size=EllipticCurveOID.Brainpool_P256,
        )
        self.encrypt_key.protect(
            self._config.siyuan_pgp_encrypt_passphrase,
            SymmetricKeyAlgorithm.AES256,
            HashAlgorithm.SHA256,
        )
        with self.primary_key.unlock(
            self._config.siyuan_pgp_primary_passphrase
        ) as unlock_primary_key:
            unlock_primary_key.add_subkey(
                self.encrypt_key,
                usage={
                    KeyFlags.EncryptCommunications,
                    KeyFlags.EncryptStorage,
                },
            )
