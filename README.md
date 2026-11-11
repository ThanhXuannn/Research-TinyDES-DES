HỆ THỐNG MÃ HÓA TINYDES/DES (Python + Flask + HTML)

Cài đặt thuật toán TinyDES (mô hình thu nhỏ của DES theo tài liệu Chương 2 - Mã hoá khoá đối xứng, trang 67–72, in đầy đủ các bước trung gian) và DES chuẩn (mã hóa/giải mã văn bản, tệp ảnh, tệp văn bản), có giao diện web, đo thời gian và demo 4 kiểu tấn công vào TinyDES.

1. Cài đặt & chạy bằng PyCharm

Yêu cầu: Python ≥ 3.10 (đã chạy thử trên 3.12; project cấu hình sẵn với 3.14). Chỉ cần 2 thư viện: Flask (web) và pycryptodome (chỉ để đối chiếu).

Bước 1 — Cài Python
Windows: tải Windows installer (64-bit) tại https://www.python.org/downloads/windows/. Khi cài, ở màn hình đầu tích ô “Add python.exe to PATH” rồi Install Now.
macOS: brew install python@3.12 (hoặc tải từ python.org).
Linux (Ubuntu): sudo apt install python3.12 python3.12-venv.
Kiểm tra: python --version (Windows) hoặc python3 --version (macOS/Linux) → thấy Python 3.1x.x.
Bước 2 — Cài PyCharm

Tải bản Community (miễn phí) tại https://www.jetbrains.com/pycharm/download/ → cài như phần mềm bình thường. PyCharm không kèm Python nên phải làm Bước 1 trước.

Bước 3 — Mở dự án

PyCharm → Open → chọn thư mục Research-TinyDES-DES (không chọn lẻ 1 file) → Trust Project. (Lấy mã nguồn: git clone <link-repo> hoặc giải nén tệp được giao.)

Bước 4 — Tạo môi trường ảo & cài thư viện

Mở Terminal trong PyCharm (Alt + F12) rồi gõ lần lượt:

bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Sau khi activate, đầu dòng terminal có (.venv).

Nếu PowerShell báo “running scripts is disabled”: chạy một lần Set-ExecutionPolicy -Scope CurrentUser RemoteSigned rồi activate lại, hoặc đổi Terminal sang Command Prompt.

Bước 5 — Chọn Interpreter

Settings → Project: Research-TinyDES-DES → Python Interpreter → Add Interpreter → Add Local Interpreter → Existing → trỏ tới:

Windows: .venv\Scripts\python.exe
macOS/Linux: .venv/bin/python

Góc dưới phải PyCharm phải hiện Python 3.1x (.venv).

Bước 6 — Chạy

Mở app.py → bấm ▶ (hoặc chuột phải → Run 'app') → đợi dòng Running on http://127.0.0.1:5000 → mở trình duyệt vào địa chỉ đó. Tắt bằng nút ⏹. Các lệnh chạy khác (console, kịch bản tấn công, kiểm thử): xem mục 2.

Không dùng PyCharm cũng được: mở terminal ở thư mục dự án, làm Bước 4 rồi chạy python app.py.

Lỗi hay gặp
Hiện tượng	Cách xử lý
'python' is not recognized (Windows)	Chưa tích Add to PATH ở Bước 1 → gỡ Python rồi cài lại, nhớ tích ô đó.
ModuleNotFoundError: No module named 'flask'	Chưa cài hoặc sai interpreter → làm lại Bước 4 & 5.
.venv\Scripts\activate bị chặn (PowerShell)	Chạy Set-ExecutionPolicy -Scope CurrentUser RemoteSigned, hoặc dùng Command Prompt.
Address already in use (cổng 5000 bận)	Đang có 1 bản app.py chạy → tắt (⏹ / Ctrl+C) rồi chạy lại.
Web sửa code mà không đổi	Tải lại trình duyệt bằng Ctrl + Shift + R.
ImportError / UndefinedError / Unknown format code 'X' khi mở trang web hoặc chạy test	Các file trong core/ hoặc test_runner.py không cùng một phiên bản với app.py. Chép đủ cả core/, test_runner.py và app.py từ cùng một bản, rồi chạy python test_runner.py: phải ra Passed 43/43.
ModuleNotFoundError: No module named 'core' khi chạy 1 file trong core/	Chạy từ thư mục gốc dự án (python core/attack_brute_force.py) hoặc bấm ▶ ngay trong PyCharm.
2. Chạy chương trình
Lệnh	Kết quả
python app.py	Giao diện web tại http://127.0.0.1:5000
python test_runner.py	Bộ kiểm thử 3 nhóm, in bảng đối chiếu → Passed 43/43
python cli_demo.py	Menu console cho TinyDES (class TinyDES): mã hóa / giải mã 1 khối 8 bit, in từng bước sinh khóa và 3 vòng Feistel (verbose=True), hỏi có muốn giải mã ngược lại để kiểm tra
python core/attack_brute_force.py	Tấn công vét cạn 1 khối trên console (phía phòng thủ + phía tấn công)
python core/attack_chosen_plaintext.py	Tấn công chọn bản rõ 1 khối trên console (phía phòng thủ + phía tấn công)
python core/des_utils.py	Chạy thử DES trên console: mã hóa / giải mã một đoạn tiếng Việt và 1 tệp (test_input.txt → test_encrypted.bin → test_decrypted.txt)
python xuat_web_tinh.py	Xuất các trang không cần server (/, /huong-dan, /chat, /doc-code…) thành HTML tĩnh trong web_tinh/ để đưa lên mạng, không cần chạy Python (thêm --artifact để ra dạng đăng lên claude.ai)

