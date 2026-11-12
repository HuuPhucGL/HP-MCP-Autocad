# HP MCP AutoCAD

Máy chủ MCP cho phép Claude (Claude Desktop, Claude Code) điều khiển AutoCAD đang mở: vẽ, sửa,
ghi kích thước, chèn block, chụp màn hình, lưu và xuất PDF. Không có AutoCAD thì vẫn tạo được
file DXF ở chế độ ezdxf.

Bản này do **Nguyễn Hữu Phúc** biên soạn, sửa đổi. Giấy phép MIT; nguồn gốc và bản quyền gốc: xem NOTICE.md và LICENSE.
Ghi công chi tiết: [NOTICE.md](NOTICE.md).

## Khác gì bản gốc

| Mục | Bản gốc | Bản HP |
|---|---|---|
| `drawing create` | Xóa toàn bộ đối tượng và purge ngay | Từ chối nếu bản vẽ đang có đối tượng, trừ khi người dùng xác nhận |
| Lưu, xuất DXF, in PDF | Ghi đè nếu file đã có | Không ghi đè; gợi ý tên mới `YYMMDD - tên file` |
| `execute_lisp` | Chạy mọi đoạn LISP | Chặn đoạn có lệnh xóa (ERASE, entdel, vl-file-delete, PURGE...) khi chưa xác nhận |
| `batch` | Nhận mọi lệnh trong danh sách cho phép | Không nhận lệnh xóa sạch, LISP tùy ý, batch lồng nhau; lệnh xóa đối tượng cần xác nhận |
| Bản vẽ mới (ezdxf) | Không đặt đơn vị | Đơn vị mm, hệ mét |
| Layer tên tiếng Việt | Treo, báo Timeout | Đọc đúng (`1.MẢNH`, `1.ĐÈN`...) |
| In PDF | Khổ Letter inch, lệch prompt, báo thành công dù không ra file | Khổ A3 ngang, mm, in theo CTB, kiểm tra file PDF đã tạo |
| Tài liệu | Tiếng Anh | Tiếng Việt |

Chi tiết: [CHANGELOG.md](CHANGELOG.md).

## Yêu cầu

- Windows 10/11
- AutoCAD bản đầy đủ, hoặc AutoCAD LT 2024 trở lên trên Windows (LT có AutoLISP từ bản 2024)
- Python 3.10 trở lên (Python Windows, không dùng Python trong WSL)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) và Git

Chế độ ezdxf (không cần AutoCAD) chạy được trên mọi hệ điều hành.

## Cài đặt

### 1. Tải mã và cài thư viện

```powershell
git clone https://github.com/HuuPhucGL/HP-MCP-Autocad.git
cd HP-MCP-Autocad
uv sync
```

> **Nên đặt thư mục repo ở đường dẫn không dấu**, ví dụ `C:\HP-MCP-Autocad`. AutoLISP nạp file từ
> đường dẫn có chữ tiếng Việt có dấu dễ lỗi.

### 2. Nạp file trung gian vào AutoCAD

1. Mở AutoCAD, tạo một bản vẽ mới.
2. Gõ `APPLOAD`, chọn `lisp-code/mcp_dispatch.lsp`, bấm **Load**.
3. Dòng lệnh báo `=== MCP Dispatch v3.1 loaded ===` là xong.
4. Thêm file vào **Startup Suite** trong hộp thoại APPLOAD để lần sau AutoCAD tự nạp.

### 3. Khai báo MCP cho Claude

Tạo file `.mcp.json` ở thư mục gốc dự án (Claude Code, tab Code của Claude Desktop):

```json
{
  "mcpServers": {
    "hp-mcp-autocad": {
      "command": "C:\\duong-dan\\HP-MCP-Autocad\\.venv\\Scripts\\python.exe",
      "args": ["-m", "autocad_mcp"],
      "env": { "AUTOCAD_MCP_BACKEND": "auto" }
    }
  }
}
```

Thay `C:\\duong-dan\\` bằng đường dẫn thật. Hoặc dùng lệnh:

```powershell
claude mcp add hp-mcp-autocad -- C:\duong-dan\HP-MCP-Autocad\.venv\Scripts\python.exe -m autocad_mcp
```

`AUTOCAD_MCP_BACKEND`: `auto` (mặc định, có AutoCAD thì dùng, không thì chuyển ezdxf),
`file_ipc` (bắt buộc AutoCAD), `ezdxf` (không cần AutoCAD).

### 4. Kiểm tra

Thoát hẳn Claude rồi mở lại, mở phiên mới và hỏi:

> Kiểm tra kết nối MCP với AutoCAD: đang mở bản vẽ nào, đơn vị gì, đang chạy chế độ nào.

Kết nối đúng thì Claude báo `backend: file_ipc`.

## Chốt an toàn

Mỗi khi gặp chốt, máy chủ trả về lỗi `[HP an toàn]` kèm hướng dẫn, để Claude dừng lại hỏi người dùng.

| Thao tác | Khi nào bị chặn | Mở khóa (chỉ khi người dùng đồng ý) |
|---|---|---|
| `drawing create` | Bản vẽ đang có đối tượng | `data.xac_nhan_xoa = true` |
| `drawing save` không kèm đường dẫn | Luôn chặn (sẽ lưu đè bản vẽ đang mở) | `data.ghi_de = true` |
| `drawing save`, `save_as_dxf`, `plot_pdf` | File đích đã tồn tại | `data.ghi_de = true` |
| `system execute_lisp` | Đoạn LISP có lệnh xóa | `data.cho_phep_xoa = true` |
| `system batch` | Có `entity-erase` | `data.cho_phep_xoa = true` |
| `system batch` | Có `drawing-create`, `execute-lisp`, `drawing-purge`, `batch` | Không mở khóa; gọi riêng từng công cụ |

