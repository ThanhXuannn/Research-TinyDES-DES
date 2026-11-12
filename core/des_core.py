try:
    from core import des_tables
except ImportError:          # chạy trực tiếp file này (python core/des_core.py)
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core import des_tables

class StandardDES:

    # CÁC HÀM HỖ TRỢ BITWISE
    def permute(self, bit_string, table):
        """Hoán vị chuỗi bit dựa trên mảng vị trí (1-indexed)"""
        return "".join([bit_string[i - 1] for i in table])

    def xor(self, bits1, bits2):
        """Phép XOR giữa 2 chuỗi nhị phân"""
        return "".join(["1" if b1 != b2 else "0" for b1, b2 in zip(bits1, bits2)])

    def left_shift(self, bit_string, shifts):
        """Dịch trái xoay vòng (Circular Left Shift)"""
        return bit_string[shifts:] + bit_string[:shifts]

    # HỆ THỐNG SINH KHÓA
    def generate_subkeys(self, key_64bit):
        """Từ khóa 64-bit ban đầu, sinh ra 16 khóa con 48-bit"""
        subkeys = []

        # 1. PC-1: Nén khóa 64-bit xuống 56-bit (Loại bỏ các bit chẵn lẻ)
        key_56bit = self.permute(key_64bit, des_tables.PC1)

        # 2. Chia đôi khóa 56-bit thành C0 và D0 (Mỗi nửa 28-bit)
        C, D = key_56bit[:28], key_56bit[28:]

        # 3. Tạo 16 khóa con
        for shift in des_tables.SHIFTS:
            C = self.left_shift(C, shift)
            D = self.left_shift(D, shift)

            # PC-2: Ghép C, D và nén từ 56-bit xuống 48-bit
            subkey_48bit = self.permute(C + D, des_tables.PC2)
            subkeys.append(subkey_48bit)

        return subkeys

    #HÀM MẠNG FEISTEL (f_k)
    def feistel_function(self, R_32bit, subkey_48bit):
        """Hàm f biến đổi nửa phải 32-bit kết hợp khóa 48-bit"""
        # 1. Expand: 32-bit -> 48-bit
        expanded_R = self.permute(R_32bit, des_tables.E)

        # 2. XOR với khóa con
        xor_result = self.xor(expanded_R, subkey_48bit)

        # 3. Qua 8 hộp S-Box (48-bit -> 32-bit)
        sbox_output = ""
        # Cắt thành 8 khối, mỗi khối 6 bit
        chunks_6bit = [xor_result[i:i + 6] for i in range(0, 48, 6)]

        for i in range(8):
            chunk = chunks_6bit[i]
            # Bit ngoài cùng (đầu + cuối) quyết định Hàng
            row = int(chunk[0] + chunk[5], 2)
            # 4 bit giữa quyết định Cột
            col = int(chunk[1:5], 2)

            # Tra cứu giá trị S-box tương ứng (S1 đến S8)
            val = des_tables.S_BOXES[i][row][col]
            # Đổi giá trị ra nhị phân 4-bit và nối vào kết quả
            sbox_output += format(val, '04b')

        # 4. Hoán vị P-box (32-bit -> 32-bit)
        return self.permute(sbox_output, des_tables.P)

    #  LUỒNG MÃ HÓA / GIẢI MÃ
    def process_block(self, block_64bit, key_64bit, mode="encrypt", verbose=False):
        """Xử lý 1 khối dữ liệu 64-bit (Mã hóa hoặc Giải mã)"""
        # Sinh 16 khóa con
        subkeys = self.generate_subkeys(key_64bit)

        # Nếu giải mã, đảo ngược thứ tự 16 khóa con (K16 -> K1)
        if mode == "decrypt":
            subkeys = subkeys[::-1]

        # 1. Hoán vị khởi tạo (IP)
        ip_result = self.permute(block_64bit, des_tables.IP)
        L, R = ip_result[:32], ip_result[32:]

        # 2. Chạy 16 vòng Feistel
        for i in range(16):
            if verbose:
                print(f"Vòng {i + 1:02d}: L = {L}, R = {R}")

            L_next = R
            f_result = self.feistel_function(R, subkeys[i])
            R_next = self.xor(L, f_result)

            L, R = L_next, R_next

        # 3. Đổi chỗ lần cuối (Swap) -> R16 L16
        combined = R + L

        # 4. Hoán vị kết thúc (IP-1)
        final_result = self.permute(combined, des_tables.IP_INV)

        if verbose:
            print(f"Kết quả {mode}: {final_result}")

        return final_result


# TEST CASE: Kiểm tra thuật toán DES với Vector chuẩn Quốc tế
#def hex_to_bin(hex_str, bits=64):
#   """Hàm phụ trợ chuyển Hex sang Binary để test"""
#    return format(int(hex_str, 16), f'0{bits}b')


