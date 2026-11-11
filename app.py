import base64                   # mã hóa base64 (để nhúng ảnh trực tiếp vào HTML)
import inspect                  # đọc mã nguồn thật của 1 hàm (trang "Đọc code cùng thuật toán")
import io                       # io.BytesIO: biến bytes trong RAM thành "tệp ảo" để gửi cho trình duyệt tải về
import os                       # os.path (xử lý tên tệp), os.urandom (sinh byte ngẫu nhiên)
import time                     # time.perf_counter() để đo thời gian chạy
import uuid                     # sinh mã ngẫu nhiên không trùng (token cho link tải về)

# Flask: thư viện web. Các thứ lấy về:
#   Flask           - tạo ứng dụng web
#   abort           - trả lỗi HTTP (VD 404 không tìm thấy)
#   redirect        - chuyển hướng trình duyệt sang trang khác
#   render_template - ghép dữ liệu vào file HTML trong templates/
#   request         - dữ liệu trình duyệt gửi lên (form, tệp, tham số trên URL)
#   send_file       - gửi 1 tệp về cho trình duyệt tải
#   url_for         - tạo đường dẫn từ tên hàm, VD url_for("history") -> "/history"
#   jsonify         - trả dữ liệu dạng JSON (trang chat gọi bằng JavaScript, không tải lại trang)
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

import db                                           # db.py: lưu lịch sử thao tác vào SQLite
from core import des_core, tinydes_core, des_utils as utils     # phần THUẬT TOÁN (nhóm tự cài đặt)

app = Flask(__name__)                               # tạo ứng dụng web; __name__ giúp Flask tìm thư mục templates/, static/
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # tối đa 20 MB / file (20 * 1024 * 1024 byte)
db.init_db()                                        # tạo bảng history trong history.db nếu chưa có

DOWNLOADS = {}       # token -> (tên file, dữ liệu) - lưu tạm trong RAM
#                      VD {"3f2a...": ("anh.png.enc", b"...")}
MAX_DOWNLOADS = 20   # chỉ giữ 20 tệp gần nhất để không tốn RAM
MAX_LOG_BLOCKS = 8   # chỉ in log chi tiết cho vài khối đầu để trang không quá dài
# đuôi tệp ảnh -> kiểu MIME (để trình duyệt biết hiển thị ảnh loại gì)
IMAGE_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".gif": "image/gif", ".bmp": "image/bmp", ".webp": "image/webp"}
MAX_PREVIEW = 3 * 1024 * 1024                               # ảnh > 3 MB thì không xem trước (trang sẽ quá nặng)
BENCH_SIZES = [1024, 10 * 1024, 100 * 1024, 1024 * 1024]   # 1 KB, 10 KB, 100 KB, 1 MB cho phần đo thời gian


def render(template, **ctx):
    """
    Hàm phụ dùng chung: hiển thị 1 trang HTML.
    **ctx: nhận mọi tham số dạng tên=giá_trị, VD render("sdes.html", sdes=result) -> ctx = {"sdes": result}
    Luôn gửi kèm SBOX (bảng S-box TinyDES) và form (dữ liệu vừa nhập, để điền lại vào ô nhập).
    """
    # POST: dữ liệu nằm trong form; GET: dữ liệu nằm trên URL (VD /bruteforce?bf_plain=Hello)
    form = request.form if request.method == "POST" else request.args
    # render_template: mở templates/<template>, thay {{ ... }} bằng dữ liệu, trả về chuỗi HTML
    return render_template(template, sbox=tinydes_core.TinyDES().sbox, form=form, **ctx)


def store_download(filename, data):
    """
    Cất tệp kết quả vào RAM, trả về token để tạo link /download/<token>.
    VD: store_download("anh.png.enc", b"...") -> "9c1e4f..." (32 ký tự hex ngẫu nhiên)
    """
    if len(DOWNLOADS) >= MAX_DOWNLOADS:             # đầy rồi thì bỏ tệp cũ nhất
        DOWNLOADS.pop(next(iter(DOWNLOADS)))        # next(iter(dict)) = khóa ĐẦU TIÊN (cũ nhất) của dict
    token = uuid.uuid4().hex                        # chuỗi ngẫu nhiên không trùng
    DOWNLOADS[token] = (filename, data)
    return token


def image_data_uri(name, data):
    """
    Trả về data URI để xem trước ảnh trên trang (None nếu không phải ảnh).
    Data URI = nhúng nguyên ảnh vào HTML: <img src="data:image/png;base64,iVBORw0KG...">
    """
    ext = os.path.splitext(name.lower())[1]         # lấy đuôi tệp: "Anh.PNG" -> ".png"
    if ext not in IMAGE_EXT or not data or len(data) > MAX_PREVIEW:
        return None
    # base64.b64encode: bytes -> chữ an toàn để nhét vào HTML; .decode(): bytes -> str
    return f"data:{IMAGE_EXT[ext]};base64," + base64.b64encode(data).decode()


def action_name(action):
    """'enc' -> 'Mã hóa', 'dec' -> 'Giải mã' (để ghi lịch sử)."""
    return "Mã hóa" if action == "enc" else "Giải mã"    # biểu thức điều kiện: A if điều_kiện else B


def parse_sdes_data(raw, fmt, is_input_cipher):
    """
    Chuyển dữ liệu nhập về list các khối 8-bit ('0'/'1').
    raw            : chuỗi người dùng nhập
    fmt            : "bin" (nhập nhị phân) hoặc "text" (nhập văn bản)
    is_input_cipher: True nếu đang nhập BẢN MÃ dạng văn bản (khi đó nhập bằng hex)
    VD: ("01011100 10010010", "bin", False) -> ["01011100", "10010010"]
        ("Hi", "text", False)                -> ["01001000", "01101001"]   ('H' = 72, 'i' = 105)
        ("E0 F8", "text", True)              -> ["11100000", "11111000"]
    """
    if fmt == "bin":
        bits = "".join(raw.split())         # raw.split() tách theo khoảng trắng, join lại -> bỏ mọi khoảng trắng
        # any(...): True nếu CÓ ÍT NHẤT 1 ký tự không phải 0/1
        if not bits or len(bits) % 8 or any(c not in "01" for c in bits):
            raise ValueError("Dữ liệu nhị phân phải gồm các khối 8 bit (VD: 01011100).")
        return [bits[i:i + 8] for i in range(0, len(bits), 8)]     # cắt mỗi 8 ký tự 1 khối
    if is_input_cipher:  # bản mã dạng văn bản được nhập bằng hex
        try:
            data = bytes.fromhex(raw.strip())       # "E0 F8" -> b'\xe0\xf8' (fromhex bỏ qua khoảng trắng)
        except ValueError:                          # có ký tự không phải hex -> báo lỗi dễ hiểu hơn
            raise ValueError("Bản mã dạng văn bản phải nhập ở dạng hex (VD: 3A F0 12).")
    else:
        data = raw.encode("utf-8")                  # văn bản -> bytes  VD "Hi" -> b'Hi' = [72, 105]
    if not data:
        raise ValueError("Chưa nhập dữ liệu.")
    return [format(b, "08b") for b in data]         # mỗi byte -> chuỗi 8 bit  VD 72 -> "01001000"


# ---------------------------------------------------------------------------
# Các trang (GET) - chỉ mở trang, chưa xử lý dữ liệu
# @app.get("/x"): khi trình duyệt mở địa chỉ /x thì chạy hàm ngay bên dưới
# ---------------------------------------------------------------------------
@app.get("/")
def index():
    """Trang chủ: 2 form chạy nhanh TinyDES / DES, bảng chức năng, số lượt sử dụng."""
    return render("home.html", stats=db.get_stats())      # db.get_stats() -> VD {"TinyDES": 5, "DES": 2}


# Các trang chỉ hiện form trống:
@app.get("/sdes")
def sdes_page():
    return render("sdes.html")


@app.get("/bruteforce")
def bruteforce_page():
    return render("bruteforce.html")


