"""
BỘ KIỂM THỬ: chạy `python test_runner.py` (in bảng + "Passed N/N") hoặc bấm nút ở trang /tests của web.
  A. Nhóm tự viết     (13 ca): ví dụ TinyDES trang 72, khứ hồi 256 x 256, class TinyDES, tấn công, DES Grabbe, tiếng Việt, padding, sai khóa
  B. NIST SP 800-17   (16 ca): 8 test vector chuẩn (Known Answer Test) x (mã hóa + giải mã)
  C. pycryptodome     (14 ca): đối chiếu với thư viện chuẩn (thư viện chỉ dùng để so sánh, không dùng trong phần lõi)
"""
import os
import time

from Crypto.Cipher import DES as LibDES
from Crypto.Util.Padding import pad

from core import des_core, des_utils as utils, tinydes_core

# ---- Dữ liệu mẫu (app.py cũng dùng để điền sẵn vào ô "tự nhập") ----
TINYDES_EXAMPLE = {"plain": "01011100", "key": "10011010", "cipher": "10010010"}          # tài liệu Chương 2, trang 72
DES_CLASS_EXAMPLE = {"plain": "0123456789ABCDEF", "key": "133457799BBCDFF1", "cipher": "85E813540F0AB405"}   # Grabbe

# NIST SP 800-17 (Known Answer Tests): (loại, khóa, bản rõ, bản mã) - đều dạng hex
NIST_VECTORS = [
    ("Variable Plaintext", "0101010101010101", "8000000000000000", "95F8A5E5DD31D900"),
    ("Variable Plaintext", "0101010101010101", "4000000000000000", "DD7F121CA5015619"),
    ("Variable Plaintext", "0101010101010101", "2000000000000000", "2E8653104F3834EA"),
    ("Variable Plaintext", "0101010101010101", "1000000000000000", "4BD388FF6CD81D4F"),
    ("Variable Key", "8001010101010101", "0000000000000000", "95A8D72813DAA94D"),
    ("Variable Key", "4001010101010101", "0000000000000000", "0EEC1487DD8C26D5"),
    ("Variable Key", "2001010101010101", "0000000000000000", "7AD16FFB79C45926"),
    ("Variable Key", "1001010101010101", "0000000000000000", "D3746294CA6A6CF3"),
]

GROUP_A = "A. Nhóm tự viết"
GROUP_B = "B. NIST SP 800-17"
GROUP_C = "C. pycryptodome"


def _case(group, name, input_, expected, actual, rerun=None):
    """Một ca kiểm thử: ok = (thực tế == mong đợi)."""
    return {"group": group, "name": name, "input": str(input_), "expected": str(expected), "actual": str(actual),
            "ok": expected == actual, "rerun": rerun}


def _bits(b):
    return "".join(f"{x:08b}" for x in b)


def _hex(b):
    return b.hex().upper()


