# Created: 07.01.2020
# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import re
import unicodedata
from .exceptions import StringDecodingError

EOF = '\0'
HEX_8BIT = "{:02X}"
HEX_16BIT = "{:04X}"
HEX_32BIT = "{:08X}"
EXT_START_16 = '\\X2\\'
EXT_START_32 = '\\X4\\'
EXT_END = "\\X0\\"
EXT_ENCODING = {
    16: HEX_16BIT,
    32: HEX_32BIT,
}


def step_encoder(s: str) -> str:
    buffer = []
    encoding = 0  # 0 for no encoding, 16 for 16bit encoding, 32 for 32bit encoding
    for char in s:
        value = ord(char)
        if value < 127:  # just ASCII code
            if encoding:  # stop extended encoding
                buffer.append(EXT_END)
                encoding = 0
            if char == '\\':  # escaping backslash
                char = '\\\\'
            elif char == "'":  # escaping apostrophe
                char = "''"
            buffer.append(char)
        else:  # value > 126
            if not encoding:  # start new extended character sequence
                if value < 65536:  # 16bit character
                    encoding = 16
                    buffer.append(EXT_START_16)
                else:  # 32bit character
                    encoding = 32
                    buffer.append(EXT_START_32)
            elif value >= 65536 and encoding == 16:
                # already extended 16bit encoding, but 32bit encoding is required
                # stop 16bit encoding
                buffer.append(EXT_END)
                # and start 32bit encoding
                encoding = 32
                buffer.append(EXT_START_32)
            buffer.append(EXT_ENCODING[encoding].format(value))
    if encoding:
        buffer.append(EXT_END)
    return ''.join(buffer)


# control_directive = page | alphabet | extended2 | extended4 | arbitrary .
# page = '\S\' character  - not decoded, left as written
# alphabet = '\P' upper '\'  - not decoded, left as written
# arbitrary = '\X\' HEX_ONE  - one character, from exactly two hex digits: '\X\AE820' is '®820'
# extended2 = '\X2\' HEX_TWO { HEX_TWO } END_EXTENDED  - four hex digits a character
# extended4 = '\X4\' HEX_FOUR { HEX_FOUR } END_EXTENDED  - eight hex digits a character
# END_EXTENDED = '\X0\'
#
# A string is decoded in one pass, left to right, so a decoded character is never read again as
# the start of a directive, and the backslash of an escaped backslash '\\' never starts one.
# An '\X0\' after '\X\' and its two digits ends nothing and is dropped, as it always was.
# '\X\' and a single hex digit is an invalid encoding, which the last alternative catches.
DIRECTIVE = re.compile(r'\\(?:(\\)|X\\([0-9A-F]{2})(?:\\X0\\)?|(X[24]?)\\([0-9A-F]+)(\\X0\\)?)')


def _decode_bytes(ext_type: str, hexstr: str) -> str:
    if ext_type == 'X':
        hex_char_count = 2
    elif ext_type == 'X2':
        hex_char_count = 4
    else:
        hex_char_count = 8
    length = len(hexstr)
    if length % hex_char_count:
        raise StringDecodingError
    chars = []
    start = 0

    while start < length:
        char = chr(int(hexstr[start:start + hex_char_count], 16))
        chars.append(char)
        start += hex_char_count
    return ''.join(chars)


def is_raw_unicode_char(char: str) -> bool:
    """Return True for a character outside the 7-bit ASCII range that ISO
    10303-21-2016 allows to appear directly in a string literal, because the
    standard permits UTF-8 encoded files. Some real-world exporters rely on
    this and write non-ASCII characters directly instead of using the
    \\X2\\..\\X0\\ extended encoding -- including non-ASCII space separators
    (e.g. U+00A0 NO-BREAK SPACE), which str.isprintable() excludes even
    though they are ordinary, renderable content.
    """
    if char <= "\x7e":
        return False
    return char.isprintable() or unicodedata.category(char) == "Zs"


def step_decoder(s: str) -> str:
    if '\\' not in s:
        return s

    def decode(m) -> str:
        if m[1]:  # an escaped backslash
            return '\\'
        if m[2]:  # arbitrary
            return chr(int(m[2], 16))
        try:
            return _decode_bytes(m[3], m[4])
        except (StringDecodingError, ValueError):  # ValueError: a code point beyond U+10FFFF
            raise StringDecodingError(f'Invalid extended encoding in string "{s}".')

    return DIRECTIVE.sub(decode, s)


class StringBuffer:
    def __init__(self, buffer: str):
        self._buffer = buffer
        self._cursor = 0
        self.line_number = 1

    def look(self, n: int = 0) -> str:
        try:
            return self._buffer[self._cursor + n]
        except IndexError:
            self._cursor = len(self._buffer)
            return EOF

    def get(self) -> str:
        value = self.look()
        if value == '\n':
            self.line_number += 1
        self._cursor += 1
        return value

    def skip(self, n: int = 1) -> None:
        self._cursor += n

    def content_after_cursor(self) -> bool:
        """Return True when anything but white space and NULs is left from the cursor on."""
        return any(char > ' ' for char in self._buffer[self._cursor:])
