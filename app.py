import base64
import inspect
import io
import os
import time
import uuid

from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

import db
from core import des_core, tinydes_core, utils

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
db.init_db()

DOWNLOADS = {}
MAX_DOWNLOADS = 20
MAX_LOG_BLOCKS = 8
IMAGE_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".gif": "image/gif", ".bmp": "image/bmp", ".webp": "image/webp"}
MAX_PREVIEW = 3 * 1024 * 1024
BENCH_SIZES = [1024, 10 * 1024, 100 * 1024, 1024 * 1024]


def render(template, **ctx):
    """Hiển thị 1 trang HTML, luôn kèm SBOX và dữ liệu form vừa nhập."""
    form = request.form if request.method == "POST" else request.args
    return render_template(template, sbox=tinydes_core.SBOX, form=form, **ctx)


def store_download(filename, data):
    """Cất tệp kết quả vào RAM, trả về token cho link /download/<token>."""
    if len(DOWNLOADS) >= MAX_DOWNLOADS:
        DOWNLOADS.pop(next(iter(DOWNLOADS)))
    token = uuid.uuid4().hex
    DOWNLOADS[token] = (filename, data)
    return token


def image_data_uri(name, data):
    """Trả về data URI để xem trước ảnh (None nếu không phải ảnh)."""
    ext = os.path.splitext(name.lower())[1]
    if ext not in IMAGE_EXT or not data or len(data) > MAX_PREVIEW:
        return None
    return f"data:{IMAGE_EXT[ext]};base64," + base64.b64encode(data).decode()


def action_name(action):
    return "Mã hóa" if action == "enc" else "Giải mã"


def parse_sdes_data(raw, fmt, is_input_cipher):
    """Chuyển dữ liệu nhập về list các khối 8-bit ('0'/'1')."""
    if fmt == "bin":
        bits = "".join(raw.split())
        if not bits or len(bits) % 8 or any(c not in "01" for c in bits):
            raise ValueError("Dữ liệu nhị phân phải gồm các khối 8 bit (VD: 01011100).")
        return [bits[i:i + 8] for i in range(0, len(bits), 8)]
    if is_input_cipher:
        try:
            data = bytes.fromhex(raw.strip())
        except ValueError:
            raise ValueError("Bản mã dạng văn bản phải nhập ở dạng hex (VD: 3A F0 12).")
    else:
        data = raw.encode("utf-8")
    if not data:
        raise ValueError("Chưa nhập dữ liệu.")
    return [format(b, "08b") for b in data]


@app.get("/")
def index():
    return render("home.html", stats=db.get_stats())


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
    """Ca mẫu để chọn nhanh trong mục tự nhập."""
    import test_runner

    ex, dx = test_runner.TINYDES_EXAMPLE, test_runner.DES_CLASS_EXAMPLE
    presets = [
        {"label": "TinyDES — ví dụ trong tài liệu (trang 72)", "algo": "sdes", "plain": ex["plain"], "key": ex["key"], "expected": ex["cipher"]},
        {"label": "DES — ví dụ Grabbe", "algo": "des", "plain": dx["plain"], "key": dx["key"], "expected": dx["cipher"]},
    ]
    for i, (kind, key, pt, ct) in enumerate(test_runner.NIST_VECTORS, start=1):
        presets.append({"label": f"DES — NIST SP 800-17 #{i} ({kind})", "algo": "des", "plain": pt, "key": key, "expected": ct})
    return presets