@app.get("/des")
def des_page():
    return render("des.html")


@app.get("/benchmark")
def benchmark_page():
    return render("benchmark.html")


def test_presets():
    """Ca mẫu để chọn nhanh trong mục tự nhập (lấy từ test_runner)."""
    import test_runner

    ex, dx = test_runner.TINYDES_EXAMPLE, test_runner.DES_CLASS_EXAMPLE
    presets = [
        {"label": "TinyDES — ví dụ trong tài liệu (trang 72)", "algo": "sdes", "plain": ex["plain"], "key": ex["key"], "expected": ex["cipher"]},
        {"label": "DES — ví dụ Grabbe", "algo": "des", "plain": dx["plain"], "key": dx["key"], "expected": dx["cipher"]},
    ]
    # enumerate(..., start=1): đánh số từ 1; mỗi vector là tuple 4 phần tử -> tách thành kind, key, pt, ct
    for i, (kind, key, pt, ct) in enumerate(test_runner.NIST_VECTORS, start=1):
        presets.append({"label": f"DES — NIST SP 800-17 #{i} ({kind})", "algo": "des", "plain": pt, "key": key, "expected": ct})
    return presets


def run_custom_test(algo, plain, key_text, expected):
    """
    Chạy 1 ca kiểm thử do người dùng nhập, trả về danh sách bước (mỗi bước có thể có kết quả PASS/FAIL).
    algo: "sdes" hoặc "des"; expected: bản mã mong đợi (có thể rỗng).
    VD: run_custom_test("sdes", "01011100", "10011010", "10010010") -> passed 4/4
    """
    steps = []

    def step(title, desc, items, ok=None, detail=None):
        """Hàm lồng: thêm 1 bước vào steps. ok=None: bước chỉ hiển thị; True/False: bước kiểm tra PASS/FAIL."""
        steps.append({"title": title, "desc": desc, "fields": items, "ok": ok, "detail": detail})

    if algo == "sdes":
        plain = "".join(plain.split())                      # bỏ mọi khoảng trắng người dùng gõ thừa
        key = "".join(key_text.split())
        expected = "".join(expected.split())
        ok_in = tinydes_core.is_bits(plain, 8) and tinydes_core.is_bits(key, 8)
        step("Kiểm tra dữ liệu nhập", "Bản rõ đúng 8 bit, khóa đúng 8 bit (chỉ gồm 0/1)",
             [("Bản rõ", plain), ("Khóa", key)], ok_in)
        if not ok_in:
            raise ValueError("TinyDES: bản rõ và khóa đều phải là 8 bit (chỉ gồm 0 và 1).")
        if expected and not tinydes_core.is_bits(expected, 8):
            raise ValueError("Bản mã mong đợi của TinyDES phải là 8 bit.")

        t = tinydes_core.trace(plain, key)                  # lấy toàn bộ bước trung gian
        step("B1 · Sinh khóa con — generate_keys()", "KL0|KR0 → dịch 1, 2, 1 bit → Compress = K1, K2, K3",
             [(s["name"], s["bits"][:4] + " " + s["bits"][4:] if s.get("split") else s["bits"]) for s in t["key_steps"]])
        for r in t["rounds"]:                               # 3 vòng Feistel
            n = r["n"]
            step(f"B2 · Vòng {n} — K{n} = {r['k']}", "Expand → ⊕K → S-box → P-box = F → L, R mới",
                 [("L | R", r["left"] + " " + r["right"]), ("Expand(R)", r["expand"]), (f"⊕ K{n}", r["xor"]),
                  ("S-box", f"{r['sbox']['in']} → hàng {r['sbox']['row']}, cột {r['sbox']['col']} → {r['sbox']['out']}"),
                  ("P-box = F", r["f"]), (f"R{n} = L{n - 1} ⊕ F", f"{r['mix']} ⊕ {r['f']} = {r['mixed']}"),
                  (f"L{n} R{n}", r["output"][:4] + " " + r["output"][4:])])
        cipher = t["output"]
        step("B2 · Bản mã C = L3 R3", "TinyDES không có hoán vị khởi tạo / kết thúc", [("Bản mã", cipher)])
        # so hàm encrypt() (dùng khi chạy thật) với trace() (dùng để hiển thị) -> 2 đường phải cho cùng kết quả
        step("Đối chiếu: hàm encrypt() cho cùng kết quả", "Hàm mã hóa chính của chương trình, độc lập với trace() dùng để hiển thị",
             [("encrypt()", tinydes_core.encrypt(plain, key)[0]), ("trace()", cipher)],
             tinydes_core.encrypt(plain, key)[0] == cipher)
        back = tinydes_core.trace(cipher, key, decrypt=True)["output"]      # giải mã ngược
    else:
        key = utils.parse_des_key(key_text)                 # "133457799BBCDFF1" hoặc "nhom2026" -> 8 byte
        try:
            block = bytes.fromhex(plain.strip())
            # nếu có nhập bản mã mong đợi thì đổi sang bytes, không thì None
            exp_bytes = bytes.fromhex(expected.strip()) if expected.strip() else None
        except ValueError:
            raise ValueError("DES: bản rõ và bản mã mong đợi phải nhập dạng hex.")
        ok_in = len(block) == 8 and (exp_bytes is None or len(exp_bytes) == 8)
        step("Kiểm tra dữ liệu nhập", "Bản rõ là 1 khối 64 bit (16 ký tự hex), khóa 8 ký tự hoặc 16 hex",
             [("Bản rõ", block.hex().upper()), ("Khóa", key.hex().upper())], ok_in)
        if not ok_in:
            raise ValueError("DES: bản rõ (và bản mã mong đợi) phải đúng 16 ký tự hex = 1 khối 64 bit.")
        plain, expected = block.hex().upper(), exp_bytes.hex().upper() if exp_bytes else ""   # chuẩn hóa in hoa

        key_log = []
        subkeys = des_core.generate_subkeys(key, key_log)   # key_log[0] = PC-1 (C0, D0), key_log[1..16] = K1..K16
        step("B1 · Sinh 16 khóa con — generate_subkeys()", "PC-1 → C0, D0 → 16 lần (dịch trái + PC-2)",
             [("C0", key_log[0]["c"]), ("D0", key_log[0]["d"]), ("K1", key_log[1]["k"]), ("K2", key_log[2]["k"]),
              ("K16", key_log[16]["k"])], detail={"type": "keys", "rows": key_log})
        out, rounds = des_core.crypt_block_verbose(block, subkeys)  # rounds[0] = IP, rounds[1..16] = vòng 1..16
        step("B2 · Hoán vị khởi tạo IP", "Chia thành L0 | R0 (mỗi nửa 32 bit)",
             [("L0", rounds[0]["l"]), ("R0", rounds[0]["r"])])
        r1 = rounds[1]
        step("B2 · Vòng 1: f(R0, K1)", "E → ⊕K1 → 8 S-box → P, rồi L1 = R0, R1 = L0 ⊕ f",
             [("E(R0)", r1["e"]), ("⊕ K1", r1["xor"]), ("S-box", r1["s"]), ("f", r1["f"]),
              ("L1", r1["l"]), ("R1", r1["r"])])
        step("B2 · Vòng 2 → 16", "Lặp giống hệt vòng 1, mỗi vòng dùng khóa con của nó",
             [("L16", rounds[16]["l"]), ("R16", rounds[16]["r"])], detail={"type": "rounds", "rows": rounds[1:17]})
        cipher = out.hex().upper()
        step("B2 · Đổi chỗ + IP⁻¹ → bản mã", "R16‖L16 rồi hoán vị ngược",
             [("R16‖L16", rounds[16]["r"] + rounds[16]["l"]), ("Bản mã", cipher)])
        fast = des_core.encrypt_block(block, key).hex().upper()     # bản nhanh (bảng tra)
        step("Đối chiếu: bản tối ưu crypt_block_fast()", "Bản dùng để mã hóa tệp phải cho cùng kết quả với bản có log",
             [("verbose", cipher), ("fast", fast)], fast == cipher)
        from Crypto.Cipher import DES as LibDES
        lib = LibDES.new(key, LibDES.MODE_ECB).encrypt(block).hex().upper()
        step("Đối chiếu thư viện pycryptodome", "Thư viện chuẩn chỉ dùng để so sánh, không dùng trong phần lõi",
             [("Nhóm tự code", cipher), ("pycryptodome", lib)], lib == cipher)
        back = des_core.decrypt_block(out, key).hex().upper()

    if expected:                                            # chuỗi rỗng "" được coi là False -> bỏ qua bước này
        step("So với bản mã mong đợi", "Bản mã mong đợi do bạn nhập (ví dụ trên lớp, NIST…)",
             [("Mong đợi", expected), ("Thực tế", cipher)], expected.upper() == cipher.upper())
    step("B3 · Giải mã ngược lại bản mã", "Dùng khóa con theo thứ tự ngược, phải ra đúng bản rõ ban đầu",
         [("Bản mã", cipher), ("Giải mã", back), ("Bản rõ ban đầu", plain)], back == plain)

    checks = [s for s in steps if s["ok"] is not None]      # chỉ lấy các bước có kiểm tra PASS/FAIL
    return {"algo": algo, "plain": plain, "cipher": cipher, "steps": steps,
            "passed": sum(s["ok"] for s in checks),         # True = 1, False = 0 -> sum = số bước PASS
            "total": len(checks)}


