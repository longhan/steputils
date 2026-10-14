
News
====

Version 0.1.2
-------------

- BUGFIX: `\X\` takes exactly two hex digits, as ISO 10303-21 (6.4.3.1) says, so `\X\AE820` decodes to `®820` and `\X\AE90` to `®90`
- BUGFIX: strings are decoded in one pass, so decoded text is never read again as a directive; a code point beyond U+10FFFF raises `StringDecodingError`
- BUGFIX: a NUL byte with content after it fails the file with "Found a NUL byte in line N: the file is corrupt."; NULs padding the end are still read as the end
- BUGFIX: line numbers after a multi-line string are right
- BUGFIX: raw UTF-8 non-ASCII characters are accepted in string literals

Version 0.1b0
-------------

- BUGFIX: [#3](https://github.com/mozman/steputils/pull/3) multiline string support

Version 0.1a5
-------------

- EXPRESS parser implemented with antlr4

Version 0.1a2
-------------

- optimized STEP-file loader and serializer, speed gain about 7x
- renamed module ``stepfile`` into ``p21`` and implemented factory functions at module level

Version 0.1a1
-------------

- pre-alpha state
- STEP-file loader and serializer works