def run_custom_test(algo, plain, key_text, expected):
    """Chạy 1 ca kiểm thử do người dùng nhập, trả về danh sách bước (có thể kèm PASS/FAIL)."""
    steps = []

    def step(title, desc, items, ok=None, detail=None):
        steps.append({"title": title, "desc": desc, "fields": items, "ok": ok, "detail": detail})

    if algo == "sdes":
        plain = "".join(plain.split())
        key = "".join(key_text.split())
        expected = "".join(expected.split())
        ok_in = tinydes_core.is_bits(plain, 8) and tinydes_core.is_bits(key, 8)
        step("Kiểm tra dữ liệu nhập", "Bản rõ đúng 8 bit, khóa đúng 8 bit (chỉ gồm 0/1)",
             [("Bản rõ", plain), ("Khóa", key)], ok_in)
        if not ok_in:
            raise ValueError("TinyDES: bản rõ và khóa đều phải là 8 bit (chỉ gồm 0 và 1).")
        if expected and not tinydes_core.is_bits(expected, 8):
            raise ValueError("Bản mã mong đợi của TinyDES phải là 8 bit.")

        t = tinydes_core.trace(plain, key)
        step("B1 · Sinh khóa con — generate_keys()", "KL0|KR0 → dịch 1, 2, 1 bit → Compress = K1, K2, K3",
             [(s["name"], s["bits"][:4] + " " + s["bits"][4:] if s.get("split") else s["bits"]) for s in t["key_steps"]])
        for r in t["rounds"]:
            n = r["n"]
            step(f"B2 · Vòng {n} — K{n} = {r['k']}", "Expand → ⊕K → S-box → P-box = F → L, R mới",
                 [("L | R", r["left"] + " " + r["right"]), ("Expand(R)", r["expand"]), (f"⊕ K{n}", r["xor"]),
                  ("S-box", f"{r['sbox']['in']} → hàng {r['sbox']['row']}, cột {r['sbox']['col']} → {r['sbox']['out']}"),
                  ("P-box = F", r["f"]), (f"R{n} = L{n - 1} ⊕ F", f"{r['mix']} ⊕ {r['f']} = {r['mixed']}"),
                  (f"L{n} R{n}", r["output"][:4] + " " + r["output"][4:])])
        cipher = t["output"]
        step("B2 · Bản mã C = L3 R3", "TinyDES không có hoán vị khởi tạo / kết thúc", [("Bản mã", cipher)])
        step("Đối chiếu: hàm encrypt() cho cùng kết quả", "Hàm mã hóa chính của chương trình, độc lập với trace() dùng để hiển thị",
             [("encrypt()", tinydes_core.encrypt(plain, key)[0]), ("trace()", cipher)],
             tinydes_core.encrypt(plain, key)[0] == cipher)
        back = tinydes_core.trace(cipher, key, decrypt=True)["output"]
    else:
        key = utils.parse_des_key(key_text)
        try:
            block = bytes.fromhex(plain.strip())
            exp_bytes = bytes.fromhex(expected.strip()) if expected.strip() else None
        except ValueError:
            raise ValueError("DES: bản rõ và bản mã mong đợi phải nhập dạng hex.")
        ok_in = len(block) == 8 and (exp_bytes is None or len(exp_bytes) == 8)
        step("Kiểm tra dữ liệu nhập", "Bản rõ là 1 khối 64 bit (16 ký tự hex), khóa 8 ký tự hoặc 16 hex",
             [("Bản rõ", block.hex().upper()), ("Khóa", key.hex().upper())], ok_in)
        if not ok_in:
            raise ValueError("DES: bản rõ (và bản mã mong đợi) phải đúng 16 ký tự hex = 1 khối 64 bit.")
        plain, expected = block.hex().upper(), exp_bytes.hex().upper() if exp_bytes else ""

        key_log = []
        subkeys = des_core.generate_subkeys(key, key_log)
        step("B1 · Sinh 16 khóa con — generate_subkeys()", "PC-1 → C0, D0 → 16 lần (dịch trái + PC-2)",
             [("C0", key_log[0]["c"]), ("D0", key_log[0]["d"]), ("K1", key_log[1]["k"]), ("K2", key_log[2]["k"]),
              ("K16", key_log[16]["k"])], detail={"type": "keys", "rows": key_log})
        out, rounds = des_core.crypt_block_verbose(block, subkeys)
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
        fast = des_core.encrypt_block(block, key).hex().upper()
        step("Đối chiếu: bản tối ưu crypt_block_fast()", "Bản dùng để mã hóa tệp phải cho cùng kết quả với bản có log",
             [("verbose", cipher), ("fast", fast)], fast == cipher)
        from Crypto.Cipher import DES as LibDES
        lib = LibDES.new(key, LibDES.MODE_ECB).encrypt(block).hex().upper()
        step("Đối chiếu thư viện pycryptodome", "Thư viện chuẩn chỉ dùng để so sánh, không dùng trong phần lõi",
             [("Nhóm tự code", cipher), ("pycryptodome", lib)], lib == cipher)
        back = des_core.decrypt_block(out, key).hex().upper()

    if expected:
        step("So với bản mã mong đợi", "Bản mã mong đợi do bạn nhập (ví dụ trên lớp, NIST…)",
             [("Mong đợi", expected), ("Thực tế", cipher)], expected.upper() == cipher.upper())
    step("B3 · Giải mã ngược lại bản mã", "Dùng khóa con theo thứ tự ngược, phải ra đúng bản rõ ban đầu",
         [("Bản mã", cipher), ("Giải mã", back), ("Bản rõ ban đầu", plain)], back == plain)

    checks = [s for s in steps if s["ok"] is not None]
    return {"algo": algo, "plain": plain, "cipher": cipher, "steps": steps,
            "passed": sum(s["ok"] for s in checks),
            "total": len(checks)}