@app.get("/tests")
def tests_page():
    return render("tests.html", presets=test_presets())


@app.route("/tests/custom", methods=["GET", "POST"])        # nhận cả GET (link "Chạy từng bước") lẫn POST (form)
def tests_custom():
    f = request.values                                      # gộp cả dữ liệu form (POST) và tham số URL (GET)
    algo = f.get("t_algo", "sdes")                          # .get(tên, mặc_định): không có thì lấy mặc định
    if not f.get("t_plain"):  # mở từ link "Chạy từng bước" mà thiếu dữ liệu
        return render("tests.html", presets=test_presets())
    try:
        result = run_custom_test(algo, f.get("t_plain", ""), f.get("t_key", ""), f.get("t_expected", ""))
        db.add_history("Kiểm thử", "Ca tự nhập", f"{algo.upper()} P={result['plain']}", result["cipher"], None, None,
                       status="ok" if result["passed"] == result["total"] else "error",
                       note=f"Passed {result['passed']}/{result['total']} bước kiểm tra")
        return render("tests.html", presets=test_presets(), custom=result)
    except ValueError as e:                                 # dữ liệu nhập sai -> hiện lỗi trên trang
        db.add_history("Kiểm thử", "Ca tự nhập", f.get("t_plain", ""), status="error", note=str(e))
        return render("tests.html", presets=test_presets(), custom_error=str(e))


@app.post("/tests")
def tests_run():
    """Chạy toàn bộ test_runner.run_all() rồi nhóm kết quả theo A, B, C."""
    import test_runner

    results, ms = test_runner.run_all()                     # list các ca + thời gian chạy (ms)
    groups = {}
    for c in results:
        # setdefault: nếu chưa có khóa này thì tạo list rỗng, rồi append ca vào list đó
        groups.setdefault(c["group"], []).append(c)
    passed = sum(c["ok"] for c in results)
    db.add_history("Kiểm thử", "Chạy bộ test", "test_runner.run_all()", f"Passed {passed}/{len(results)}",
                   None, round(ms, 3), status="ok" if passed == len(results) else "error",
                   note="Nhóm tự viết + NIST SP 800-17 + pycryptodome")
    return render("tests.html", presets=test_presets(), groups=groups, passed=passed, total=len(results),
                  elapsed=f"{ms / 1000:.1f}")              # ".1f": làm tròn 1 chữ số thập phân


# ---------------------------------------------------------------------------
# TinyDES demo: hiển thị từng bước sinh khóa và mã hóa
# @app.post: chỉ chạy khi form được GỬI LÊN (bấm nút Mã hóa / Giải mã)
# ---------------------------------------------------------------------------
@app.post("/sdes_demo")
def sdes_demo():
    # request.form.get("tên ô"): lấy giá trị ô nhập có name="tên ô" trong sdes.html
    key = request.form.get("sdes_key", "").strip()          # VD "10011010"
    fmt = request.form.get("sdes_fmt", "bin")               # "bin" hoặc "text"
    action = request.form.get("sdes_action", "enc")         # nút nào được bấm: "enc" hoặc "dec"
    raw_input = request.form.get("sdes_input", "")          # VD "01011100" hoặc "Hello"
    try:
        blocks = parse_sdes_data(raw_input, fmt, action == "dec")   # -> list khối 8 bit
        key_log = []
        keys = tinydes_core.generate_keys(key, key_log)     # B1: sinh K1, K2, K3 (khóa sai -> ValueError)

        # chọn hàm theo nút được bấm (hàm cũng là 1 giá trị, gán vào biến được)
        fn = tinydes_core.encrypt if action == "enc" else tinydes_core.decrypt
        out_blocks, block_logs = [], []
        t0 = time.perf_counter()                            # bấm giờ
        for i, blk in enumerate(blocks):
            out, log = fn(blk, key)                         # mã hóa/giải mã 1 khối, kèm log
            out_blocks.append(out)
            if i < MAX_LOG_BLOCKS:
                # log[len(key_log):] bỏ phần sinh khóa ở đầu log (đã hiển thị riêng)
                block_logs.append({"input": blk, "output": out, "steps": log[len(key_log):]})

        elapsed = (time.perf_counter() - t0) * 1000         # giây -> mili-giây
        out_bytes = bytes(int(b, 2) for b in out_blocks)    # ["10010010", ...] -> b'\x92...'
        traces = [tinydes_core.trace(b, key, decrypt=(action == "dec")) for b in blocks[:MAX_LOG_BLOCKS]]
        result = {
            "subkeys": keys, "key_log": key_log, "blocks": block_logs,
            "total_blocks": len(blocks),
            "out_bin": " ".join(out_blocks),                # VD "10010010 01100111"
            "out_hex": out_bytes.hex(" ").upper(),          # VD "92 67"
            # giải mã thì thử đổi bytes -> chữ; errors="replace": byte không hợp lệ thành dấu �
            "out_text": out_bytes.decode("utf-8", errors="replace") if action == "dec" else None,
            "action": action, "fmt": fmt,
            # Dữ liệu minh họa từng bit (sinh khóa, 3 vòng Feistel) cho vài khối đầu
            "traces": traces,
        }
        # Dải luồng của khối đầu: Đầu vào -> Vòng 1 -> Vòng 2 -> Vòng 3 (mã hóa) hoặc 3 -> 2 -> 1 (giải mã)
        first = traces[0]
        result["flow"] = [("Đầu vào", first["input"])] + [(f"Vòng {r['n']}", r["output"]) for r in first["rounds"]]
        if action == "enc":  # tự giải mã ngược để chứng minh D(E(P)) = P
            original = bytes(int(b, 2) for b in blocks)
            back = tinydes_core.decrypt_bytes(out_bytes, key)
            result["roundtrip"] = {
                "ok": back == original,
                "bin": " ".join(format(b, "08b") for b in back),
                "text": back.decode("utf-8", errors="replace") if fmt == "text" else None,
            }
        db.add_history("TinyDES", action_name(action), raw_input,       # ghi lịch sử (KHÔNG ghi khóa)
                       result["out_text"] if action == "dec" and fmt == "text" else result["out_hex"],
                       len(out_bytes), round(elapsed, 3), note=f"{len(blocks)} khối 8-bit")
        return render("sdes.html", sdes=result)             # trả trang sdes.html kèm kết quả
    except ValueError as e:                                 # nhập sai -> hiện thông báo lỗi trên trang
        db.add_history("TinyDES", action_name(action), raw_input, status="error", note=str(e))
        return render("sdes.html", sdes_error=str(e))


