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
