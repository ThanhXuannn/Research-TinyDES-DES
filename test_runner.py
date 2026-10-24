from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import des_utils

def run_tests():
    print("="*55)
    print(" BỘ KIỂM THỬ ĐỐI CHIẾU DES ")
    print("="*55)

    my_des = des_utils.DESHandler()

    test_cases = [
        {
            "id": 1,
            "plaintext": b"HelloDES",
            "key": b"Secrett1"
        },
        {
            "id": 2,
            "plaintext": b"Code DES from scratch!",
            "key": b"Key12345"
        },
        {
            "id": 3,
            "plaintext": "Test case có tiếng Việt 123!@#".encode('utf-8'),
            "key": b"NEU_IT_K"
        }
    ]

    passed_count = 0

    for tc in test_cases:
        print(f"\n[+] Đang chạy Test Case {tc['id']}...")
        pt = tc['plaintext']
        key = tc['key']

        # 1. Mã hóa bằng thư viện chuẩn (PyCryptodome)
        # Sử dụng chế độ ECB
        cipher_standard = DES.new(key, DES.MODE_ECB)
        padded_pt = pad(pt, DES.block_size) # Áp dụng đệm chuẩn PKCS7
        expected_ct = cipher_standard.encrypt(padded_pt)

        # 2. Mã hóa bằng code
        # Đổi key dạng bytes sang chuỗi Hex vì hàm process_data của ta nhận Hex
        key_hex = key.hex()
        actual_ct = my_des.process_data(pt, key_hex, mode="encrypt")

        # In dữ liệu đối chiếu
        print(f"   - Khóa sử dụng : {key}")
        print(f"   -> Thư viện chuẩn trả ra : {expected_ct.hex().upper()}")
        print(f"   -> Code trả ra  : {actual_ct.hex().upper()}")

        # 3. Dùng hàm assert để so sánh chuỗi byte
        try:
            assert actual_ct == expected_ct, f"Lỗi lệch byte tại Test Case {tc['id']}"
            print("   => TRẠNG THÁI: KHỚP 100%")
            passed_count += 1
        except AssertionError as e:
            print(f"   => TRẠNG THÁI: LỆCH (FAIL) - {e}")

    print("\n" + "="*55)
    # Chạy file in ra "Passed 3/3" nếu tất cả assert đều đúng
    if passed_count == len(test_cases):
        print(f"Passed {passed_count}/{len(test_cases)}.")
    else:
        print(f"Failed. Đạt {passed_count}/{len(test_cases)}.")
    print("="*55)

if __name__ == "__main__":
    run_tests()