def _group_a():
    ex, dx = TINYDES_EXAMPLE, DES_CLASS_EXAMPLE
    out = []
    tr = {"t_algo": "sdes", "t_plain": ex["plain"], "t_key": ex["key"], "t_expected": ex["cipher"]}
    out.append(_case(GROUP_A, "TinyDES mã hóa — ví dụ trang 72", f"P={ex['plain']} K={ex['key']}", ex["cipher"],
                     tinydes_core.encrypt(ex["plain"], ex["key"])[0], tr))
    out.append(_case(GROUP_A, "TinyDES giải mã — ví dụ trang 72", f"C={ex['cipher']} K={ex['key']}", ex["plain"],
                     tinydes_core.decrypt(ex["cipher"], ex["key"])[0]))

    # khứ hồi toàn bộ 256 khóa x 256 bản rõ; đồng thời so với class TinyDES (cách viết khác của cùng thuật toán)
    cls = tinydes_core.TinyDES()
    bad_round = bad_cls = 0
    for k in tinydes_core.all_keys():
        keys = tinydes_core.generate_keys(k)
        for i in range(256):
            p = format(i, "08b")
            c = tinydes_core._encrypt_block(p, keys)
            if tinydes_core._decrypt_block(c, keys) != p:
                bad_round += 1
            if cls.encrypt(p, k) != c:
                bad_cls += 1
    out.append(_case(GROUP_A, "TinyDES khứ hồi D(E(P)) = P", "256 khóa × 256 bản rõ = 65.536 cặp", "0 cặp sai", f"{bad_round} cặp sai"))
    out.append(_case(GROUP_A, "Hàm TinyDES = class TinyDES", "65.536 cặp (bản rõ, khóa)", "0 cặp lệch", f"{bad_cls} cặp lệch"))

    # tấn công: biết bản rõ + bản mã -> vét cạn phải ra khóa thật
    secret = "10101100"
    c = cls.encrypt("01101111", secret)
    found = [k for k in tinydes_core.all_keys() if cls.decrypt(c, k) == "01101111"]
    out.append(_case(GROUP_A, "Vét cạn 1 khối tìm ra khóa thật", f"P=01101111 C={c}", True, secret in found))
    secret_keys = tinydes_core.generate_keys(secret)
    target = tinydes_core.encrypt_bytes(bytes([0x6F]), keys=secret_keys)          # bản mã chặn được
    book_plain, book = tinydes_core.chosen_plaintext_attack(
        target, lambda p: tinydes_core._encrypt_block(p, secret_keys))            # hộp đen: chỉ gọi, không đọc khóa
    out.append(_case(GROUP_A, "Chọn bản rõ: bảng tra 256 dòng dịch đúng", f"bản mã {_hex(target)}", "6F, 256 dòng",
                     f"{_hex(book_plain)}, {len(book)} dòng"))
    msg = "Xin chào các bạn".encode("utf-8")
    top = tinydes_core.brute_force_ciphertext_only(tinydes_core.encrypt_bytes(msg, secret), top=1)
    out.append(_case(GROUP_A, "Chỉ biết bản mã: khóa thật xếp hạng 1", "\"Xin chào các bạn\", 256 khóa", secret, top[0]["key"]))
    # lưu ý: ECB nên hai chữ 'l' trong "Hello" cho cùng 1 byte mã
    out.append(_case(GROUP_A, "TinyDES mã hóa chữ \"Hello\" (ECB)", "K=10011010", "67 B3 20 20 A2",
                     tinydes_core.encrypt_bytes(b"Hello", "10011010").hex(" ").upper()))

    out.append(_case(GROUP_A, "DES mã hóa — ví dụ Grabbe", f"P={dx['plain']} K={dx['key']}", dx["cipher"],
                     _hex(des_core.encrypt_block(bytes.fromhex(dx["plain"]), bytes.fromhex(dx["key"]))),
                     {"t_algo": "des", "t_plain": dx["plain"], "t_key": dx["key"], "t_expected": dx["cipher"]}))
    # bản nhanh (số nguyên) phải giống hệt class StandardDES (chuỗi bit)
    std = des_core.StandardDES()
    kb = bytes.fromhex(dx["key"])
    mism = 0
    for _ in range(30):
        blk = os.urandom(8)
        std_out = std.process_block(_bits(blk), _bits(kb), "encrypt")
        if int(std_out, 2).to_bytes(8, "big") != des_core.encrypt_block(blk, kb):
            mism += 1
    out.append(_case(GROUP_A, "DES bản nhanh = class StandardDES", "30 khối ngẫu nhiên", "0 khối lệch", f"{mism} khối lệch"))

    text = "Xin chào, đây là bản thử tiếng Việt 123!"
    key = utils.parse_des_key("nhom2026")
    back = utils.des_decrypt_bytes(utils.des_encrypt_bytes(text.encode("utf-8"), key), key).decode("utf-8")
    out.append(_case(GROUP_A, "DES văn bản tiếng Việt khứ hồi", text, text, back))

    pad_ok = all(len(utils.des_encrypt_bytes(b"A" * n, key)) == (n // 8 + 1) * 8 for n in (0, 1, 7, 8, 9, 16))
    out.append(_case(GROUP_A, "Đệm PKCS#7 (8 byte tròn vẫn thêm 1 khối)", "độ dài 0, 1, 7, 8, 9, 16", True, pad_ok))

    try:
        utils.des_decrypt_bytes(utils.des_encrypt_bytes(b"Xin chao", key), utils.parse_des_key("nhom2025"))
        got = "không báo lỗi"
    except ValueError:
        got = "báo lỗi"
    out.append(_case(GROUP_A, "DES giải mã sai khóa phải báo lỗi", "khóa nhom2025 (đúng: nhom2026)", "báo lỗi", got))
    return out


def _group_b():
    out = []
    for n, (kind, key, pt, ct) in enumerate(NIST_VECTORS, start=1):
        k, p, c = bytes.fromhex(key), bytes.fromhex(pt), bytes.fromhex(ct)
        rerun = {"t_algo": "des", "t_plain": pt, "t_key": key, "t_expected": ct}
        out.append(_case(GROUP_B, f"#{n} {kind}: mã hóa", f"K={key} P={pt}", ct, _hex(des_core.encrypt_block(p, k)), rerun))
        out.append(_case(GROUP_B, f"#{n} {kind}: giải mã", f"K={key} C={ct}", pt, _hex(des_core.decrypt_block(c, k))))
    return out


def _lib_encrypt(data, key):
    return LibDES.new(key, LibDES.MODE_ECB).encrypt(pad(data, 8))


def _group_c():
    out = []
    key = b"nhom2026"
    for blk in (b"HelloDES", bytes(8), bytes(range(8))):
        exp = LibDES.new(key, LibDES.MODE_ECB).encrypt(blk)
        out.append(_case(GROUP_C, "Khối cố định", f"K=nhom2026 P={_hex(blk)}", _hex(exp), _hex(des_core.encrypt_block(blk, key))))
    for text in ("Hello", "Code DES from scratch!", "Test case có tiếng Việt 123!@#"):
        data = text.encode("utf-8")
        out.append(_case(GROUP_C, "Đoạn văn bản (đệm PKCS#7)", text, _hex(_lib_encrypt(data, key)),
                         _hex(utils.des_encrypt_bytes(data, key))))
    bad = 0
    for _ in range(200):
        k, p = os.urandom(8), os.urandom(8)
        if des_core.encrypt_block(p, k) != LibDES.new(k, LibDES.MODE_ECB).encrypt(p):
            bad += 1
    out.append(_case(GROUP_C, "200 cặp (khóa, khối) ngẫu nhiên", "os.urandom", "0 cặp lệch", f"{bad} cặp lệch"))
    for size in (0, 1, 7, 8, 1000, 10 * 1024, 100 * 1024):
        data = os.urandom(size)
        mine = utils.des_encrypt_bytes(data, key)
        ok = mine == _lib_encrypt(data, key) and utils.des_decrypt_bytes(mine, key) == data
        out.append(_case(GROUP_C, f"Tệp {size} byte: mã hóa = thư viện và giải mã khôi phục đúng", f"{size} byte ngẫu nhiên", True, ok))
    return out


def run_all():
    """Chạy cả 3 nhóm. Trả về (list ca kiểm thử, thời gian chạy ms)."""
    t0 = time.perf_counter()
    results = _group_a() + _group_b() + _group_c()
    return results, (time.perf_counter() - t0) * 1000


def main():
    print("=" * 70)
    print(" BỘ KIỂM THỬ TinyDES + DES ")
    print("=" * 70)
    results, ms = run_all()
    group = None
    for i, c in enumerate(results, start=1):
        if c["group"] != group:
            group = c["group"]
            print(f"\n[{group}]")
        print(f"  {i:2d}. {'PASS' if c['ok'] else 'FAIL'}  {c['name']}")
        if not c["ok"]:
            print(f"        mong đợi: {c['expected']}\n        thực tế : {c['actual']}")
    passed = sum(c["ok"] for c in results)
    print("\n" + "=" * 70)
    print(f"Passed {passed}/{len(results)}   ({ms / 1000:.1f} s)")
    print("=" * 70)
    return passed == len(results)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
