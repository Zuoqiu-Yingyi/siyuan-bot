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
import re
import typing as T

from pgpy.constants import (
    CompressionAlgorithm,
    EllipticCurveOID,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)
import pgpy

from .config import SiyuanConfig


class PGP:
    primary_key: pgpy.PGPKey = None
    encrypt_key: pgpy.PGPKey = None
    primary_file: Path

    __public_key: T.Optional[str] = None

    # REF: pgpy.types.Armorable.__armor_regex
    armor_regex: re.Pattern = re.compile(
        pattern=r"""# This capture group is optional because it will only be present in signed cleartext messages
        (^-{5}BEGIN\ PGP\ SIGNED\ MESSAGE-{5}(?:\r?\n)
        (Hash:\ (?P<hashes>[A-Za-z0-9\-,]+)(?:\r?\n){2})?
        (?P<cleartext>(.*\r?\n)*(.*(?=\r?\n-{5})))(?:\r?\n)
        )?
        # armor header line; capture the variable part of the magic text
        ^-{5}BEGIN\ PGP\ (?P<magic>[A-Z0-9 ,]+)-{5}(?:\r?\n)
        # try to capture all the headers into one capture group
        # if this doesn't match, m['headers'] will be None
        (?P<headers>(^.+:\ .+(?:\r?\n))+)?(?:\r?\n)?
        # capture all lines of the body, up to 76 characters long,
        # including the newline, and the pad character(s)
        (?P<body>([A-Za-z0-9+/]{1,76}={,2}(?:\r?\n))+)
        # capture the armored CRC24 value
        ^=(?P<crc>[A-Za-z0-9+/]{4})(?:\r?\n)
        # finally, capture the armor tail line, which must match the armor header line
        ^-{5}END\ PGP\ (?P=magic)-{5}(?:\r?\n)?
        """,
        flags=re.MULTILINE | re.VERBOSE,
    )

    _config: SiyuanConfig

    def __init__(
        self,
        config: SiyuanConfig,
        pgp_primary_file: Path,
    ):
        self._config = config
        self.primary_file = pgp_primary_file

        if not self.primary_file.exists():
            self.init_keys()
            self.save_keys()
        elif not self.primary_file.is_file():
            raise RuntimeError(f"{self.primary_file} is not a file")
        else:
            # REF: https://pgpy.readthedocs.io/en/latest/examples.html#loading-keys
            self.primary_key, _ = pgpy.PGPKey.from_file(self.primary_file)
            self.add_uid()

            sub_key: pgpy.PGPKey
            for sub_key_id, sub_key in self.primary_key.subkeys.items():
                if not sub_key.is_public:
                    self.encrypt_key = sub_key
                    break
            if self.encrypt_key is None:
                self.init_keys()
                self.save_keys()

        # print(self.public_key)
        self.__test()

    def __test(self):
        pass

    def add_uid(
        self,
        name: T.Optional[str] = None,
        comment: T.Optional[str] = None,
        email: T.Optional[str] = None,
    ):
        if name is None:
            name = self._config.siyuan_pgp_name
        if comment is None:
            comment = self._config.siyuan_pgp_comment
        if email is None:
            email = self._config.siyuan_pgp_email

        uid = pgpy.PGPUID.new(
            pn=name,
            comment=comment,
            email=email,
        )
        prefs = {
            "hash": HashAlgorithm.SHA512,
            "exportable": True,
            "usage": {
                KeyFlags.Sign,
                KeyFlags.EncryptCommunications,
                KeyFlags.EncryptStorage,
                KeyFlags.Authentication,
            },
            "ciphers": [
                SymmetricKeyAlgorithm.AES128,
                SymmetricKeyAlgorithm.AES192,
                SymmetricKeyAlgorithm.AES256,
                SymmetricKeyAlgorithm.Camellia128,
                SymmetricKeyAlgorithm.Camellia192,
                SymmetricKeyAlgorithm.Camellia256,
            ],
            "hashes": [
                HashAlgorithm.SHA224,
                HashAlgorithm.SHA256,
                HashAlgorithm.SHA384,
                HashAlgorithm.SHA512,
            ],
            "compression": [
                CompressionAlgorithm.ZLIB,
                CompressionAlgorithm.BZ2,
                CompressionAlgorithm.ZIP,
                CompressionAlgorithm.Uncompressed,
            ],
        }
        with self.primary_key.unlock(self._config.siyuan_pgp_primary_passphrase) as unlock_primary_key:
            unlock_primary_key.add_uid(
                uid,
                **prefs,
            )

    def init_keys(self) -> None:
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

        # 生成加密密钥
        self.encrypt_key = pgpy.PGPKey.new(
            key_algorithm=PubKeyAlgorithm.ECDH,
            key_size=EllipticCurveOID.Brainpool_P256,
        )

        self.primary_key.add_subkey(
            self.encrypt_key,
            hash=HashAlgorithm.SHA512,
            usage={
                KeyFlags.EncryptCommunications,
                KeyFlags.EncryptStorage,
            },
        )

        # 添加用户
        self.add_uid()

        # 使用口令保护密钥
        self.primary_key.protect(
            passphrase=self._config.siyuan_pgp_primary_passphrase,
            enc_alg=SymmetricKeyAlgorithm.AES256,
            hash_alg=HashAlgorithm.SHA256,
        )
        self.primary_key.protect(
            passphrase=self._config.siyuan_pgp_primary_passphrase,
            enc_alg=SymmetricKeyAlgorithm.AES256,
            hash_alg=HashAlgorithm.SHA256,
        )

    def save_keys(self):
        """保存 PGP 密钥"""
        self.primary_file.write_text(str(self.primary_key))

    def decrypt(
        self,
        ciphertext: str,
        charset: str = "utf-8",
    ) -> str:
        # REF: https://pgpy.readthedocs.io/en/latest/examples.html#encryption
        cipher_message = pgpy.PGPMessage.from_blob(ciphertext)
        with self.encrypt_key.unlock(self._config.siyuan_pgp_primary_passphrase) as unlock_encrypt_key:
            plain_message: pgpy.PGPMessage = unlock_encrypt_key.decrypt(cipher_message)
        return plain_message.message.decode(charset)

    @property
    def public_key(self) -> str:
        if self.__public_key is None:
            self.__public_key = str(self.primary_key.pubkey)
        return self.__public_key