@app.get("/tests")
def tests_page():
    return render("tests.html", presets=test_presets())


@app.route("/tests/custom", methods=["GET", "POST"])
def tests_custom():
    f = request.values
    algo = f.get("t_algo", "sdes")
    if not f.get("t_plain"):
        return render("tests.html", presets=test_presets())
    try:
        result = run_custom_test(algo, f.get("t_plain", ""), f.get("t_key", ""), f.get("t_expected", ""))
        db.add_history("Kiểm thử", "Ca tự nhập", f"{algo.upper()} P={result['plain']}", result["cipher"], None, None,
                       status="ok" if result["passed"] == result["total"] else "error",
                       note=f"Passed {result['passed']}/{result['total']} bước kiểm tra")
        return render("tests.html", presets=test_presets(), custom=result)
    except ValueError as e:
        db.add_history("Kiểm thử", "Ca tự nhập", f.get("t_plain", ""), status="error", note=str(e))
        return render("tests.html", presets=test_presets(), custom_error=str(e))


@app.post("/tests")
def tests_run():
    """Chạy toàn bộ test_runner.run_all() rồi nhóm kết quả theo A, B, C."""
    import test_runner

    results, ms = test_runner.run_all()
    groups = {}
    for c in results:
        groups.setdefault(c["group"], []).append(c)
    passed = sum(c["ok"] for c in results)
    db.add_history("Kiểm thử", "Chạy bộ test", "test_runner.run_all()", f"Passed {passed}/{len(results)}",
                   None, round(ms, 3), status="ok" if passed == len(results) else "error",
                   note="Nhóm tự viết + NIST SP 800-17 + pycryptodome")
    return render("tests.html", presets=test_presets(), groups=groups, passed=passed, total=len(results),
                  elapsed=f"{ms / 1000:.1f}")


@app.post("/sdes_demo")
def sdes_demo():
    key = request.form.get("sdes_key", "").strip()
    fmt = request.form.get("sdes_fmt", "bin")
    action = request.form.get("sdes_action", "enc")
    raw_input = request.form.get("sdes_input", "")
    try:
        blocks = parse_sdes_data(raw_input, fmt, action == "dec")
        key_log = []
        keys = tinydes_core.generate_keys(key, key_log)

        fn = tinydes_core.encrypt if action == "enc" else tinydes_core.decrypt
        out_blocks, block_logs = [], []
        t0 = time.perf_counter()
        for i, blk in enumerate(blocks):
            out, log = fn(blk, key)
            out_blocks.append(out)
            if i < MAX_LOG_BLOCKS:
                block_logs.append({"input": blk, "output": out, "steps": log[len(key_log):]})

        elapsed = (time.perf_counter() - t0) * 1000
        out_bytes = bytes(int(b, 2) for b in out_blocks)
        traces = [tinydes_core.trace(b, key, decrypt=(action == "dec")) for b in blocks[:MAX_LOG_BLOCKS]]
        result = {
            "subkeys": keys, "key_log": key_log, "blocks": block_logs,
            "total_blocks": len(blocks),
            "out_bin": " ".join(out_blocks),
            "out_hex": out_bytes.hex(" ").upper(),
            "out_text": out_bytes.decode("utf-8", errors="replace") if action == "dec" else None,
            "action": action, "fmt": fmt,
            "traces": traces,
        }
        first = traces[0]
        result["flow"] = [("Đầu vào", first["input"])] + [(f"Vòng {r['n']}", r["output"]) for r in first["rounds"]]
        if action == "enc":
            original = bytes(int(b, 2) for b in blocks)
            back = tinydes_core.decrypt_bytes(out_bytes, key)
            result["roundtrip"] = {
                "ok": back == original,
                "bin": " ".join(format(b, "08b") for b in back),
                "text": back.decode("utf-8", errors="replace") if fmt == "text" else None,
            }
        db.add_history("TinyDES", action_name(action), raw_input,
                       result["out_text"] if action == "dec" and fmt == "text" else result["out_hex"],
                       len(out_bytes), round(elapsed, 3), note=f"{len(blocks)} khối 8-bit")
        return render("sdes.html", sdes=result)
    except ValueError as e:
        db.add_history("TinyDES", action_name(action), raw_input, status="error", note=str(e))
        return render("sdes.html", sdes_error=str(e))