#def bin_to_hex(bin_str):
#    """Hàm phụ trợ chuyển Binary sang Hex để test"""
#    return format(int(bin_str, 2), f'0{len(bin_str) // 4}X')


#if __name__ == "__main__":
#    des = StandardDES()

    # Vector Test Chuẩn NIST:
    # Plaintext: 0123456789ABCDEF
    # Key:       133457799BBCDFF1
    # Kỳ vọng Ciphertext: 85E813540F0AB405

#    pt_hex = "0123456789ABCDEF"
#    key_hex = "133457799BBCDFF1"

#    print("=== BẮT ĐẦU TEST DES 64-BIT ===")
#    print(f"Bản rõ (Hex) : {pt_hex}")
#    print(f"Khóa (Hex)   : {key_hex}\n")

    # Ép sang nhị phân để lõi xử lý
#    pt_bin = hex_to_bin(pt_hex)
#    key_bin = hex_to_bin(key_hex)

    # Chạy mã hóa
#    ct_bin = des.process_block(pt_bin, key_bin, mode="encrypt", verbose=False)
#    ct_hex = bin_to_hex(ct_bin)

#   print(f"Bản mã tạo ra (Hex)     : {ct_hex}")
#    print(f"Bản mã kỳ vọng (NIST)   : 85E813540F0AB405")
#    print(f"Khớp dữ liệu (OK)       : {ct_hex == '85E813540F0AB405'}\n")

    # Chạy giải mã ngược lại
#    recovered_bin = des.process_block(ct_bin, key_bin, mode="decrypt")
#    recovered_hex = bin_to_hex(recovered_bin)
#    print(f"Bản rõ khôi phục (Hex)  : {recovered_hex}")
#    print(f"Giải mã thành công (OK) : {recovered_hex == pt_hex}")

# =====================================================================
# PHẦN DÙNG CHO WEB (app.py): cùng thuật toán DES với class StandardDES ở trên,
# nhưng viết bằng SỐ NGUYÊN + bảng tra tính sẵn để chạy nhanh khi mã hóa file/ảnh,
# và có bản "verbose" ghi log từng vòng để trang web hiển thị.
# test_runner.py kiểm tra bản này cho kết quả GIỐNG HỆT class StandardDES và pycryptodome.
# =====================================================================

def permute(value, table, in_bits):
    """Hoán vị số nguyên theo bảng (đếm bit từ 1, từ trái). VD permute(0b1011, [2,4,3,1], 4) = 0b0111."""
    out = 0
    for pos in table:
        out = (out << 1) | ((value >> (in_bits - pos)) & 1)
    return out


def rotl(value, n, bits):
    """Dịch vòng trái n bit trong một số `bits` bit."""
    mask = (1 << bits) - 1
    return ((value << n) | (value >> (bits - n))) & mask


def sbox_sub(x48):
    """48 bit -> 32 bit: cắt 8 nhóm 6 bit, mỗi nhóm tra 1 S-box (hàng = bit đầu+cuối, cột = 4 bit giữa)."""
    out = 0
    for i in range(8):
        chunk = (x48 >> (42 - 6 * i)) & 0x3F
        row = ((chunk >> 4) & 2) | (chunk & 1)
        col = (chunk >> 1) & 0xF
        out = (out << 4) | des_tables.S_BOXES[i][row][col]
    return out


def feistel_f(r32, k48, detail=None):
    """f(R, K) = P(S(E(R) xor K)). Nếu detail là dict thì ghi lại e, xor, s, f (số nguyên)."""
    e = permute(r32, des_tables.E, 32)
    x = e ^ k48
    s = sbox_sub(x)
    f = permute(s, des_tables.P, 32)
    if detail is not None:
        detail.update(e=e, xor=x, s=s, f=f)
    return f


def generate_subkeys(key_bytes, key_log=None):
    """8 byte khóa -> list 16 khóa con (số 48 bit). key_log (list) nhận log: [PC-1, K1..K16] dạng hex."""
    k56 = permute(int.from_bytes(key_bytes, "big"), des_tables.PC1, 64)
    c, d = k56 >> 28, k56 & 0x0FFFFFFF
    if key_log is not None:
        key_log.append({"vong": "PC-1", "c": f"{c:07X}", "d": f"{d:07X}"})
    subkeys = []
    for i, s in enumerate(des_tables.SHIFTS, start=1):
        c, d = rotl(c, s, 28), rotl(d, s, 28)
        k = permute((c << 28) | d, des_tables.PC2, 56)
        subkeys.append(k)
        if key_log is not None:
            key_log.append({"vong": f"K{i}", "c": f"{c:07X}", "d": f"{d:07X}", "k": f"{k:012X}"})
    return subkeys


