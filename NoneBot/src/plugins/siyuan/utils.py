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

import re

uri_pattern = re.compile(r"(?:(?<=\s|')|^)(\w+://[^\s']+)(?=\s|'|$)")


def desensitizeURI(
    text: str,
    placeholder: str = "[URI]",
) -> str:
    """隐藏文本中的 URI

    Args:
        text: 文本
        placeholder: 替换文本

    Returns:
        替换后的文本
    """
    return uri_pattern.sub(placeholder, text)
