from action_pack.extractor import extract_text_from_path, extract_text_from_upload


def test_extract_text_from_plain_text_path(tmp_path):
    sample = tmp_path / "notice.txt"
    sample.write_text("Council notice\nPay by 30 June 2026", encoding="utf-8")
    assert "Pay by 30 June 2026" in extract_text_from_path(sample)


def test_extract_text_from_upload_rejects_unsupported_suffix():
    try:
        extract_text_from_upload("file.exe", b"bad")
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("Expected unsupported suffix error")