# ---------------------------------------------------------------------------
# DES: mã hóa / giải mã văn bản hoặc file (ảnh, txt, ...)
# ---------------------------------------------------------------------------
@app.post("/des_file")
def des_file():
    action = request.form.get("des_action", "enc")
    upload = request.files.get("des_file")                  # tệp người dùng chọn (None nếu không chọn)
    try:
        key = utils.parse_des_key(request.form.get("des_key", ""))     # -> 8 byte

        if upload and upload.filename:                      # có chọn tệp
            # gán 3 biến cùng lúc: nội dung tệp, tên tệp (bỏ đường dẫn thư mục), cờ "từ tệp"
            data, name, from_file = upload.read(), os.path.basename(upload.filename), True
        else:                                               # không chọn tệp -> dùng ô văn bản
            text = request.form.get("des_text", "")
            if action == "enc":
                data = text.encode("utf-8")                 # mã hóa: chữ -> bytes
            else:
                try:
                    data = bytes.fromhex(text.strip())      # giải mã: bản mã nhập dạng hex -> bytes
                except ValueError:
                    raise ValueError("Bản mã dạng văn bản phải nhập ở dạng hex.")
            name, from_file = "text.txt", False
        if not data and action == "dec":
            raise ValueError("Chưa nhập dữ liệu hoặc chưa chọn file.")

        key_log = []
        subkeys = des_core.generate_subkeys(key, key_log)   # 16 khóa con + log để hiển thị

        t0 = time.perf_counter()
        if action == "enc":
            out = utils.des_encrypt_bytes(data, key)        # đệm PKCS#7 + mã hóa mọi khối
            first_in = utils.pkcs7_pad(data)[:8]            # khối đầu tiên (sau khi đệm) để in log 16 vòng
            out_name = name + ".enc"                        # VD "anh.png" -> "anh.png.enc"
            round_keys = subkeys
        else:
            out = utils.des_decrypt_bytes(data, key)        # giải mã + bỏ đệm (sai khóa -> ValueError)
            first_in = data[:8]
            # "anh.png.enc" -> "anh.png" (bỏ 4 ký tự cuối); tên khác -> thêm tiền tố "decrypted_"
            out_name = name[:-4] if name.endswith(".enc") else "decrypted_" + name
            round_keys = subkeys[::-1]                      # giải mã: khóa con đảo ngược
        elapsed = (time.perf_counter() - t0) * 1000

        _, round_log = des_core.crypt_block_verbose(first_in, round_keys)  # log 16 vòng của khối đầu

        result = {
            "action": action, "name": name, "out_name": out_name,
            "in_size": len(data), "out_size": len(out),
            "blocks": (len(out) + 7) // 8,                  # số khối 8 byte ("//" là chia lấy phần nguyên)
            "elapsed": f"{elapsed:.1f}", "key_hex": key.hex().upper(),
            "key_log": key_log, "round_log": round_log, "first_in": first_in.hex().upper(),
            "preview_hex": out[:128].hex(" ").upper(),      # 128 byte đầu để xem trước
            "out_text": None, "token": store_download(out_name, out),   # cất tệp, lấy token cho link tải
        }
        if action == "enc":  # giải mã ngược lại bản mã vừa tạo
            back = utils.des_decrypt_bytes(out, key)
            result["roundtrip_ok"] = back == data           # True nếu khôi phục đúng 100%
            result["img_before"] = image_data_uri(name, data)       # ảnh gốc (nếu là ảnh)
            result["img_after"] = image_data_uri(name, back)        # ảnh sau khi giải mã
            if not from_file:
                result["roundtrip_text"] = back.decode("utf-8", errors="replace")
        else:
            result["img_after"] = image_data_uri(out_name, out)
        db.add_history("DES", action_name(action), name if from_file else request.form.get("des_text", ""),
                       out_name if from_file else out[:30].hex().upper(), len(data), round(elapsed, 3),
                       note=f"{'File' if from_file else 'Văn bản'} · {result['blocks']} khối · ECB/PKCS#7")
        if not from_file:                                   # nhập văn bản thì hiện kết quả dạng chữ luôn
            if action == "enc":
                result["out_text"] = out.hex().upper()
            else:
                result["out_text"] = out.decode("utf-8", errors="replace")
        return render("des.html", des=result)
    except ValueError as e:
        name = upload.filename if upload and upload.filename else "văn bản"
        db.add_history("DES", action_name(action), name, status="error", note=str(e))
        return render("des.html", des_error=str(e))


@app.get("/download/<token>")                               # <token>: phần này của URL được truyền vào hàm
def download(token):
    """VD /download/9c1e4f... -> gửi tệp đã cất với token đó về cho trình duyệt tải."""
    if token not in DOWNLOADS:                              # token sai hoặc server đã khởi động lại
        abort(404)
    name, data = DOWNLOADS[token]
    # io.BytesIO(data): bọc bytes thành "tệp ảo"; as_attachment=True: trình duyệt tải về thay vì mở
    return send_file(io.BytesIO(data), as_attachment=True, download_name=name)


# ---------------------------------------------------------------------------
# GIAI ĐOẠN 5: Bẻ khóa TinyDES bằng vét cạn 2^8 = 256 khóa (known-plaintext attack)
# Biết 1 cặp (bản rõ, bản mã) -> thử hết 256 khóa, khóa nào mã hóa bản rõ ra đúng bản mã thì giữ lại.
# ---------------------------------------------------------------------------
@app.post("/sdes_bruteforce")
def sdes_bruteforce():
    fmt = request.form.get("bf_fmt", "text")
    try:
        plain_blocks = parse_sdes_data(request.form.get("bf_plain", ""), fmt, False)   # bản rõ đã biết
        cipher_blocks = parse_sdes_data(request.form.get("bf_cipher", ""), fmt, True)  # bản mã chặn được
        if len(plain_blocks) != len(cipher_blocks):
            raise ValueError("Bản rõ và bản mã phải có cùng số khối (byte).")
        plain = bytes(int(b, 2) for b in plain_blocks)      # list chuỗi 8 bit -> bytes
        cipher = bytes(int(b, 2) for b in cipher_blocks)

        found = []
        t0 = time.perf_counter()
        for key in tinydes_core.all_keys():                 # "00000000", ..., "11111111"
            keys = tinydes_core.generate_keys(key)          # (K1, K2, K3) của khóa đang thử
            if tinydes_core.encrypt_bytes(plain, key, keys) == cipher:
                found.append({"key": key, "dec": int(key, 2), "subkeys": keys})
        elapsed = (time.perf_counter() - t0) * 1000

        db.add_history("Brute-force", "Bẻ khóa", request.form.get("bf_plain", ""),
                       # ", ".join(...) nối các khóa tìm được; nếu rỗng thì "or" lấy "không tìm thấy"
                       ", ".join(f["key"] for f in found) or "không tìm thấy", len(plain), round(elapsed, 3),
                       status="ok" if found else "error", note=f"Thử {tinydes_core.KEY_SPACE} khóa, khớp {len(found)}")
        return render("bruteforce.html", bf={"found": found, "tried": tinydes_core.KEY_SPACE, "elapsed": f"{elapsed:.2f}", "n_bytes": len(plain)})
    except ValueError as e:
        db.add_history("Brute-force", "Bẻ khóa", request.form.get("bf_plain", ""), status="error", note=str(e))
        return render("bruteforce.html", bf_error=str(e))


