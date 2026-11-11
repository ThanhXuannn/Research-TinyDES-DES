class TinyDES:
    """
    TinyDES:
    - 3 vòng lặp (Feistel cipher)
    - Block size 8-bit (L: 4-bit, R: 4-bit)
    - Key size 8-bit (KL: 4-bit, KR: 4-bit)
    - Subkey size 6-bit
    """

    def __init__(self):
        self.sbox = [
            [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8, 0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7],
            [0x0, 0xF, 0x7, 0x4, 0xE, 0x2, 0xD, 0x1, 0xA, 0x6, 0xC, 0xB, 0x9, 0x5, 0x3, 0x8],
            [0x4, 0x1, 0xE, 0x8, 0xD, 0x6, 0x2, 0xB, 0xF, 0xC, 0x9, 0x7, 0x3, 0xA, 0x5, 0x0],
            [0xF, 0xC, 0x8, 0x2, 0x4, 0x9, 0x1, 0x7, 0x5, 0xB, 0x3, 0xE, 0xA, 0x0, 0x6, 0xD]
        ]

    # CÁC HÀM HỖ TRỢ CHUYỂN ĐỔI
    def int_to_binary(self, value, bits):
        return format(value, f'0{bits}b')

    def binary_to_int(self, binary_str):
        return int(binary_str, 2)

    def left_circular_shift(self, value_bin, shift_amount):
        return value_bin[shift_amount:] + value_bin[:shift_amount]

    # CÁC HÀM HOÁN VỊ VÀ BIẾN ĐỔI LÕI
    def expand(self, r_bin):
        # b2 b3 b1 b2 b1 b0
        return r_bin[2] + r_bin[3] + r_bin[1] + r_bin[2] + r_bin[1] + r_bin[0]

    def sbox_lookup(self, input_6bit):
        row = self.binary_to_int(input_6bit[0] + input_6bit[5])
        col = self.binary_to_int(input_6bit[1:5])
        result = self.sbox[row][col]
        return self.int_to_binary(result, 4)

    def pbox_permute(self, input_4bit):
        # b2 b0 b3 b1
        return input_4bit[2] + input_4bit[0] + input_4bit[3] + input_4bit[1]

    def compress_key(self, kl_bin, kr_bin):
        # k5 k1 k3 k2 k7 k0
        combined = kl_bin + kr_bin
        return combined[5] + combined[1] + combined[3] + combined[2] + combined[7] + combined[0]

    # LUỒNG MÃ HÓA CHÍNH
    def encrypt(self, pt_bin, key_bin, verbose=False):
        """Mã hóa bản rõ 8-bit với khóa 8-bit. In chi tiết các bước nếu verbose=True"""

        # 1. Khởi tạo
        L = [pt_bin[:4]] * 4
        R = [pt_bin[4:]] * 4
        KL = [key_bin[:4]] * 4
        KR = [key_bin[4:]] * 4
        K = [""] * 4

        if verbose:
            print("=" * 40)
            print(f"BẢN RÕ (P) : {pt_bin} | KHÓA (K) : {key_bin}")
            print(f"L0 = {L[0]}, R0 = {R[0]}, KL0 = {KL[0]}, KR0 = {KR[0]}")
            print("=" * 40)

        # Mảng số lượng bit dịch vòng tương ứng với từng vòng lặp: Vòng 1(1 bit), Vòng 2(2 bit), Vòng 3(1 bit)
        shifts = [0, 1, 2, 1]

        # 2. Chạy 3 vòng Feistel
        for i in range(1, 4):
            if verbose:
                print(f"\n--- VÒNG {i} ---")
                print(f"- L{i} = R{i - 1} = {R[i - 1]}, Expand(R{i - 1}) = {self.expand(R[i - 1])}")

            # Sinh khóa con (Key Schedule)
            KL[i] = self.left_circular_shift(KL[i - 1], shifts[i])
            KR[i] = self.left_circular_shift(KR[i - 1], shifts[i])
            K[i] = self.compress_key(KL[i], KR[i])

            if verbose:
                print(f"- KL{i} = KL{i - 1} << {shifts[i]} = {KL[i]}, KR{i} = KR{i - 1} << {shifts[i]} = {KR[i]}")
                print(f"- K{i} = Compress(KL{i}, KR{i}) = {K[i]}")

            # Mạng Feistel
            expanded_R = self.expand(R[i - 1])
            xor_result = self.int_to_binary(self.binary_to_int(expanded_R) ^ self.binary_to_int(K[i]), 6)
            sbox_out = self.sbox_lookup(xor_result)
            f_result = self.pbox_permute(sbox_out)

            if verbose:
                print(f"- Expand(R{i - 1}) XOR K{i} = {xor_result}")
                print(f"- S-box({xor_result}) = {sbox_out}")
                print(f"- F{i} = P-box({sbox_out}) = {f_result}")

            # Tính R mới
            R[i] = self.int_to_binary(self.binary_to_int(L[i - 1]) ^ self.binary_to_int(f_result), 4)
            L[i] = R[i - 1]

            if verbose:
                print(f"- R{i} = L{i - 1} XOR F{i} = {R[i]}")

        ciphertext = L[3] + R[3]
        if verbose:
            print("=" * 40)
            print(f"KẾT QUẢ BẢN MÃ C = L3 + R3 = {ciphertext}")
            print("=" * 40)

        return ciphertext

    def decrypt(self, ct_bin, key_bin, verbose=False):
        """Giải mã bản mã 8-bit khôi phục bản rõ"""
        if verbose:
            print("\n" + "=" * 40)
            print(f"BẢN MÃ (C) : {ct_bin} | KHÓA (K) : {key_bin}")
            print("=" * 40)
            print("[BƯỚC 1] SINH KHÓA CON (Sinh chiều xuôi, dùng chiều ngược):")

        # Sinh toàn bộ khóa trước
        KL = [key_bin[:4]] * 4
        KR = [key_bin[4:]] * 4
        K = [""] * 4
        shifts = [0, 1, 2, 1]
        for i in range(1, 4):
            KL[i] = self.left_circular_shift(KL[i - 1], shifts[i])
            KR[i] = self.left_circular_shift(KR[i - 1], shifts[i])
            K[i] = self.compress_key(KL[i], KR[i])
            if verbose:
                print(f"- K{i} = {K[i]}")

        L = ct_bin[:4]
        R = ct_bin[4:]

        if verbose:
            print(f"\n[BƯỚC 2] CHẠY NGƯỢC MẠNG FEISTEL:")
            print(f"Đầu vào: L3 = {L}, R3 = {R}")

        # Chạy ngược 3 vòng
        for i in range(3, 0, -1):
            if verbose:
                print(f"\n--- VÒNG DÙNG K{i} ---")

            expanded_L = self.expand(L)
            xor_result = self.int_to_binary(self.binary_to_int(expanded_L) ^ self.binary_to_int(K[i]), 6)
            sbox_out = self.sbox_lookup(xor_result)
            f_result = self.pbox_permute(sbox_out)

            if verbose:
                print(f"- Expand(L) = {expanded_L}")
                print(f"- Expand(L) XOR K{i} = {xor_result}")
                print(f"- S-box({xor_result}) = {sbox_out}")
                print(f"- F = P-box({sbox_out}) = {f_result}")

            new_R = L
            new_L = self.int_to_binary(self.binary_to_int(R) ^ self.binary_to_int(f_result), 4)

            if verbose:
                print(f"- L_mới = R cũ XOR F = {new_L}")
                print(f"- R_mới = L cũ = {new_R}")

            L, R = new_L, new_R

        plaintext = L + R

        if verbose:
            print("=" * 40)
            print(f"KẾT QUẢ BẢN RÕ P = L0 + R0 = {plaintext}")
            print("=" * 40)

        return plaintext


