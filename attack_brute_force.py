import tinydes_core

def run_brute_force(ciphertext, known_plaintext):
    """
    Tấn công vét cạn 256 khóa (8-bit) của TinyDES.
    """
    print("\n[+] ĐANG CHẠY: Tấn công vét cạn (Brute-force) - Không gian khóa: 256")
    sdes = tinydes_core.TinyDES()
    possible_keys = []

    for i in range(256):
        test_key = format(i, '08b')
        decrypted_text = sdes.decrypt(ciphertext, test_key)

        if decrypted_text == known_plaintext:
            possible_keys.append(test_key)
            print(f"    -> [THÀNH CÔNG] Tìm thấy khóa khả nghi: {test_key} (vòng lặp {i + 1})")

    if not possible_keys:
        print("    -> [THẤT BẠI] Không tìm thấy khóa nào khớp.")

    return possible_keys

#Test case
if __name__ == "__main__":
    sdes_machine = tinydes_core.TinyDES()
    CT_TEST = sdes_machine.encrypt("01101111", "10101100")
    run_brute_force(CT_TEST, "01101111")