# ---------------------------------------------------------------------------
# KỊCH BẢN: chỉ chặn được bản mã (ciphertext-only attack)
#   1) Người gửi mã hóa thông điệp bí mật bằng khóa bí mật -> gửi bản mã qua mạng
#   2) Kẻ tấn công chặn được bản mã, KHÔNG biết bản rõ, KHÔNG biết khóa
#   3) Kẻ tấn công thử 256 khóa, chấm điểm bản giải mã "đọc được" -> đoán ra khóa
#   4) So khóa đoán được với khóa thật của người gửi
# ---------------------------------------------------------------------------
@app.post("/sdes_bruteforce_cipher")
def sdes_bruteforce_cipher():
    message = request.form.get("co_message", "")
    secret = request.form.get("co_key", "").strip()
    try:
        if not message:
            raise ValueError("Người gửi chưa nhập thông điệp.")
        if not tinydes_core.is_bits(secret, 8):
            raise ValueError("Khóa bí mật phải gồm đúng 8 bit 0/1.")

        # BƯỚC 1 - phía NGƯỜI GỬI: mã hóa thông điệp
        cipher = tinydes_core.encrypt_bytes(message.encode("utf-8"), secret)

        # BƯỚC 2, 3 - phía KẺ TẤN CÔNG: chỉ dùng `cipher`, không dùng message / secret
        t0 = time.perf_counter()
        top = tinydes_core.brute_force_ciphertext_only(cipher, top=5)
        elapsed = (time.perf_counter() - t0) * 1000
        for c in top:                                       # bytes -> chữ để hiển thị (rác thì thành "�")
            c["text"] = c["plain"].decode("utf-8", errors="replace")
        guess = top[0]                                      # ứng viên điểm cao nhất = khóa kẻ tấn công đoán

        # BƯỚC 4 - kiểm chứng (chỉ làm được vì đây là mô phỏng, ta biết khóa thật)
        success = guess["key"] == secret
        db.add_history("Brute-force", "Chỉ biết bản mã", message, guess["key"], len(cipher), round(elapsed, 3),
                       status="ok" if success else "error",
                       note=f"Khóa thật {'được' if success else 'KHÔNG được'} xếp hạng 1")
        return render("bruteforce.html", co={
            "message": message, "secret": secret, "cipher_hex": cipher.hex(" ").upper(),
            "top": top, "guess": guess, "success": success, "elapsed": f"{elapsed:.2f}", "n_bytes": len(cipher),
            "tried": tinydes_core.KEY_SPACE,
        })
    except ValueError as e:
        db.add_history("Brute-force", "Chỉ biết bản mã", message, status="error", note=str(e))
        return render("bruteforce.html", co_error=str(e))


# ---------------------------------------------------------------------------
# KỊCH BẢN: tấn công chọn bản rõ (chosen-plaintext attack), theo attack_chosen_plaintext.py
#   1) An mã hóa tin bằng khóa bí mật, kẻ xấu chặn được bản mã
#   2) Kẻ xấu mượn được "hộp đen" mã hóa của An (có khóa bên trong nhưng không xem được khóa)
#   3) Đưa 256 bản rõ 00000000 ... 11111111 vào hộp đen -> bảng tra 256 dòng (bản mã -> bản rõ)
#   4) Tra bảng từng byte của bản mã chặn được -> đọc được tin, KHÔNG cần biết khóa
# ---------------------------------------------------------------------------
@app.post("/sdes_chosen_plaintext")
def sdes_chosen_plaintext():
    message = request.form.get("cp_message", "")
    secret = request.form.get("cp_key", "").strip()
    try:
        if not message:
            raise ValueError("Người gửi chưa nhập thông điệp.")
        if not tinydes_core.is_bits(secret, 8):
            raise ValueError("Khóa bí mật phải gồm đúng 8 bit 0/1.")

        # BƯỚC 1 - phía AN: mã hóa thông điệp, bản mã bị chặn
        keys = tinydes_core.generate_keys(secret)
        cipher = tinydes_core.encrypt_bytes(message.encode("utf-8"), secret, keys)

        # BƯỚC 2 - hộp đen: kẻ xấu chỉ được gọi hàm này, không đọc được biến secret bên trong
        def oracle(plain_8bit):
            return tinydes_core._encrypt_block(plain_8bit, keys)

        # BƯỚC 3, 4 - phía KẺ XẤU: lập bảng 256 dòng rồi tra bảng
        t0 = time.perf_counter()
        plain, book = tinydes_core.chosen_plaintext_attack(cipher, oracle)
        elapsed = (time.perf_counter() - t0) * 1000
        text = plain.decode("utf-8", errors="replace") if plain is not None else None

        # bảng 16 x 16 để hiển thị: hàng = 4 bit đầu của bản rõ, cột = 4 bit cuối; ô = bản mã (hex)
        enc_of = {p: c for c, p in book.items()}            # đảo bảng: bản rõ -> bản mã
        grid = [[f"{int(enc_of[format(r * 16 + c, '08b')], 2):02X}" for c in range(16)] for r in range(16)]
        used = sorted({b for b in cipher})                  # các byte bản mã thật sự xuất hiện (tô màu)
        lookups = [{"c": f"{b:02X}", "p": f"{int(book[format(b, '08b')], 2):02X}"} for b in cipher[:12]]

        db.add_history("Brute-force", "Chọn bản rõ", message, text or "không dịch được", len(cipher),
                       round(elapsed, 3), status="ok" if text == message else "error",
                       note=f"Gọi hộp đen {tinydes_core.BLOCK_SPACE} lần, bảng {len(book)} dòng")
        return render("bruteforce.html", cp={
            "message": message, "secret": secret, "cipher_hex": cipher.hex(" ").upper(), "n_bytes": len(cipher),
            "calls": tinydes_core.BLOCK_SPACE, "rows": len(book), "elapsed": f"{elapsed:.2f}",
            "text": text, "success": text == message, "grid": grid,
            "used": [f"{b:02X}" for b in used], "lookups": lookups,
        })
    except ValueError as e:
        db.add_history("Brute-force", "Chọn bản rõ", message, status="error", note=str(e))
        return render("bruteforce.html", cp_error=str(e))


# ---------------------------------------------------------------------------
# KỊCH BẢN: gặp nhau ở giữa (meet-in-the-middle) vào TinyDES 2 lớp (giống Double DES, slide 82-83)
#   1) An mã hóa 2 lớp bằng K1 rồi K2 (khóa ghép 16 bit), tưởng phải thử 65.536 cặp khóa
#   2) Kẻ xấu biết 1 tin cũ và bản mã của nó (VD lời chào "Chào Bình" An hay gửi)
#   3) Mã hóa xuôi bằng 256 K1, giải mã ngược bằng 256 K2, chỗ nào trùng ở giữa là cặp khóa
#   4) Có cặp khóa rồi thì đọc được tin bí mật An gửi sau đó
# ---------------------------------------------------------------------------
MITM_SAMPLE = 8     # vét cạn thường: chỉ chạy thử 8 khóa K1 (x 256 K2) rồi nhân lên để ước lượng thời gian