# ==========================================
# KHU VỰC TEST
# ==========================================
#if __name__ == "__main__":
 #   des = TinyDES()
  #  # Test case lấy y hệt trong tài liệu NEU trang 81
    # Plaintext: 5C (01011100), Key: 10011010
  #  P = "01011100"
  #  K = "10011010"

  #  print("DEMO CHIỀU MÃ HÓA:")
   # C = des.encrypt(P, K, verbose=True)

    #print("\nDEMO CHIỀU GIẢI MÃ:")
    #recovered_P = des.decrypt(C, K)
    #print(f"Bản mã {C} sau khi giải mã quay về: {recovered_P}")

# =====================================================================
# CÁC HÀM DÙNG CHO WEB (app.py) - cùng thuật toán với class TinyDES ở trên.
# Bit được lưu bằng chuỗi '0'/'1' để in từng bước. Đánh số bit từ 0, từ trái sang phải.
# test_runner.py kiểm tra các hàm này cho kết quả giống hệt class TinyDES trên cả 65.536 cặp (bản rõ, khóa).
# =====================================================================
EXPAND = [2, 3, 1, 2, 1, 0]        # b2 b3 b1 b2 b1 b0
PBOX = [2, 0, 3, 1]                # b2 b0 b3 b1
COMPRESS = [5, 1, 3, 2, 7, 0]      # k5 k1 k3 k2 k7 k0
SHIFTS = [1, 2, 1]                 # vòng 1 dịch 1, vòng 2 dịch 2, vòng 3 dịch 1
SBOX = TinyDES().sbox              # 4 hàng x 16 cột
KEY_SPACE = 256                    # 2^8 khóa
BLOCK_SPACE = 256                  # 2^8 bản rõ khác nhau (khối 8 bit)