@app.post("/des_file")
def des_file():
    action = request.form.get("des_action", "enc")
    upload = request.files.get("des_file")
    try:
        key = utils.parse_des_key(request.form.get("des_key", ""))

        if upload and upload.filename:
            data, name, from_file = upload.read(), os.path.basename(upload.filename), True
        else:
            text = request.form.get("des_text", "")
            if action == "enc":
                data = text.encode("utf-8")
            else:
                try:
                    data = bytes.fromhex(text.strip())
                except ValueError:
                    raise ValueError("Bản mã dạng văn bản phải nhập ở dạng hex.")
            name, from_file = "text.txt", False
        if not data and action == "dec":
            raise ValueError("Chưa nhập dữ liệu hoặc chưa chọn file.")

        key_log = []
        subkeys = des_core.generate_subkeys(key, key_log)

        t0 = time.perf_counter()
        if action == "enc":
            out = utils.des_encrypt_bytes(data, key)
            first_in = utils.pkcs7_pad(data)[:8]
            out_name = name + ".enc"
            round_keys = subkeys
        else:
            out = utils.des_decrypt_bytes(data, key)
            first_in = data[:8]
            out_name = name[:-4] if name.endswith(".enc") else "decrypted_" + name
            round_keys = subkeys[::-1]
        elapsed = (time.perf_counter() - t0) * 1000

        _, round_log = des_core.crypt_block_verbose(first_in, round_keys)

        result = {
            "action": action, "name": name, "out_name": out_name,
            "in_size": len(data), "out_size": len(out),
            "blocks": (len(out) + 7) // 8,
            "elapsed": f"{elapsed:.1f}", "key_hex": key.hex().upper(),
            "key_log": key_log, "round_log": round_log, "first_in": first_in.hex().upper(),
            "preview_hex": out[:128].hex(" ").upper(),
            "out_text": None, "token": store_download(out_name, out),
        }
        if action == "enc":
            back = utils.des_decrypt_bytes(out, key)
            result["roundtrip_ok"] = back == data
            result["img_before"] = image_data_uri(name, data)
            result["img_after"] = image_data_uri(name, back)
            if not from_file:
                result["roundtrip_text"] = back.decode("utf-8", errors="replace")
        else:
            result["img_after"] = image_data_uri(out_name, out)
        db.add_history("DES", action_name(action), name if from_file else request.form.get("des_text", ""),
                       out_name if from_file else out[:30].hex().upper(), len(data), round(elapsed, 3),
                       note=f"{'File' if from_file else 'Văn bản'} · {result['blocks']} khối · ECB/PKCS#7")
        if not from_file:
            if action == "enc":
                result["out_text"] = out.hex().upper()
            else:
                result["out_text"] = out.decode("utf-8", errors="replace")
        return render("des.html", des=result)
    except ValueError as e:
        name = upload.filename if upload and upload.filename else "văn bản"
        db.add_history("DES", action_name(action), name, status="error", note=str(e))
        return render("des.html", des_error=str(e))


@app.get("/download/<token>")
def download(token):
    if token not in DOWNLOADS:
        abort(404)
    name, data = DOWNLOADS[token]
    return send_file(io.BytesIO(data), as_attachment=True, download_name=name)