@app.post("/sdes_mitm")
def sdes_mitm():
    known = request.form.get("mm_known", "")
    secret_msg = request.form.get("mm_secret", "")
    k1, k2 = request.form.get("mm_k1", "").strip(), request.form.get("mm_k2", "").strip()
    try:
        if not known or not secret_msg:
            raise ValueError("Cần nhập cả tin đã biết và tin bí mật.")
        if not (tinydes_core.is_bits(k1, 8) and tinydes_core.is_bits(k2, 8)):
            raise ValueError("K1 và K2 phải gồm đúng 8 bit 0/1.")

        # BƯỚC 1 - phía AN: mã hóa 2 lớp cả 2 tin
        known_cipher = tinydes_core.double_encrypt_bytes(known.encode("utf-8"), k1, k2)
        secret_cipher = tinydes_core.double_encrypt_bytes(secret_msg.encode("utf-8"), k1, k2)

        # BƯỚC 2, 3 - phía KẺ XẤU: chỉ dùng (known, known_cipher), không dùng k1, k2
        t0 = time.perf_counter()
        pairs, n_middle, runs = tinydes_core.meet_in_the_middle(known.encode("utf-8"), known_cipher)
        elapsed = (time.perf_counter() - t0) * 1000

        # so sánh: vét cạn thường thử 256 x 256 cặp. Chạy thử MITM_SAMPLE hàng rồi nhân lên
        all_sub = [tinydes_core.generate_keys(k) for k in tinydes_core.all_keys()]
        t0 = time.perf_counter()
        for sub1 in all_sub[:MITM_SAMPLE]:
            mid = tinydes_core.encrypt_bytes(known.encode("utf-8"), None, sub1)
            for sub2 in all_sub:
                tinydes_core.encrypt_bytes(mid, None, sub2)
        naive_ms = (time.perf_counter() - t0) * 1000 * tinydes_core.KEY_SPACE / MITM_SAMPLE

        # BƯỚC 4 - dùng cặp khóa đầu tiên tìm được để đọc tin bí mật
        read = None
        if pairs:
            read = tinydes_core.double_decrypt_bytes(secret_cipher, *pairs[0]).decode("utf-8", errors="replace")
        success = (k1, k2) in pairs
        db.add_history("Brute-force", "Gặp nhau ở giữa", known, " ".join(pairs[0]) if pairs else "không tìm thấy",
                       len(known_cipher), round(elapsed, 3), status="ok" if success else "error",
                       note=f"{runs} lần chạy TinyDES, {len(pairs)} cặp khóa ứng viên")
        return render("bruteforce.html", mm={
            "known": known, "secret": secret_msg, "k1": k1, "k2": k2,
            "known_hex": known_cipher.hex(" ").upper(), "secret_hex": secret_cipher.hex(" ").upper(),
            "pairs": pairs[:10], "n_pairs": len(pairs), "n_middle": n_middle, "runs": runs,
            "naive_runs": tinydes_core.KEY_SPACE ** 2, "elapsed": f"{elapsed:.1f}", "naive_ms": f"{naive_ms:,.0f}".replace(",", "."),
            "speedup": round(naive_ms / elapsed) if elapsed else 0, "read": read, "success": success,
        })
    except ValueError as e:
        db.add_history("Brute-force", "Gặp nhau ở giữa", known, status="error", note=str(e))
        return render("bruteforce.html", mm_error=str(e))


# ---------------------------------------------------------------------------
# KỊCH BẢN (bản gọn, đúng code git nhóm): VÉT CẠN 1 KHỐI 8 BIT
#   An mã hóa đúng 1 khối 8 bit. Kẻ xấu biết trước bản rõ khối đó, thử hết 256 khóa,
#   khóa nào giải ra đúng bản rõ là khóa khả nghi. Giống hàm run_brute_force trong git.
# ---------------------------------------------------------------------------
@app.post("/sdes_bf_block")
def sdes_bf_block():
    plain = request.form.get("bfb_plain", "").strip()
    key = request.form.get("bfb_key", "").strip()
    try:
        if not tinydes_core.is_bits(plain, 8):
            raise ValueError("Bản rõ phải gồm đúng 8 bit 0/1 (VD 01101111).")
        if not tinydes_core.is_bits(key, 8):
            raise ValueError("Khóa phải gồm đúng 8 bit 0/1 (VD 10101100).")

        sdes = tinydes_core.TinyDES()

        # PHÍA AN: mã hóa 1 khối
        cipher = sdes.encrypt(plain, key)

        # PHÍA KẺ XẤU: biết bản rõ, thử 256 khóa, giữ khóa giải ra đúng bản rõ
        t0 = time.perf_counter()
        found = []
        for k in tinydes_core.all_keys():               # "00000000" ... "11111111"
            if sdes.decrypt(cipher, k) == plain:
                found.append({"key": k, "i": int(k, 2) + 1})   # i: thử tới lần thứ mấy
        elapsed = (time.perf_counter() - t0) * 1000

        success = key in [f["key"] for f in found]
        db.add_history("Brute-force", "Vét cạn 1 khối", plain, cipher,
                       1, round(elapsed, 3), status="ok" if success else "error",
                       note=f"Thử {tinydes_core.KEY_SPACE} khóa, khớp {len(found)}")
        return render("bruteforce.html", bfb={
            "plain": plain, "key": key, "cipher": cipher,
            "found": found, "tried": tinydes_core.KEY_SPACE, "elapsed": f"{elapsed:.2f}",
            "success": success,
        })
    except ValueError as e:
        db.add_history("Brute-force", "Vét cạn 1 khối", plain, status="error", note=str(e))
        return render("bruteforce.html", bfb_error=str(e))


# ---------------------------------------------------------------------------
# KỊCH BẢN (bản gọn, đúng code git nhóm): CHỌN BẢN RÕ 1 KHỐI 8 BIT
#   Kẻ xấu mượn hộp đen mã hóa của An, nạp đủ 256 bản rõ 8 bit để dựng bảng tra
#   (bản mã -> bản rõ), rồi dịch ngược bản mã mục tiêu bằng tra bảng, không cần tìm khóa.
#   Giống hàm run_chosen_plaintext trong git.
# ---------------------------------------------------------------------------
@app.post("/sdes_cp_block")
def sdes_cp_block():
    plain = request.form.get("cpb_plain", "").strip()
    key = request.form.get("cpb_key", "").strip()
    try:
        if not tinydes_core.is_bits(plain, 8):
            raise ValueError("Bản rõ phải gồm đúng 8 bit 0/1 (VD 01101111).")
        if not tinydes_core.is_bits(key, 8):
            raise ValueError("Khóa phải gồm đúng 8 bit 0/1 (VD 10101100).")

        sdes = tinydes_core.TinyDES()

        # PHÍA AN: hộp đen giữ khóa bên trong + bản mã mục tiêu
        def oracle(pt):                                 # kẻ xấu gọi được, nhưng không xem được khóa
            return sdes.encrypt(pt, key)
        target = oracle(plain)

        # PHÍA KẺ XẤU: nạp 256 bản rõ dựng bảng tra, rồi tra ngược bản mã mục tiêu
        t0 = time.perf_counter()
        lookup = {}
        for i in range(tinydes_core.KEY_SPACE):
            pt = format(i, "08b")
            lookup[oracle(pt)] = pt
        cracked = lookup.get(target)
        elapsed = (time.perf_counter() - t0) * 1000

        success = cracked == plain
        db.add_history("Brute-force", "Chọn bản rõ 1 khối", plain, target,
                       1, round(elapsed, 3), status="ok" if success else "error",
                       note=f"Gọi hộp đen {tinydes_core.KEY_SPACE} lần, bảng {len(lookup)} dòng")
        return render("bruteforce.html", cpb={
            "plain": plain, "key": key, "cipher": target,
            "cracked": cracked, "calls": tinydes_core.KEY_SPACE, "rows": len(lookup),
            "elapsed": f"{elapsed:.2f}", "success": success,
        })
    except ValueError as e:
        db.add_history("Brute-force", "Chọn bản rõ 1 khối", plain, status="error", note=str(e))
        return render("bruteforce.html", cpb_error=str(e))


# ---------------------------------------------------------------------------
# PHÒNG CHAT: An gửi tin cho Bình, kẻ xấu ngồi giữa đường truyền
#   - An và Bình đã thống nhất trước 1 khóa bí mật (kẻ xấu không biết)
#   - Mỗi tin An gửi được mã hóa thật bằng core/ (TinyDES hoặc DES), Bình giải mã bằng cùng khóa
#   - Kẻ xấu chỉ thấy bản mã: có thể vét cạn khóa, hoặc sửa bản mã rồi chuyển tiếp cho Bình
# Trang /chat gọi 3 địa chỉ /api/chat/... bằng JavaScript (static/chat.js), nhận lại JSON.
# ---------------------------------------------------------------------------
DES_TRY = 2000      # số khóa DES kẻ xấu thử để đo tốc độ (thử hết 2^56 khóa là không thể)