def is_bits(text, n):
    """True nếu text gồm đúng n ký tự '0'/'1'."""
    return isinstance(text, str) and len(text) == n and all(c in "01" for c in text)


def all_keys():
    """'00000000', '00000001', ..., '11111111'."""
    return (format(i, "08b") for i in range(KEY_SPACE))


def permute(bits, table):
    """Xếp lại bit: bit thứ i của kết quả = bits[table[i]]. Dùng cho Expand, P-box, Compress."""
    return "".join(bits[i] for i in table)


def left_shift(bits, n):
    """Dịch vòng trái n bit: n bit đầu chạy ra cuối."""
    return bits[n:] + bits[:n]


def xor(a, b):
    """XOR từng cặp bit của 2 chuỗi cùng độ dài."""
    return "".join("0" if x == y else "1" for x, y in zip(a, b))


def _log(log, buoc, gia_tri, ghi_chu=""):
    """Ghi 1 dòng log (nếu log là list). Giao diện hiển thị 3 cột: Bước | Giá trị | Ghi chú."""
    if log is not None:
        log.append({"buoc": buoc, "gia_tri": gia_tri, "ghi_chu": ghi_chu})


def _need_bits(text, what):
    if not is_bits(text, 8):
        raise ValueError(f"{what} phải gồm đúng 8 bit 0/1.")


def generate_keys(key_8bit, log=None):
    """Khóa 8 bit -> (K1, K2, K3), mỗi khóa con 6 bit. log: list nhận các bước sinh khóa."""
    _need_bits(key_8bit, "Khóa")
    kl, kr = key_8bit[:4], key_8bit[4:]
    _log(log, "Khóa K", key_8bit, "8 bit")
    _log(log, "KL0 | KR0", f"{kl} | {kr}", "chia đôi khóa")
    keys = []
    for i, s in enumerate(SHIFTS, start=1):
        kl, kr = left_shift(kl, s), left_shift(kr, s)
        k = permute(kl + kr, COMPRESS)
        _log(log, f"KL{i} | KR{i}", f"{kl} | {kr}", f"dịch trái {s} bit")
        _log(log, f"K{i}", k, "Compress k5 k1 k3 k2 k7 k0")
        keys.append(k)
    return tuple(keys)


def sbox_lookup(bits6):
    """6 bit -> (4 bit, hàng, cột). Hàng = b0 b5, cột = b1 b2 b3 b4."""
    row = int(bits6[0] + bits6[5], 2)
    col = int(bits6[1:5], 2)
    return format(SBOX[row][col], "04b"), row, col


def f_function(half4, subkey, log=None, tag=""):
    """F(R, K) = P-box(S-box(Expand(R) xor K)). Trả về 4 bit."""
    ex = permute(half4, EXPAND)
    x = xor(ex, subkey)
    s, row, col = sbox_lookup(x)
    f = permute(s, PBOX)
    _log(log, f"{tag} Expand", ex, f"Expand({half4})")
    _log(log, f"{tag} ⊕ K", x, f"{ex} ⊕ {subkey}")
    _log(log, f"{tag} S-box", s, f"hàng {row}, cột {col}")
    _log(log, f"{tag} F", f, "P-box b2 b0 b3 b1")
    return f