@app.post("/sdes_bruteforce")
def sdes_bruteforce():
    """Bẻ khóa TinyDES bằng vét cạn 256 khóa khi biết 1 cặp (bản rõ, bản mã)."""
    fmt = request.form.get("bf_fmt", "text")
    try:
        plain_blocks = parse_sdes_data(request.form.get("bf_plain", ""), fmt, False)
        cipher_blocks = parse_sdes_data(request.form.get("bf_cipher", ""), fmt, True)
        if len(plain_blocks) != len(cipher_blocks):
            raise ValueError("Bản rõ và bản mã phải có cùng số khối (byte).")
        plain = bytes(int(b, 2) for b in plain_blocks)
        cipher = bytes(int(b, 2) for b in cipher_blocks)

        found = []
        t0 = time.perf_counter()
        for key in tinydes_core.all_keys():
            keys = tinydes_core.generate_keys(key)
            if tinydes_core.encrypt_bytes(plain, key, keys) == cipher:
                found.append({"key": key, "dec": int(key, 2), "subkeys": keys})
        elapsed = (time.perf_counter() - t0) * 1000

        db.add_history("Brute-force", "Bẻ khóa", request.form.get("bf_plain", ""),
                       ", ".join(f["key"] for f in found) or "không tìm thấy", len(plain), round(elapsed, 3),
                       status="ok" if found else "error", note=f"Thử {tinydes_core.KEY_SPACE} khóa, khớp {len(found)}")
        return render("bruteforce.html", bf={"found": found, "tried": tinydes_core.KEY_SPACE, "elapsed": f"{elapsed:.2f}", "n_bytes": len(plain)})
    except ValueError as e:
        db.add_history("Brute-force", "Bẻ khóa", request.form.get("bf_plain", ""), status="error", note=str(e))
        return render("bruteforce.html", bf_error=str(e))


@app.post("/sdes_bruteforce_cipher")
def sdes_bruteforce_cipher():
    """Tấn công chỉ biết bản mã (ciphertext-only)."""
    message = request.form.get("co_message", "")
    secret = request.form.get("co_key", "").strip()
    try:
        if not message:
            raise ValueError("Người gửi chưa nhập thông điệp.")
        if not tinydes_core.is_bits(secret, 8):
            raise ValueError("Khóa bí mật phải gồm đúng 8 bit 0/1.")

        cipher = tinydes_core.encrypt_bytes(message.encode("utf-8"), secret)

        t0 = time.perf_counter()
        top = tinydes_core.brute_force_ciphertext_only(cipher, top=5)
        elapsed = (time.perf_counter() - t0) * 1000
        for c in top:
            c["text"] = c["plain"].decode("utf-8", errors="replace")
        guess = top[0]

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


@app.post("/sdes_chosen_plaintext")
def sdes_chosen_plaintext():
    """Tấn công chọn bản rõ (chosen-plaintext): lập bảng tra 256 dòng từ hộp đen mã hóa."""
    message = request.form.get("cp_message", "")
    secret = request.form.get("cp_key", "").strip()
    try:
        if not message:
            raise ValueError("Người gửi chưa nhập thông điệp.")
        if not tinydes_core.is_bits(secret, 8):
            raise ValueError("Khóa bí mật phải gồm đúng 8 bit 0/1.")

        keys = tinydes_core.generate_keys(secret)
        cipher = tinydes_core.encrypt_bytes(message.encode("utf-8"), secret, keys)

        def oracle(plain_8bit):
            return tinydes_core._encrypt_block(plain_8bit, keys)

        t0 = time.perf_counter()
        plain, book = tinydes_core.chosen_plaintext_attack(cipher, oracle)
        elapsed = (time.perf_counter() - t0) * 1000
        text = plain.decode("utf-8", errors="replace") if plain is not None else None

        enc_of = {p: c for c, p in book.items()}
        grid = [[f"{int(enc_of[format(r * 16 + c, '08b')], 2):02X}" for c in range(16)] for r in range(16)]
        used = sorted({b for b in cipher})
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


MITM_SAMPLE = 8