def chat_cipher(algo, key):
    """
    Trả về 2 hàm (mã hóa, giải mã) dạng bytes -> bytes cho thuật toán đã chọn.
    VD: enc, dec = chat_cipher("tinydes", "11011010"); dec(enc(b"Hi")) == b"Hi"
        chat_cipher("des", "nhom2026")  -> dùng DES với khóa 8 byte b"nhom2026"
    """
    if algo == "tinydes":
        if not tinydes_core.is_bits(key, 8):
            raise ValueError("Khóa TinyDES phải gồm đúng 8 bit 0/1, VD 11011010.")
        keys = tinydes_core.generate_keys(key)              # sinh K1, K2, K3 một lần, dùng cho mọi byte
        return (lambda data: tinydes_core.encrypt_bytes(data, key, keys),
                lambda data: tinydes_core.decrypt_bytes(data, key, keys))
    des_key = utils.parse_des_key(key)                      # 8 ký tự hoặc 16 hex -> 8 byte (sai -> ValueError)
    return (lambda data: utils.des_encrypt_bytes(data, des_key),
            lambda data: utils.des_decrypt_bytes(data, des_key))


def chat_json():
    """Đọc dữ liệu JSON trang chat gửi lên. VD {"algo": "tinydes", "key": "11011010", "text": "Hi"}"""
    data = request.get_json(silent=True) or {}              # silent=True: dữ liệu hỏng thì trả None thay vì báo lỗi
    algo = "des" if data.get("algo") == "des" else "tinydes"
    return data, algo, str(data.get("key", "")).strip()


@app.get("/huong-dan")
def guide():
    """Trang hướng dẫn: web chạy thế nào (HTML, Python, JavaScript), phòng chat gửi tin bằng gì (nội dung tĩnh trong guide.html)."""
    return render("guide.html")


def source_of(fn):
    """
    Lấy mã nguồn THẬT của 1 hàm kèm số dòng, để trang /doc-code luôn khớp với code (sửa code là trang tự đổi).
    VD: source_of(tinydes_core.xor)
        -> {"file": "core/tinydes_core.py", "start": 64, "end": 70, "lines": [(64, "def xor(a, b):"), ...]}
    """
    lines, start = inspect.getsourcelines(fn)             # danh sách dòng code + số dòng bắt đầu
    path = os.path.relpath(inspect.getsourcefile(fn), os.path.dirname(os.path.abspath(__file__)))
    return {"file": path, "start": start, "end": start + len(lines) - 1,
            # enumerate(lines): đánh số từng dòng 0, 1, 2...; cộng start ra số dòng thật trong file
            "lines": [(start + i, line.rstrip("\n")) for i, line in enumerate(lines)]}

@app.get("/doc-code")
def code_guide():
    """Trang "Đọc code cùng thuật toán": mỗi bước thuật toán đặt cạnh đoạn code thật và giá trị chạy thật."""
    t, d = tinydes_core, des_core
    funcs = {
        "permute": t.permute, "left_shift": t.left_shift, "xor": t.xor,
        "generate_keys": t.generate_keys, "sbox_lookup": t.sbox_lookup, "f_function": t.f_function,
        "encrypt_block": t._encrypt_block, "decrypt_block": t._decrypt_block, "encrypt": t.encrypt,
        "encrypt_bytes": t.encrypt_bytes, "brute_force_co": t.brute_force_ciphertext_only,
        "parse_des_key": utils.parse_des_key, "des_permute": d.permute, "rotl": d.rotl,
        "generate_subkeys": d.generate_subkeys, "pkcs7_pad": utils.pkcs7_pad, "pkcs7_unpad": utils.pkcs7_unpad,
        "sbox_sub": d.sbox_sub, "feistel_f": d.feistel_f, "crypt_block_verbose": d.crypt_block_verbose,
        "des_encrypt_bytes": utils.des_encrypt_bytes,
        "sdes_demo": sdes_demo, "chat_send": chat_send, "chat_attack": chat_attack, "chat_tamper": chat_tamper,
    }
    src = {name: source_of(fn) for name, fn in funcs.items()}

    # Ví dụ TinyDES: bài tập slide 72, chạy thật bằng trace()
    key, pt = "10011010", "01011100"
    tr = t.trace(pt, key)

    # Ví dụ DES: chạy thật khối 0123456789ABCDEF với khóa 133457799BBCDFF1, và "Xin chào" với khóa nhom2026
    des_key = bytes.fromhex("133457799BBCDFF1")
    des_key_log = []
    des_subkeys = d.generate_subkeys(des_key, des_key_log)
    des_out, des_log = d.crypt_block_verbose(bytes.fromhex("0123456789ABCDEF"), des_subkeys)
    xin = "Xin chào".encode("utf-8")
    xin_key = utils.parse_des_key("nhom2026")
    ex = {
        "key": key, "pt": pt, "tr": tr,
        "hello": t.encrypt_bytes(b"Hello", key).hex(" ").upper(),
        "des_key_log": des_key_log, "des_log": des_log, "des_out": des_out.hex().upper(),
        "des_f1": des_log[1],
        "subkeys": [f"{k:012X}" for k in des_subkeys],
        "k1": f"{des_subkeys[0]:012X}", "k16": f"{des_subkeys[15]:012X}",
        "xin": xin.hex(" ").upper(), "xin_pad": utils.pkcs7_pad(xin).hex(" ").upper(),
        "xin_enc": utils.des_encrypt_bytes(xin, xin_key).hex(" ").upper(),
    }

    return render("code_guide.html", src=src, ex=ex)

@app.get("/chat")
def chat():
    """Trang phòng chat: chỉ hiện khung, mọi thao tác do static/chat.js gọi /api/chat/..."""
    return render("chat.html")


@app.post("/api/chat/send")
def chat_send():
    """
    An gửi 1 tin. Trả về bản mã (thứ đi trên đường truyền) và tin Bình giải mã được.
    VD vào {"algo": "tinydes", "key": "11011010", "text": "Hello"}
       ra  {"ok": true, "cipher_hex": "43 61 DA DA C0", "bob_text": "Hello", "weak": false, ...}
    """
    data, algo, key = chat_json()
    text = str(data.get("text", ""))
    try:
        if not text:
            raise ValueError("An chưa gõ tin nhắn.")
        enc, dec = chat_cipher(algo, key)
        t0 = time.perf_counter()
        cipher = enc(text.encode("utf-8"))                  # phía AN: chữ -> byte -> mã hóa
        bob = dec(cipher).decode("utf-8", errors="replace")  # phía BÌNH: giải mã bằng cùng khóa -> chữ
        elapsed = (time.perf_counter() - t0) * 1000
        # Khóa TinyDES yếu: 3 khóa con không khác nhau hết (VD 11110000 -> 3 khóa con giống hệt)
        weak = algo == "tinydes" and len(set(tinydes_core.generate_keys(key))) < 3
        db.add_history("Chat", "An gửi Bình", text, cipher.hex(" ").upper(), len(cipher), round(elapsed, 3),
                       note="TinyDES" if algo == "tinydes" else "DES")
        return jsonify(ok=True, cipher_hex=cipher.hex(" ").upper(), n_bytes=len(cipher), n_plain=len(text.encode("utf-8")),
                       bob_text=bob, elapsed=round(elapsed, 2), weak=weak)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/chat/attack")
