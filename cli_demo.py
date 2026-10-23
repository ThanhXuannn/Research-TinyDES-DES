import tinydes_core


def run_interactive_menu():
    des = tinydes_core.TinyDES()

    while True:
        print("\n" + "=" * 45)
        print("   HỆ THỐNG MÃ HÓA TINY-DES (NHẬP TAY)")
        print("=" * 45)
        print("1. Mã hóa dữ liệu (Encrypt)")
        print("2. Giải mã dữ liệu (Decrypt)")
        print("3. Thoát chương trình")

        choice = input("🔸 Chọn chức năng (1-3): ").strip()

        if choice == "1":
            print("\n[CHẾ ĐỘ MÃ HÓA]")
            p_input = input("Nhập Bản rõ P (8-bit nhị phân, vd: 01011100): ").strip()
            k_input = input("Nhập Khóa K   (8-bit nhị phân, vd: 10011010): ").strip()

            if len(p_input) != 8 or len(k_input) != 8:
                print("❌ Lỗi: Bản rõ và khóa bắt buộc phải đúng 8 ký tự (0 hoặc 1)!")
                continue

            print("\n--- QUÁ TRÌNH MÃ HÓA ---")
            c_result = des.encrypt(p_input, k_input, verbose=True)
            print(f"\n✅ BẢN MÃ THU ĐƯỢC CUỐI CÙNG: {c_result}")

            # Hỏi người dùng có muốn giải mã ngược lại không
            reverse_choice = input("\n🔄 Bạn có muốn giải mã ngược lại bản mã vừa tạo không? (y/n): ").strip().lower()
            if reverse_choice in ['y', 'yes', 'có', '1']:
                print("\n--- QUÁ TRÌNH GIẢI MÃ NGƯỢC LẠI ---")
                p_recovered = des.decrypt(c_result, k_input, verbose=True)
                print(f"\n✅ BẢN RÕ KHÔI PHỤC ĐƯỢC: {p_recovered}")

                # So sánh để chứng minh tính đúng đắn
                if p_recovered == p_input:
                    print("🎉 HOÀN HẢO! Bản rõ khôi phục khớp 100% với bản rõ ban đầu.")
                else:
                    print("❌ Có lỗi xảy ra trong quá trình khôi phục.")

        elif choice == "2":
            print("\n[CHẾ ĐỘ GIẢI MÃ]")
            c_input = input("Nhập Bản mã C (8-bit nhị phân): ").strip()
            k_input = input("Nhập Khóa K   (8-bit nhị phân): ").strip()

            if len(c_input) != 8 or len(k_input) != 8:
                print("❌ Lỗi: Bản mã và khóa bắt buộc phải đúng 8 ký tự (0 hoặc 1)!")
                continue

            print("\n--- QUÁ TRÌNH GIẢI MÃ ---")
            p_result = des.decrypt(c_input, k_input, verbose=True)
            print(f"\n✅ BẢN RÕ KHÔI PHỤC ĐƯỢC: {p_result}")

            # Hỏi người dùng có muốn mã hóa ngược lại không
            reverse_choice = input(
                "\n🔄 Bạn có muốn mã hóa ngược lại bản rõ vừa tìm được không? (y/n): ").strip().lower()
            if reverse_choice in ['y', 'yes', 'có', '1']:
                print("\n--- QUÁ TRÌNH MÃ HÓA NGƯỢC LẠI ---")
                c_recovered = des.encrypt(p_result, k_input, verbose=True)
                print(f"\n✅ BẢN MÃ THU ĐƯỢC: {c_recovered}")

                # So sánh để chứng minh tính đúng đắn
                if c_recovered == c_input:
                    print("🎉 HOÀN HẢO! Bản mã tạo ra khớp 100% với bản mã ban đầu.")
                else:
                    print("❌ Có lỗi xảy ra trong quá trình mã hóa.")

        elif choice == "3":
            print("👋 Tạm biệt! Hẹn gặp lại.")
            break
        else:
            print("❌ Lựa chọn không hợp lệ, vui lòng chọn lại!")


if __name__ == "__main__":
    run_interactive_menu()