@app.post("/sdes_mitm")
def sdes_mitm():
    """Tấn công gặp nhau ở giữa (meet-in-the-middle) vào TinyDES 2 lớp."""
    known = request.form.get("mm_known", "")
    secret_msg = request.form.get("mm_secret", "")
    k1, k2 = request.form.get("mm_k1", "").strip(), request.form.get("mm_k2", "").strip()
    try:
        if not known or not secret_msg:
            raise ValueError("Cần nhập cả tin đã biết và tin bí mật.")
        if not (tinydes_core.is_bits(k1, 8) and tinydes_core.is_bits(k2, 8)):
            raise ValueError("K1 và K2 phải gồm đúng 8 bit 0/1.")

        known_cipher = tinydes_core.double_encrypt_bytes(known.encode("utf-8"), k1, k2)
        secret_cipher = tinydes_core.double_encrypt_bytes(secret_msg.encode("utf-8"), k1, k2)

        t0 = time.perf_counter()
        pairs, n_middle, runs = tinydes_core.meet_in_the_middle(known.encode("utf-8"), known_cipher)
        elapsed = (time.perf_counter() - t0) * 1000

        all_sub = [tinydes_core.generate_keys(k) for k in tinydes_core.all_keys()]
        t0 = time.perf_counter()
        for sub1 in all_sub[:MITM_SAMPLE]:
            mid = tinydes_core.encrypt_bytes(known.encode("utf-8"), None, sub1)
            for sub2 in all_sub:
                tinydes_core.encrypt_bytes(mid, None, sub2)
        naive_ms = (time.perf_counter() - t0) * 1000 * tinydes_core.KEY_SPACE / MITM_SAMPLE

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


DES_TRY = 2000


def chat_cipher(algo, key):
    """Trả về 2 hàm (mã hóa, giải mã) dạng bytes -> bytes cho thuật toán đã chọn."""
    if algo == "tinydes":
        if not tinydes_core.is_bits(key, 8):
            raise ValueError("Khóa TinyDES phải gồm đúng 8 bit 0/1, VD 11011010.")
        keys = tinydes_core.generate_keys(key)
        return (lambda data: tinydes_core.encrypt_bytes(data, key, keys),
                lambda data: tinydes_core.decrypt_bytes(data, key, keys))
    des_key = utils.parse_des_key(key)
    return (lambda data: utils.des_encrypt_bytes(data, des_key),
            lambda data: utils.des_decrypt_bytes(data, des_key))


def chat_json():
    """Đọc dữ liệu JSON trang chat gửi lên."""
    data = request.get_json(silent=True) or {}
    algo = "des" if data.get("algo") == "des" else "tinydes"
    return data, algo, str(data.get("key", "")).strip()


@app.get("/huong-dan")
def guide():
    return render("guide.html")


def source_of(fn):
    """Lấy mã nguồn thật của 1 hàm kèm số dòng, cho trang /doc-code."""
    lines, start = inspect.getsourcelines(fn)
    path = os.path.relpath(inspect.getsourcefile(fn), os.path.dirname(os.path.abspath(__file__)))
    return {"file": path, "start": start, "end": start + len(lines) - 1,
            "lines": [(start + i, line.rstrip("\n")) for i, line in enumerate(lines)]}