Biến môi trường `HP_MCP_TAT_AN_TOAN=1` tắt toàn bộ chốt. Không khuyến khích.

Nên ghi thêm vào CLAUDE.md của dự án:

> Chỉ vẽ đúng phần tôi yêu cầu. Không xóa đối tượng có sẵn trong bản vẽ. Trước khi sửa bản vẽ có sẵn, lưu bản sao vào _backup.

## Công cụ

| Công cụ | Việc làm được |
|---|---|
| `drawing` | Tạo, mở, xem thông tin, lưu, xuất DXF, in PDF, purge, đọc biến hệ thống, undo, redo |
| `entity` | Vẽ line, circle, polyline, rectangle, arc, ellipse, mtext, hatch; liệt kê, đếm, đọc; copy, move, rotate, scale, mirror, offset, array, fillet, chamfer, erase |
| `layer` | Liệt kê, tạo, đặt hiện hành, đổi thuộc tính, freeze, thaw, lock, unlock |
| `block` | Liệt kê, chèn, chèn kèm thuộc tính, đọc và sửa thuộc tính, định nghĩa block (ezdxf) |
| `annotation` | Chữ, kích thước thẳng, xiên, góc, bán kính, đường dẫn ghi chú |
| `pid` | Sơ đồ công nghệ đường ống (cần thư viện CTO) |
| `view` | Zoom toàn bộ, zoom cửa sổ, chụp màn hình bản vẽ |
| `system` | Trạng thái, kiểm tra, khởi tạo lại, `execute_lisp`, `batch` (nhiều lệnh trong một lần, một nhóm undo) |

## Cách hoạt động

```
Claude
  │  MCP qua stdio
  ▼
Máy chủ Python (autocad_mcp) ── chốt an toàn hp_an_toan
  │
  ├── file_ipc ──► C:/temp/*.json ──► mcp_dispatch.lsp trong AutoCAD
  └── ezdxf    ──► tạo DXF trong bộ nhớ, không cần AutoCAD
```

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `AUTOCAD_MCP_BACKEND` | `auto` | `auto`, `file_ipc`, `ezdxf` |
| `AUTOCAD_MCP_IPC_DIR` | `C:/temp` | Thư mục trao đổi file lệnh (phải khớp phía LISP) |
| `AUTOCAD_MCP_IPC_TIMEOUT` | `10.0` | Thời gian chờ mỗi lệnh, giây (1–300) |
| `AUTOCAD_MCP_ONLY_TEXT` | `false` | Tắt chụp màn hình |
| `HP_MCP_TAT_AN_TOAN` | tắt | `1` để tắt chốt an toàn |
| `HP_MCP_CTB` | `monochrome.ctb` | File CTB dùng khi in PDF (in theo màu) |

## In PDF

`drawing plot_pdf` in không gian Model ra PDF khổ **A3 ngang**, đơn vị mm, phạm vi Extents, Fit, căn giữa,
in theo CTB. Muốn dùng CTB riêng, đặt biến `HP_MCP_CTB` (ví dụ `HP-KT-A3.ctb`) và để file CTB trong thư mục
Plot Styles của AutoCAD. Máy chủ chỉ báo thành công khi file PDF thực sự được tạo.

## Lưu ý đơn vị

Bản vẽ mới tạo từ mẫu `acad.dwt` dùng đơn vị inch. Nên tạo bản vẽ từ `acadiso.dwt` hoặc file `.dwt` hệ mét
của công ty, để chữ và kích thước đúng tỷ lệ mm.

## Lỗi hay gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Claude chờ rất lâu | AutoCAD chưa mở, chưa nạp `mcp_dispatch.lsp`, hoặc đang mở hộp thoại |
| Luôn ra `ezdxf` dù AutoCAD đang mở | Yêu cầu Claude khởi tạo lại kết nối (`system init`); vẫn lỗi thì nạp lại LSP |
| Ảnh chụp bản vẽ toàn màu đen | Cửa sổ AutoCAD đang thu nhỏ |
| Claude không thấy `hp-mcp-autocad` | Chưa mở phiên mới, hoặc `.mcp.json` sai thư mục, sai đường dẫn |

## Đã chạy thử

AutoCAD 2023 bản đầy đủ trên Windows 11 (08/11/2026): kết nối, đọc bản vẽ có layer tiếng Việt, vẽ line,
polyline, chữ tiếng Việt, kích thước, batch, lưu file mới, in PDF A3, zoom, chụp màn hình và các chốt an
toàn đều đạt. Chưa thử AutoCAD LT và AutoCAD for Mac.

## AutoCAD for Mac

Bản gốc có hỗ trợ thử nghiệm AutoCAD bản đầy đủ trên Mac (không phải LT). Xem hướng dẫn của bản gốc (đường dẫn trong NOTICE.md).
Bản HP chưa thử trên Mac.

## Phát triển

```powershell
uv sync
uv run pytest tests/ -v
```

## Giới hạn

- Không thay kỹ sư: kết quả vẽ phải được kiểm tra, đo lại trước khi dùng.
- Chốt an toàn lọc theo mẫu lệnh, không chặn được mọi cách xóa; vẫn cần CLAUDE.md và thư mục `_backup`.
- `execute_lisp` vẫn chạy được AutoLISP tùy ý khi không có lệnh xóa; chỉ dùng với yêu cầu rõ ràng.

## Giấy phép

[MIT](LICENSE). Ghi công: [NOTICE.md](NOTICE.md).
