"""Kiểm thử chốt an toàn của bản HP (chạy ở chế độ ezdxf, không cần AutoCAD)."""

import json
from datetime import date

import pytest

from autocad_mcp import client, hp_an_toan, server


@pytest.fixture(autouse=True)
def backend_ezdxf(monkeypatch):
    monkeypatch.setenv("AUTOCAD_MCP_BACKEND", "ezdxf")
    monkeypatch.delenv("HP_MCP_TAT_AN_TOAN", raising=False)
    monkeypatch.setattr("autocad_mcp.config.detect_backend", lambda: "ezdxf")
    monkeypatch.setattr("autocad_mcp.client.detect_backend", lambda: "ezdxf")
    client._backend = None
    yield
    client._backend = None


def _doc(kq):
    return json.loads(kq if isinstance(kq, str) else kq[0].text)


# --- Hàm thuần ---

def test_ten_goi_y_them_ngay(tmp_path):
    f = tmp_path / "250101 - Nha pho.dwg"
    assert hp_an_toan.ten_goi_y(str(f), date(2026, 11, 7)).endswith("261107 - Nha pho.dwg")


def test_ten_goi_y_khong_trung(tmp_path):
    (tmp_path / "261107 - A.dxf").write_text("x")
    kq = hp_an_toan.ten_goi_y(str(tmp_path / "A.dxf"), date(2026, 11, 7))
    assert kq.endswith("261107 - A (2).dxf")


@pytest.mark.parametrize("code", [
    '(command "_.ERASE" (entlast) "")',
    "(entdel (entlast))",
    '(vl-file-delete "C:/a.dwg")',
    '(command "_.-PURGE" "_ALL" "*" "_N")',
])
def test_lisp_xoa_bi_chan(code):
    assert hp_an_toan.kiem_tra_lisp(code, {}) is not None
    assert hp_an_toan.kiem_tra_lisp(code, {"cho_phep_xoa": True}) is None


def test_lisp_thuong_duoc_chay():
    assert hp_an_toan.kiem_tra_lisp('(command "_.LINE" "0,0" "100,0" "")', {}) is None


def test_batch():
    assert hp_an_toan.kiem_tra_batch([{"command": "drawing-create"}], {"cho_phep_xoa": True}) is not None
    assert hp_an_toan.kiem_tra_batch([{"command": "entity-erase"}], {}) is not None
    assert hp_an_toan.kiem_tra_batch([{"command": "entity-erase"}], {"cho_phep_xoa": True}) is None
    assert hp_an_toan.kiem_tra_batch([{"command": "create-line"}], {}) is None


def test_tat_an_toan(monkeypatch):
    monkeypatch.setenv("HP_MCP_TAT_AN_TOAN", "1")
    assert hp_an_toan.kiem_tra_lisp("(entdel (entlast))", {}) is None


# --- Qua công cụ MCP ---

async def test_create_tren_ban_ve_trong_duoc_phep():
    assert _doc(await server.drawing(operation="create"))["ok"] is True


async def test_create_tren_ban_ve_co_noi_dung_bi_chan():
    await server.entity(operation="create_line", x1=0, y1=0, x2=1000, y2=0)
    kq = _doc(await server.drawing(operation="create"))
    assert kq["ok"] is False and "HP an toàn" in kq["error"]
    kq = _doc(await server.drawing(operation="create", data={"xac_nhan_xoa": True}))
    assert kq["ok"] is True


async def test_khong_ghi_de_file_co_san(tmp_path):
    f = tmp_path / "ban-ve.dxf"
    assert _doc(await server.drawing(operation="save", data={"path": str(f)}))["ok"] is True
    kq = _doc(await server.drawing(operation="save", data={"path": str(f)}))
    assert kq["ok"] is False and "goi_y_ten_moi" in kq
    kq = _doc(await server.drawing(operation="save", data={"path": str(f), "ghi_de": True}))
    assert kq["ok"] is True


async def test_luu_khong_duong_dan_bi_chan():
    kq = _doc(await server.drawing(operation="save"))
    assert kq["ok"] is False


async def test_ban_ve_moi_don_vi_mm():
    await server.drawing(operation="create")
    be = await client.get_backend()
    assert be._doc.header["$INSUNITS"] == 4
    assert be._doc.header["$MEASUREMENT"] == 1