Tấn công gặp nhau ở giữa (TinyDES 2 lớp) chỉ có trên giao diện web (trang Tấn công TinyDES), chưa có kịch bản console riêng.

3. Chức năng trên giao diện web

Menu bên trái chia 3 nhóm: Bắt đầu, Thuật toán, Tấn công & kiểm chứng.

Trang	Chức năng
Trang chủ (/)	2 form chạy nhanh TinyDES / DES, bảng các chức năng, thống kê số lượt sử dụng
Hướng dẫn (/huong-dan)	Web chạy thế nào: HTML (Jinja), Python (Flask + core/), phòng chat dùng fetch() + JSON, bảng "trang nào gọi hàm nào"
Demo: An gửi Bình (/chat)	An gửi tin mã hóa thật (TinyDES hoặc DES) cho Bình; kẻ xấu ngồi giữa đường truyền: vét cạn khóa, tấn công chọn bản rõ, hoặc sửa 1 bit của bản mã
TinyDES từng bước (/sdes)	Nhập bản rõ (nhị phân hoặc văn bản) và khóa 8 bit → hiện bản mã và tự giải mã ngược để kiểm tra khớp. Hiển thị quá trình sinh khóa (KL/KR dịch 1, 2, 1 bit → Compress → K1, K2, K3), log thanh ghi từng vòng (Expand, ⊕K, S-box, P-box, L ⊕ F), tô màu ô S-box được tra ở mỗi vòng. Giải mã chạy vòng 3 → 1
DES: văn bản & tệp (/des)	Mã hóa / giải mã văn bản hoặc tệp bất kỳ (ảnh, txt…, tối đa 20 MB) bằng DES-ECB + PKCS#7. Tự giải mã ngược để kiểm tra, xem trước ảnh gốc / ảnh sau giải mã, tải tệp kết quả. Hiển thị 16 khóa con và 16 vòng Feistel của khối đầu
Đọc code cùng thuật toán (/doc-code)	Mỗi bước của TinyDES / DES đặt cạnh đoạn code thật (số dòng lấy trực tiếp từ file nguồn) và giá trị chạy thật của ví dụ trang 72 / ví dụ Grabbe
Tấn công TinyDES (/bruteforce)	Chỉ có bản mã: thử 2⁸ = 256 khóa, chấm điểm bản giải mã "đọc được", đoán ra khóa. Biết bản rõ: liệt kê các khóa khớp (cả bản nhiều byte lẫn bản vét cạn 1 khối). Chọn bản rõ: mượn hộp đen mã hóa, đưa 256 bản rõ vào → bảng tra 256 dòng (hiển thị dạng bảng 16 × 16), dịch bản mã mà không cần khóa. Gặp nhau ở giữa: TinyDES 2 lớp (K1 rồi K2, khóa 16 bit), biết 1 cặp bản rõ / bản mã → 256 + 256 lần chạy thay vì 65.536 cặp, giống lý do Double DES yếu (slide 82–83); có so sánh thời gian với vét cạn thường
Đo thời gian (/benchmark)	Đo DES tự viết (mã hóa, giải mã) với dữ liệu 1 KB → 1 MB, so sánh với pycryptodome; TinyDES đo tới 100 KB (vì chạy trên chuỗi bit nên chậm)
Kiểm thử (/tests)	Chạy bộ kiểm thử ngay trên web, bảng mong đợi / thực tế / PASS-FAIL theo từng nhóm. Có thêm mục tự nhập ca kiểm thử (chọn ca mẫu: ví dụ trang 72, Grabbe, NIST) và nút "Chạy từng bước" cho từng ca
Lịch sử (/history)	Lưu các thao tác vào SQLite (history.db). Không lưu khóa; với tệp chỉ lưu tên tệp, không lưu nội dung
Gợi ý kịch bản demo (5–7 phút)
TinyDES với khóa 10011010 và bản rõ 01011100 (5C) → bản mã 10010010 (92), đúng lời giải trang 72. Giải thích bảng sinh khóa, log từng vòng và các ô S-box được tô màu.
Tấn công TinyDES → Chỉ có bản mã: người gửi gửi "Hẹn gặp ở cổng trường lúc 8h tối", kẻ tấn công chỉ có bản mã vẫn tìm ra khóa sau 256 lần thử.
DES: văn bản & tệp: tải một ảnh nhỏ, khóa 133457799BBCDFF1 → Mã hóa, cho xem ảnh gốc, bản mã và ảnh sau giải mã, rồi tải tệp .enc. Tải tệp .enc lên lại → Giải mã → nhận lại ảnh gốc. Thử sai khóa → báo lỗi padding.
Đo thời gian → nhận xét thời gian tăng tuyến tính theo kích thước dữ liệu.
Demo: An gửi Bình → so sánh TinyDES (bị vét cạn ngay) với DES (cần hàng chục nghìn năm ở tốc độ này).
Mở Lịch sử để xem lại toàn bộ thao tác.
4. Cấu trúc mã nguồn

