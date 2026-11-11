"""
XUẤT WEB TĨNH: biến web Flask (app.py) thành các tệp HTML/CSS/JS để đưa lên mạng, KHÔNG cần chạy Python.

Chạy:
    python xuat_web_tinh.py              -> ra thư mục web_tinh/ (mở index.html, hoặc đăng lên GitHub Pages / Netlify)
    python xuat_web_tinh.py --artifact   -> index.html dạng đăng lên claude.ai (bỏ thẻ <html>, <head>, <body>)

Làm gì:
  1) Dùng Flask "giả làm trình duyệt" (app.test_client) để lấy HTML các trang không cần server:
       /  /huong-dan  /chat  /doc-code
  2) Sửa đường dẫn: "/chat" -> "chat.html", "/static/style.css" -> "style.css" ...
  3) Phòng chat: thay 4 API /api/chat/... bằng crypto-local.js (file nguồn trong web_tinh/)
     (TinyDES + DES viết lại bằng JavaScript, cho kết quả giống hệt core/)
  4) 2 trang "từng bước" có màu: lấy từ *-tung-buoc.html trong web_tinh/
  5) 4 trang cần Python (tấn công, đo thời gian, kiểm thử, lịch sử) -> trỏ về trang ban-day-du.html

Code thuật toán (core/) và app.py KHÔNG bị sửa gì.
"""

import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))           # thư mục đồ án (chứa file này)
# Gộp chung 1 thư mục: web_tinh/ vừa chứa file NGUỒN viết tay (crypto-local.js,
# *-tung-buoc.html, ban-day-du.part.html) vừa chứa file KẾT QUẢ sinh ra khi chạy file này.
SRC = OUT = os.path.join(ROOT, "web_tinh")
ARTIFACT = "--artifact" in sys.argv                         # sys.argv: các chữ gõ sau "python xuat_web_tinh.py"

import app as A                                             # noqa: E402  (import sau khi biết ROOT)

# Trang Flask -> tên tệp tĩnh
PAGES = {"/": "index.html", "/huong-dan": "huong-dan.html", "/chat": "chat.html", "/doc-code": "doc-code.html"}
# Trang dùng bản tĩnh "từng bước" có sẵn trong web_tinh/
OTHER = {"/sdes": "tinydes.html", "/des": "des.html"}
# Trang cần server Python -> trỏ về trang hướng dẫn chạy bản đầy đủ
NEED_SERVER = ["/bruteforce", "/benchmark", "/tests", "/history"]
# Gộp 3 dict: "**" trải các cặp khóa-giá trị vào dict mới
LINKS = {**PAGES, **OTHER, **{p: "ban-day-du.html" for p in NEED_SERVER}}


def fix_links(html):
    """
    Đổi đường dẫn của Flask thành tên tệp.
    VD: href="/chat" -> href="chat.html" ; href="/huong-dan#canh-3" -> href="huong-dan.html#canh-3"
    """
    html = html.replace('href="/static/style.css"', 'href="style.css"')
    # phòng chat: nạp crypto-local.js trước chat.js
    html = html.replace('src="/static/chat.js"', 'src="crypto-local.js"></script><script src="chat.js"')

    def sub(m):                                             # m: 1 chỗ khớp; group(1) = đường dẫn, group(2) = phần "#..."
        path, rest = m.group(1), m.group(2)
        return f'href="{LINKS[path]}{rest}"' if path in LINKS else m.group(0)
    return re.sub(r'href="(/[^"#?]*)([^"]*)"', sub, html)


def fix_nav(html):
    """Menu trái: bỏ 4 mục cần server, thay nhóm "Tấn công & kiểm chứng" bằng 1 mục dẫn tới bản đầy đủ."""
    a, b = html.index("<nav>"), html.index("</nav>")       # chỉ sửa trong menu, không đụng link trong nội dung
    nav = re.sub(r'\s*<a href="ban-day-du.html" class="[^"]*">.*?</a>', "", html[a:b], flags=re.S)
    html = html[:a] + nav + html[b:]
    return html.replace('<span class="nav-group">Tấn công &amp; kiểm chứng</span>',
                        '<span class="nav-group">Bản đầy đủ</span>\n    <a href="ban-day-du.html" class="">'
                        'Tấn công, kiểm thử, đo thời gian</a>')


def fix_home_forms(html):
    """
    Trang chủ có 2 form gửi lên Python (/sdes_demo, /des_file). Bản tĩnh không có Python,
    nên đổi thành form mở trang "từng bước" kèm dữ liệu trên URL: tinydes.html?p=...&k=..., des.html?t=...&k=...
    """
    html = html.replace('<form method="post" action="/sdes_demo" class="form-grid">',
                        '<form method="get" action="tinydes.html" class="form-grid">')
    html = html.replace('<form method="post" action="/des_file" enctype="multipart/form-data" class="form-grid">',
                        '<form method="get" action="des.html" class="form-grid">')
    html = html.replace('name="sdes_input"', 'name="p"').replace('name="sdes_key"', 'name="k"')
    html = html.replace('name="des_text"', 'name="t"').replace('name="des_key"', 'name="k"')
    html = re.sub(r'\s*<input type="hidden" name="sdes_fmt"[^>]*>', "", html)
    html = re.sub(r'\s*<button name="(sdes|des)_action" value="dec" class="btn">Giải mã</button>', "", html)
    html = re.sub(r'<button name="(sdes|des)_action" value="enc" class="btn primary">Mã hóa</button>',
                  '<button class="btn primary">Mã hóa, xem từng bước</button>', html)
    return html.replace("Văn bản (giải mã thì nhập bản mã hex)", "Văn bản")