def _encrypt_block(bits8, keys, log=None):
    """1 khối 8 bit qua 3 vòng Feistel với keys = (K1, K2, K3)."""
    left, right = bits8[:4], bits8[4:]
    for i, k in enumerate(keys, start=1):
        f = f_function(right, k, log, f"Vòng {i}")
        left, right = right, xor(left, f)
        _log(log, f"Vòng {i}", left + right, f"L{i} = R{i - 1}, R{i} = L{i - 1} ⊕ F")
    return left + right


def _decrypt_block(bits8, keys, log=None):
    """Giải mã: đi ngược vòng 3 -> 1, dùng lại đúng hàm F."""
    left, right = bits8[:4], bits8[4:]
    for i in range(len(keys), 0, -1):
        f = f_function(left, keys[i - 1], log, f"Vòng {i}")
        left, right = xor(right, f), left
        _log(log, f"Vòng {i}", left + right, f"R{i - 1} = L{i}, L{i - 1} = R{i} ⊕ F")
    return left + right


def encrypt(plain_8bit, key_8bit):
    """Mã hóa 1 khối. Trả về (bản mã 8 bit, log). log gồm phần sinh khóa rồi tới các vòng."""
    _need_bits(plain_8bit, "Bản rõ")
    log = []
    keys = generate_keys(key_8bit, log)
    _log(log, "Bản rõ", plain_8bit, f"L0 = {plain_8bit[:4]}, R0 = {plain_8bit[4:]}")
    cipher = _encrypt_block(plain_8bit, keys, log)
    _log(log, "Bản mã", cipher, "C = L3 R3")
    return cipher, log


def decrypt(cipher_8bit, key_8bit):
    """Giải mã 1 khối. Trả về (bản rõ 8 bit, log)."""
    _need_bits(cipher_8bit, "Bản mã")
    log = []
    keys = generate_keys(key_8bit, log)
    _log(log, "Bản mã", cipher_8bit, f"L3 = {cipher_8bit[:4]}, R3 = {cipher_8bit[4:]}")
    plain = _decrypt_block(cipher_8bit, keys, log)
    _log(log, "Bản rõ", plain, "P = L0 R0")
    return plain, log


def _cells(src_bits, indexes):
    """Danh sách ô cho giao diện: mỗi ô {b: giá trị bit, src: bit nguồn, perm: True}."""
    return [{"b": src_bits[i], "src": i, "perm": True} for i in indexes]


def trace(bits8, key_8bit, decrypt=False):
    """
    Toàn bộ thanh ghi trung gian của 1 khối, để trang web vẽ từng bước.
    Mã hóa: vòng 1, 2, 3.  Giải mã (decrypt=True): vòng 3, 2, 1.
    """
    _need_bits(bits8, "Dữ liệu khối")
    keys = generate_keys(key_8bit)

    kl, kr = key_8bit[:4], key_8bit[4:]
    key_steps = [{"name": "KL0 | KR0", "desc": "chia đôi khóa", "bits": kl + kr, "cells": kl + kr, "split": 4, "key": False}]
    before = kl + kr                                    # KL|KR trước lần dịch
    for i, s in enumerate(SHIFTS, start=1):
        kl, kr = left_shift(kl, s), left_shift(kr, s)
        after = kl + kr
        src = [(p + s) % 4 for p in range(4)] + [4 + (p + s) % 4 for p in range(4)]    # bit nào chạy về đâu
        key_steps.append({"name": f"KL{i} | KR{i}", "desc": f"dịch trái {s} bit", "bits": after,
                          "cells": _cells(before, src), "split": 4, "key": False})
        key_steps.append({"name": f"K{i}", "desc": "Compress k5 k1 k3 k2 k7 k0", "bits": keys[i - 1],
                          "cells": _cells(after, COMPRESS), "split": 0, "key": True})
        before = after

    left, right = bits8[:4], bits8[4:]
    rounds = []
    order = range(len(keys), 0, -1) if decrypt else range(1, len(keys) + 1)
    for n in order:
        k = keys[n - 1]
        start = left + right
        f_in = left if decrypt else right
        ex = permute(f_in, EXPAND)
        x = xor(ex, k)
        s_out, row, col = sbox_lookup(x)
        f = permute(s_out, PBOX)
        if decrypt:
            mix, mixed = right, xor(right, f)           # L(n-1) = R(n) xor F(L(n))
            left, right = mixed, left
            f_name, mix_name = f"L{n}", f"R{n}"
        else:
            mix, mixed = left, xor(left, f)             # R(n) = L(n-1) xor F(R(n-1))
            left, right = right, mixed
            f_name, mix_name = f"R{n - 1}", f"L{n - 1}"
        rounds.append({
            "n": n, "k": k, "input": start, "left": start[:4], "right": start[4:],
            "f_name": f_name, "f_in": f_in, "expand": ex, "expand_cells": _cells(f_in, EXPAND),
            "xor": x, "sbox": {"in": x, "row": row, "col": col, "out": s_out},
            "f": f, "f_cells": _cells(s_out, PBOX), "mix_name": mix_name, "mix": mix, "mixed": mixed,
            "output": left + right,
        })
    return {"input": bits8, "output": left + right, "decrypt": decrypt, "subkeys": keys,
            "key_steps": key_steps, "rounds": rounds}


