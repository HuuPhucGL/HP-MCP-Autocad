# Ghi công và thông báo sửa đổi

HP MCP AutoCAD là bản sửa đổi, phát hành theo giấy phép MIT (xem `LICENSE`), dựa trên:

- **autocad-mcp** của puran-water: https://github.com/puran-water/autocad-mcp (MIT)
- **vn-autocad-claude** của andyluu98: https://github.com/andyluu98/vn-autocad-claude (MIT),
  bổ sung hiển thị tiếng Việt, lệnh batch và hỗ trợ AutoCAD for Mac.

Toàn bộ mã gốc, gồm máy chủ Python và file `lisp-code/mcp_dispatch.lsp`, giữ nguyên bản quyền
của các tác giả trên.

## Phần sửa đổi bởi Nguyễn Hữu Phúc (2026)

- Thêm `src/autocad_mcp/hp_an_toan.py`: chốt an toàn không xóa sạch bản vẽ, không ghi đè file,
  không chạy lệnh xóa khi người dùng chưa xác nhận.
- Gắn chốt an toàn vào công cụ `drawing` (create, save, save_as_dxf, plot_pdf) và `system`
  (execute_lisp, batch) trong `server.py`.
- Bản vẽ mới ở chế độ không cần AutoCAD (ezdxf) mặc định đơn vị mm, hệ mét.
- Đổi tên gói thành `hp-mcp-autocad`, tài liệu tiếng Việt, thêm kiểm thử `tests/test_hp_an_toan.py`.
- Không kèm file bản vẽ mẫu (DXF) và file khóa phiên bản của bản gốc.
