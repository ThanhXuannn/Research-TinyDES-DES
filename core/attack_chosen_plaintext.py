def run_chosen_plaintext(target_ciphertext, encryption_oracle):
    """
    Tấn công chọn bản rõ: Nạp 256 bản rõ để xây dựng bảng tra cứu.
    """
    print("\n[+] ĐANG CHẠY: Tấn công chọn bản rõ (Chosen-plaintext) - Sinh bảng 256 dòng")
    lookup_table = {}

    # 1. Quét tạo bảng
    for i in range(256):
        pt = format(i, '08b')
        ct = encryption_oracle(pt)
        lookup_table[ct] = pt

    print("    -> [HOÀN TẤT] Đã xây dựng xong bảng tra cứu 256 cặp (PT - CT).")

    # 2. Dịch ngược bản mã mục tiêu
    cracked_plaintext = lookup_table.get(target_ciphertext)

    if cracked_plaintext:
        print(f"    -> [THÀNH CÔNG] Dịch ngược từ bảng tra cứu: Bản rõ là {cracked_plaintext}")
    else:
        print("    -> [LỖI] Bản mã mục tiêu không tồn tại trong bảng.")

    return cracked_plaintext, lookup_table

#Test case

if __name__ == "__main__":
    import tinydes_core

    sdes_machine = tinydes_core.TinyDES()
    SECRET_KEY = "10101100"
    CT_TEST = sdes_machine.encrypt("01101111", SECRET_KEY)


    # Mô phỏng Hộp đen
    def oracle(pt):
        return sdes_machine.encrypt(pt, SECRET_KEY)


    run_chosen_plaintext(CT_TEST, oracle)