@app.get("/doc-code")
def code_guide():
    """Trang "Đọc code cùng thuật toán"."""
    t, d = tinydes_core, des_core
    funcs = {
        "permute": t.permute, "left_shift": t.left_shift, "xor": t.xor,
        "generate_keys": t.generate_keys, "sbox_lookup": t.sbox_lookup, "f_function": t.f_function,
        "encrypt_block": t._encrypt_block, "decrypt_block": t._decrypt_block, "encrypt": t.encrypt,
        "encrypt_bytes": t.encrypt_bytes, "brute_force_co": t.brute_force_ciphertext_only,
        "parse_des_key": utils.parse_des_key, "des_permute": d.permute, "rotl": d.rotl,
        "generate_subkeys": d.generate_subkeys, "pkcs7_pad": utils.pkcs7_pad, "pkcs7_unpad": utils.pkcs7_unpad,
        "sbox_sub": d.sbox_sub, "feistel_f": d.feistel_f, "crypt_block_verbose": d.crypt_block_verbose,
        "decrypt_block": d.decrypt_block, "des_encrypt_bytes": utils.des_encrypt_bytes,
        "sdes_demo": sdes_demo, "chat_send": chat_send, "chat_attack": chat_attack, "chat_tamper": chat_tamper,
    }
    src = {name: source_of(fn) for name, fn in funcs.items()}

    key, pt = "10011010", "01011100"
    tr = t.trace(pt, key)
    des_key, des_pt = bytes.fromhex("133457799BBCDFF1"), bytes.fromhex("0123456789ABCDEF")
    key_log = []
    subkeys = d.generate_subkeys(des_key, key_log)
    des_out, des_log = d.crypt_block_verbose(des_pt, subkeys)
    detail = {}
    d.feistel_f(int(des_log[0]["r"], 16), subkeys[0], detail)
    text = "Xin chào".encode("utf-8")
    ex = {
        "key": key, "pt": pt, "tr": tr, "hello": t.encrypt_bytes(b"Hello", key).hex(" ").upper(),
        "des_key_log": key_log, "des_log": des_log, "des_out": des_out.hex().upper(), "des_f1": detail,
        "k1": f"{subkeys[0]:012X}", "k16": f"{subkeys[15]:012X}",
        "xin": text.hex(" ").upper(), "xin_pad": utils.pkcs7_pad(text).hex(" ").upper(),
        "xin_enc": utils.des_encrypt_bytes(text, b"nhom2026").hex(" ").upper(),
    }
    return render("code_guide.html", src=src, ex=ex)


@app.get("/chat")
def chat():
    return render("chat.html")


@app.post("/api/chat/send")
def chat_send():
    """An gửi 1 tin: trả về bản mã trên đường truyền và tin Bình giải mã được."""
    data, algo, key = chat_json()
    text = str(data.get("text", ""))
    try:
        if not text:
            raise ValueError("An chưa gõ tin nhắn.")
        enc, dec = chat_cipher(algo, key)
        t0 = time.perf_counter()
        cipher = enc(text.encode("utf-8"))
        bob = dec(cipher).decode("utf-8", errors="replace")
        elapsed = (time.perf_counter() - t0) * 1000
        weak = algo == "tinydes" and len(set(tinydes_core.generate_keys(key))) < 3
        db.add_history("Chat", "An gửi Bình", text, cipher.hex(" ").upper(), len(cipher), round(elapsed, 3),
                       note="TinyDES" if algo == "tinydes" else "DES")
        return jsonify(ok=True, cipher_hex=cipher.hex(" ").upper(), n_bytes=len(cipher), n_plain=len(text.encode("utf-8")),
                       bob_text=bob, elapsed=round(elapsed, 2), weak=weak)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/chat/attack")
def chat_attack():
    """Kẻ xấu vét cạn khóa chỉ từ bản mã (TinyDES thử đủ 256 khóa, DES chỉ đo tốc độ rồi ước lượng)."""
    data, algo, key = chat_json()
    try:
        cipher = bytes.fromhex(str(data.get("cipher_hex", "")))
        if not cipher:
            raise ValueError("Không có bản mã để tấn công.")
        t0 = time.perf_counter()
        if algo == "tinydes":
            top = tinydes_core.brute_force_ciphertext_only(cipher, top=3)
            elapsed = (time.perf_counter() - t0) * 1000
            guess = top[0]
            success = guess["key"] == key
            db.add_history("Brute-force", "Kẻ xấu vét cạn (chat)", data.get("cipher_hex"), guess["key"], len(cipher),
                           round(elapsed, 3), status="ok" if success else "error", note="TinyDES, 256 khóa")
            return jsonify(ok=True, algo=algo, tried=tinydes_core.KEY_SPACE, elapsed=round(elapsed, 2), success=success,
                           top=[{"key": c["key"], "score": c["score"],
                                 "text": c["plain"].decode("utf-8", errors="replace")} for c in top])
        first = cipher[:8]
        for k in range(DES_TRY):
            des_core.decrypt_block(first, k.to_bytes(8, "big"))
        elapsed = (time.perf_counter() - t0) * 1000
        per_sec = DES_TRY / (elapsed / 1000)
        years = 2 ** 56 / per_sec / (3600 * 24 * 365)
        db.add_history("Brute-force", "Kẻ xấu vét cạn (chat)", data.get("cipher_hex"), "không tìm thấy", len(cipher),
                       round(elapsed, 3), status="error", note=f"DES, thử {DES_TRY} khóa")
        return jsonify(ok=True, algo=algo, tried=DES_TRY, elapsed=round(elapsed, 2), success=False,
                       per_sec=round(per_sec), years=years, total_keys=2 ** 56)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/chat/chosen")
