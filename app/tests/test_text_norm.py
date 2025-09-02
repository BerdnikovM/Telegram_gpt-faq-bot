from app.services.text_norm import normalize, qhash, shorten


def test_normalize():
    assert normalize("   Привет   мир  ") == "привет мир"
    assert normalize("HELLO\tWORLD") == "hello world"
    assert normalize("") == ""
    assert normalize("  Один\nДва\tТри  ") == "один два три"


def test_qhash_consistency():
    h1 = qhash("Привет")
    h2 = qhash("  привет  ")
    assert h1 == h2  # хэши совпадают, потому что normalize приводит их к одному виду
    assert len(h1) == 64  # SHA-256 всегда 64 символа hex


def test_shorten():
    text = "a" * 250
    short = shorten(text, max_len=50)
    assert len(short) == 50
    assert short.endswith("...")

    text2 = "короткий текст"
    assert shorten(text2, max_len=50) == text2
