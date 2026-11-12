# Nhật ký thay đổi

## 3.2.0+hp.2 (08/11/2026)

Sửa lỗi phát hiện khi chạy thử với AutoCAD 2023 thật (bản đầy đủ, Windows 11).

- **Treo khi bản vẽ có layer tên tiếng Việt.** AutoCAD trả tên layer dạng `\U+1EA2`, LISP ghi thẳng vào
  JSON nên file kết quả không hợp lệ; máy chủ chờ tới hết giờ rồi báo Timeout.
  - `mcp_dispatch.lsp`: `drawing-info` thoát ký tự đặc biệt trong tên layer.
  - `file_ipc.py`: hàm `doc_ket_qua_json` đổi `\U+XXXX` thành chữ thật, chịu được dấu `\` lẻ.
- **In PDF báo thành công nhưng không ra file.** Lệnh `-PLOT` bản gốc thiếu câu trả lời bước plot offset
  nên lệch prompt. Viết lại: in Model, khổ A3 ngang (`ISO_full_bleed_A3`), đơn vị mm, Extents, Fit,
  Center, in theo CTB (mặc định `monochrome.ctb`, đổi bằng biến `HP_MCP_CTB`), tắt in nền, Zoom
  Extents trước khi in, và kiểm tra file PDF thực sự được tạo.
- Kết quả trả về giữ nguyên chữ tiếng Việt (không còn dạng `à`).
- Thêm `tests/test_hp_doc_ket_qua.py`. Tổng 165 kiểm thử đạt.
- Đã chạy thử với AutoCAD 2023: kết nối, đọc bản vẽ 1.892 đối tượng có layer tiếng Việt, vẽ line,
  polyline, chữ tiếng Việt, kích thước, batch, lưu file mới, in PDF A3, zoom, chụp màn hình,
  và 5 chốt an toàn.

## 3.2.0+hp.1 (07/11/2026)

Bản đầu tiên của HP MCP AutoCAD, dựa trên vn-autocad-claude 3.2.0.

- Chốt an toàn `hp_an_toan`:
  - `drawing create` không chạy trên bản vẽ đang có đối tượng nếu thiếu `data.xac_nhan_xoa = true`.
  - `drawing save`, `save_as_dxf`, `plot_pdf` không ghi đè file có sẵn, không lưu đè bản vẽ đang mở
    nếu thiếu `data.ghi_de = true`; trả về tên gợi ý dạng `YYMMDD - tên file`.
  - `system execute_lisp` chặn đoạn LISP có lệnh xóa (ERASE, entdel, vl-file-delete, PURGE...)
    nếu thiếu `data.cho_phep_xoa = true`.
  - `system batch` không nhận `drawing-create`, `execute-lisp`, `drawing-purge`, batch lồng nhau;
    lệnh `entity-erase` cần `data.cho_phep_xoa = true`.
  - Biến môi trường `HP_MCP_TAT_AN_TOAN=1` tắt toàn bộ chốt (không khuyến khích).
- Chế độ ezdxf: bản vẽ mới mặc định đơn vị mm (`$INSUNITS = 4`), hệ mét.
- Tên máy chủ MCP: `hp-mcp-autocad`. Tên gói: `hp-mcp-autocad`.
- README tiếng Việt, thêm `NOTICE.md`.
- Bỏ `uv.lock` cũ và file DXF mẫu trong `tests/golden` (tạo lại bằng `tests/generate_golden.py` khi cần).
