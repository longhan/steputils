import pytest

from steputils.strings import step_encoder, step_decoder, StringDecodingError, StringBuffer, EOF


def test_buffer():
    b = StringBuffer('test')
    assert b.look() == 't'
    assert b.look(1) == 'e'
    assert b.get() == 't'
    assert b.look() == 'e'
    assert b.get() == 'e'
    assert b.get() == 's'
    assert b.get() == 't'
    assert b.get() == EOF
    assert b.get() == EOF
    assert b.get() == EOF
    assert b.look() == EOF
    assert b.look(3) == EOF


def test_string_encoder():
    assert step_encoder('ABC') == 'ABC'
    assert step_encoder('"') == '"'
    assert step_encoder("'") == "''"
    assert step_encoder('\'') == '\'\''
    assert step_encoder('\\') == '\\\\'
    assert step_encoder('ABCÄ') == 'ABC\\X2\\00C4\\X0\\'
    assert step_encoder('ABCÄÖ') == 'ABC\\X2\\00C400D6\\X0\\'
    assert step_encoder('CÄÖC') == 'C\\X2\\00C400D6\\X0\\C'
    assert step_encoder('CÄ\\ÖC') == 'C\\X2\\00C4\\X0\\\\\\\\X2\\00D6\\X0\\C'
    assert step_encoder('CÄ\'ÖC') == 'C\\X2\\00C4\\X0\\\'\'\\X2\\00D6\\X0\\C'


def test_string_decoder():
    assert step_decoder('ABC') == 'ABC'
    assert step_decoder("\"") == "\""
    assert step_decoder("'") == "'"
    assert step_decoder("''") == "''", "Apostrophe decoding has to be done by the lexer."
    assert step_decoder("x''x") == "x''x"
    assert step_decoder("x\"x") == "x\"x"
    assert step_decoder("\\\\") == "\\"
    assert step_decoder("x\\\\x") == "x\\x"
    assert step_decoder('ABC\\X2\\00C4\\X0\\') == 'ABCÄ'
    assert step_decoder('ABC\\X2\\00C400D6\\X0\\') == 'ABCÄÖ'
    assert step_decoder('C\\X2\\00C400D6\\X0\\C') == 'CÄÖC'
    assert step_decoder('C\\X2\\00C4\\X0\\\\\\\\X2\\00D6\\X0\\C') == 'CÄ\\ÖC'
    # does not decode escaped apostrophes '
    assert step_decoder('C\\X2\\00C4\\X0\\\'\'\\X2\\00D6\\X0\\C') == 'CÄ\'\'ÖC'


def test_extended_string_decoderx2():
    assert step_decoder("\\X2\\00E4\\X0\\") == '\u00E4'


def test_extended_string_decoder_multi_x2():
    assert step_decoder("\\X2\\00E400E4\\X0\\") == '\u00E4\u00E4'


def test_extended_string_decoder_x4():
    assert step_decoder("\\X4\\000000E4\\X0\\") == '\u00E4'


def test_extended_string_decoder_x4_beyond_16bit():
    assert step_decoder("\\X4\\0001F600\\X0\\") == '\U0001F600'


def test_extended_string_decoder_error():
    # invalid count of hex chars
    pytest.raises(StringDecodingError, step_decoder, "\\X2\\0E4\\X0\\")
    pytest.raises(StringDecodingError, step_decoder, "\\X2\\123\\X0\\")
    pytest.raises(StringDecodingError, step_decoder, "\\X4\\00000E4\\X0\\")
    # every group is decoded, so an invalid one raises even after a valid one like it
    pytest.raises(StringDecodingError, step_decoder, "\\X2\\0041 \\X2\\0041A\\X0\\")


def test_extended_string_decoder_error_beyond_unicode():
    with pytest.raises(StringDecodingError, match='Invalid extended encoding in string'):
        step_decoder("\\X4\\00110000\\X0\\")


def test_arbitrary_string_decoder():
    assert step_decoder('\\X\\C4') == 'Ä'
    assert step_decoder('\\X\\C4\\X\\D6') == 'ÄÖ'
    # an end of extended encoding after it ends nothing, and is dropped
    assert step_decoder('\\X\\C4\\X0\\') == 'Ä'


@pytest.mark.parametrize('s, expected', [
    # strings of Sandvik Coromant's GTC package: '\X\' is followed by exactly two hex digits, any
    # digit after them is text
    ('CoroBore\\X\\AE820\\X2\\752830B730E030BB30C330C8\\X0\\', 'CoroBore®820用シムセット'),
    ('\\X2\\53EF4E506EE1\\X0\\Capto\\X\\AE90\\X\\B0\\X2\\7F295F8463A56746\\X0\\', '可乐满Capto®90°缩径接杆'),
    ('FL\\X\\C4CHE2', 'FLÄCHE2'),
    ('C5_390.5804_50 \\X\\0D100_6_stp-None', 'C5_390.5804_50 \r100_6_stp-None'),
    ('CoroBore\\X\\AEBR20', 'CoroBore®BR20'),
])
def test_arbitrary_string_decoder_takes_two_hex_digits(s, expected):
    assert step_decoder(s) == expected


def test_arbitrary_string_decoder_error():
    # a single hex digit
    pytest.raises(StringDecodingError, step_decoder, "x\\X\\A y")
    pytest.raises(StringDecodingError, step_decoder, "x\\X\\A")


def test_string_decoder_decodes_in_one_pass():
    # a decoded backslash does not start a directive
    assert step_decoder('\\X\\5C\\X\\5C') == '\\\\'
    assert step_decoder('\\X\\5CX2\\0041\\X0\\') == '\\X2\\0041\\X0\\'
    # nor does the backslash of an escaped backslash
    assert step_decoder('\\\\X2\\00C4\\X0\\') == '\\X2\\00C4\\X0\\'
    assert step_decoder('\\\\\\X2\\00C4\\X0\\') == '\\Ä'
    assert step_decoder('\\X\\\\X\\41') == '\\X\\X\\41'


if __name__ == '__main__':
    pytest.main([__file__])