def chat_chosen():
    """Kẻ xấu tấn công chọn bản rõ: TinyDES lập được bảng 256 dòng, DES cần 2^64 dòng nên không thể."""
    data, algo, key = chat_json()
    try:
        cipher = bytes.fromhex(str(data.get("cipher_hex", "")))
        if not cipher:
            raise ValueError("Không có bản mã để tấn công.")
        if algo == "des":
            return jsonify(ok=True, algo=algo, rows=2 ** 64, success=False)
        enc, _ = chat_cipher(algo, key)
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
    """Kẻ xấu đổi 1 bit của byte thứ `index` trong bản mã rồi chuyển tiếp cho Bình."""
    data, algo, key = chat_json()
    try:
        cipher = bytearray(bytes.fromhex(str(data.get("cipher_hex", ""))))
        if not cipher:
            raise ValueError("Không có bản mã để sửa.")
        index = int(data.get("index", 0)) % len(cipher)
        cipher[index] ^= 0x01
        _, dec = chat_cipher(algo, key)
        try:
            bob, bob_error = dec(bytes(cipher)).decode("utf-8", errors="replace"), None
        except ValueError as e:
            bob, bob_error = None, str(e)
        db.add_history("Chat", "Kẻ xấu sửa tin", data.get("cipher_hex"), bob or bob_error, len(cipher),
                       status="error", note=f"Đổi 1 bit ở byte {index}")
        return jsonify(ok=True, cipher_hex=bytes(cipher).hex(" ").upper(), index=index,
                       bob_text=bob, bob_error=bob_error)
    except ValueError as e:
        return jsonify(ok=False, error=str(e)), 400


def _measure(fn):
    """Chạy hàm fn 1 lần, trả về thời gian chạy (ms)."""
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000


@app.post("/benchmark")
def benchmark():
    from Crypto.Cipher import DES as LibDES
    from Crypto.Util.Padding import pad

    key = b"benchkey"
    sdes_key = "10011010"
    rows = []
    for size in BENCH_SIZES:
        data = os.urandom(size)
        enc = utils.des_encrypt_bytes(data, key)
        des_enc = _measure(lambda: utils.des_encrypt_bytes(data, key))
        des_dec = _measure(lambda: utils.des_decrypt_bytes(enc, key))
        lib = _measure(lambda: LibDES.new(key, LibDES.MODE_ECB).encrypt(pad(data, 8)))
        sdes = _measure(lambda: tinydes_core.encrypt_bytes(data, sdes_key)) if size <= 100 * 1024 else None
        rows.append({
            "size": size, "label": f"{size // 1024} KB" if size < 1024 * 1024 else f"{size // (1024 * 1024)} MB",
            "des_enc": des_enc, "des_dec": des_dec, "lib": lib, "sdes": sdes,
            "speed": size / 1024 / (des_enc / 1000),
        })
    max_ms = max(r["des_enc"] for r in rows)
    for r in rows:
        r["bar"] = 100 * r["des_enc"] / max_ms
    db.add_history("Benchmark", "Đo thời gian", "1 KB → 1 MB", f"DES 1 MB: {rows[-1]['des_enc']:.0f} ms",
                   sum(BENCH_SIZES), round(sum(r["des_enc"] for r in rows), 3), note="DES tự code vs pycryptodome")
    return render("benchmark.html", bench=rows)


@app.get("/history")
def history():
    return render("history.html", rows=db.get_history(), stats=db.get_stats(), db_path=db.DB_PATH)


@app.post("/history/clear")
def history_clear():
    db.clear_history()
    return redirect(url_for("history"))


@app.errorhandler(413)
def too_large(_):
    return render("des.html", des_error="File quá lớn (tối đa 20 MB)."), 413


if __name__ == "__main__":
    app.run(debug=True)
