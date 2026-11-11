"""
Lưu lịch sử thao tác vào SQLite (file history.db cạnh mã nguồn).
Không lưu khóa và nội dung file - chỉ lưu thông tin mô tả.

SQLite = cơ sở dữ liệu nằm gọn trong 1 tệp, có sẵn trong Python (module sqlite3), không cần cài server.
"""

import os
import sqlite3
from datetime import datetime

# Đường dẫn tệp CSDL: cùng thư mục với file db.py này
#   __file__                   = đường dẫn của db.py
#   os.path.abspath(__file__)  = đổi thành đường dẫn đầy đủ
#   os.path.dirname(...)       = lấy thư mục chứa nó
#   os.path.join(thư_mục, "history.db") = ghép thành đường dẫn tệp
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.db")
PREVIEW_LEN = 60        # chỉ lưu tối đa 60 ký tự đầu của đầu vào / đầu ra


def _connect():
    """Mở kết nối tới history.db (chưa có thì SQLite tự tạo tệp)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # mỗi dòng đọc ra truy cập được theo tên cột: row["algo"]
    return conn


def init_db():
    """Tạo bảng history nếu chưa có (gọi 1 lần khi app.py khởi động)."""
    # "with": tự lưu (commit) khi xong khối lệnh; nếu có lỗi thì hủy thay đổi
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  TEXT    NOT NULL,
                algo        TEXT    NOT NULL,   -- TinyDES / DES / Brute-force
                action      TEXT    NOT NULL,   -- Mã hóa / Giải mã / Bẻ khóa
                input_desc  TEXT,
                output_desc TEXT,
                size_bytes  INTEGER,
                elapsed_ms  REAL,
                status      TEXT    NOT NULL,   -- ok / error
                note        TEXT
            )
        """)
        # id tự tăng 1, 2, 3...; NOT NULL = bắt buộc có giá trị; REAL = số thực


def _short(text):
    """
    Cắt ngắn chuỗi dài để lưu gọn.
    VD: chuỗi 100 ký tự -> 60 ký tự đầu + "…" ; None -> None
    """
    if text is None:
        return None
    text = str(text)                    # đổi mọi kiểu (số, bytes...) sang chuỗi
    return text if len(text) <= PREVIEW_LEN else text[:PREVIEW_LEN] + "…"


def add_history(algo, action, input_desc=None, output_desc=None, size_bytes=None,
                elapsed_ms=None, status="ok", note=None):
    """
    Thêm 1 dòng lịch sử.
    VD: add_history("TinyDES", "Mã hóa", "01011100", "92", 1, 0.13, note="1 khối 8-bit")
    """
    with _connect() as conn:
        conn.execute(
            "INSERT INTO history (created_at, algo, action, input_desc, output_desc, size_bytes, elapsed_ms, status, note)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            # Các dấu "?" được thay lần lượt bằng giá trị trong tuple bên dưới.
            # Dùng "?" thay vì ghép chuỗi để tránh lỗi/tấn công SQL injection.
            # datetime.now().strftime(...): thời gian hiện tại dạng "2026-10-24 19:33:47"
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), algo, action, _short(input_desc),
             _short(output_desc), size_bytes, elapsed_ms, status, note),
        )


def get_history(limit=200):
    """Lấy tối đa 200 dòng mới nhất (ORDER BY id DESC = id lớn nhất, tức mới nhất, lên đầu)."""
    with _connect() as conn:
        # (limit,): tuple 1 phần tử phải có dấu phẩy
        return conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def get_stats():
    """
    Đếm số lượt theo từng thuật toán.
    VD: -> {"TinyDES": 5, "DES": 2, "Brute-force": 1}
    """
    with _connect() as conn:
        # GROUP BY algo: gom các dòng cùng algo; COUNT(*): đếm số dòng mỗi nhóm
        rows = conn.execute("SELECT algo, COUNT(*) AS n FROM history GROUP BY algo").fetchall()
    return {r["algo"]: r["n"] for r in rows}   # dict comprehension: tạo dict từ các dòng


def clear_history():
    """Xóa toàn bộ lịch sử."""
    with _connect() as conn:
        conn.execute("DELETE FROM history")
