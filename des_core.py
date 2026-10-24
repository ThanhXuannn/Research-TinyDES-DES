import des_tables

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