Phần thuật toán (thư mục core/) tách riêng khỏi phần giao diện (app.py, templates/, static/, cli_demo.py). Phần thuật toán không gọi bất kỳ thư viện mật mã nào; giao diện chỉ gọi vào core.

Research-TinyDES-DES/
├── core/                        # THUẬT TOÁN — nhóm tự cài đặt
│   ├── tinydes_core.py          # class TinyDES (mã hóa/giải mã từng bước) + các hàm cho web:
│   │                            #   generate_keys, f_function, encrypt/decrypt kèm log, trace, encrypt_bytes,
│   │                            #   vét cạn, chọn bản rõ, gặp nhau ở giữa
│   ├── des_tables.py            # Bảng chuẩn DES: IP, IP⁻¹, E, P, PC-1, PC-2, SHIFTS, 8 S-box
│   ├── des_core.py              # class StandardDES (bản chuỗi bit, dễ đọc) + bản số nguyên cho web:
│   │                            #   generate_subkeys, crypt_block_verbose (có log 16 vòng), crypt_block_fast (bảng tra)
│   ├── des_utils.py             # class DESHandler + parse_des_key, PKCS#7, mã hóa/giải mã bytes và tệp (ECB)
│   ├── attack_brute_force.py    # Kịch bản console: vét cạn 1 khối
│   └── attack_chosen_plaintext.py  # Kịch bản console: chọn bản rõ 1 khối
├── test_runner.py               # KIỂM THỬ: nhóm tự viết + NIST SP 800-17 + đối chiếu pycryptodome
├── cli_demo.py                  # Menu console cho class TinyDES
├── app.py                       # GIAO DIỆN web (Flask): nhận form → gọi core → trả kết quả
├── db.py                        # Lưu lịch sử thao tác (SQLite → history.db)
├── xuat_web_tinh.py             # Xuất web tĩnh → thư mục web_tinh/
├── giaithich.md                 # Tài liệu giải thích chi tiết thuật toán và code
├── templates/                   # HTML: base, home, guide, chat, sdes, des, code_guide, bruteforce, benchmark, tests, history
├── static/                      # style.css, chat.js (phòng chat), present.js
├── web_tinh/                    # Bản web tĩnh (HTML/CSS/JS), đưa lên GitHub Pages / Netlify được
└── requirements.txt             # flask, pycryptodome

Hai cách viết cùng một thuật toán được kiểm tra khớp nhau trong test_runner.py: class (TinyDES, StandardDES) dễ đọc theo từng bước, và các hàm dạng số nguyên / bảng tra dùng cho web và mã hóa tệp lớn.

