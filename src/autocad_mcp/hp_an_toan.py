"""Chốt an toàn của HP MCP AutoCAD.

Bổ sung bởi Nguyễn Hữu Phúc (2026) so với bản gốc, theo quy định làm việc:
  1. Không xóa sạch bản vẽ đang có nội dung khi người dùng chưa xác nhận.
  2. Không ghi đè file đã có khi người dùng chưa xác nhận; gợi ý tên mới
     dạng "YYMMDD - Tên file".
  3. Không chạy AutoLISP hoặc batch có thao tác xóa khi người dùng chưa xác nhận.

Cách mở khóa có chủ đích (người dùng phải đồng ý trước):
  - drawing create:              data.xac_nhan_xoa = true
  - drawing save / save_as_dxf / plot_pdf ghi đè file có sẵn: data.ghi_de = true
  - system execute_lisp / batch có lệnh xóa: data.cho_phep_xoa = true
  - Tắt toàn bộ chốt (không khuyến khích): biến môi trường HP_MCP_TAT_AN_TOAN=1
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

# Lệnh trong batch luôn bị chặn: xóa sạch bản vẽ, chạy LISP tùy ý, batch lồng nhau.
LENH_BATCH_CAM = {"drawing-create", "execute-lisp", "batch", "drawing-purge"}
# Lệnh trong batch cần xác nhận: xóa đối tượng.
LENH_BATCH_XOA = {"entity-erase"}

# Mẫu AutoLISP có thao tác xóa đối tượng hoặc xóa file.
_MAU_LISP_XOA = re.compile(
    r"""(\(\s*entdel\b)                       # (entdel ...)
      | (\(\s*vl-file-delete\b)                # (vl-file-delete ...)
      | (\(\s*vla-delete\b)                    # (vla-delete ...)
      | (\(\s*vla-erase\b)
      | (["']_?\.?_?erase["'])                 # (command "_.ERASE" ...)
      | (["']_?\.?_?-?purge["'])               # (command "_.-PURGE" ...)
      | (["']_?\.?_?del["'])
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _bat(ten: str) -> bool:
    return os.environ.get(ten, "").strip().lower() in ("1", "true", "yes", "on")


def tat_an_toan() -> bool:
    """True khi người dùng chủ động tắt toàn bộ chốt an toàn."""
    return _bat("HP_MCP_TAT_AN_TOAN")


def ten_goi_y(path: str, hom_nay: date | None = None) -> str:
    """Gợi ý tên file mới: 'YYMMDD - <tên cũ bỏ tiền tố ngày>.<đuôi>', không trùng file có sẵn."""
    p = Path(path)
    ngay = (hom_nay or date.today()).strftime("%y%m%d")
    goc = re.sub(r"^\d{6}\s*-\s*", "", p.stem)
    ung_vien = p.with_name(f"{ngay} - {goc}{p.suffix}")
    i = 2
    while ung_vien.exists():
        ung_vien = p.with_name(f"{ngay} - {goc} ({i}){p.suffix}")
        i += 1
    return str(ung_vien)


def _tu_choi(ly_do: str, huong_dan: str, **them) -> dict:
    d = {"ok": False, "error": f"[HP an toàn] {ly_do}", "hint": huong_dan}
    d.update(them)
    return d


def kiem_tra_ghi_de(path: str | None, data: dict) -> dict | None:
    """Trả về lời từ chối nếu thao tác lưu sẽ ghi đè file có sẵn mà chưa được xác nhận."""
    if tat_an_toan() or data.get("ghi_de"):
        return None
    if not path:
        return _tu_choi(
            "Lưu không kèm đường dẫn sẽ ghi đè lên file bản vẽ đang mở.",
            "Hỏi người dùng. Nên lưu thành file mới (data.path) với tên bắt đầu bằng ngày YYMMDD. "
            "Chỉ khi người dùng đồng ý ghi đè mới gọi lại với data.ghi_de = true.",
        )
    if Path(path).exists():
        return _tu_choi(
            f"File đã tồn tại: {path}",
            "Không ghi đè file có sẵn. Dùng tên gợi ý, hoặc hỏi người dùng; "
            "chỉ khi người dùng đồng ý mới gọi lại với data.ghi_de = true.",
            goi_y_ten_moi=ten_goi_y(path),
        )
    return None


def kiem_tra_xoa_sach(so_doi_tuong: int | None, data: dict) -> dict | None:
    """Trả về lời từ chối nếu drawing create sẽ xóa bản vẽ đang có nội dung."""
    if tat_an_toan() or data.get("xac_nhan_xoa"):
        return None
    if so_doi_tuong is None or so_doi_tuong > 0:
        return _tu_choi(
            f"drawing create sẽ XÓA TOÀN BỘ {so_doi_tuong if so_doi_tuong is not None else 'các'} đối tượng trong bản vẽ đang mở.",
            "Không xóa nội dung có sẵn. Hãy mở hoặc tạo một bản vẽ trống trong AutoCAD. "
            "Chỉ khi người dùng đồng ý xóa sạch mới gọi lại với data.xac_nhan_xoa = true.",
            so_doi_tuong=so_doi_tuong,
        )
    return None


def kiem_tra_lisp(code: str, data: dict) -> dict | None:
    """Trả về lời từ chối nếu đoạn AutoLISP có thao tác xóa mà chưa được xác nhận."""
    if tat_an_toan() or data.get("cho_phep_xoa"):
        return None
    m = _MAU_LISP_XOA.search(code or "")
    if m:
        return _tu_choi(
            f"Đoạn AutoLISP có thao tác xóa: {m.group(0).strip()}",
            "Hỏi người dùng trước. Chỉ khi người dùng đồng ý mới gọi lại với data.cho_phep_xoa = true.",
        )
    return None


def kiem_tra_batch(commands: list[dict], data: dict) -> dict | None:
    """Trả về lời từ chối nếu batch có lệnh bị cấm hoặc lệnh xóa chưa được xác nhận."""
    if tat_an_toan():
        return None
    ten = [str((c or {}).get("command", "")).strip().lower() for c in commands or []]
    cam = sorted({t for t in ten if t in LENH_BATCH_CAM})
    if cam:
        return _tu_choi(
            f"Batch không được chứa lệnh: {', '.join(cam)}",
            "Gọi các lệnh này riêng lẻ qua công cụ tương ứng để chốt an toàn kiểm tra.",
        )
    xoa = [t for t in ten if t in LENH_BATCH_XOA]
    if xoa and not data.get("cho_phep_xoa"):
        return _tu_choi(
            f"Batch có {len(xoa)} lệnh xóa đối tượng.",
            "Hỏi người dùng trước. Chỉ khi người dùng đồng ý mới gọi lại với data.cho_phep_xoa = true.",
        )
    return None
