import des_core

class DESHandler:
    """
    Trạm xử lý : Nhận văn bản hoặc File bất kỳ (padding),
    băm nhỏ thành các khối 64-bit và đẩy vào lõi DES tiêu chuẩn.
    """

    def __init__(self):
        self.des = des_core.StandardDES()

    # CÁC HÀM XỬ LÝ CHUYỂN ĐỔI VÀ ĐỆM
    def _pad(self, data_bytes):
        """PKCS#7 Padding: Đệm thêm byte để tổng chiều dài chia hết cho 8"""
        padding_len = 8 - (len(data_bytes) % 8)
        padding = bytes([padding_len] * padding_len)
        return data_bytes + padding

    def _unpad(self, data_bytes):
        """Gọt bỏ byte đệm PKCS#7 sau khi giải mã"""
        padding_len = data_bytes[-1]
        return data_bytes[:-padding_len]

    def _bytes_to_bin(self, data_bytes):
        """Chuyển mảng Byte thành chuỗi nhị phân (0 và 1) dài liên tục"""
        return "".join([format(b, '08b') for b in data_bytes])

    def _bin_to_bytes(self, bin_str):
        """Chuyển chuỗi nhị phân trở lại thành mảng Byte"""
        return bytes([int(bin_str[i:i + 8], 2) for i in range(0, len(bin_str), 8)])

    #LUỒNG XỬ LÝ LÕI
    def process_data(self, data_bytes, key_hex, mode="encrypt"):
        """Xử lý một cục dữ liệu Byte khổng lồ (băm nhỏ, mã hóa, ráp lại)"""
        # Chuyển khóa từ Hex sang nhị phân 64-bit
        key_bytes = bytes.fromhex(key_hex)
        key_bin = self._bytes_to_bin(key_bytes)

        if mode == "encrypt":
            data_bytes = self._pad(data_bytes)

        result_bin = ""
        full_bin_str = self._bytes_to_bin(data_bytes)

        # Cắt từng khúc 64-bit ném vào lõi DES
        for i in range(0, len(full_bin_str), 64):
            block_64bit = full_bin_str[i:i + 64]
            processed_block = self.des.process_block(block_64bit, key_bin, mode=mode, verbose=False)
            result_bin += processed_block

        result_bytes = self._bin_to_bytes(result_bin)

        if mode == "decrypt":
            result_bytes = self._unpad(result_bytes)

        return result_bytes

    # CÁC HÀM DÀNH CHO GIAO DIỆN (UI)

    def encrypt_text(self, text, key_hex):
        """Nhận chuỗi văn bản -> Trả ra bản mã dạng HEX để dễ hiển thị"""
        data_bytes = text.encode('utf-8')
        cipher_bytes = self.process_data(data_bytes, key_hex, mode="encrypt")
        return cipher_bytes.hex().upper()

    def decrypt_text(self, hex_cipher, key_hex):
        """Nhận bản mã HEX -> Trả về văn bản gốc tiếng Việt"""
        cipher_bytes = bytes.fromhex(hex_cipher)
        plain_bytes = self.process_data(cipher_bytes, key_hex, mode="decrypt")
        return plain_bytes.decode('utf-8')

    def process_file(self, input_path, output_path, key_hex, mode="encrypt"):
        """Đọc file bất kỳ (txt, png, pdf...), mã hóa/giải mã, lưu thành file mới"""
        with open(input_path, 'rb') as f:
            data = f.read()

        processed_data = self.process_data(data, key_hex, mode)

        with open(output_path, 'wb') as f:
            f.write(processed_data)

        return True


# CHẠY THỬ

if __name__ == "__main__":
    handler = DESHandler()

    # Một khóa 16 ký tự Hex (8 bytes = 64 bits)
    KEY = "133457799BBCDFF1"

    print(" 1. TEST MÃ HÓA VĂN BẢN (CHỮ CÓ DẤU)")
    van_ban_goc = "Chào thầy, đây là đoạn văn bản test mã hóa DES chuẩn của Suan. Dài bao nhiêu cũng được!"
    print(f"Bản rõ     : {van_ban_goc}")

    # Mã hóa
    ban_ma_hex = handler.encrypt_text(van_ban_goc, KEY)
    print(f"Bản mã HEX : {ban_ma_hex}")

    # Giải mã
    van_ban_khoi_phuc = handler.decrypt_text(ban_ma_hex, KEY)
    print(f"Khôi phục  : {van_ban_khoi_phuc}")
    print(f"Khớp 100%? : {van_ban_goc == van_ban_khoi_phuc}\n")

    print("2. TEST MÃ HÓA FILE TỰ ĐỘNG")
    # Tạo một file txt giả lập để test
    with open("test_input.txt", "w", encoding="utf-8") as f:
        f.write("Bí mật quốc gia: Mật khẩu wifi phòng Lab là 12345678")

    # Gọi module xử lý file
    handler.process_file("test_input.txt", "test_encrypted.bin", KEY, mode="encrypt")
    handler.process_file("test_encrypted.bin", "test_decrypted.txt", KEY, mode="decrypt")
    print("Đã tạo file 'test_input.txt', mã hóa thành 'test_encrypted.bin', rồi giải mã ra 'test_decrypted.txt'.")