5. Bộ kiểm thử (python test_runner.py → Passed 43/43)

A. Ca kiểm thử nhóm tự viết (13 ca)

Ca	Đầu vào	Mong đợi
TinyDES mã hóa (ví dụ tài liệu)	P = 01011100, K = 10011010	C = 10010010
TinyDES giải mã (ví dụ tài liệu)	C = 10010010, K = 10011010	P = 01011100
TinyDES khứ hồi toàn bộ	256 khóa × 256 bản rõ = 65.536 cặp	D(E(P)) = P, 0 cặp sai
Hàm TinyDES khớp class TinyDES	65.536 cặp (bản rõ, khóa)	0 cặp lệch
Vét cạn 1 khối	P = 01101111, K = 10101100	khóa thật nằm trong các khóa tìm được
Chọn bản rõ	bản mã chặn được của byte 6F	dịch ra 6F, bảng 256 dòng
Chỉ biết bản mã	"Xin chào các bạn", K = 10101100	khóa thật xếp hạng 1
TinyDES mã hóa chữ "Hello" (ECB)	K = 10011010	67 B3 20 20 A2
DES mã hóa (ví dụ Grabbe)	P = 0123456789ABCDEF, K = 133457799BBCDFF1	C = 85E813540F0AB405
DES bản nhanh khớp class StandardDES	30 khối ngẫu nhiên	0 khối lệch
DES văn bản tiếng Việt	"Xin chào, đây là bản thử tiếng Việt 123!"	giải mã ra đúng văn bản
DES PKCS#7	độ dài 0, 1, 7, 8, 9, 16 byte	luôn thêm 1–8 byte (đủ 8 byte vẫn thêm 1 khối)
DES sai khóa	nhom2025 thay cho nhom2026	báo lỗi padding

B. Test vector chuẩn NIST SP 800-17 (16 ca): 8 vector Known Answer Test (4 vector Variable Plaintext + 4 vector Variable Key), mỗi vector kiểm tra cả mã hóa và giải mã.

C. Đối chiếu pycryptodome (14 ca): 3 khối cố định, 3 đoạn văn bản (Hello, Code DES from scratch!, câu tiếng Việt), 200 cặp khóa/khối ngẫu nhiên (os.urandom), 7 tệp ngẫu nhiên 0 B, 1 B, 7 B, 8 B, 1.000 B, 10 KB, 100 KB ở chế độ ECB + PKCS#7 (mã hóa giống thư viện và giải mã khôi phục đúng).

6. Nguồn tham khảo và phần tự viết
Tham khảo (chỉ dữ liệu, không lấy mã nguồn):
Test vector DES lấy từ NIST SP 800-17, Modes of Operation Validation System, Appendix A.
Các bảng hoán vị và S-box của DES lấy từ chuẩn NIST FIPS PUB 46-3, Data Encryption Standard.
Thuật toán TinyDES (Expand, S-box, P-box, Compress, lịch dịch khóa 1-2-1) và ví dụ P = 01011100, K = 10011010 → C = 10010010 lấy từ tài liệu môn học Chương 2 - Mã hoá khoá đối xứng, mục 3.2, trang 67–72.
Ví dụ DES 133457799BBCDFF1 lấy từ bài viết The DES Algorithm Illustrated của J. Orlin Grabbe.
Thư viện ngoài:
pycryptodome chỉ dùng trong test_runner.py, ca kiểm thử tự nhập trên web và trang đo thời gian để đối chiếu; thư mục core/ không import thư viện mật mã nào.
Flask dùng cho giao diện web.
Nhóm tự viết: toàn bộ phần cài đặt thuật toán TinyDES và DES, padding, xử lý tệp, tấn công (vét cạn, chọn bản rõ, gặp nhau ở giữa), giao diện, kiểm thử.
7. Lưu ý bảo mật
DES dùng khóa 56 bit nên đã bị phá được bằng vét cạn; trong thực tế nên dùng AES.
TinyDES chỉ có khóa 8 bit (256 khóa) và khối 8 bit (256 bản rõ), nên bị phá ngay bằng vét cạn hoặc chọn bản rõ. Đồ án chỉ dùng để học.
Chế độ ECB làm lộ cấu trúc dữ liệu: các khối giống nhau cho ra bản mã giống nhau. Đồ án dùng ECB để đối chiếu trực tiếp với thư viện chuẩn.
Server chỉ giữ tệp kết quả trong RAM (20 tệp gần nhất) và không lưu khóa.