def body_only(html):
    """(chỉ khi --artifact) claude.ai tự bọc trang chính, nên bỏ <!doctype>, <html>, <head>, <body>."""
    head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)        # re.S: dấu "." khớp cả xuống dòng
    head = re.sub(r'<meta charset="utf-8">|<meta name="viewport"[^>]*>', "", head)
    body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
    return head.strip() + "\n" + body.strip() + "\n"


def write(name, text):
    """Ghi 1 tệp vào web_tinh/. Ký tự "�" (có trong vài ghi chú code) đổi thành dạng an toàn."""
    text = text.replace("�", "&#xFFFD;" if name.endswith(".html") else "\\uFFFD")
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    os.makedirs(OUT, exist_ok=True)                         # tạo thư mục nếu chưa có
    for old in ("ly-thuyet.html", "luong-code.html"):       # 2 trang đã bỏ ở bản cuối
        if os.path.exists(os.path.join(OUT, old)):
            os.remove(os.path.join(OUT, old))
    client = A.app.test_client()                            # "trình duyệt giả" của Flask, không cần bật server

    # 1-2) Các trang Flask
    for path, name in PAGES.items():
        html = fix_nav(fix_links(client.get(path).data.decode("utf-8")))
        if name == "index.html":
            html = fix_home_forms(html)
            html = html.replace("<title>Trang chủ · DES &amp; TinyDES</title>", "<title>Mật thư An–Bình</title>")
            if ARTIFACT:
                html = body_only(html)
        write(name, html)

    # 3) CSS và JS. chat.js: thay hàm api() gọi server bằng LOCAL_API (tính ngay trong trình duyệt)
    shutil.copy(os.path.join(ROOT, "static", "style.css"), os.path.join(OUT, "style.css"))
    # crypto-local.js là file nguồn viết tay, đã nằm sẵn trong web_tinh/ nên không cần copy
    js = read(os.path.join(ROOT, "static", "chat.js"))
    start = js.index("  function api(path, body) {")
    end = js.index("\n  }\n", start) + 4                    # hết hàm api()
    js = js[:start] + "  function api(path, body) { return window.LOCAL_API(path, body); }   // bản tĩnh\n" + js[end:]
    write("chat.js", js)

    # 4) 2 trang "từng bước": thêm khung <html><head><body> + nút quay về trang chủ
    back = ('<a href="index.html" style="position:fixed;top:12px;left:12px;z-index:30;padding:6px 12px;border-radius:8px;'
            'background:#0c1a2c;color:#fff;font:600 13px system-ui;text-decoration:none">← Mật thư An–Bình</a>')
    for src, name in [("tinydes-tung-buoc.html", "tinydes.html"), ("des-tung-buoc.html", "des.html")]:
        body = read(os.path.join(SRC, src)).replace('<div class="wrap">', back + '\n<div class="wrap">', 1)
        body = body.replace("</style>\n", "</style>\n</head>\n<body>\n", 1)      # hết phần <head> ngay sau </style>
        write(name, '<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + body + "\n</body>\n</html>\n")

    # 5) Trang "bản đầy đủ": mượn khung trang hướng dẫn, thay phần nội dung
    tpl = read(os.path.join(OUT, "huong-dan.html"))
    content = read(os.path.join(SRC, "ban-day-du.part.html"))
    page = tpl[:tpl.index("<main>") + len("<main>")] + content + tpl[tpl.index("</main>"):]
    page = re.sub(r'<header class="page-head">\s*<div>\s*<h1>.*?</h1>\s*<p>.*?</p>',
                  '<header class="page-head">\n    <div>\n      <h1>Bản đầy đủ chạy trên máy</h1>\n'
                  '      <p>Tấn công, kiểm thử, đo thời gian và lịch sử cần chạy code Python</p>', page, count=1, flags=re.S)
    page = page.replace("<title>Hướng dẫn · DES &amp; TinyDES</title>", "<title>Bản đầy đủ · DES &amp; TinyDES</title>")
    write("ban-day-du.html", page.replace('class="active"', 'class=""'))

    print(f"Đã xuất {len(os.listdir(OUT))} tệp vào {OUT}" + (" (dạng claude.ai)" if ARTIFACT else ""))
    for n in sorted(os.listdir(OUT)):
        print("  ", n)


if __name__ == "__main__":
    main()