def chat_attack():
    """
    Kẻ xấu vét cạn khóa. Chỉ dùng BẢN MÃ, không dùng khóa thật để tìm.
    (khóa thật chỉ được gửi lên để kiểm chứng "kẻ xấu đoán đúng chưa" vì đây là mô phỏng)
    TinyDES: thử đủ 256 khóa -> thường đoán ra ngay.
    DES    : thử DES_TRY khóa để đo tốc độ, rồi tính cần bao lâu để thử hết 2^56 khóa.
    """
    data, algo, key = chat_json()
    try:
        cipher = bytes.fromhex(str(data.get("cipher_hex", "")))   # "43 61 DA" -> b'\x43\x61\xda'
        if not cipher:
            raise ValueError("Không có bản mã để tấn công.")
        t0 = time.perf_counter()
        if algo == "tinydes":
            top = tinydes_core.brute_force_ciphertext_only(cipher, top=3)
            elapsed = (time.perf_counter() - t0) * 1000
            guess = top[0]                                  # ứng viên điểm "giống chữ" cao nhất
            success = guess["key"] == key
            db.add_history("Brute-force", "Kẻ xấu vét cạn (chat)", data.get("cipher_hex"), guess["key"], len(cipher),
                           round(elapsed, 3), status="ok" if success else "error", note="TinyDES, 256 khóa")
            return jsonify(ok=True, algo=algo, tried=tinydes_core.KEY_SPACE, elapsed=round(elapsed, 2), success=success,
                           top=[{"key": c["key"], "score": c["score"],
                                 "text": c["plain"].decode("utf-8", errors="replace")} for c in top])
        # DES: chỉ giải mã thử khối đầu tiên với khóa 0, 1, 2, ... (mỗi lần phải sinh lại 16 khóa con)
        first = cipher[:8]
        for k in range(DES_TRY):
            des_core.decrypt_block(first, k.to_bytes(8, "big"))   # số k -> 8 byte làm khóa thử
        elapsed = (time.perf_counter() - t0) * 1000
        per_sec = DES_TRY / (elapsed / 1000)                # tốc độ: số khóa thử được mỗi giây
        years = 2 ** 56 / per_sec / (3600 * 24 * 365)       # thời gian thử hết 2^56 khóa, đổi ra năm
        db.add_history("Brute-force", "Kẻ xấu vét cạn (chat)", data.get("cipher_hex"), "không tìm thấy", len(cipher),
                       round(elapsed, 3), status="error", note=f"DES, thử {DES_TRY} khóa")
        return jsonify(ok=True, algo=algo, tried=DES_TRY, elapsed=round(elapsed, 2), success=False,
                       per_sec=round(per_sec), years=years, total_keys=2 ** 56)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/chat/chosen")
def chat_chosen():
    """
    Kẻ xấu tấn công chọn bản rõ: mượn hộp đen mã hóa của An (có khóa bên trong), đưa 256 bản rõ vào để lập bảng tra,
    rồi tra bảng dịch bản mã. Không tìm khóa.
    TinyDES: khối 8 bit -> bảng chỉ 256 dòng, dịch được ngay.
    DES    : khối 64 bit -> bảng cần 2^64 dòng, không thể lập.
    """
    data, algo, key = chat_json()
    try:
        cipher = bytes.fromhex(str(data.get("cipher_hex", "")))
        if not cipher:
            raise ValueError("Không có bản mã để tấn công.")
        if algo == "des":
            return jsonify(ok=True, algo=algo, rows=2 ** 64, success=False)
        enc, _ = chat_cipher(algo, key)                     # hộp đen: chỉ gọi enc, không đọc key
        t0 = time.perf_counter()
        plain, book = tinydes_core.chosen_plaintext_attack(cipher, lambda p: format(enc(bytes([int(p, 2)]))[0], "08b"))
        elapsed = (time.perf_counter() - t0) * 1000
        text = plain.decode("utf-8", errors="replace")
        db.add_history("Brute-force", "Chọn bản rõ (chat)", data.get("cipher_hex"), text, len(cipher),
                       round(elapsed, 3), status="ok", note=f"Bảng tra {len(book)} dòng")
        return jsonify(ok=True, algo=algo, calls=tinydes_core.BLOCK_SPACE, rows=len(book),
                       elapsed=round(elapsed, 2), success=True, text=text)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/chat/tamper")
def chat_tamper():
    """
    Kẻ xấu đổi 1 bit của byte thứ `index` trong bản mã rồi chuyển tiếp. Bình giải mã bản mã đã bị sửa.
    TinyDES: chỉ đúng 1 chữ bị hỏng (mỗi byte mã riêng).
    DES    : cả khối 8 byte chứa nó bị hỏng; nếu hỏng khối cuối thì thường báo lỗi đệm.
    """
    data, algo, key = chat_json()
    try:
        cipher = bytearray(bytes.fromhex(str(data.get("cipher_hex", ""))))   # bytearray: sửa được từng byte
        if not cipher:
            raise ValueError("Không có bản mã để sửa.")
        index = int(data.get("index", 0)) % len(cipher)     # "%": vị trí vượt quá độ dài thì quay vòng lại
        cipher[index] ^= 0x01                               # đổi đúng 1 bit cuối của byte đó (0 <-> 1)
        _, dec = chat_cipher(algo, key)
        try:
            bob, bob_error = dec(bytes(cipher)).decode("utf-8", errors="replace"), None
        except ValueError as e:                             # DES: đệm sai -> giải mã báo lỗi
            bob, bob_error = None, str(e)
        db.add_history("Chat", "Kẻ xấu sửa tin", data.get("cipher_hex"), bob or bob_error, len(cipher),
                       status="error", note=f"Đổi 1 bit ở byte {index}")
        return jsonify(ok=True, cipher_hex=bytes(cipher).hex(" ").upper(), index=index,
                       bob_text=bob, bob_error=bob_error)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


# ---------------------------------------------------------------------------
# Đo thời gian chạy theo kích thước dữ liệu
# ---------------------------------------------------------------------------
def _measure(fn):
    """Chạy hàm fn 1 lần, trả về thời gian chạy (ms)."""
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000


@app.post("/benchmark")
def benchmark():
    from Crypto.Cipher import DES as LibDES                 # thư viện chỉ để so sánh tốc độ
    from Crypto.Util.Padding import pad

    key = b"benchkey"                                       # khóa 8 byte cố định
    sdes_key = "10011010"
    rows = []
    for size in BENCH_SIZES:                                # 1 KB, 10 KB, 100 KB, 1 MB
        data = os.urandom(size)                             # dữ liệu ngẫu nhiên đúng `size` byte
        enc = utils.des_encrypt_bytes(data, key)            # bản mã để đo thời gian giải mã
        # lambda: hàm không tên viết 1 dòng, truyền vào _measure để đo
        des_enc = _measure(lambda: utils.des_encrypt_bytes(data, key))
        des_dec = _measure(lambda: utils.des_decrypt_bytes(enc, key))
        lib = _measure(lambda: LibDES.new(key, LibDES.MODE_ECB).encrypt(pad(data, 8)))
        # TinyDES dùng chuỗi bit nên chậm -> chỉ đo tới 100 KB
        sdes = _measure(lambda: tinydes_core.encrypt_bytes(data, sdes_key)) if size <= 100 * 1024 else None
        rows.append({
            "size": size, "label": f"{size // 1024} KB" if size < 1024 * 1024 else f"{size // (1024 * 1024)} MB",
            "des_enc": des_enc, "des_dec": des_dec, "lib": lib, "sdes": sdes,
            "speed": size / 1024 / (des_enc / 1000),        # KB / giây
        })
    max_ms = max(r["des_enc"] for r in rows)
    for r in rows:
        r["bar"] = 100 * r["des_enc"] / max_ms              # % độ dài thanh so sánh trên trang
    db.add_history("Benchmark", "Đo thời gian", "1 KB → 1 MB", f"DES 1 MB: {rows[-1]['des_enc']:.0f} ms",
                   sum(BENCH_SIZES), round(sum(r["des_enc"] for r in rows), 3), note="DES tự code vs pycryptodome")
    return render("benchmark.html", bench=rows)


# ---------------------------------------------------------------------------
# Lịch sử thao tác (SQLite)
# ---------------------------------------------------------------------------
@app.get("/history")
def history():
    return render("history.html", rows=db.get_history(), stats=db.get_stats(), db_path=db.DB_PATH)


@app.post("/history/clear")
def history_clear():
    db.clear_history()
    return redirect(url_for("history"))                     # xóa xong quay lại trang /history


@app.errorhandler(413)                                      # 413 = tệp tải lên vượt MAX_CONTENT_LENGTH
def too_large(_):
    return render("des.html", des_error="File quá lớn (tối đa 20 MB)."), 413


# Chỉ chạy khi chạy trực tiếp "python app.py" (không chạy khi file khác import app)
if __name__ == "__main__":
    app.run(debug=True)
