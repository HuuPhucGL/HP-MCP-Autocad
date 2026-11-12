"""Kiểm thử đọc kết quả LISP có tên layer tiếng Việt (lỗi phát hiện khi chạy với AutoCAD 2023 thật)."""

from autocad_mcp.backends.file_ipc import doc_ket_qua_json


def test_json_hop_le_giu_nguyen():
    assert doc_ket_qua_json('{"ok":true,"payload":"pong"}') == {"ok": True, "payload": "pong"}


def test_unicode_acad_chua_thoat():
    # LISP bản cũ ghi thẳng tên layer: 1.M\U+1EA2NH -> JSON không hợp lệ
    raw = '{"ok":true,"payload":{"layers":["0","1.M\\U+1EA2NH","1.\\U+0110ÈN"]}}'
    kq = doc_ket_qua_json(raw)
    assert kq["payload"]["layers"] == ["0", "1.MẢNH", "1.ĐÈN"]


def test_unicode_acad_da_thoat():
    # LISP bản HP thoát dấu \ : 1.M\\U+1EA2NH -> giải mã sau khi đọc
    raw = '{"ok":true,"payload":{"layers":["1.M\\\\U+1EA2NH"]}}'
    assert doc_ket_qua_json(raw)["payload"]["layers"] == ["1.MẢNH"]


def test_dau_gach_le_trong_duong_dan():
    raw = '{"ok":true,"payload":{"path":"D:\\Ban ve\\a.dwg"}}'
    assert doc_ket_qua_json(raw)["payload"]["path"] == "D:\\Ban ve\\a.dwg"