def encrypt_bytes(data, key_8bit=None, keys=None):
    """Mã hóa từng byte độc lập (mỗi byte = 1 khối 8 bit, kiểu ECB). Truyền key hoặc keys = (K1, K2, K3)."""
    if keys is None:
        keys = generate_keys(key_8bit)
    return bytes(int(_encrypt_block(format(b, "08b"), keys), 2) for b in data)


def decrypt_bytes(data, key_8bit=None, keys=None):
    if keys is None:
        keys = generate_keys(key_8bit)
    return bytes(int(_decrypt_block(format(b, "08b"), keys), 2) for b in data)


def double_encrypt_bytes(data, key1, key2):
    """TinyDES 2 lớp (giống Double DES): mã bằng K1 rồi mã tiếp bằng K2."""
    return encrypt_bytes(encrypt_bytes(data, key1), key2)


def double_decrypt_bytes(data, key1, key2):
    return decrypt_bytes(decrypt_bytes(data, key2), key1)


_PUNCT = ".,!?:;'\"-()\n"


def readability_score(data):
    """Điểm 'giống chữ đọc được' của một dãy byte (giống hàm readability trong web_tinh/crypto-local.js)."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return -1000 + sum(1 for b in data if 32 <= b < 127)
    score = 0
    for ch in text:
        if ch == " ":
            score += 3
        elif ch.isalpha():
            score += 2 if ch.islower() else 1
        elif ch.isdigit() or ch in _PUNCT:
            score += 1
        elif not ch.isprintable():
            score -= 5
    return round(score / len(data), 3) if data else 0


def brute_force_ciphertext_only(cipher, top=5):
    """Chỉ có bản mã: thử 256 khóa, chấm điểm bản giải mã, trả về `top` ứng viên điểm cao nhất."""
    cands = []
    for key in all_keys():
        plain = decrypt_bytes(cipher, key)
        cands.append({"key": key, "plain": plain, "score": readability_score(plain)})
    cands.sort(key=lambda c: -c["score"])
    return cands[:top]


def chosen_plaintext_attack(cipher, oracle):
    """
    Tấn công chọn bản rõ: nạp đủ 256 bản rõ 8 bit vào hộp đen `oracle(bits8) -> bits8` để lập bảng tra
    (bản mã -> bản rõ), rồi dịch từng byte của `cipher`. Trả về (bản rõ bytes hoặc None, bảng tra).
    """
    book = {}
    for i in range(BLOCK_SPACE):
        pt = format(i, "08b")
        book[oracle(pt)] = pt
    try:
        plain = bytes(int(book[format(b, "08b")], 2) for b in cipher)
    except KeyError:
        plain = None
    return plain, book


def meet_in_the_middle(plain, cipher):
    """
    Gặp nhau ở giữa vào TinyDES 2 lớp, biết 1 cặp (bản rõ, bản mã 2 lớp).
    Mã xuôi bằng 256 khóa K1, giải ngược bằng 256 khóa K2, giá trị ở giữa trùng nhau là cặp khóa.
    Trả về (list (K1, K2), số giá trị khác nhau ở giữa, số lần chạy TinyDES = 2 x 256).
    """
    middle = {}
    for k1 in all_keys():
        middle.setdefault(encrypt_bytes(plain, k1), []).append(k1)
    pairs = []
    for k2 in all_keys():
        for k1 in middle.get(decrypt_bytes(cipher, k2), []):
            pairs.append((k1, k2))
    return pairs, len(middle), 2 * KEY_SPACE