def _build_tables():
    """Tính sẵn: IP/IP^-1 theo từng byte, và SP-box (S-box + P-box gộp) cho 8 nhóm 6 bit."""
    def byte_tables(table):
        tabs = []
        for b in range(8):                       # byte thứ b của khối 64 bit
            t = []
            for v in range(256):
                t.append(permute(v << (56 - 8 * b), table, 64))
            tabs.append(t)
        return tabs
    sp = []
    for i in range(8):
        t = []
        for g in range(64):
            row = ((g >> 4) & 2) | (g & 1)
            col = (g >> 1) & 0xF
            t.append(permute(des_tables.S_BOXES[i][row][col] << (28 - 4 * i), des_tables.P, 32))
        sp.append(t)
    return byte_tables(des_tables.IP), byte_tables(des_tables.IP_INV), sp


_IP_T, _FP_T, _SP = _build_tables()


def _perm64(x, tabs):
    return (tabs[0][(x >> 56) & 255] | tabs[1][(x >> 48) & 255] | tabs[2][(x >> 40) & 255] |
            tabs[3][(x >> 32) & 255] | tabs[4][(x >> 24) & 255] | tabs[5][(x >> 16) & 255] |
            tabs[6][(x >> 8) & 255] | tabs[7][x & 255])


def crypt_block_fast(block_int, subkeys):
    """1 khối 64 bit (số nguyên) qua IP -> 16 vòng -> hoán đổi -> IP^-1. Giải mã = truyền khóa con đảo ngược."""
    ip = _perm64(block_int, _IP_T)
    left, right = ip >> 32, ip & 0xFFFFFFFF
    sp0, sp1, sp2, sp3, sp4, sp5, sp6, sp7 = _SP
    for k in subkeys:
        ext = ((right & 1) << 33) | (right << 1) | (right >> 31)      # 34 bit: b32, b1..b32, b1
        x = k ^ (((ext >> 28) & 63) << 42 | ((ext >> 24) & 63) << 36 | ((ext >> 20) & 63) << 30 |
                 ((ext >> 16) & 63) << 24 | ((ext >> 12) & 63) << 18 | ((ext >> 8) & 63) << 12 |
                 ((ext >> 4) & 63) << 6 | (ext & 63))
        f = (sp0[(x >> 42) & 63] | sp1[(x >> 36) & 63] | sp2[(x >> 30) & 63] | sp3[(x >> 24) & 63] |
             sp4[(x >> 18) & 63] | sp5[(x >> 12) & 63] | sp6[(x >> 6) & 63] | sp7[x & 63])
        left, right = right, left ^ f
    return _perm64((right << 32) | left, _FP_T)


def crypt_block_verbose(block_bytes, subkeys):
    """
    Bản dễ đọc, ghi log từng vòng cho web. Trả về (8 byte kết quả, rounds):
      rounds[0]   = {"vong": "IP", "l", "r"}                     (hex)
      rounds[1..16] = {"vong": "Vòng i", "k", "e", "xor", "s", "f", "l", "r"}
      rounds[17]  = {"vong": "IP⁻¹", "out"}                      (kết quả cuối)
    """
    b = int.from_bytes(block_bytes, "big")
    ip = permute(b, des_tables.IP, 64)
    left, right = ip >> 32, ip & 0xFFFFFFFF
    rounds = [{"vong": "IP", "l": f"{left:08X}", "r": f"{right:08X}"}]
    for i, k in enumerate(subkeys, start=1):
        d = {}
        f = feistel_f(right, k, d)
        left, right = right, left ^ f
        rounds.append({"vong": f"Vòng {i}", "k": f"{k:012X}", "e": f"{d['e']:012X}", "xor": f"{d['xor']:012X}",
                       "s": f"{d['s']:08X}", "f": f"{d['f']:08X}", "l": f"{left:08X}", "r": f"{right:08X}"})
    out = permute((right << 32) | left, des_tables.IP_INV, 64)
    rounds.append({"vong": "IP⁻¹", "out": f"{out:016X}"})
    return out.to_bytes(8, "big"), rounds


def encrypt_block(block_bytes, key_bytes):
    """Mã hóa 1 khối 8 byte với khóa 8 byte (bản nhanh)."""
    return crypt_block_fast(int.from_bytes(block_bytes, "big"), generate_subkeys(key_bytes)).to_bytes(8, "big")


def decrypt_block(block_bytes, key_bytes):
    """Giải mã 1 khối 8 byte: giống mã hóa, chỉ đảo thứ tự khóa con."""
    return crypt_block_fast(int.from_bytes(block_bytes, "big"), generate_subkeys(key_bytes)[::-1]).to_bytes(8, "big")
