# Giải thích đồ án TinyDES và DES: An gửi Bình, kẻ xấu chặn giữa

> TinyDES được cài đặt **đúng theo tài liệu môn học** *Chương 2 - Mã hoá khoá đối xứng*, mục 3.2, trang 67–72. DES theo trang 73–83.
> Mọi con số ví dụ trong file này đều lấy từ **kết quả chạy thật** của chương trình.

## 🚦 Bắt đầu ở đây: đọc theo thứ tự này là hiểu

| Bước | Làm gì | Ở đâu | Mất khoảng |
|---|---|---|---|
| 1 | Chạy web, chơi thử câu chuyện An gửi Bình, bấm vét cạn khóa, sửa tin | `python app.py` → mở http://127.0.0.1:5000 → menu **💬 An gửi Bình** | 5 phút |
| 2 | Đọc kịch bản: mỗi cảnh bấm gì, nói gì | Web → **🎬 Kịch bản & hướng dẫn** | 10 phút |
| 3 | Hiểu thuật toán bằng lời thường, không cần code | File này → **Bước 0.1 → 0.4** (TinyDES), **D0 → D12** (DES) | 20 phút |
| 4 | Đọc code đặt cạnh thuật toán, code thật kèm số dòng | Web → **📗 Đọc code cùng thuật toán** | 20 phút |
| 5 | Tra nghĩa từng biến khi đọc code thấy lạ | File này → **📖 Từ điển biến** (V1 → V22) | khi cần |
| 6 | Xem bên trong từng bit | Web → **🔑 TinyDES từng bước** (bấm “Trình chiếu từng bước”) | 5 phút |

> **3 câu nhớ trong đầu khi đọc mọi thứ bên dưới:**
> 1. **Khóa** là mật khẩu An và Bình tự chọn và giữ bí mật. **Mã hóa** biến tin thành dãy số lộn xộn, **giải mã** biến ngược lại.
> 2. Mỗi **vòng** chỉ làm 1 việc: nửa phải vào “máy xay” cùng chìa, kết quả trộn vào nửa trái, rồi đổi chỗ 2 nửa.
> 3. Code chia 2 phần: **`core/` là bếp** (thuật toán thật), **`app.py` và `templates/` là bồi bàn** (nhận dữ liệu, trả trang web).

**Mục lục file này:**

| Phần | Nội dung |
|---|---|
| 📖 **Từ điển biến** V1 → V17 | Từng biến trong `core/` là gì, đựng gì, đổi thế nào qua từng dòng |
| 📖 **Từ điển biến** V18 → V22 | Code trang chat (`chat_send`, `chat_attack`, `chat_tamper`), `static/chat.js`, trang Đọc code, xuất web tĩnh |
| 🎓 TinyDES → **Bước 0.1** | Vào gì, ra gì, "mã", "dịch vòng", "b0 b1 b2" nghĩa là gì; cả quá trình từng bước |
| 🎓 TinyDES → **Bước 0.2** | Tin nhắn dạng chữ biến thành bit thế nào ("Hello" → `67 B3 20 20 A2`) |
| 🎓 TinyDES → **Bước 0.3** | Khóa K do ai chọn, nhập ở đâu, khóa yếu |
| 🎓 TinyDES → **Bước 0.4** | 🗺️ 10 sơ đồ: bấm nút → hàm nào chạy → từng hàm vào gì, ra gì |
| 🎓 TinyDES → **T0 … T7** | Từng bước slide 67–72 ↔ từng dòng code |
| 🎓 DES → **D0 … D12** | DES slide 73–83, kĩ như TinyDES: khóa, đệm, IP, 1 vòng, 16 vòng, IP⁻¹, giải mã, tệp |
| 🔓 **Kẻ xấu bẻ khóa TinyDES** | Thử 256 khóa: khi biết bản rõ, và khi chỉ có bản mã |
| ⭐ **Đọc phần này trước**, PHẦN 0–5 | Bản tóm tắt bằng lời thường, luồng chạy web, cú pháp Python |

**Các trang web của đồ án** (menu bên trái, chia 3 nhóm):

| Nhóm | Trang | Địa chỉ | Dùng để |
|---|---|---|---|
| Bắt đầu | 🏠 Trang chủ | `/` | Câu chuyện An, Bình, kẻ xấu; lối tắt tới các trang |
| | 🎬 Kịch bản & hướng dẫn | `/huong-dan` | Kịch bản thuyết trình 8 cảnh, hướng dẫn từng trang, hỏi đáp, sự cố |
| | 💬 An gửi Bình | `/chat` | Phòng chat: mã hóa thật, kẻ xấu vét cạn khóa / sửa tin, phòng thủ |
| Bên trong máy mã hóa | 🔑 TinyDES từng bước | `/sdes` | (trước đây tên “TinyDES Demo”) từng bit 3 vòng, trình chiếu |
| | 📁 DES: văn bản & tệp | `/des` | (trước đây “DES File”) mã hóa chữ, ảnh, tệp; xem 16 vòng |
| | 📗 Đọc code cùng thuật toán | `/doc-code` | Mỗi bước thuật toán đặt cạnh code thật (số dòng thật) và giá trị chạy thật |
| | 📘 Lý thuyết · 🧭 Luồng chạy code | `/theory` · `/flow` | Sơ đồ lý thuyết · cây gọi hàm có giá trị thật |
| Kẻ xấu & kiểm chứng | 🕵️ Kẻ xấu bẻ khóa | `/bruteforce` | (trước đây “Bẻ khóa TinyDES”) 2 kịch bản vét cạn |
| | ⏱️ Đo thời gian · ✅ Kiểm thử · 🕘 Lịch sử | `/benchmark` · `/tests` · `/history` | So tốc độ · chứng minh code đúng · xem đã làm gì |

### 🌐 Bản web trên mạng (chỉ HTML, không cần Python)

- Đã đăng: **https://claude.ai/artifact/4q9jxYp1R3GXg3bUSPSd2S** (đang riêng tư, bấm **Share** trên trang để chia sẻ).
- Xuất lại sau khi sửa code: `python xuat_web_tinh.py` → thư mục `web_tinh/` (12 tệp). Mở `web_tinh/index.html` là chạy.
  Muốn đăng lên claude.ai thì thêm `--artifact`. Đăng chỗ khác: kéo thả `web_tinh/` vào Netlify Drop, hoặc đưa lên GitHub Pages.
- Bản tĩnh **có**: Trang chủ, Kịch bản, An gửi Bình (bấm được), Đọc code, Lý thuyết, Luồng code, TinyDES/DES từng bước.
  **Không có** (cần Python): Kẻ xấu bẻ khóa, Đo thời gian, Kiểm thử, Lịch sử.
- Chi tiết từng bước: web → **🎬 Kịch bản & hướng dẫn** → mục **🌐 Đưa đồ án lên web**. Giải thích code: mục **V22** bên dưới.

Trang có màu, đi từng bước: TinyDES https://claude.ai/artifact/HK4CxoE1EY6v2hLSGzVWbE · DES https://claude.ai/artifact/65DZ6C7qMPoH1uh2DhnLQj

---

# 📖 Từ điển biến: từng biến trong code là gì?

## Đọc phần này trước: "biến" là gì?

**Biến = một cái hộp có dán nhãn tên.** Bên trong hộp đựng một giá trị.

```python
kl = "1001"
```

Đọc là: *"lấy cái hộp tên `kl`, bỏ chữ `"1001"` vào"*. Dấu `=` trong Python **không phải "bằng nhau"** như trong toán, mà là **"bỏ vào hộp"**.

Nếu sau đó viết `kl = "0011"`, hộp `kl` **bị đổ ra và bỏ đồ mới vào**. Giá trị cũ `"1001"` mất.

**Các loại "đồ" hay gặp trong code:**

| Loại | Trông như thế nào | Ví dụ trong code |
|---|---|---|
| **Chuỗi** (str) | chữ trong dấu `" "` | `"10011010"`: 8 ký tự '0'/'1', TinyDES dùng loại này |
| **Số nguyên** (int) | số không có dấu `" "` | `3`, `0x133457799BBCDFF1` (DES dùng loại này) |
| **List** | nhiều thứ trong `[ ]`, **thêm bớt được** | `[1, 2, 1]`, `keys = []` rồi `keys.append(...)` |
| **Tuple** | nhiều thứ trong `( )`, **không sửa được** | `("101110", "110011", "001001")` |
| **Dict** | cặp "tên: giá trị" trong `{ }` | `{"buoc": "K1", "gia_tri": "101110"}` |
| **Bytes** | dãy byte, viết `b"..."` | `b"Hello"` = 5 số 72, 101, 108, 108, 111 |
| **None** | "hộp rỗng, không có gì" | `log=None`: không cần ghi nhật ký |

**Tham số** là biến nằm trong ngoặc của `def`. Ví dụ `def generate_keys(key_8bit, log=None)`: khi ai đó gọi `generate_keys("10011010")`, hộp `key_8bit` tự được bỏ `"10011010"` vào. `log=None` nghĩa là nếu người gọi không đưa gì thì hộp `log` rỗng.

> Mọi giá trị ví dụ dưới đây lấy từ ví dụ slide 72: **P = `01011100`, K = `10011010`** (TinyDES),
> và ví dụ kinh điển **khối `0123456789ABCDEF`, khóa `133457799BBCDFF1`** (DES). Đều là kết quả chạy thật.

---

## V1. TinyDES: các "bảng luật" cố định (đầu file `core/tinydes_core.py:25-38`)

Đây là các hộp **đổ đồ vào 1 lần lúc đầu, không bao giờ đổi**. Tên viết HOA để báo "đây là hằng số, đừng sửa". Tất cả chép từ slide.

| Biến | Đựng gì | Giá trị | Nghĩa bằng lời thường | Slide |
|---|---|---|---|---|
| `EXPAND` | list 6 số | `[2, 3, 1, 2, 1, 0]` | "Muốn kéo 4 ô thành 6 ô thì lấy ô 2, ô 3, ô 1, ô 2, ô 1, ô 0" | 69 |
| `PBOX` | list 4 số | `[2, 0, 3, 1]` | "Xếp lại 4 ô: lấy ô 2, ô 0, ô 3, ô 1" | 70 |
| `COMPRESS` | list 6 số | `[5, 1, 3, 2, 7, 0]` | "Từ 8 ô chọn ra 6 ô: ô 5, 1, 3, 2, 7, 0" | 71 |
| `SHIFTS` | list 3 số | `[1, 2, 1]` | "Vòng 1 xoay 1 ô, vòng 2 xoay 2 ô, vòng 3 xoay 1 ô" | 71 |
| `ROUNDS` | số | `3` | TinyDES trộn 3 lần | 67 |
| `SBOX` | list 4 hàng, mỗi hàng 16 số | `[[0xE, 0x4, …], …]` | Bảng tra 4 × 16. `SBOX[3][2]` = hàng 3, cột 2 = `8` | 70 |
| `KEY_SPACE` | số | `256` | Có tất cả 2⁸ = 256 khóa (dùng khi bẻ khóa) | |
| `PUNCT` | chuỗi | `".,!?:;'\"-()\n"` | Các dấu câu, dùng khi chấm điểm "giống chữ" | |

---

## V2. TinyDES: 4 hàm "dụng cụ" (`core/tinydes_core.py:44-79`)

### `permute(bits, table)`: chép ô theo bảng

| Biến | Là gì | Ví dụ (Expand vòng 1) |
|---|---|---|
| `bits` | dãy ô đưa vào | `"1100"` |
| `table` | bảng luật: lấy ô số mấy | `EXPAND` = `[2, 3, 1, 2, 1, 0]` |
| `i` | số ô đang lấy, lần lượt từng số trong `table` | 2 → 3 → 1 → 2 → 1 → 0 |
| `bits[i]` | ký tự ở ô số `i` | `bits[2]` = `"0"`, `bits[3]` = `"0"`, `bits[1]` = `"1"`… |
| (kết quả) | nối các ký tự lấy được | `"001011"` |

Theo dõi từng bước:

| Lần | `i` | `bits[i]` | Kết quả đã nối |
|---|---|---|---|
| 1 | 2 | `0` | `0` |
| 2 | 3 | `0` | `00` |
| 3 | 1 | `1` | `001` |
| 4 | 2 | `0` | `0010` |
| 5 | 1 | `1` | `00101` |
| 6 | 0 | `1` | `001011` |

### `left_shift(bits, n)`: xoay vòng trái

| Biến | Là gì | Ví dụ |
|---|---|---|
| `bits` | dãy ô cần xoay | `"1001"` |
| `n` | xoay mấy ô | `1` |
| `bits[n:]` | phần **từ ô n đến hết** | `"001"` |
| `bits[:n]` | **n ô đầu** | `"1"` |
| (kết quả) | phần sau + phần đầu | `"001" + "1"` = `"0011"` |

### `xor(a, b)`: so từng cặp

| Biến | Là gì | Ví dụ |
|---|---|---|
| `a`, `b` | 2 dãy dài bằng nhau | `"001011"`, `"101110"` |
| `x`, `y` | 1 cặp ký tự cùng vị trí (do `zip(a, b)` ghép) | lần 1: `x="0"`, `y="1"` |
| (kết quả) | giống → `"0"`, khác → `"1"` | `"100101"` |

### `is_bits(s, length)`: kiểm tra nhập đúng chưa

| Biến | Là gì | Ví dụ |
|---|---|---|
| `s` | chuỗi cần kiểm tra | `"10011010"` |
| `length` | phải dài bao nhiêu | `8` |
| `c` | từng ký tự của `s` | `"1"`, `"0"`, … |
| (kết quả) | `True` nếu đủ dài **và** chỉ có 0/1 | `True`. Với `"1001"` → `False` |

---

## V3. `generate_keys(key_8bit, log=None)`: làm 3 chìa (`core/tinydes_core.py:95-118`)

| Biến | Loại | Là gì |
|---|---|---|
| `key_8bit` | chuỗi | Khóa bạn gõ vào. Ví dụ `"10011010"` |
| `log` | list hoặc None | Cuốn sổ ghi lại các bước để in ra. `None` = không ghi |
| `kl` | chuỗi 4 ký tự | **Nửa trái** của khóa (slide gọi KL). Bị xoay và **ghi đè** mỗi vòng |
| `kr` | chuỗi 4 ký tự | **Nửa phải** của khóa (slide gọi KR). Bị xoay và ghi đè mỗi vòng |
| `keys` | list | Cái giỏ đựng các chìa làm xong. Ban đầu rỗng `[]` |
| `i` | số | Đang ở vòng mấy: 1, 2, 3 |
| `s` | số | Vòng này xoay mấy ô, lấy từ `SHIFTS`: 1, 2, 1 |
| `k` | chuỗi 6 ký tự | Chìa vừa làm xong ở vòng này |

**Theo dõi các hộp qua từng dòng:**

| Thời điểm | `i` | `s` | `kl` | `kr` | `k` | `keys` |
|---|---|---|---|---|---|---|
| Sau `kl, kr = key_8bit[:4], key_8bit[4:]` | | | `1001` | `1010` | | `[]` |
| Vòng 1, sau dòng xoay | 1 | 1 | `0011` | `0101` | | `[]` |
| Vòng 1, sau `k = permute(...)` và `append` | 1 | 1 | `0011` | `0101` | `101110` | `["101110"]` |
| Vòng 2, sau dòng xoay | 2 | 2 | `1100` | `0101` | | |
| Vòng 2, xong | 2 | 2 | `1100` | `0101` | `110011` | `["101110", "110011"]` |
| Vòng 3, sau dòng xoay | 3 | 1 | `1001` | `1010` | | |
| Vòng 3, xong | 3 | 1 | `1001` | `1010` | `001001` | `["101110", "110011", "001001"]` |
| `return tuple(keys)` | | | | | | → `("101110", "110011", "001001")` |

Dòng `for i, s in enumerate(SHIFTS, start=1)` nghĩa là: *"đi qua từng số trong `SHIFTS`; mỗi lần bỏ số thứ tự vào hộp `i` (đếm từ 1), bỏ số đó vào hộp `s`"*.

---

## V4. `sbox_lookup(bits6)`: tra bảng (`core/tinydes_core.py:124-133`)

| Biến | Là gì | Ví dụ (vòng 1) |
|---|---|---|
| `bits6` | 6 ô đưa vào | `"100101"` |
| `bits6[0] + bits6[5]` | ô đầu ghép ô cuối | `"1" + "1"` = `"11"` |
| `row` | số hàng (đổi `"11"` từ nhị phân ra số) | `3` |
| `bits6[1:5]` | 4 ô giữa (ô 1, 2, 3, 4) | `"0010"` |
| `col` | số cột | `2` |
| `SBOX[row][col]` | con số trong bảng | `8` |
| (kết quả) | `(4 ô ra, row, col)` | `("1000", 3, 2)` |

---

## V5. `f_function(half4, subkey, log=None, tag="")`: máy xay F (`core/tinydes_core.py:136-150`)

| Biến | Là gì | Ví dụ (vòng 1) |
|---|---|---|
| `half4` | nửa đưa vào máy xay (lúc mã hóa là nửa phải R) | `"1100"` |
| `subkey` | chìa của vòng này | K1 = `"101110"` |
| `log` | cuốn sổ ghi bước (có thể `None`) | |
| `tag` | chữ dán đầu mỗi dòng nhật ký | `"Vòng 1"` |
| `ex` | kết quả **kéo dài** 4 → 6 ô (việc a) | `"001011"` |
| `x` | kết quả **trộn với chìa** (việc b) | `"100101"` |
| `s` | kết quả **tra bảng** 6 → 4 ô (việc c) | `"1000"` |
| `row`, `col` | hàng, cột đã tra (chỉ để ghi nhật ký) | `3`, `2` |
| `f` | kết quả **xếp lại chỗ** (việc d) = **F** | `"0100"` |

Đường đi của dữ liệu: `half4` → `ex` → `x` → `s` → `f`. Mỗi hộp đựng kết quả của 1 việc.

---

## V6. `_encrypt_block(bits8, keys, log=None)`: 3 vòng trộn (`core/tinydes_core.py:156-167`)

| Biến | Là gì |
|---|---|
| `bits8` | 8 ô bản rõ. Ví dụ `"01011100"` |
| `keys` | 3 chìa. Ví dụ `("101110", "110011", "001001")` |
| `left` | **nửa trái hiện tại** (slide gọi L). Mỗi vòng bị ghi đè |
| `right` | **nửa phải hiện tại** (slide gọi R). Mỗi vòng bị ghi đè |
| `i` | vòng mấy: 1, 2, 3 |
| `k` | chìa của vòng này |
| `f` | kết quả máy xay của vòng này |

**Theo dõi các hộp:**

| Thời điểm | `i` | `k` | `f` | `left` | `right` |
|---|---|---|---|---|---|
| Sau `left, right = bits8[:4], bits8[4:]` | | | | `0101` | `1100` |
| Vòng 1: `f = f_function(right, k)` | 1 | `101110` | `0100` | `0101` | `1100` |
| Vòng 1: `left, right = right, xor(left, f)` | 1 | | | `1100` | `0001` |
| Vòng 2: tính `f` | 2 | `110011` | `0101` | `1100` | `0001` |
| Vòng 2: đổi chỗ | 2 | | | `0001` | `1001` |
| Vòng 3: tính `f` | 3 | `001001` | `0011` | `0001` | `1001` |
| Vòng 3: đổi chỗ | 3 | | | `1001` | `0010` |
| `return left + right` | | | | | → `"10010010"` |

**Dòng quan trọng nhất:** `left, right = right, xor(left, f)`. Python làm 2 bước:
1. Tính **hết vế phải trước**, dùng hộp cũ: `right` = `"1100"`, `xor("0101", "0100")` = `"0001"`.
2. **Rồi mới bỏ cùng lúc** vào 2 hộp: `left` ← `"1100"`, `right` ← `"0001"`.

---

## V7. `_decrypt_block(bits8, keys, log=None)`: đi ngược (`core/tinydes_core.py:170-181`)

Cùng các hộp `left`, `right`, `f` như V6. Khác ở 2 chỗ:
- `i` chạy **3, 2, 1** (`range(3, 0, -1)` = "từ 3, lùi dần, dừng trước 0").
- `keys[i - 1]`: chìa của vòng `i`. Trừ 1 vì giỏ `keys` đánh số từ 0 (K1 là `keys[0]`, K3 là `keys[2]`).

| Thời điểm | `i` | chìa | `f` | `left` | `right` |
|---|---|---|---|---|---|
| Bắt đầu (bản mã) | | | | `1001` | `0010` |
| Vòng 3: `f = f_function(left, keys[2])`, rồi `left, right = xor(right, f), left` | 3 | K3 `001001` | `0011` | `0001` | `1001` |
| Vòng 2 | 2 | K2 `110011` | `0101` | `1100` | `0001` |
| Vòng 1 | 1 | K1 `101110` | `0100` | `0101` | `1100` |
| `return left + right` | | | | | → `"01011100"` ✔ |

---

## V8. `encrypt()` / `decrypt()`: cửa ngõ (`core/tinydes_core.py:184-211`)

| Biến | Là gì | Ví dụ |
|---|---|---|
| `plain_8bit` | bản rõ bạn đưa vào | `"01011100"` |
| `cipher_8bit` | (trong `decrypt`) bản mã đưa vào | `"10010010"` |
| `key_8bit` | khóa | `"10011010"` |
| `log_trung_gian` | cuốn sổ rỗng `[]`, các hàm con ghi thêm vào | sau khi chạy có nhiều dòng, mỗi bước 1 dòng |
| `keys` | 3 chìa | `("101110", "110011", "001001")` |
| `cipher` / `plain` | kết quả | `"10010010"` / `"01011100"` |

Mỗi dòng trong `log_trung_gian` là một dict 3 ngăn, do hàm `_log(log, buoc, gia_tri, ghi_chu)` tạo ra:

| Ngăn | Là gì | Ví dụ |
|---|---|---|
| `"buoc"` | tên bước | `"K1"` |
| `"gia_tri"` | giá trị ở bước đó | `"101110"` |
| `"ghi_chu"` | giải thích | `"Compress: k5 k1 k3 k2 k7 k0"` |

---

## V9. Mã hóa câu chữ và bẻ khóa (`core/tinydes_core.py:217-311`)

### `encrypt_bytes(data, key_8bit, keys=None)` / `decrypt_bytes(...)`

| Biến | Là gì | Ví dụ |
|---|---|---|
| `data` | dãy byte cần mã | `b"Hello"` = `[72, 101, 108, 108, 111]` |
| `key_8bit` | khóa | `"10011010"` |
| `keys` | 3 chìa. Nếu người gọi đưa sẵn thì dùng luôn, không thì tự làm (`keys or generate_keys(...)`) | |
| `b` | từng byte trong `data`, lần lượt | `72`, rồi `101`, … |
| (kết quả) | dãy byte bản mã | `67 B3 20 20 A2` |

### `brute_force(plain_bytes, cipher_bytes)`: biết cả bản rõ lẫn bản mã

| Biến | Là gì | Ví dụ |
|---|---|---|
| `plain_bytes` | bản rõ kẻ tấn công biết | `b"Hello"` |
| `cipher_bytes` | bản mã chặn được | `43 61 DA DA C0` |
| `found` | giỏ đựng các khóa khớp. Ban đầu `[]` | cuối cùng `["11011010"]` |
| `key` | khóa đang thử, lần lượt 256 khóa | `"00000000"`, `"00000001"`, … |

### `readability_score(data)`: chấm điểm "giống chữ"

| Biến | Là gì | Ví dụ |
|---|---|---|
| `data` | dãy byte giải mã thử | |
| `text` | `data` đổi ra chữ. Đổi không được thì là rác, trả điểm khoảng −1000 | `"Hẹn gặp lúc 8h"` |
| `score` | tổng điểm, cộng dần qua từng chữ | |
| `ch` | từng chữ trong `text` | `"H"`, `"ẹ"`, … |
| (kết quả) | `score` chia số byte | `1.526` |

### `brute_force_ciphertext_only(cipher_bytes, top=5)`: chỉ có bản mã

| Biến | Là gì |
|---|---|
| `cipher_bytes` | bản mã chặn được |
| `top` | lấy bao nhiêu ứng viên tốt nhất (mặc định 5) |
| `candidates` | giỏ 256 ứng viên, mỗi ứng viên là dict `{"key", "dec", "subkeys", "score", "plain"}` |
| `key` | khóa đang thử |
| `keys` | 3 chìa của khóa đang thử |
| `plain` | bản giải mã thử với khóa đó |

Cuối hàm: xếp `candidates` theo `score` từ cao xuống thấp, lấy `top` cái đầu.

---

## V10. `app.py → sdes_demo()`: lúc bạn bấm nút trên web (`app.py:350-403`)

Ví dụ: gõ khóa `10011010`, bản rõ `01011100`, chọn kiểu nhị phân, bấm **Mã hóa**.

| Biến | Lấy từ đâu | Giá trị ví dụ |
|---|---|---|
| `key` | ô "Khóa" trên trang (`request.form.get("sdes_key")`) | `"10011010"` |
| `fmt` | ô chọn kiểu nhập | `"bin"` (nhị phân) hoặc `"text"` (chữ) |
| `action` | nút bạn bấm | `"enc"` (Mã hóa) hoặc `"dec"` (Giải mã) |
| `raw_input` | ô nhập dữ liệu | `"01011100"` |
| `blocks` | `raw_input` cắt thành các khối 8 ô (`parse_sdes_data`) | `["01011100"]` |
| `key_log` | cuốn sổ ghi bước làm chìa | 8 dòng |
| `keys` | 3 chìa | `("101110", "110011", "001001")` |
| `fn` | **cái máy** sẽ dùng: bấm Mã hóa thì là `encrypt`, bấm Giải mã thì là `decrypt` | `tinydes_core.encrypt` |
| `out_blocks` | giỏ đựng kết quả từng khối | `["10010010"]` |
| `block_logs` | giỏ đựng nhật ký từng khối (để vẽ bảng trên web) | |
| `t0` | giờ lúc bắt đầu chạy (để đo nhanh chậm) | |
| `i`, `blk` | số thứ tự và khối đang xử lý | `0`, `"01011100"` |
| `out`, `log` | kết quả và nhật ký của khối đang xử lý | `"10010010"`, `[...]` |
| `elapsed` | chạy mất bao nhiêu mili-giây | một số rất nhỏ |
| `out_bytes` | `out_blocks` đổi ra byte | `b'\x92'` |
| `traces` | dữ liệu từng ô bit để web vẽ màu | |
| `result` | dict gom tất cả kết quả, gửi cho trang `sdes.html` | `{"out_hex": "92", ...}` |
| `original`, `back` | (khi mã hóa) bản rõ gốc, và kết quả giải mã ngược lại để kiểm tra | `back == original` → `True` |

Trong `parse_sdes_data(raw, fmt, is_input_cipher)` (`app.py:89`):

| Biến | Là gì | Ví dụ |
|---|---|---|
| `raw` | chữ bạn gõ | `"01011100"` hoặc `"Hi"` |
| `fmt` | kiểu nhập | `"bin"` / `"text"` |
| `is_input_cipher` | đang nhập bản mã dạng chữ không (khi đó phải gõ hex) | `False` |
| `bits` | (kiểu bin) bỏ hết khoảng trắng | `"01011100"` |
| `data` | (kiểu text) chữ đổi ra byte | `"Hi"` → `b"Hi"` |
| (kết quả) | list khối 8 ô | `["01001000", "01101001"]` |

---

## V11. DES: các bảng luật (`core/des_tables.py`)

Giống V1, chỉ to hơn. Các số đếm **từ 1** (slide đếm từ 0, nên lệch 1).

| Biến | Đựng gì | Nghĩa |
|---|---|---|
| `IP` | 64 số | Xáo chỗ 64 ô lúc đầu: "ô mới 1 chép từ ô 58, ô mới 2 chép từ ô 50, …" |
| `IP_INV` | 64 số | Xáo chỗ ngược lại lúc cuối |
| `E` | 48 số | Kéo dài 32 ô thành 48 ô |
| `P` | 32 số | Xếp lại chỗ 32 ô sau khi tra bảng |
| `PC1` | 56 số | Bỏ 8 ô thừa của khóa, 64 → 56 |
| `PC2` | 48 số | Chọn 48 trong 56 ô làm chìa |
| `SHIFTS` | 16 số | Vòng 1…16 xoay mấy ô: `[1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]` |
| `S_BOX` | 8 bảng × 4 hàng × 16 cột | 8 bảng tra. `S_BOX[0]` là S1, `S_BOX[7]` là S8 |

---

## V12. DES: dụng cụ trên số nguyên (`core/des_core.py:23-53`)

DES không dùng chuỗi `"0101"` mà dùng **số nguyên**, nên các dụng cụ dùng phép toán bit (`>>`, `<<`, `&`, `|`, `^`). Xem bảng phép toán ở PHẦN 5.5.

### `permute(value, table, in_bits)`

| Biến | Là gì | Ví dụ nhỏ |
|---|---|---|
| `value` | số đưa vào | `0b1011` |
| `table` | bảng luật (đếm từ 1) | `[2, 4, 3, 1]` |
| `in_bits` | số đưa vào dài mấy ô | `4` |
| `out` | kết quả, bắt đầu từ `0`, gắn dần từng ô vào cuối | `0` → `0` → `01` → `011` → `0111` |
| `pos` | ô số mấy đang lấy | 2, 4, 3, 1 |
| `bit` | giá trị ô đó (0 hoặc 1) | 0, 1, 1, 1 |

### `rotl(value, n, bits)`

| Biến | Là gì | Ví dụ |
|---|---|---|
| `value` | số cần xoay | `0b1000` |
| `n` | xoay mấy ô | `1` |
| `bits` | số dài mấy ô | `4` |
| `mask` | dãy `bits` số 1, dùng để cắt phần thừa | `0b1111` |
| (kết quả) | | `0b0001` |

---

## V13. `generate_subkeys(key, log=None)`: làm 16 chìa DES (`core/des_core.py:59-91`)

| Biến | Loại | Là gì | Ví dụ |
|---|---|---|---|
| `key` | bytes | 8 byte khóa | `13 34 57 79 9B BC DF F1` |
| `log` | list hoặc None | cuốn sổ để web hiện C, D, K từng vòng | |
| `k64` | số 64 bit | khóa đổi ra 1 số | `0x133457799BBCDFF1` |
| `k56` | số 56 bit | sau khi bỏ 8 ô thừa (PC-1) | `0xF0CCAAF556678F` |
| `c` | số 28 bit | **nửa trái** (slide gọi KL). Ghi đè mỗi vòng | `F0CCAAF` |
| `d` | số 28 bit | **nửa phải** (slide gọi KR). Ghi đè mỗi vòng | `556678F` |
| `subkeys` | list | giỏ đựng 16 chìa | |
| `i` | số | vòng 1 … 16 | |
| `s` | số | vòng này xoay mấy ô (1 hoặc 2) | |
| `k` | số 48 bit | chìa vừa làm | K1 = `1B02EFFC7072` |

| Thời điểm | `i` | `s` | `c` | `d` | `k` |
|---|---|---|---|---|---|
| Sau PC-1 và cắt đôi | | | `F0CCAAF` | `556678F` | |
| Vòng 1 | 1 | 1 | `E19955F` | `AACCF1E` | `1B02EFFC7072` |
| Vòng 2 | 2 | 1 | `C332ABF` | `5599E3D` | `79AED9DBC9E5` |
| Vòng 3 | 3 | 2 | `0CCAAFF` | `56678F5` | `55FC8A42CF99` |
| … | … | … | … | … | … |
| Vòng 16 | 16 | 1 | `F0CCAAF` | `556678F` | `CB3D8B0E17F5` |

---

## V14. `sbox_sub(x48)`: tra 8 bảng (`core/des_core.py:97-117`)

| Biến | Là gì |
|---|---|
| `x48` | 48 ô sau khi trộn với chìa. Ví dụ `0x6117BA866527` |
| `out` | kết quả, bắt đầu `0`, mỗi lần gắn thêm 4 ô vào cuối |
| `i` | đang tra bảng thứ mấy: 0 … 7 (ứng với S1 … S8) |
| `chunk` | nhóm 6 ô thứ `i` |
| `row` | số hàng = ô đầu + ô cuối của `chunk` |
| `col` | số cột = 4 ô giữa của `chunk` |

| `i` | Bảng | `chunk` | `row` | `col` | Số trong bảng | `out` sau lần này (hex) |
|---|---|---|---|---|---|---|
| 0 | S1 | `011000` | 0 | 12 | 5 | `5` |
| 1 | S2 | `010001` | 1 | 8 | 12 (C) | `5C` |
| 2 | S3 | `011110` | 0 | 15 | 8 | `5C8` |
| 3 | S4 | `111010` | 2 | 13 | 2 | `5C82` |
| 4 | S5 | `100001` | 3 | 0 | 11 (B) | `5C82B` |
| 5 | S6 | `100110` | 2 | 3 | 5 | `5C82B5` |
| 6 | S7 | `010100` | 0 | 10 | 9 | `5C82B59` |
| 7 | S8 | `100111` | 3 | 3 | 7 | `5C82B597` |

---

## V15. `feistel_f(r32, k48, detail=None)`: máy xay DES (`core/des_core.py:120-137`)

| Biến | Là gì | Ví dụ (vòng 1) |
|---|---|---|
| `r32` | nửa phải đưa vào (32 ô) | `F0AAF0AA` |
| `k48` | chìa của vòng (48 ô) | `1B02EFFC7072` |
| `detail` | dict để ghi lại các bước cho web hiện (có thể `None`) | |
| `e` | kéo dài 32 → 48 ô (việc a) | `7A15557A1555` |
| `x` | trộn với chìa (việc b) | `6117BA866527` |
| `s` | tra 8 bảng, 48 → 32 ô (việc c) | `5C82B597` |
| `f` | xếp lại chỗ (việc d) = **F** | `234AA9BB` |

---

## V16. `crypt_block_verbose(block, subkeys)`: mã 1 khối DES (`core/des_core.py:140-170`)

| Biến | Là gì | Ví dụ |
|---|---|---|
| `block` | 8 byte bản rõ | `01 23 45 67 89 AB CD EF` |
| `subkeys` | 16 chìa. Mã hóa: K1→K16. Giải mã: K16→K1 | |
| `log` | sổ ghi từng vòng cho web | |
| `b` | `block` đổi ra 1 số 64 bit | `0x0123456789ABCDEF` |
| `ip` | sau khi xáo chỗ lần đầu (IP) | `0xCC00CCFFF0AAF0AA` |
| `left` | nửa trái hiện tại (32 ô), ghi đè mỗi vòng | `CC00CCFF` |
| `right` | nửa phải hiện tại (32 ô), ghi đè mỗi vòng | `F0AAF0AA` |
| `i`, `k` | vòng mấy, chìa của vòng đó | `1`, `1B02EFFC7072` |
| `detail` | dict ghi `e`, `xor`, `s`, `f` của vòng này | |
| `out` | kết quả cuối, sau khi ghép phải‖trái và xáo ngược (IP⁻¹) | `0x85E813540F0AB405` |

| Thời điểm | `left` | `right` |
|---|---|---|
| Sau IP, cắt đôi | `CC00CCFF` | `F0AAF0AA` |
| Sau vòng 1 | `F0AAF0AA` | `EF4A6544` |
| Sau vòng 2 | `EF4A6544` | `CC017709` |
| … (xem bảng 16 vòng ở D6) | … | … |
| Sau vòng 16 | `43423234` | `0A4CD995` |
| `out = permute((right << 32) \| left, IP_INV, 64)` | | → `85E813540F0AB405` |

---

## V17. `core/utils.py`: đệm, chia khối, khóa

| Hàm | Biến | Là gì | Ví dụ |
|---|---|---|---|
| (đầu file) | `BLOCK_SIZE` | mỗi khối DES dài 8 byte | `8` |
| `pkcs7_pad(data, block_size)` | `data` | dữ liệu cần đệm | `"Xin chào"` = 9 byte |
| | `n` | cần độn mấy byte = `8 - 9 % 8` | `7` |
| `pkcs7_unpad(data, block_size)` | `n` | byte cuối cùng = số byte đã độn | `7` |
| `split_blocks(data, block_size)` | `i` | vị trí bắt đầu mỗi khối | `0`, `8` |
| `parse_des_key(text)` | `text` | chữ bạn gõ ở ô khóa | `"nhom2026"` |
| | `raw` | `text` đổi ra byte | `6E 68 6F 6D 32 30 32 36` |
| `_crypt_blocks(data, subkeys)` | `sk` | 16 chìa đã cắt sẵn thành nhóm 6 ô (cho bản chạy nhanh) | |
| | `out` | giỏ đựng các khối đã mã (`bytearray`: dãy byte thêm vào được) | |
| | `block` | khối 8 byte đang mã | `58 69 6E 20 63 68 C3 A0` |
| `read_file(path)` / `write_file(path, data)` | `path` | đường dẫn tệp | `"anh.png"` |
| | `f` | tệp đang mở | |

> Các biến của **bản chạy nhanh** (`_IP_LUT`, `_FP_LUT`, `_SP`, `_fast_f`, `kc`, `ext`…) chỉ để chạy nhanh hơn, kết quả giống hệt bản dễ đọc.
> Khi thuyết trình **không cần giải thích** phần này.

---

## V18. Phòng chat An → Bình: phía server (`app.py:575-760`)

### Bức tranh: trang chat chạy thế nào?

Các trang cũ dùng **form**: bấm nút → cả trang tải lại. Trang chat thì **không tải lại trang**:
JavaScript (`static/chat.js`) gửi một gói dữ liệu nhỏ dạng **JSON** lên server, server trả JSON về, JavaScript tự vẽ thêm bong bóng chat.

```
 Trình duyệt (chat.js)                         Server (app.py)                         Bếp (core/)
 ─────────────────────                         ───────────────                         ───────────
 An bấm "Mã hóa & gửi"
   send(text) ──POST /api/chat/send──────────► chat_send()
               {"algo":"tinydes",                ├─ chat_json()      đọc gói JSON
                "key":"11011010",                ├─ chat_cipher()    chọn máy ──────────► generate_keys
                "text":"Hello"}                  ├─ enc(...)         An mã hóa ─────────► encrypt_bytes
                                                 └─ dec(...)         Bình giải mã ──────► decrypt_bytes
             ◄──JSON──────────────────────────── {"ok":true, "cipher_hex":"43 61 DA DA C0", "bob_text":"Hello", ...}
   addAn() addPacket() addBinh()   vẽ 3 cột

 Kẻ xấu bấm "Vét cạn khóa"
   attack() ──POST /api/chat/attack──────────► chat_attack()  ─────────────────────────► brute_force_ciphertext_only
             ◄──JSON──────────────────────────── {"success":true, "top":[...]}      (DES: thử 2000 khóa, tính số năm)

 Kẻ xấu bấm "Sửa 1 bit rồi chuyển"
   tamper() ──POST /api/chat/tamper──────────► chat_tamper()   đổi 1 bit, Bình giải mã bản đã sửa
             ◄──JSON──────────────────────────── {"bob_text": "…" hoặc "bob_error": "Padding sai…"}
```

**JSON** là cách viết dữ liệu giống dict của Python: `{"algo": "tinydes", "key": "11011010"}`. Python đọc bằng `request.get_json()`, trả bằng `jsonify(...)`.

### Hằng số và 2 hàm phụ

| Tên | Là gì | Giá trị / ví dụ |
|---|---|---|
| `DES_TRY` | Số khóa DES kẻ xấu thử để **đo tốc độ** (thử hết 2⁵⁶ khóa là không thể) | `2000` |
| `chat_cipher(algo, key)` | Trả về **2 cái máy**: (mã hóa, giải mã), mỗi máy nhận bytes trả bytes | `enc, dec = chat_cipher("tinydes", "11011010")` |
| `chat_json()` | Đọc gói JSON trình duyệt gửi lên, trả `(data, algo, key)` | `({...}, "tinydes", "11011010")` |

Bên trong `chat_cipher`:

| Biến | Là gì | Ví dụ |
|---|---|---|
| `algo` | thuật toán: `"tinydes"` hoặc `"des"` | `"tinydes"` |
| `key` | khóa người dùng gõ | `"11011010"` hoặc `"nhom2026"` |
| `keys` | (TinyDES) 3 chìa, làm **1 lần** rồi dùng cho mọi byte | `("…", "…", "…")` |
| `des_key` | (DES) khóa đã đổi ra 8 byte bằng `parse_des_key` | `b"nhom2026"` |
| `lambda data: ...` | **hàm không tên viết 1 dòng**. `lambda data: encrypt_bytes(data, key, keys)` nghĩa là “cái máy nhận `data`, trả `encrypt_bytes(data, key, keys)`” | |

Bên trong `chat_json`:

| Biến | Là gì |
|---|---|
| `data` | dict đọc từ JSON. `get_json(silent=True)`: dữ liệu hỏng thì trả `None` thay vì báo lỗi, rồi `or {}` đổi thành dict rỗng |
| `algo` | chỉ nhận `"des"` hoặc `"tinydes"`; gửi linh tinh thì coi là `"tinydes"` |
| `key` | `str(...).strip()`: đổi ra chuỗi, bỏ khoảng trắng 2 đầu |

### `chat_send()`: An gửi tin (`app.py:668`)

| Biến | Là gì | Ví dụ (TinyDES, khóa `11011010`, tin `"Hello"`) |
|---|---|---|
| `data, algo, key` | lấy từ `chat_json()` | `"tinydes"`, `"11011010"` |
| `text` | tin An gõ | `"Hello"` |
| `enc`, `dec` | 2 cái máy từ `chat_cipher` | |
| `t0` | giờ bắt đầu, để đo thời gian | |
| `cipher` | **bản mã**: thứ đi trên đường truyền, kẻ xấu thấy được | bytes `43 61 DA DA C0` |
| `bob` | Bình giải mã bằng cùng khóa, đổi về chữ | `"Hello"` |
| `elapsed` | mất bao nhiêu mili-giây | rất nhỏ |
| `weak` | khóa yếu? `len(set(generate_keys(key))) < 3` | `False`. Khóa `11110000` → `True` |

Dòng `weak` đọc thế nào: `generate_keys(key)` ra 3 chìa; `set(...)` bỏ các chìa trùng nhau; `len(...)` đếm còn mấy chìa khác nhau. Còn ít hơn 3 nghĩa là có chìa trùng → khóa yếu.

Hàm trả về `jsonify(ok=True, cipher_hex=..., n_bytes=..., n_plain=..., bob_text=..., elapsed=..., weak=...)`.
Nhập sai (khóa sai định dạng, tin rỗng) thì `except ValueError` trả `{"ok": false, "error": "..."}` kèm mã lỗi `400`, trang chat hiện chữ đỏ.

### `chat_attack()`: kẻ xấu vét cạn (`app.py:695`)

| Biến | Là gì | Ví dụ |
|---|---|---|
| `cipher` | bản mã kẻ xấu chặn được, đổi từ chuỗi hex ra bytes (`bytes.fromhex`) | `43 61 DA DA C0` |
| `key` | khóa thật, **chỉ dùng để kiểm chứng** “đoán đúng chưa”, không dùng để tìm | `"11011010"` |
| `top` | (TinyDES) 3 ứng viên điểm “giống chữ” cao nhất từ `brute_force_ciphertext_only` | `[{"key": "11011010", "score": …}, …]` |
| `guess` | ứng viên đứng đầu = khóa kẻ xấu đoán | `top[0]` |
| `success` | đoán đúng khóa thật chưa | `True` |
| `first` | (DES) 8 byte đầu của bản mã, đủ để thử | |
| `k` | (DES) khóa đang thử: số `0, 1, 2, …, 1999`; `k.to_bytes(8, "big")` đổi số ra 8 byte | |
| `per_sec` | (DES) tốc độ: số khóa thử được mỗi giây = `DES_TRY / giây đã chạy` | khoảng 7.600 (tùy máy) |
| `years` | (DES) thử hết 2⁵⁶ khóa mất bao nhiêu năm = `2**56 / per_sec / (3600*24*365)` | khoảng 300.000 năm |

### `chat_tamper()`: kẻ xấu sửa tin (`app.py:734`)

| Biến | Là gì | Ví dụ |
|---|---|---|
| `cipher` | bản mã dạng `bytearray`: **sửa được từng byte** (bytes thường thì không sửa được) | |
| `index` | sửa byte thứ mấy; `% len(cipher)` để số quá lớn thì quay vòng | `0` (byte đầu) |
| `cipher[index] ^= 0x01` | XOR với `00000001`: **đổi đúng bit cuối** của byte đó, 0 thành 1, 1 thành 0 | `43` → `42` |
| `bob` | Bình giải mã bản đã sửa | TinyDES: chỉ chữ đầu hỏng |
| `bob_error` | (DES) lỗi khi bỏ đệm nếu hỏng trúng khối cuối | `"Padding sai - …"` |

Vì sao TinyDES chỉ hỏng 1 chữ mà DES hỏng cả khối 8 byte? TinyDES mã **từng byte riêng**. DES trộn **cả 64 bit** của khối với nhau, đổi 1 bit vào là khoảng một nửa số bit ra bị đổi.

---

## V19. Phòng chat: phía trình duyệt (`static/chat.js`)

File này **chỉ vẽ giao diện**, không mã hóa gì. Mọi thứ bọc trong `(function () { ... })();` để các biến không lẫn với trang khác.

### Biến dùng chung

| Biến | Là gì | Ví dụ |
|---|---|---|
| `DEFAULT_KEY` | khóa mẫu cho mỗi thuật toán (điền tự động khi đổi thuật toán) | `{tinydes: "11011010", des: "nhom2026"}` |
| `NAME` | tên hiển thị | `{tinydes: "TinyDES", des: "DES"}` |
| `packets` | danh sách mọi gói tin đã gửi, mỗi gói `{n, algo, key, text, hex}` | gói #1: `{n: 1, algo: "tinydes", hex: "43 56 36 …"}` |
| `lastText` | tin An gửi gần nhất, cho nút “Gửi lại tin vừa rồi” | `"Hẹn gặp ở cổng trường lúc 8h tối"` |

### Các hàm, theo thứ tự chạy khi An bấm gửi

| Hàm | Làm gì |
|---|---|
| `$(id)` | lấy thẻ HTML theo id. `$("anText")` = ô gõ tin của An |
| `algo()` | đọc đang chọn TinyDES hay DES |
| `api(path, body)` | gửi JSON lên server bằng `fetch`, nhận JSON về. Server báo `ok: false` thì ném lỗi để hiện chữ đỏ |
| `send(text)` | gọi `/api/chat/send`, rồi gọi 3 hàm vẽ dưới đây. So `hex` với các gói cũ: trùng thì đánh dấu `dup` (tin lặp lại) |
| `addAn(p, d)` | vẽ bong bóng xanh bên An: tin gốc + dòng nhỏ “🔒 TinyDES · khóa … · … byte” |
| `addPacket(p, d, dup)` | vẽ gói tin ở đường truyền: các ô hex + 2 nút “Vét cạn khóa”, “Sửa 1 bit rồi chuyển” |
| `addBinh(text, meta, extra)` | vẽ bong bóng bên Bình; `extra = "tampered"` thì tô đỏ (tin bị sửa) |
| `attack(p, card, btn)` | gọi `/api/chat/attack`, viết kết quả ngay dưới gói tin |
| `tamper(p, card, btn)` | gọi `/api/chat/tamper`, vẽ bản mã đã sửa (byte bị đổi tô đỏ) và tin hỏng bên Bình |
| `el(tag, cls, text)` | tạo 1 thẻ HTML. Chữ đi qua `textContent`, nên chữ người dùng gõ **không bao giờ biến thành mã HTML** (an toàn) |
| `vn(n)`, `years(y)` | viết số kiểu Việt Nam: `300000` → `"300.000"`, `3e5` năm → `"300 nghìn năm"` |

Cuối file là các dòng `addEventListener`: **gắn việc cần làm vào nút**. Ví dụ `$("anForm").addEventListener("submit", ...)` nghĩa là “khi An bấm gửi thì chạy `send(...)`”.

---

## V20. Trang “📗 Đọc code cùng thuật toán” (`app.py:612-659`)

| Tên | Là gì |
|---|---|
| `source_of(fn)` | đọc **mã nguồn thật** của hàm `fn` bằng thư viện `inspect`, trả `{file, start, end, lines}`. Nhờ vậy trang luôn khớp với code, sửa code là trang tự đổi |
| `inspect.getsourcelines(fn)` | trả (danh sách dòng code, số dòng bắt đầu) |
| `os.path.relpath(...)` | đổi đường dẫn đầy đủ thành đường dẫn ngắn, VD `core/tinydes_core.py` |
| `funcs` | dict “tên hiển thị → hàm”, VD `"xor": tinydes_core.xor` |
| `src` | dict “tên → mã nguồn”, template in bằng macro `code(src.xor)` |
| `tr` | `tinydes_core.trace("01011100", "10011010")`: mọi thanh ghi TinyDES, dùng điền bảng “các hộp thay đổi thế nào” |
| `key_log`, `des_log` | nhật ký 16 chìa và 16 vòng DES từ `generate_subkeys` và `crypt_block_verbose` |
| `ex` | dict gom mọi giá trị ví dụ gửi sang `code_guide.html` |

## V21. Trang “🎬 Kịch bản & hướng dẫn” (`app.py:606`, `templates/guide.html`)

Hàm `guide()` chỉ có 1 dòng `return render("guide.html")`: trang **toàn chữ tĩnh**, không tính toán gì.
Muốn sửa lời thoại thì mở `templates/guide.html`, tìm đoạn `<blockquote class="say">` của cảnh cần sửa.

## V22. Xuất web tĩnh: `xuat_web_tinh.py` và `web_tinh_nguon/`

### Các tệp

| Tệp | Là gì |
|---|---|
| `xuat_web_tinh.py` | Script chạy 1 lần: biến web Flask thành 12 tệp HTML/CSS/JS trong `web_tinh/` |
| `web_tinh_nguon/crypto-local.js` | TinyDES + DES + đệm + chấm điểm vét cạn **viết lại bằng JavaScript**, thay cho 3 API của `app.py` |
| `web_tinh_nguon/tinydes-tung-buoc.html`, `des-tung-buoc.html` | 2 trang “từng bước” có màu (thành `tinydes.html`, `des.html`) |
| `web_tinh_nguon/ban-day-du.html` | Nội dung trang “Bản đầy đủ chạy trên máy” |
| `web_tinh/` | **Kết quả** (tự sinh ra, không sửa tay; sửa thì chạy lại script) |

### `xuat_web_tinh.py` chạy những gì

```
python xuat_web_tinh.py [--artifact]
│
├─ client = app.test_client()          "trình duyệt giả" của Flask: lấy HTML mà không cần bật server
├─ với mỗi trang trong PAGES (/, /huong-dan, /chat, /doc-code, /theory, /flow):
│     client.get(path) → fix_links() → fix_nav() → write("….html")
├─ chép style.css, crypto-local.js; chat.js: thay hàm api() bằng window.LOCAL_API
├─ 2 trang từng bước: thêm khung <html><head><body> + nút "← Mật thư An–Bình"
└─ ban-day-du.html: mượn khung trang hướng dẫn, thay phần <main>
```

| Biến / hàm | Là gì | Ví dụ |
|---|---|---|
| `ROOT`, `SRC`, `OUT` | thư mục đồ án / `web_tinh_nguon/` / `web_tinh/` | |
| `ARTIFACT` | `True` nếu gõ thêm `--artifact` (`sys.argv` = các chữ gõ sau tên file) | `False` |
| `PAGES` | trang Flask → tên tệp tĩnh | `"/chat": "chat.html"` |
| `OTHER` | trang dùng bản có sẵn | `"/sdes": "tinydes.html"` |
| `NEED_SERVER` | 4 trang cần Python, mọi link tới đó trỏ về `ban-day-du.html` | `["/bruteforce", …]` |
| `LINKS` | gộp 3 dict trên (`{**a, **b}`): đường dẫn → tên tệp | |
| `fix_links(html)` | đổi `href="/chat"` thành `href="chat.html"`, giữ phần `#…` | `/huong-dan#canh-3` → `huong-dan.html#canh-3` |
| `fix_nav(html)` | bỏ 4 mục menu cần server, thêm mục “Bản đầy đủ” | |
| `body_only(html)` | (chỉ khi `--artifact`) bỏ `<!doctype>`, `<html>`, `<head>`, `<body>` vì claude.ai tự bọc | |
| `write(name, text)` | ghi tệp; đổi ký tự `�` thành `&#xFFFD;` (claude.ai không nhận ký tự này ở dạng thô) | |

### `crypto-local.js`: “server bỏ túi” cho phòng chat

| Phần | Giống hàm Python nào |
|---|---|
| `genKeys`, `fF`, `encBlock`, `decBlock`, `tinyBytes` | `generate_keys`, `f_function`, `_encrypt_block`, `_decrypt_block`, `encrypt_bytes` |
| `readability` | `readability_score` (chấm điểm “giống chữ”) |
| `desKeys`, `desF`, `desBlock`, `pad`, `unpad`, `parseDesKey` | `generate_subkeys`, `feistel_f`, `crypt_block_verbose`, `pkcs7_pad`, `pkcs7_unpad`, `parse_des_key` |
| `cipherFor(algo, key)` | `chat_cipher` |
| `routes["/api/chat/send"]`, `["/api/chat/attack"]`, `["/api/chat/tamper"]` | `chat_send`, `chat_attack`, `chat_tamper` (trả dữ liệu y hệt) |
| `window.LOCAL_API(path, body)` | thay cho `fetch(path)` trong `chat.js` |

Đã đối chiếu: TinyDES “Hẹn gặp ở cổng trường lúc 8h tối”, khóa `11011010` → `43 56 36 88 FF 40 B2 …` và DES khóa `nhom2026` → `9F 49 28 9C D4 1E 76 76 …`, **khớp từng byte** với Python.
**Lưu ý:** sửa thuật toán trong `core/` thì phải sửa cả `crypto-local.js` cho khớp, vì đây là bản viết lại, không tự đổi theo.

---

# 🎓 TinyDES (slide trang 67 → 72): từng bước của thuật toán và code tương ứng

> Phần này bám theo slide **"3.2 – Mã khối / Hệ mã TinyDES"** (trang 67) và các trang tiếp theo
> (68: cấu trúc 1 vòng, 69–70: Expand / S-box / P-box, 71: sinh khóa con, 72: bài tập ví dụ).
> Mỗi bước có 3 phần: **(1) slide nói gì → (2) hiểu bằng lời thường + ví dụ → (3) code làm thế nào**.
> Code nằm trong `core/tinydes_core.py`. Mọi con số dưới đây đều lấy từ kết quả chạy thật của code
> (`python core/tinydes_core.py`), và trùng khớp từng bit với lời giải ở slide trang 72.

## Bước 0.1. Bắt đầu từ con số 0: vào gì, ra gì, mã là gì?

### Đầu vào (input) và đầu ra (output)

Bạn đưa vào **2 thứ**, mỗi thứ là một dãy **8 số 0/1**:

| Tên | Là gì | Ví dụ (slide 72) |
|---|---|---|
| **Bản rõ P** | Tin nhắn gốc mà bạn muốn giấu | `01011100` |
| **Khóa K** | "Mật khẩu" bí mật, chỉ người gửi và người nhận biết | `10011010` |

Bạn nhận lại **1 thứ**:

| Tên | Là gì | Ví dụ |
|---|---|---|
| **Bản mã C** | Tin nhắn đã bị xáo trộn, người ngoài nhìn vào không hiểu | `10010010` |

```
   P = 01011100  ──┐
                   ├──►  [ TinyDES MÃ HÓA ]  ──►  C = 10010010
   K = 10011010  ──┘
```

Trong code, cả quá trình trên là **1 dòng**:

```python
cipher, log = encrypt("01011100", "10011010")
# cipher = "10010010"                      ← bản mã
# log    = [ {...}, {...}, ... ]           ← nhật ký mọi bước trung gian (để in ra màn hình)
```

`encrypt` là **tên hàm** (một "cái máy" viết sẵn trong `core/tinydes_core.py:184`). Hai thứ trong ngoặc là **đầu vào**: bản rõ và khóa,
viết trong dấu `" "` vì code lưu bit dưới dạng **chuỗi ký tự** `'0'`/`'1'`. Hàm trả về **2 thứ**: bản mã và nhật ký các bước.

### Mấy chữ dễ nhầm

| Từ | Nghĩa |
|---|---|
| **Mã hóa** | Biến P thành C (giấu tin) |
| **Giải mã** | Biến C về lại P (đọc tin). Cần **đúng** khóa K |
| **Dịch vòng trái** | **Không phải** "dịch" như dịch tiếng Anh. Nghĩa là **xoay** các bit sang trái: bit đầu chạy ra cuối |
| **b0, b1, b2, b3** | **Không phải phép tính.** Chỉ là **tên của từng ô** (ô số 0, 1, 2, 3, đếm từ trái sang) |
| **⊕ (XOR)** | So từng cặp bit: giống nhau → 0, khác nhau → 1 |

Ví dụ dịch vòng trái 1 bit: `1001` → bit đầu `1` chạy ra cuối → `0011`.

Ví dụ tên ô, với dãy `1100`:

```
ô:     b0  b1  b2  b3
bit:    1   1   0   0
```

Nên b0 = 1, b1 = 1, b2 = 0, b3 = 0.
Khi slide viết "Expand cho ra **b2 b3 b1 b2 b1 b0**", nghĩa là: **lấy bit ở ô 2, rồi ô 3, rồi ô 1, rồi ô 2, rồi ô 1, rồi ô 0, xếp thành hàng**.

### Toàn bộ quá trình, từng bước: vào gì, ra gì

**BƯỚC 1: Từ khóa K làm ra 3 chìa nhỏ K1, K2, K3.** TinyDES chạy 3 vòng, mỗi vòng cần 1 chìa riêng dài 6 bit.

**Vào:** K = `10011010` → **Ra:** K1 = `101110`, K2 = `110011`, K3 = `001001`

```
① Cắt đôi khóa:        1001 | 1010          (trái KL | phải KR)

② Xoay trái 1 bit:      0011 | 0101          (mỗi nửa xoay riêng)
③ Chọn 6 trong 8 bit theo thứ tự ô 5,1,3,2,7,0:

   ô:   0 1 2 3 4 5 6 7
   bit: 0 0 1 1 0 1 0 1
   ô5=1, ô1=0, ô3=1, ô2=1, ô7=1, ô0=0   →  K1 = 101110

④ Xoay tiếp 2 bit:      1100 | 0101   → chọn 6 bit →  K2 = 110011
⑤ Xoay tiếp 1 bit:      1001 | 1010   → chọn 6 bit →  K3 = 001001
```


Code: `generate_keys("10011010")` trả về `("101110", "110011", "001001")`.

**BƯỚC 2: Cắt bản rõ P làm đôi.**

**Vào:** P = `01011100` → **Ra:** L0 = `0101` (trái), R0 = `1100` (phải)

Code: `left, right = bits8[:4], bits8[4:]`

**BƯỚC 3: Vòng 1 (dùng chìa K1 = `101110`).** Mỗi vòng làm đúng 6 việc nhỏ. Các việc a–d gọi chung là **hàm F**:

| Việc | Vào | Làm gì | Ra |
|---|---|---|---|
| a. **Expand** (kéo dài) | R0 = `1100` | Lấy ô 2,3,1,2,1,0 → `0 0 1 0 1 1` | `001011` (6 bit) |
| b. **XOR với chìa** | `001011` và K1 `101110` | So từng cặp: giống → 0, khác → 1 | `100101` |
| c. **S-box** (tra bảng) | `100101` | Hàng = bit đầu + bit cuối = `11` = 3. Cột = 4 bit giữa = `0010` = 2. Bảng hàng 3 cột 2 là số 8 | `1000` (4 bit) |
| d. **P-box** (xếp lại) | `1000` | Lấy ô 2,0,3,1 → `0 1 0 0` | **F = `0100`** |
| e. **Nửa phải mới** | L0 `0101` và F `0100` | XOR | R1 = `0001` |
| f. **Nửa trái mới** | R0 `1100` | Chép y nguyên | L1 = `1100` |

**Kết quả vòng 1:** `0101 1100` → **`1100 0001`**

Việc b viết rõ ra:

```
  0 0 1 0 1 1
⊕ 1 0 1 1 1 0
= 1 0 0 1 0 1
```

**BƯỚC 4: Vòng 2 và vòng 3.** Lặp y hệt bước 3, chỉ đổi chìa: vòng 2 dùng K2, vòng 3 dùng K3. **Đầu ra vòng trước là đầu vào vòng sau.**

| | Vào (L R) | F | Ra (L R) |
|---|---|---|---|
| Vòng 1 (K1) | `0101 1100` | `0100` | `1100 0001` |
| Vòng 2 (K2) | `1100 0001` | `0101` | `0001 1001` |
| Vòng 3 (K3) | `0001 1001` | `0011` | **`1001 0010`** |

**BƯỚC 5: Kết quả.** Ghép L3 và R3: **C = `10010010`** (hệ 16 là `92`). Đây là **bản mã**, đúng đáp án slide 72.

**Giải mã: người nhận làm ngược lại.**
**Vào:** C = `10010010` + cùng khóa K = `10011010` → **Ra:** P = `01011100` (lấy lại đúng tin gốc).
Chạy lại 3 vòng nhưng **từ vòng 3 về vòng 1**, dùng chìa theo thứ tự **K3 → K2 → K1**:

```
1001 0010  →(K3)→  0001 1001  →(K2)→  1100 0001  →(K1)→  0101 1100 ✔
```

Đây chính là bảng ở bước 4 đi **từ dưới lên**. Code: `plain, log = decrypt("10010010", "10011010")` cho `plain = "01011100"`.

**Tóm gọn trong 1 hình:**

```
K = 10011010 ──► [Bước 1: làm chìa] ──► K1=101110  K2=110011  K3=001001
                                            │          │          │
P = 0101 1100 ──► [Vòng 1] ─────────────────┘          │          │
                     ▼ 1100 0001                       │          │
                  [Vòng 2] ────────────────────────────┘          │
                     ▼ 0001 1001                                  │
                  [Vòng 3] ───────────────────────────────────────┘
                     ▼
              C = 1001 0010   (bản mã)
```

Tự chạy để xem máy in đúng các bước trên: `python core/tinydes_core.py`. Khi chương trình hỏi bản rõ và khóa, nhấn Enter 2 lần là dùng ví dụ này.

---

## Bước 0.2. Tin nhắn dạng chữ thì biến thành bit thế nào?

Máy tính không hiểu chữ, nó chỉ hiểu 0 và 1. Vì vậy trước khi mã hóa phải **đổi chữ thành bit**, sau khi giải mã thì **đổi bit về lại chữ**.
Ví dụ: tin nhắn **"Hello"**, khóa K = `10011010`. Mọi số đều lấy từ kết quả chạy thật.

### ① Mỗi chữ cái có một "số thứ tự" cố định

Thế giới đã thống nhất một bảng tên là **ASCII** (tiếng Việt có dấu thì dùng bảng mở rộng **UTF-8**). Bảng này gán cho mỗi chữ một con số, giống số báo danh:

| Chữ | Số thứ tự (thập phân) | Viết hệ 16 | Viết thành 8 bit |
|---|---|---|---|
| H | 72 | 48 | `01001000` |
| e | 101 | 65 | `01100101` |
| l | 108 | 6C | `01101100` |
| l | 108 | 6C | `01101100` |
| o | 111 | 6F | `01101111` |

Một chữ cái thường là **1 byte = 8 bit**, vừa khít với **1 khối TinyDES (8 bit)**. Đây là lý do TinyDES mã hóa được văn bản.

Số 72 thành 8 bit vì 72 = 64 + 8, nên ta bật ô 64 và ô 8:

```
giá trị ô:  128  64  32  16   8   4   2   1
bit:          0   1   0   0   1   0   0   0     → 01001000
```

### ② Mã hóa từng chữ một (mỗi chữ = 1 khối 8 bit)

Mỗi khối 8 bit đi qua **đúng 3 vòng TinyDES** ở Bước 0.1, với cùng khóa K:

```
"H" → 01001000 ──TinyDES──► 01100111  (67)
"e" → 01100101 ──TinyDES──► 10110011  (B3)
"l" → 01101100 ──TinyDES──► 00100000  (20)
"l" → 01101100 ──TinyDES──► 00100000  (20)
"o" → 01101111 ──TinyDES──► 10100010  (A2)
```

**Bản mã gửi đi:** `67 B3 20 20 A2`. Người ngoài chặn được dãy này cũng không biết đó là "Hello".

### ③ Người nhận giải mã rồi đổi về chữ

```
67 → giải mã → 01001000 = 72  → "H"
B3 → giải mã → 01100101 = 101 → "e"
...
→ "Hello" ✔
```

Nếu dùng **sai khóa**, ví dụ chỉ sai 1 bit (`10011011`), giải mã ra toàn ký tự rác: `97 BA 50 50 20` → `"\x97\xbaPP "`, không đọc được.

### Trong code làm thế nào?

**Đổi chữ thành byte** (`app.py:111`):

```python
data = raw.encode("utf-8")      # "Hello" → b'Hello' = các số [72, 101, 108, 108, 111]
```

**Mã hóa từng byte** (`core/tinydes_core.py:230`):

```python
return bytes(int(_encrypt_block(format(b, "08b"), keys), 2) for b in data)
```

Đọc từ trong ra ngoài, với mỗi byte `b` trong `data`:

| Đoạn code | Làm gì | Ví dụ với chữ "H" |
|---|---|---|
| `format(b, "08b")` | Đổi số thành chuỗi 8 bit | 72 → `"01001000"` |
| `_encrypt_block(...)` | Chạy 3 vòng TinyDES | → `"01100111"` |
| `int(..., 2)` | Đổi chuỗi bit về số | → 103 (= 67 hệ 16) |
| `bytes(...)` | Gom tất cả các số thành dãy byte | → `67 B3 20 20 A2` |

**Giải mã rồi đổi về chữ:**

```python
decrypt_bytes(cipher, key)          # → b'Hello'
b'Hello'.decode("utf-8")            # → "Hello"
```

### 2 điểm thầy hay hỏi

**1. Tiếng Việt có dấu thì sao?** Chữ có dấu chiếm **nhiều byte**. "Hẹn" có 3 chữ nhưng thành **5 byte**:

```
H  → 48
ẹ  → E1 BA B9      (1 chữ, 3 byte)
n  → 6E
```

Code vẫn mã hóa bình thường, vì nó chỉ coi đó là 5 khối 8 bit và mã từng khối: bản mã `67 18 B0 35 49`.

**2. Điểm yếu: chữ giống nhau thì ra bản mã giống nhau.** Hai chữ "l" trong "Hello" đều thành `20`.
Kẻ tấn công nhìn `67 B3 20 20 A2` đoán được "chữ thứ 3 và thứ 4 giống nhau". Kiểu mã từng khối riêng lẻ như vậy gọi là chế độ **ECB**.

**Tóm lại cả quá trình:**

```
"Hello" ─encode─► 48 65 6C 6C 6F ─TinyDES từng byte─► 67 B3 20 20 A2   (gửi đi)
                                                            │
"Hello" ◄─decode─ 48 65 6C 6C 6F ◄─giải mã từng byte────────┘   (người nhận)
```

---

## Bước 0.3. Khóa K do ai chọn?

**Khóa K do bạn tự chọn.** Thuật toán không quy định khóa phải là số nào, nó chỉ yêu cầu khóa là **đúng 8 bit, mỗi bit là 0 hoặc 1**.

- Chọn dãy 8 bit nào cũng được: `10011010`, `11011010`, `00110101`…
- Có tổng cộng 2⁸ = **256 khóa** khác nhau, từ `00000000` đến `11111111`.
- `10011010` chỉ là khóa **thầy chọn để làm ví dụ** ở slide 72, không có gì đặc biệt.

**Quy tắc duy nhất:** người gửi và người nhận phải **dùng cùng một khóa** và **giữ bí mật** khóa đó.
Đó là lý do chương này tên là "mã hóa **khóa đối xứng**": hai bên dùng chung một chìa.

```
Người gửi (A)                                   Người nhận (B)
"Hello" + K=10011010 → 67 B3 20 20 A2 ──gửi──►  67 B3 20 20 A2 + K=10011010 → "Hello"
                              ▲
                     kẻ xấu chặn được, nhưng không có K → không đọc được
```

### Đổi khóa thì bản mã đổi theo

Cùng bản rõ, khác khóa thì ra bản mã khác hẳn (kết quả chạy thật):

| Khóa K | K1, K2, K3 | Mã `01011100` | Mã "Hello" |
|---|---|---|---|
| `10011010` | 101110, 110011, 001001 | `10010010` | `67 B3 20 20 A2` |
| `11110000` | 011101, 011101, 011101 | `01101110` | `6A 0D D1 D1 13` |
| `00000001` | 000000, 000000, 000010 | `11110100` | `77 8F 7D 7D 52` |

### Trong code, khóa được nhập ở đâu?

Khóa là **đầu vào do người dùng gõ**, code không tự đặt khóa:

| Nơi chạy | Chỗ nhập khóa |
|---|---|
| Web (`python app.py`) | Ô nhập khóa trên trang TinyDES. Code đọc tại `app.py:352`: `key = request.form.get("sdes_key", "")` |
| Menu console (`python tinydes_menu.py`) | `tinydes_menu.py:26`: `input("Nhập Khóa K (8-bit nhị phân): ")` |
| `python cli.py` hoặc `python core/tinydes_core.py` | Chương trình hỏi khóa. Nhấn Enter không gõ gì thì dùng mặc định `10011010` (lấy từ slide) |

Sau đó code kiểm tra khóa hợp lệ (`core/tinydes_core.py:105`):

```python
if not is_bits(key_8bit, 8):
    raise ValueError("Khóa TinyDES phải là chuỗi 8 bit (0/1).")
```

- Gõ `1001` (thiếu bit) → báo lỗi.
- Gõ `1001101a` (có chữ "a") → báo lỗi.
- Gõ `11001100` → hợp lệ, chạy bình thường.

### Mẹo khi thuyết trình: tránh "khóa yếu"

Không phải khóa nào cũng tốt. Nhìn bảng trên:
- Khóa `11110000` sinh ra **3 khóa con giống hệt nhau** (`011101`).
- Khóa `00000001` sinh ra 2 khóa con toàn số 0.

Những khóa như vậy gọi là **khóa yếu**: các vòng không được trộn khác nhau, nên dễ phá hơn. Nên chọn khóa có 0 và 1 lẫn lộn, ví dụ `10011010`, `11011010`.

Dù chọn khóa nào, TinyDES cũng chỉ có 256 khả năng. Kẻ tấn công **thử hết 256 khóa** trong chưa tới 1 giây (xem phần 🔓 Bẻ khóa bên dưới).

---

## Bước 0.4. 🗺️ Sơ đồ từng bước, từng hàm (ví dụ P = `01011100`, K = `10011010`)

> Đọc sơ đồ: **hộp** `┌─┐` là một hàm, **mũi tên** `▼ ►` là dữ liệu chạy từ hàm này sang hàm khác,
> chữ cạnh mũi tên là **giá trị thật** lúc chạy ví dụ slide 72.

### Sơ đồ 1. Từ lúc bấm nút đến lúc thấy kết quả

```
 ┌───────────────────────────────────────┐
 │ ① TRÌNH DUYỆT   (templates/sdes.html)  │  Bạn gõ: Khóa = 10011010
 │                                       │          Bản rõ = 01011100
 │                                       │  rồi bấm [ Mã hóa ]
 └───────────────────┬───────────────────┘
                     │  gửi 2 ô vừa gõ lên server
                     ▼
 ┌───────────────────────────────────────┐
 │ ② app.py : sdes_demo()                 │  key = "10011010"
 │    (bồi bàn: nhận order, không tự nấu) │  blk = "01011100"
 └───────────────────┬───────────────────┘
                     │  out, log = encrypt("01011100", "10011010")
                     ▼
 ┌───────────────────────────────────────┐
 │ ③ core/tinydes_core.py : encrypt()     │  ← "đầu bếp": làm mã hóa thật sự
 │    (chi tiết ở Sơ đồ 2)                │
 └───────────────────┬───────────────────┘
                     │  trả về ("10010010", log)
                     ▼
 ┌───────────────────────────────────────┐
 │ ④ app.py : render("sdes.html", ...)    │  nhét kết quả vào trang web
 └───────────────────┬───────────────────┘
                     ▼
 ┌───────────────────────────────────────┐
 │ ⑤ TRÌNH DUYỆT hiện:                    │  Bản mã: 10010010
 │                                       │  + bảng từng bước (vẽ từ log)
 └───────────────────────────────────────┘
```

### Sơ đồ 2. Bên trong `encrypt()`: gọi những hàm nào, theo thứ tự nào

```
encrypt("01011100", "10011010")                            core/tinydes_core.py:184
│
├─① is_bits("01011100", 8) ──► True  (sai thì báo lỗi, dừng luôn)
│
├─② generate_keys("10011010") ─────────────────────────► ("101110", "110011", "001001")
│     ├─ left_shift()   xoay vòng                                    K1        K2        K3
│     └─ permute(…, COMPRESS)  nén 8 → 6 bit                         (Sơ đồ 3)
│
├─③ _encrypt_block("01011100", (K1, K2, K3)) ───────────► "10010010"
│     │                                                              (Sơ đồ 4)
│     ├─ vòng 1: f_function(R0, K1) ──► F1 ;  xor(L0, F1)
│     ├─ vòng 2: f_function(R1, K2) ──► F2 ;  xor(L1, F2)
│     └─ vòng 3: f_function(R2, K3) ──► F3 ;  xor(L2, F3)
│                  │
│                  └─ f_function bên trong gọi (Sơ đồ 5):
│                       permute(…, EXPAND) → xor(…, K) → sbox_lookup(…) → permute(…, PBOX)
│
└─④ return ("10010010", log)
```

**Cách nhớ:** chỉ có **3 hàm "dụng cụ"** là `permute`, `left_shift`, `xor` và **1 hàm tra bảng** `sbox_lookup`.
Mọi hàm khác chỉ là **gọi các dụng cụ đó theo đúng thứ tự** của slide.

### Sơ đồ 3. `generate_keys()`: làm 3 chìa khóa con

```
                    key_8bit = "10011010"
                            │
                  ┌─────────┴─────────┐   key[:4]  |  key[4:]
                  ▼                   ▼
             kl = "1001"         kr = "1010"                 KL0 | KR0
                  │                   │
   ╔══ VÒNG 1 ════╪═══════════════════╪════════════════════════════════╗
   ║   left_shift(kl, 1)       left_shift(kr, 1)      xoay trái 1 bit  ║
   ║              ▼                   ▼                                 ║
   ║         kl = "0011"         kr = "0101"                            ║
   ║              └─────────┬─────────┘                                 ║
   ║                        ▼  ghép: "00110101"                         ║
   ║              permute("00110101", COMPRESS)   lấy ô 5,1,3,2,7,0     ║
   ║                        ▼                                           ║
   ║                  K1 = "101110"  ────────────────────► dùng ở vòng 1║
   ╚════════════════════════════════════════════════════════════════════╝
                  │ (kl, kr giữ lại, xoay TIẾP)
   ╔══ VÒNG 2 ════╪════════════════════════════════════════════════════╗
   ║   left_shift(…, 2) → kl = "1100", kr = "0101" → K2 = "110011"      ║
   ╚════════════════════════════════════════════════════════════════════╝
                  │
   ╔══ VÒNG 3 ════╪════════════════════════════════════════════════════╗
   ║   left_shift(…, 1) → kl = "1001", kr = "1010" → K3 = "001001"      ║
   ╚════════════════════════════════════════════════════════════════════╝
                  │
                  ▼
     return ("101110", "110011", "001001")
```

### Sơ đồ 4. `_encrypt_block()`: 3 vòng Feistel (hình chữ X giống slide 68)

```
                 bits8 = "01011100"
                         │
             ┌───────────┴───────────┐    bits8[:4] | bits8[4:]
             ▼                       ▼
        L0 = "0101"             R0 = "1100"
             │                       │
             │              ┌────────┴──────────────┐
             │              ▼                       │
             │   ┌────────────────────┐             │
             │   │ f_function(R0, K1) │ ◄── K1 = "101110"
             │   └─────────┬──────────┘             │
             │             │ F1 = "0100"            │  R0 đi thẳng,
             ▼             ▼                        │  KHÔNG bị đổi
        ┌──────────────────────┐                    │
        │ xor(L0, F1)          │                    │
        │ "0101" ⊕ "0100"      │                    │
        └──────────┬───────────┘                    │
                   │ "0001"                         │
                   └──────────╲      ╱──────────────┘
                               ╲    ╱       ← ĐỔI CHỖ (hình chữ X)
                                ╲  ╱
                                 ╳
                                ╱  ╲
                   ┌───────────╱    ╲─────────────┐
                   ▼                              ▼
              L1 = "1100"                    R1 = "0001"
                   │                              │
       ════════ VÒNG 2 (K2 = "110011") ═══════ giống hệt ══════
                   ▼                              ▼
              L2 = "0001"                    R2 = "1001"
                   │                              │
       ════════ VÒNG 3 (K3 = "001001") ═══════ giống hệt ══════
                   ▼                              ▼
              L3 = "1001"                    R3 = "0010"
                   └──────────────┬───────────────┘
                                  ▼  ghép L3 + R3
                        return "10010010"   ← BẢN MÃ
```

Trong code, cả hình chữ X trên chỉ là **1 dòng**:

```python
left, right = right, xor(left, f)
#  L mới = R cũ ;  R mới = L cũ ⊕ F
```

### Sơ đồ 5. `f_function()`: cái "máy xay" F (khung nét đứt ở slide 68)

```
        half4 = R0 = "1100"   (4 bit)
                  │
                  ▼
   ┌──────────────────────────────┐
   │ ① permute(half4, EXPAND)     │   lấy ô 2,3,1,2,1,0
   └──────────────┬───────────────┘
                  │ "001011"   (6 bit)
                  ▼
   ┌──────────────────────────────┐
   │ ② xor(…, subkey)             │ ◄──── K1 = "101110"
   └──────────────┬───────────────┘
                  │ "100101"   (6 bit)
                  ▼
   ┌──────────────────────────────┐
   │ ③ sbox_lookup(…)             │   hàng 3, cột 2 → số 8
   └──────────────┬───────────────┘
                  │ "1000"     (4 bit)
                  ▼
   ┌──────────────────────────────┐
   │ ④ permute(…, PBOX)           │   lấy ô 2,0,3,1
   └──────────────┬───────────────┘
                  │
                  ▼
           return F = "0100"   (4 bit)
```

### Sơ đồ 6. Từng "dụng cụ" làm gì (nhìn từng ô bit)

**`permute(bits, table)`**: lấy bit theo thứ tự ô ghi trong bảng. Ví dụ Expand `permute("1100", [2,3,1,2,1,0])`:

```
  ô:        0    1    2    3
  bits:   [ 1 ][ 1 ][ 0 ][ 0 ]
             │    │    │    │
  EXPAND:    │    │    │    │
   lấy ô 2 ──┼────┼────┘    │        → 0
   lấy ô 3 ──┼────┼─────────┘        → 0
   lấy ô 1 ──┼────┘                  → 1
   lấy ô 2 ──┼──── (ô 2 lần nữa)     → 0
   lấy ô 1 ──┼──── (ô 1 lần nữa)     → 1
   lấy ô 0 ──┘                       → 1
                                     ─────
  kết quả:                           "001011"
```

P-box và Compress dùng **đúng hàm này**, chỉ thay bảng: `PBOX = [2,0,3,1]`, `COMPRESS = [5,1,3,2,7,0]`.

**`left_shift(bits, n)`**: xoay vòng trái. Ví dụ `left_shift("1001", 1)`:

```
   [ 1 ][ 0 ][ 0 ][ 1 ]
     │    ◄────────────    cả dãy dịch sang trái 1 ô
     └──────────────────►  ô đầu chạy ra cuối
   [ 0 ][ 0 ][ 1 ][ 1 ]    = "0011"

   code:  bits[1:] + bits[:1]  =  "001" + "1"  =  "0011"
```

**`xor(a, b)`**: so từng cặp cùng vị trí. Ví dụ `xor("001011", "101110")`:

```
   a:   0   0   1   0   1   1
   b:   1   0   1   1   1   0
        │   │   │   │   │   │
      khác giống giống khác giống khác
        ▼   ▼   ▼   ▼   ▼   ▼
        1   0   0   1   0   1     = "100101"
```

**`sbox_lookup(bits6)`**: tra bảng. Ví dụ `sbox_lookup("100101")`:

```
   [ 1 ][ 0  0  1  0 ][ 1 ]
     │   └────┬─────┘   │
     │        │         │
     └────┬───┼─────────┘
          ▼   ▼
   hàng = "11" = 3      cột = "0010" = 2
          │                  │
          └────────┬─────────┘
                   ▼
       SBOX[3][2] = 8  →  format(8, "04b")  →  "1000"

   Bảng SBOX (slide 70):    cột: 0 1 2 3 ...
                    hàng 0:      E 4 D 1 ...
                    hàng 1:      0 F 7 4 ...
                    hàng 2:      4 1 E 8 ...
                    hàng 3:      F C [8] 2 ...   ← hàng 3, cột 2
```

### Sơ đồ 7. `decrypt()`: đi ngược, chìa dùng ngược

```
decrypt("10010010", "10011010")
│
├─ generate_keys("10011010") ──► (K1, K2, K3)   ← sinh Y HỆT lúc mã hóa
│
└─ _decrypt_block("10010010", keys)
        │
        L3 = "1001"   R3 = "0010"
        │
        ├─ vòng 3 (dùng K3): F = f_function(L3, K3) = "0011"
        │        L2 = xor(R3, F) = "0001"     R2 = L3 = "1001"
        │
        ├─ vòng 2 (dùng K2): F = f_function(L2, K2) = "0101"
        │        L1 = xor(R2, F) = "1100"     R1 = L2 = "0001"
        │
        ├─ vòng 1 (dùng K1): F = f_function(L1, K1) = "0100"
        │        L0 = xor(R1, F) = "0101"     R0 = L1 = "1100"
        │
        └─ return "01011100"   ← BẢN RÕ ban đầu ✔

So với mã hóa:   mã hóa  K1 → K2 → K3 ,  F tính trên R
                 giải mã K3 → K2 → K1 ,  F tính trên L  (vì L bây giờ chính là R cũ)
                 Giá trị F mỗi vòng GIỐNG HỆT lúc mã hóa → XOR lần 2 thì triệt tiêu.
```

### Sơ đồ 8. `encrypt_bytes()`: mã hóa cả câu chữ

```
   "Hello"
      │  .encode("utf-8")
      ▼
   [ 72 ][ 101 ][ 108 ][ 108 ][ 111 ]          5 số, mỗi số = 1 byte
      │     │      │      │      │
      │  format(b, "08b")   (số → 8 bit)
      ▼     ▼      ▼      ▼      ▼
  "01001000" "01100101" "01101100" "01101100" "01101111"
      │     │      │      │      │
      │  _encrypt_block(…, keys)   ← mỗi byte chạy riêng 3 vòng (Sơ đồ 4)
      ▼     ▼      ▼      ▼      ▼
  "01100111" "10110011" "00100000" "00100000" "10100010"
      │     │      │      │      │
      │  int(…, 2)   (8 bit → số)
      ▼     ▼      ▼      ▼      ▼
   [ 0x67 ][ 0xB3 ][ 0x20 ][ 0x20 ][ 0xA2 ]
      │
      ▼  bytes(...)
   bản mã: 67 B3 20 20 A2
```

### Sơ đồ 9. `brute_force()`: thử hết 256 khóa

```
   Kẻ tấn công biết:  bản rõ "Hello"  và  bản mã 43 61 DA DA C0
                              │
          ┌───────────────────┴───────────────────┐
          │  for key in all_keys():               │  "00000000" → "11111111"
          │      thử = encrypt_bytes("Hello", key) │
          │      thử == bản mã ?                   │
          └───────────────────┬───────────────────┘
                              │
     key = 00000000 → 74 80 7E 7E 57   ✘
     key = 00000001 → 77 8F 7D 7D 52   ✘
     ...
     key = 11011010 → 43 61 DA DA C0   ✔ ──► found.append("11011010")
     ...
     key = 11111111 → ...              ✘
                              │
                              ▼
               return ["11011010"]     (mất khoảng 0,03 giây)
```

### Sơ đồ 10. DES: cùng khuôn, chỉ to hơn (chi tiết ở phần 🎓 DES bên dưới)

```
utils.des_encrypt_bytes("Xin chào".encode(), key)              core/utils.py:97
│
├─ pkcs7_pad(data)            9 byte → 16 byte  (thêm 07 × 7)
│
├─ des_core.generate_subkeys(key)  ─────────────► [K1 … K16]   (mỗi chìa 48 bit)
│     ├─ permute(k64, PC1)   64 → 56
│     ├─ 16 lần: rotl(c), rotl(d)     xoay vòng
│     └─          permute(c‖d, PC2)   56 → 48
│
└─ _crypt_blocks(data, subkeys)
      └─ với mỗi khối 8 byte:  crypt_block_fast(...)
            ├─ IP                         64 → 64
            ├─ 16 vòng:  left, right = right, left ^ F(right, Ki)
            │               F = E (32→48) → ⊕Ki → 8 S-box (48→32) → P
            └─ IP⁻¹ (R16‖L16)             64 → 64
│
└─► bản mã EA 63 45 B5 94 48 F3 27 | 3B 7B 89 A3 C7 95 E4 14
```

So sánh nhanh 2 sơ đồ:

```
            TinyDES                              DES
   generate_keys  (3 chìa × 6 bit)      generate_subkeys (16 chìa × 48 bit)
   (không có)                           IP
   3 × [ f_function + xor ]             16 × [ feistel_f + ^ ]
   (không có)                           đổi chỗ + IP⁻¹
   ghép L3 + R3                         → bản mã
```

> Muốn xem sơ đồ **có màu, bấm được**, tính trực tiếp từ code: chạy `python app.py` rồi mở trang **🧭 Luồng chạy code** (`/flow`).

---

## T0. Trang 67 nói gì? Bức tranh tổng thể

Slide 67 nêu 4 tính chất:

| Tính chất (slide 67) | Ý nghĩa | Trong code |
|---|---|---|
| Thuộc **hệ mã Feistel**, gồm **3 vòng** | Dữ liệu được "nhào trộn" 3 lần, lần nào cũng theo cùng một khuôn | `ROUNDS = 3`, vòng `for` trong `_encrypt_block` |
| Kích thước **khối 8 bit** | Mỗi lần mã hóa đúng 8 bit (1 byte, ví dụ 1 chữ cái) | `is_bits(plain_8bit, 8)` |
| Kích thước **khóa 8 bit** | Khóa chỉ có 2⁸ = 256 khả năng, nên phá được bằng vét cạn | `is_bits(key_8bit, 8)`, `KEY_SPACE = 2 ** 8` |
| Mỗi vòng dùng **khóa con 6 bit** trích từ khóa chính | Từ 1 khóa 8 bit sinh ra 3 khóa con K1, K2, K3 | `generate_keys()` trả về `(K1, K2, K3)` |

Slide cũng chia TinyDES thành **2 phần**, và đó cũng chính là 2 phần lớn của code:

```
                 ┌──────────────── PHẦN A: CÁC VÒNG FEISTEL ────────────────┐
Bản rõ 8 bit ──► │ Vòng 1 ──► Vòng 2 ──► Vòng 3 │ ──► Bản mã 8 bit          ▲ _encrypt_block()
                 └────▲───────────▲──────────▲─────┘                         │ f_function()
                      │ K1 (6)    │ K2 (6)   │ K3 (6)
                 ┌────┴───────────┴──────────┴─────── PHẦN B: SINH KHÓA CON ─┐
Khóa 8 bit ────► │ Dịch vòng trái ─► Nén khóa (8→6)  × 3 lần                  │ generate_keys()
                 └────────────────────────────────────────────────────────────┘
```

**Đọc sơ đồ trang 67:** cột phải là "dây chuyền làm chìa khóa": khóa 8 bit → *dịch vòng trái* → vẫn 8 bit →
*nén khóa* → còn 6 bit → đưa vào vòng tương ứng. Kết quả dịch của vòng trước được dịch **tiếp** ở vòng sau
(mũi tên "8" đi xuống giữa các ô "Dịch vòng trái").

**So với DES thật:** TinyDES là DES "thu nhỏ": DES có 16 vòng, khối 64 bit, khóa 56 bit, khóa con 48 bit,
và thêm hoán vị khởi tạo/kết thúc. **TinyDES không có hoán vị khởi tạo/kết thúc** (code không có bảng IP).

### Quy ước đánh số bit (rất quan trọng)

Tài liệu đánh số bit **từ 0, từ trái sang phải**. Với chuỗi `"0110"`: b0 = 0, b1 = 1, b2 = 1, b3 = 0.
Python cũng đánh chỉ số chuỗi từ 0, nên **`bits[i]` chính là bᵢ**. Nhờ vậy các bảng trong code chép y hệt slide:

```python
EXPAND   = [2, 3, 1, 2, 1, 0]   # slide 69: b2 b3 b1 b2 b1 b0
PBOX     = [2, 0, 3, 1]         # slide 70: b2 b0 b3 b1
COMPRESS = [5, 1, 3, 2, 7, 0]   # slide 71: k5 k1 k3 k2 k7 k0
SHIFTS   = [1, 2, 1]            # slide 71: vòng 1 dịch 1, vòng 2 dịch 2, vòng 3 dịch 1
```

Code biểu diễn bit bằng **chuỗi ký tự `'0'`/`'1'`** (không dùng số nguyên) để in từng bước ra màn hình cho dễ theo dõi.

### 3 "dụng cụ" mà mọi bước đều dùng (`core/tinydes_core.py:44-70`)

| Hàm | Làm gì | Ví dụ |
|---|---|---|
| `permute(bits, table)` | Xếp lại bit theo bảng: bit thứ i của kết quả = `bits[table[i]]`. Dùng chung cho **Expand, P-box, Compress** | `permute("0110", EXPAND)` = `"101110"` |
| `left_shift(bits, n)` | Dịch vòng trái n bit: n bit đầu chạy ra cuối | `left_shift("1001", 1)` = `"0011"` |
| `xor(a, b)` | XOR từng cặp bit: giống → 0, khác → 1 | `xor("001011", "101110")` = `"100101"` |

```python
def permute(bits, table):
    return "".join(bits[i] for i in table)    # lấy lần lượt bits[2], bits[3], ... rồi nối lại
```

Một hàm `permute` dùng được cho cả 3 việc, vì **mở rộng** chỉ là hoán vị có **chỉ số lặp lại** (Expand lấy b1, b2 hai lần
nên 4 → 6 bit), còn **nén** là hoán vị **bỏ bớt chỉ số** (Compress không lấy k4, k6 nên 8 → 6 bit).

---

## T1. PHẦN B: Thuật toán sinh khóa con (slide 71) → `generate_keys()`

### Slide nói

1. Khóa K 8 bit chia đôi thành **KL₀** (4 bit trái) và **KR₀** (4 bit phải).
2. Vòng 1: KL₀, KR₀ **dịch vòng trái 1 bit** → KL₁, KR₁.
3. Vòng 2: KL₁, KR₁ **dịch vòng trái 2 bit** → KL₂, KR₂.
4. Vòng 3: KL₂, KR₂ **dịch vòng trái 1 bit** → KL₃, KR₃.
5. Khóa con Kᵢ = **Compress**(KLᵢ KRᵢ): ghép 8 bit k0…k7 rồi lấy **k5 k1 k3 k2 k7 k0** (6 bit).

### Hiểu bằng lời thường

Hình dung 2 chiếc vòng quay, mỗi vòng có 4 ghế. Mỗi vòng mã hóa, ta quay cả 2 chiếc (1, 2 rồi 1 nấc),
sau đó **chụp ảnh 6 trong 8 ghế theo thứ tự cố định** → được khóa con. Vì mỗi lần vị trí các bit khác nhau,
3 khóa con K1, K2, K3 khác nhau dù đều xuất phát từ cùng một khóa.

Để ý: tổng số bit dịch là 1 + 2 + 1 = **4 = độ dài mỗi nửa**, nên sau vòng 3 mỗi nửa **quay về đúng như ban đầu**
(KL₃KR₃ = 1001 1010 = khóa gốc). Đây là thiết kế giống DES (DES dịch tổng cộng 28 = độ dài mỗi nửa 28 bit).

### Ví dụ (khóa K = `10011010`, slide 72)

```
KL0 | KR0 = 1001 | 1010                          (chia đôi)

Vòng 1: dịch 1   KL1 | KR1 = 0011 | 0101
        ghép 8 bit:  k0 k1 k2 k3 k4 k5 k6 k7
                      0  0  1  1  0  1  0  1
        lấy k5 k1 k3 k2 k7 k0 = 1 0 1 1 1 0   →  K1 = 101110

Vòng 2: dịch 2   KL2 | KR2 = 1100 | 0101       →  K2 = 110011
Vòng 3: dịch 1   KL3 | KR3 = 1001 | 1010       →  K3 = 001001
```

### Code (`core/tinydes_core.py:95-118`)

```python
def generate_keys(key_8bit, log=None):
    if not is_bits(key_8bit, 8):                       # khóa phải đúng 8 ký tự 0/1
        raise ValueError(...)
    kl, kr = key_8bit[:4], key_8bit[4:]                # Bước 1: KL0 = "1001", KR0 = "1010"
    keys = []
    for i, s in enumerate(SHIFTS, start=1):            # i = 1,2,3 ; s = 1,2,1  (Bước 2,3,4)
        kl, kr = left_shift(kl, s), left_shift(kr, s)  # dịch TIẾP từ kết quả vòng trước
        k = permute(kl + kr, COMPRESS)                 # Bước 5: nén 8 → 6 bit
        keys.append(k)
    return tuple(keys)                                 # ("101110", "110011", "001001")
```

| Slide | Dòng code |
|---|---|
| Chia đôi K thành KL₀, KR₀ | `kl, kr = key_8bit[:4], key_8bit[4:]` |
| Dịch 1, 2, 1 bit ở vòng 1, 2, 3 | `SHIFTS = [1, 2, 1]` + `left_shift(kl, s)` |
| KLᵢ được dịch **từ KLᵢ₋₁** (không phải từ KL₀) | gán đè lại `kl, kr = ...` trong vòng lặp |
| Kᵢ = Compress(KLᵢKRᵢ) = k5 k1 k3 k2 k7 k0 | `permute(kl + kr, COMPRESS)` |

> ⚠️ Lỗi hay gặp khi tự làm tay: dịch vòng 2 **từ KL₀** thay vì từ KL₁. Code tránh lỗi này vì biến `kl` luôn giữ kết quả vòng trước.

---

## T2. PHẦN A: Một vòng Feistel (slide 68) → `_encrypt_block()`

### Slide nói

Mỗi vòng i nhận (Lᵢ₋₁, Rᵢ₋₁) 4 bit + 4 bit và tạo ra:

```
Lᵢ = Rᵢ₋₁
Rᵢ = Lᵢ₋₁ ⊕ F(Rᵢ₋₁, Kᵢ)        với   F(R, K) = P-box( S-box( Expand(R) ⊕ K ) )
```

Khung nét đứt trong hình trang 68 chính là hàm **F**: Expand (4→6) → ⊕ Kᵢ (6) → S-box (6→4) → P-box (4→4).

### Hiểu bằng lời thường

Hai người L và R chuyền bóng:
- **R** đi thẳng sang làm **L mới** (nguyên vẹn, không đổi gì).
- Đồng thời R được đưa vào "máy xay" F cùng với khóa con; kết quả F được **XOR vào L cũ** để thành **R mới**.

Mỗi vòng chỉ có **một nửa bị biến đổi**, nửa kia được giữ lại. Chính nửa giữ lại đó giúp giải mã được (xem T4).

### Code (`core/tinydes_core.py:156-167`)

```python
def _encrypt_block(bits8, keys, log=None):
    left, right = bits8[:4], bits8[4:]                 # L0, R0
    for i, k in enumerate(keys, start=1):              # vòng 1, 2, 3 với K1, K2, K3
        f = f_function(right, k, log, f"Vòng {i}")     # F(R_{i-1}, K_i)
        left, right = right, xor(left, f)              # L_i = R_{i-1} ;  R_i = L_{i-1} ⊕ F
    return left + right                                # C = L3 R3
```

Dòng `left, right = right, xor(left, f)` là **công thức Feistel viết trong 1 dòng**. Python tính hết vế phải
**trước** (dùng `left`, `right` cũ), rồi mới gán cùng lúc. Nếu viết 2 dòng `left = right` rồi `right = xor(left, f)`
thì sai, vì lúc đó `left` đã bị ghi đè.

---

## T3. Bên trong hàm F (slide 69–70) → `f_function()`

```python
def f_function(half4, subkey, log=None, tag=""):
    ex = permute(half4, EXPAND)       # ① Expand   4 → 6 bit
    x = xor(ex, subkey)               # ② ⊕ Kᵢ     6 bit
    s, row, col = sbox_lookup(x)      # ③ S-box    6 → 4 bit
    f = permute(s, PBOX)              # ④ P-box    4 → 4 bit
    return f
```

Dưới đây lấy đúng **vòng 1 của ví dụ**: R₀ = `1100`, K₁ = `101110`.

### ① Expand: 4 bit → 6 bit (slide 69)

Slide: R = b0b1b2b3 → **b2 b3 b1 b2 b1 b0**. Ví dụ trong slide: Expand(`0110`) = `101110`.

```
R0 = 1100   →  b0=1  b1=1  b2=0  b3=0
lấy:  b2 b3 b1 b2 b1 b0
       0  0  1  0  1  1      →  Expand(R0) = 001011
```

**Tại sao phải mở rộng?** Khóa con dài 6 bit, mà muốn XOR thì 2 bên phải cùng độ dài. Ngoài ra b1, b2 xuất hiện 2 lần,
nên 1 bit đầu vào ảnh hưởng tới nhiều vị trí đầu ra (hiệu ứng "lan truyền").

Code: `permute(half4, EXPAND)` với `EXPAND = [2, 3, 1, 2, 1, 0]`.

### ② XOR với khóa con

```
  Expand(R0) = 0 0 1 0 1 1
⊕ K1         = 1 0 1 1 1 0
= ─────────────────────────
               1 0 0 1 0 1      →  100101
```

Đây là **bước duy nhất khóa tham gia vào dữ liệu**. Không có khóa thì không tính được F.

Code: `xor(ex, subkey)`.

### ③ S-box: 6 bit → 4 bit (slide 69–70)

Slide: với 6 bit vào b0b1b2b3b4b5:
- **hàng** = 2 bit ngoài cùng **b0 b5** (0…3),
- **cột** = 4 bit giữa **b1 b2 b3 b4** (0…15),
- tra bảng 4 × 16 được 4 bit ra.

```
vào = 1 0 0 1 0 1
      ↑ └─────┘ ↑
      b0  giữa  b5
hàng = b0 b5      = "11"   = 3
cột  = b1 b2 b3 b4 = "0010" = 2
SBOX[3][2] = 8 = 1000      →  S-box = 1000
```

Kiểm tra với bảng hex ở slide 70: hàng 3, cột 2 là **8** ✔.
Ví dụ trong slide: S-box(`101010`): hàng `10` = 2, cột `0101` = 5 → **6** = `0110` ✔ (code ra `('0110', 2, 5)`).

**Tại sao S-box quan trọng nhất?** Expand, P-box, XOR đều là phép "tuyến tính", dễ lập phương trình giải ngược.
S-box là bảng tra **phi tuyến**, đầu vào chỉ đổi 1 bit thì đầu ra có thể đổi lung tung. Đây là nguồn gốc độ an toàn.

Code (`core/tinydes_core.py:124-133`):

```python
def sbox_lookup(bits6):
    row = int(bits6[0] + bits6[5], 2)    # "1"+"1" = "11" → đổi nhị phân sang số → 3
    col = int(bits6[1:5], 2)             # bits6[1:5] = "0010" (vị trí 1,2,3,4) → 2
    return format(SBOX[row][col], "04b"), row, col   # 8 → "1000"
```

- `int("11", 2)`: đọc chuỗi như số nhị phân → 3.
- `bits6[1:5]`: cắt từ vị trí 1 đến **trước** vị trí 5 → đúng b1 b2 b3 b4.
- `format(8, "04b")`: đổi số ra nhị phân đủ 4 chữ số → `"1000"`.
- Bảng `SBOX` trong code chép từ **bảng hex** slide 70 (`0xE, 0x4, 0xD, ...`), mỗi dòng là 1 hàng.

### ④ P-box: hoán vị 4 bit (slide 70)

Slide: b0b1b2b3 → **b2 b0 b3 b1**.

```
S-box = 1000  →  b0=1 b1=0 b2=0 b3=0
lấy b2 b0 b3 b1 = 0 1 0 0     →  F1 = 0100
```

P-box xáo trộn vị trí để bit ra của S-box không nằm yên chỗ cũ, sang vòng sau sẽ "đụng" các vị trí khác.

Code: `permute(s, PBOX)` với `PBOX = [2, 0, 3, 1]`.

### Kết thúc vòng 1

```
L1 = R0           = 1100
R1 = L0 ⊕ F1      = 0101 ⊕ 0100 = 0001
```

---

## T4. Chạy đủ 3 vòng: bài tập ví dụ slide 72 (P = `01011100` = 5C, K = `10011010`)

Bảng dưới là output thật của code (`trace()` + `print_trace()`), đặt cạnh lời giải trong slide:

| | Vòng 1 (K1 = 101110) | Vòng 2 (K2 = 110011) | Vòng 3 (K3 = 001001) |
|---|---|---|---|
| Đầu vào L R | 0101 1100 | 1100 0001 | 0001 1001 |
| Expand(R) | 001011 | 010000 | 010001 |
| ⊕ Kᵢ | 100101 | 100011 | 011000 |
| S-box (hàng, cột) | 1000 (3, 2) | 1100 (3, 1) | 0101 (0, 12) |
| P-box = F | 0100 | 0101 | 0011 |
| R mới = L ⊕ F | 0101⊕0100 = **0001** | 1100⊕0101 = **1001** | 0001⊕0011 = **0010** |
| Đầu ra L R | 1100 0001 | 0001 1001 | **1001 0010** |

➡️ **Bản mã C = L₃R₃ = `10010010` = 92 (hex)**, đúng như slide.

Tự kiểm tra bằng code:

```bash
python core/tinydes_core.py         # Enter 2 lần để dùng ví dụ mặc định
```

Đầu file có sẵn 3 dòng `assert` chép đúng đáp án slide 72. Nếu ai sửa sai bảng, chương trình dừng ngay:

```python
assert generate_keys("10011010") == ("101110", "110011", "001001")
assert encrypt("01011100", "10011010")[0] == "10010010"
assert decrypt("10010010", "10011010")[0] == "01011100"
```

---

## T5. Giải mã (slide 66) → `_decrypt_block()`

### Slide nói

Đi **ngược** các vòng, từ vòng 3 về vòng 1:

```
Rᵢ₋₁ = Lᵢ                       (vì khi mã hóa  Lᵢ = Rᵢ₋₁)
Lᵢ₋₁ = Rᵢ ⊕ F(Rᵢ₋₁, Kᵢ) = Rᵢ ⊕ F(Lᵢ, Kᵢ)
```

### Vì sao giải mã được, dù F không đảo ngược được?

Đây là "phép màu" của Feistel. Khi mã hóa: Rᵢ = Lᵢ₋₁ ⊕ F(Rᵢ₋₁). Khi giải mã, ta **có sẵn** Rᵢ₋₁ (nó chính là Lᵢ,
đã được chuyển nguyên vẹn), nên tính lại được **đúng giá trị F như lúc mã hóa**. XOR thêm F một lần nữa:

```
Rᵢ ⊕ F = (Lᵢ₋₁ ⊕ F) ⊕ F = Lᵢ₋₁         (XOR 2 lần cùng một giá trị thì triệt tiêu)
```

Nên **F có thể là "máy xay" một chiều** (S-box 6→4 bit, không thể đảo ngược), giải mã vẫn đúng.
Chỉ cần dùng **khóa con theo thứ tự ngược: K3, K2, K1**.

### Code (`core/tinydes_core.py:170-181`)

```python
def _decrypt_block(bits8, keys, log=None):
    left, right = bits8[:4], bits8[4:]                 # L3, R3
    for i in range(len(keys), 0, -1):                  # i = 3, 2, 1  (đi ngược)
        f = f_function(left, keys[i - 1], log, ...)    # F(L_i, K_i): dùng LẠI chính hàm F lúc mã hóa
        left, right = xor(right, f), left              # L_{i-1} = R_i ⊕ F ;  R_{i-1} = L_i
    return left + right                                # P = L0 R0
```

- `range(3, 0, -1)` sinh ra 3, 2, 1. `keys[i - 1]` vì tuple đánh chỉ số từ 0 (K3 là `keys[2]`).
- **Không cần viết hàm F ngược**: giải mã gọi đúng `f_function` của mã hóa. Đây là lợi thế lớn của Feistel.

Ví dụ giải mã `10010010` (output thật):

```
L3 R3 = 1001 0010
Vòng 3 (K3): F(1001) = 0011 → L2 = 0010 ⊕ 0011 = 0001, R2 = 1001  → 0001 1001
Vòng 2 (K2): F(0001) = 0101 → L1 = 1001 ⊕ 0101 = 1100, R1 = 0001  → 1100 0001
Vòng 1 (K1): F(1100) = 0100 → L0 = 0001 ⊕ 0100 = 0101, R0 = 1100  → 0101 1100 = 5C ✔
```

Để ý: giá trị F ở từng vòng (0011, 0101, 0100) **y hệt** lúc mã hóa, chỉ theo thứ tự ngược.

---

## T6. Hàm "cửa ngõ" và các phần mở rộng

### Ai gọi ai?

```
encrypt(plain_8bit, key_8bit)                     core/tinydes_core.py:184
 ├─ is_bits(plain_8bit, 8)                         kiểm tra input
 ├─ generate_keys(key_8bit, log)       → K1,K2,K3  (T1)
 └─ _encrypt_block(plain, keys, log)               (T2)
      └─ f_function(right, k)   × 3 vòng            (T3)
           ├─ permute(..., EXPAND)
           ├─ xor(...)
           ├─ sbox_lookup(...)
           └─ permute(..., PBOX)
 → trả về (bản mã, log_trung_gian)

decrypt(...) giống hệt, chỉ thay _encrypt_block bằng _decrypt_block   (T5)
```

`log_trung_gian` là list ghi lại mọi giá trị trung gian (`_log(...)`) để giao diện web/console hiển thị từng bước.
Khi `log=None` (ví dụ lúc vét cạn khóa) thì `_log` bỏ qua, chạy nhanh hơn.

### Mã hóa văn bản: `encrypt_bytes()`

Mỗi byte = 1 khối 8 bit, mã hóa độc lập từng byte:

```
'H' = 0x48 = 01001000  --TinyDES, K=10011010-->  01100111 = 0x67
```

```python
bytes(int(_encrypt_block(format(b, "08b"), keys), 2) for b in data)
#            số → "01001000" → mã hóa → "01100111" → 103
```

> Lưu ý: cùng một chữ luôn ra cùng một byte mã (ví dụ `"Hello"` → `67 B3 20 20 A2`, hai chữ `l` đều thành `20`).
> Đây là điểm yếu của cách mã từng khối độc lập (chế độ ECB).

### Vét cạn khóa: `brute_force()`, `brute_force_ciphertext_only()`

Khóa chỉ 8 bit nên chỉ có **256 khóa**. Máy thử hết trong chưa tới 1 giây. Đây là lý do TinyDES chỉ dùng để **học**,
và DES thật (56 bit, khoảng 7,2 × 10¹⁶ khóa) cũng đã bị coi là yếu.

### Class `TinyDES` (`core/tinydes_core.py:428`)

Cùng thuật toán, viết lại kiểu "mảng L[0..3], R[0..3], KL[0..3], KR[0..3]" cho giống ký hiệu slide,
và in từng dòng đúng định dạng lời giải trang 72 (dùng trong `tinydes_menu.py`). Điểm khác so với các hàm ở trên:
- sinh khóa con **ngay trong vòng lặp** mã hóa (giống lời giải slide: mỗi vòng ghi KLᵢ, KRᵢ, Kᵢ),
- `shifts = [0, 1, 2, 1]` có số 0 ở đầu để `shifts[i]` khớp chỉ số vòng i = 1, 2, 3,
- XOR làm bằng số nguyên (`int(..., 2) ^ ...`) thay vì so từng ký tự.

`test_runner.py` kiểm tra class này cho kết quả giống hệt các hàm ở trên.

---

## T7. Bảng tra nhanh: slide ↔ code

| Bước (slide) | Công thức | Hằng số / Hàm | Ví dụ (slide 72) |
|---|---|---|---|
| Chia khóa (71) | K → KL₀ \| KR₀ | `key_8bit[:4], key_8bit[4:]` | 1001 \| 1010 |
| Dịch vòng trái (71) | 1, 2, 1 bit | `SHIFTS`, `left_shift()` | 0011 \| 0101 |
| Nén khóa (71) | k5 k1 k3 k2 k7 k0 | `COMPRESS`, `permute()` | K1 = 101110 |
| Chia khối (68) | P → L₀ \| R₀ | `bits8[:4], bits8[4:]` | 0101 \| 1100 |
| Expand (69) | b2 b3 b1 b2 b1 b0 | `EXPAND`, `permute()` | 001011 |
| ⊕ khóa con (68) | Expand(R) ⊕ Kᵢ | `xor()` | 100101 |
| S-box (69–70) | hàng b0b5, cột b1b2b3b4 | `SBOX`, `sbox_lookup()` | 1000 |
| P-box (70) | b2 b0 b3 b1 | `PBOX`, `permute()` | F1 = 0100 |
| Vòng Feistel (68) | Lᵢ = Rᵢ₋₁, Rᵢ = Lᵢ₋₁ ⊕ F | `left, right = right, xor(left, f)` | 1100 0001 |
| Bản mã (72) | C = L₃R₃ | `return left + right` | 10010010 (92) |
| Giải mã (66) | Rᵢ₋₁ = Lᵢ, Lᵢ₋₁ = Rᵢ ⊕ F(Lᵢ, Kᵢ) | `_decrypt_block()` | 01011100 (5C) |

### Câu hỏi thầy hay hỏi

- **TinyDES khác DES chỗ nào?** 3 vòng thay vì 16; khối 8 thay vì 64 bit; khóa 8 thay vì 56 bit; khóa con 6 thay vì 48 bit; 1 S-box thay vì 8; không có hoán vị khởi tạo/kết thúc.
- **Tại sao giải mã dùng lại được hàm F?** Vì F luôn được tính trên nửa được giữ nguyên (Rᵢ₋₁ = Lᵢ), nên lúc giải mã tính lại được đúng F, XOR lần 2 thì triệt tiêu.
- **Khóa con giải mã lấy ở đâu?** Sinh y như khi mã hóa (`generate_keys`), chỉ **dùng theo thứ tự ngược** K3 → K2 → K1.
- **Vì sao sau vòng 3, KL₃KR₃ bằng khóa gốc?** Tổng số bit dịch 1+2+1 = 4 = độ dài mỗi nửa, quay đủ một vòng.
- **Phần nào tạo độ an toàn?** S-box (phi tuyến). Các bước còn lại chỉ xáo vị trí hoặc XOR.

---

# 🎓 DES (slide trang 73 → 81): từng bước, vào gì ra gì, và code tương ứng

> Cách đọc giống hệt phần TinyDES ở trên: mỗi bước có **slide nói gì → vào gì, ra gì (ví dụ cụ thể) → code làm thế nào**.
> Code nằm ở `core/des_core.py` (thuật toán), `core/des_tables.py` (các bảng) và `core/utils.py` (đệm, chia khối, tệp).
> Ví dụ xuyên suốt là ví dụ kinh điển của DES: **khóa `133457799BBCDFF1`, bản rõ `0123456789ABCDEF` → bản mã `85E813540F0AB405`**.
> Mọi con số dưới đây đều lấy từ kết quả chạy thật của code.

**Hiểu nhanh:** DES chính là **TinyDES phóng to**. Cùng các động tác (cắt đôi, Expand, XOR khóa, S-box, P-box, đổi chỗ L/R),
chỉ khác là to hơn và nhiều vòng hơn. Nếu đã hiểu TinyDES thì DES chỉ là "làm lại y vậy với số lớn hơn".

| | TinyDES | DES |
|---|---|---|
| 1 khối dữ liệu | 8 bit (1 chữ) | **64 bit** (8 chữ) |
| Khóa | 8 bit | **64 bit**, nhưng chỉ dùng **56 bit** |
| Số vòng | 3 | **16** |
| Khóa con | 3 chìa × 6 bit | **16 chìa × 48 bit** |
| Nửa trái / phải | 4 bit / 4 bit | **32 bit / 32 bit** |
| Expand | 4 → 6 bit | **32 → 48 bit** |
| S-box | 1 bảng | **8 bảng** (S1 chính là bảng của TinyDES) |
| Hoán vị đầu / cuối | không có | **IP** ở đầu, **IP⁻¹** ở cuối |

---

## D0. Vào gì, ra gì? Mã là gì?

### Đầu vào và đầu ra

| Tên | Là gì | Ví dụ |
|---|---|---|
| **Vào 1: Bản rõ** | Dữ liệu muốn giấu: văn bản, ảnh, tệp bất kỳ | 1 khối `0123456789ABCDEF`, hoặc chữ `"Xin chào"` |
| **Vào 2: Khóa K** | Mật khẩu bí mật, **đúng 8 byte** | `133457799BBCDFF1` (16 ký tự hex) hoặc `nhom2026` (8 ký tự) |
| **Ra: Bản mã** | Dữ liệu đã xáo trộn, dài bằng **bội số của 8 byte** | `85E813540F0AB405` |

```
   Bản rõ = 01 23 45 67 89 AB CD EF   ──┐
                                        ├──►  [ DES MÃ HÓA ]  ──►  Bản mã = 85 E8 13 54 0F 0A B4 05
   Khóa   = 13 34 57 79 9B BC DF F1   ──┘
```

Trong code:

```python
des_core.encrypt_block(bytes.fromhex("0123456789ABCDEF"), bytes.fromhex("133457799BBCDFF1"))
# → bytes 85 E8 13 54 0F 0A B4 05
```

### Vì sao viết bằng hex (hệ 16)?

64 bit viết ra rất dài, nên người ta viết gọn bằng **hex**: **cứ 4 bit thành 1 ký tự** (0–9, A–F).

```
bit:  0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111
hex:     0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F
```

Nên bản rõ `0123456789ABCDEF` (16 ký tự hex) chính là **64 bit** ở dòng trên. Hai ký tự hex = 1 byte, ví dụ `EF` = `11101111`.

### Lưu ý về cách đánh số bit: slide đếm từ 0, code đếm từ 1

- **Slide** (trang 75, 77, 78, 79) đánh số bit **từ 0**: b0, b1, …, b63. Ví dụ bảng IP trên slide bắt đầu bằng `57 49 41 …`.
- **Code** chép bảng từ **chuẩn quốc tế FIPS 46-3**, đánh số **từ 1**. Bảng IP trong `core/des_tables.py` bắt đầu bằng `58 50 42 …`.

Hai bảng **giống hệt nhau, chỉ lệch 1**: mỗi số trong code = số trên slide + 1. Ví dụ:

| Bảng | Slide (đếm từ 0) | Code (đếm từ 1) |
|---|---|---|
| IP | 57 49 41 33 … | 58 50 42 34 … |
| E | 31 0 1 2 3 4 … | 32 1 2 3 4 5 … |
| P | 15 6 19 20 … | 16 7 20 21 … |
| PC-1 | 56 48 40 32 … | 57 49 41 33 … |

Thầy hỏi "sao bảng trong code khác slide?" thì trả lời: **khác cách đếm, không khác bảng**.

### Code DES dùng số nguyên, không dùng chuỗi '0'/'1' như TinyDES

TinyDES lưu bit bằng chuỗi `"0110"` cho dễ in ra. DES phải mã hóa cả tệp ảnh vài MB, nên code lưu **cả khối 64 bit thành 1 số nguyên** để chạy nhanh:

```python
b = int.from_bytes(block, "big")     # 8 byte 01 23 45 67 89 AB CD EF → số 0x0123456789ABCDEF
out.to_bytes(8, "big")               # số → lại thành 8 byte
```

`"big"` nghĩa là byte đầu tiên là phần "lớn nhất" của số, giống cách ta viết số từ trái sang phải.

---

## D1. Khóa DES do ai chọn? → `parse_des_key()`

Giống TinyDES: **khóa do bạn tự chọn**, hai bên gửi/nhận dùng chung và giữ bí mật. Khác ở chỗ khóa DES dài **8 byte**.
Code cho phép gõ khóa theo 2 cách (`core/utils.py:65`):

| Bạn gõ | Code hiểu là | 8 byte khóa |
|---|---|---|
| `133457799BBCDFF1` (16 ký tự hex) | mỗi 2 ký tự hex = 1 byte | `13 34 57 79 9B BC DF F1` |
| `nhom2026` (8 ký tự) | mỗi ký tự = 1 byte theo bảng ASCII | `6E 68 6F 6D 32 30 32 36` (n = 6E, h = 68, …) |
| `abc` (độ dài khác) | không hợp lệ | báo lỗi *"Khóa DES phải là 8 ký tự hoặc 16 ký tự hex"* |

```python
def parse_des_key(text):
    text = text.strip()
    if len(text) == 16:                 # 16 ký tự → thử hiểu là hex
        try:
            return bytes.fromhex(text)  # "13" → 0x13, "34" → 0x34, ...
        except ValueError:
            pass
    raw = text.encode("utf-8")          # còn lại: chữ → byte
    if len(raw) == 8:
        return raw
    raise ValueError(...)
```

Trên web, khóa được nhập ở ô "Khóa" của trang DES, code đọc tại `app.py:414`: `utils.parse_des_key(request.form.get("des_key", ""))`.

### Vì sao khóa 64 bit mà nói "chỉ dùng 56 bit"?

Trong mỗi byte khóa, **bit cuối cùng** (bit số 8, 16, 24, …, 64) là **bit kiểm tra chẵn lẻ**. DES **bỏ** 8 bit này ở bước PC-1 (xem D2).
Nên khóa thật sự chỉ có 56 bit, tức 2⁵⁶ ≈ **72 triệu tỷ** khóa (so với 256 khóa của TinyDES).

**Ví dụ thú vị, chạy thật:** khóa `nhom2026` và `nhom2027` **giải mã được cho nhau**!

```
'6' = 0x36 = 0011011 0
'7' = 0x37 = 0011011 1     ← chỉ khác đúng bit cuối (bit chẵn lẻ) → bị DES bỏ đi
→ generate_subkeys("nhom2026") == generate_subkeys("nhom2027")   → True
```

Còn `nhom2025` ('5' = 0x35 = 0011010 **1**) khác ở bit thứ 7, bit thật sự được dùng, nên giải mã ra rác và báo lỗi.

---

## D2. PHẦN B: Sinh 16 khóa con (slide 79) → `generate_subkeys()`

### Slide nói

1. Khóa K 64 bit được **rút trích và hoán vị** thành 56 bit theo bảng (gọi là **PC-1**).
2. Chia 56 bit thành 2 nửa **KL₀** và **KR₀**, mỗi nửa 28 bit (code gọi là `c` và `d`, sách tiếng Anh gọi C0, D0).
3. Vòng i (i = 1…16): KLᵢ₋₁, KRᵢ₋₁ **dịch vòng trái rᵢ bit**, với **rᵢ = 1 nếu i ∈ {1, 2, 9, 16}, còn lại rᵢ = 2**.
4. Kᵢ = hoán vị và **nén** 56 bit KLᵢKRᵢ thành 48 bit theo bảng (gọi là **PC-2**).

So với TinyDES: **y hệt khuôn** "chia đôi → dịch vòng → nén", chỉ thêm bước 1 (PC-1) và làm 16 lần thay vì 3.

### Từng bước: vào gì, ra gì (khóa `133457799BBCDFF1`)

**① Khóa → 64 bit**

```
13       34       57       79       9B       BC       DF       F1
00010011 00110100 01010111 01111001 10011011 10111100 11011111 11110001
       ↑        ↑        ↑        ↑        ↑        ↑        ↑        ↑
       bit chẵn lẻ (bit 8, 16, ..., 64): sẽ bị bỏ
```

**② PC-1: 64 bit → 56 bit.** Vào 64 bit ở trên. Ra:

```
1111000 0110011 0010101 0101111 0101010 1011001 1001111 0001111     (hex F0CCAAF556678F)
```

Bảng PC-1 không có các số 8, 16, …, 64, nên 8 bit chẵn lẻ biến mất. Đồng thời các bit còn lại bị **xếp lại chỗ**.

**③ Cắt đôi**

```
C0 = 1111000011001100101010101111   (F0CCAAF)   28 bit trái
D0 = 0101010101100110011110001111   (556678F)   28 bit phải
```

**④ Vòng 1: dịch vòng trái 1 bit mỗi nửa** (r₁ = 1)

```
C0 = 1111000011001100101010101111  → bit đầu "1" chạy ra cuối →  C1 = 1110000110011001010101011111  (E19955F)
D0 = 0101010101100110011110001111  → bit đầu "0" chạy ra cuối →  D1 = 1010101011001100111100011110  (AACCF1E)
```

**⑤ PC-2: ghép C1D1 (56 bit) rồi chọn 48 bit** → khóa con vòng 1:

```
K1 = 000110 110000 001011 101111 111111 000111 000001 110010    (hex 1B02EFFC7072)
```

Bảng PC-2 thiếu 8 vị trí (9, 18, 22, 25, 35, 38, 43, 54), nên 56 bit còn 48. Giống Compress của TinyDES (8 → 6).

**⑥ Lặp lại ④–⑤ cho vòng 2 … 16.** Mỗi vòng dịch **tiếp** từ kết quả vòng trước (giống TinyDES):

| Vòng | Dịch | C | D | Khóa con Kᵢ (hex) |
|---|---|---|---|---|
| 1 | 1 | E19955F | AACCF1E | 1B02EFFC7072 |
| 2 | 1 | C332ABF | 5599E3D | 79AED9DBC9E5 |
| 3 | 2 | 0CCAAFF | 56678F5 | 55FC8A42CF99 |
| 4 | 2 | 332ABFC | 599E3D5 | 72ADD6DB351D |
| 5 | 2 | CCAAFF0 | 6678F55 | 7CEC07EB53A8 |
| 6 | 2 | 32ABFC3 | 99E3D55 | 63A53E507B2F |
| 7 | 2 | CAAFF0C | 678F556 | EC84B7F618BC |
| 8 | 2 | 2ABFC33 | 9E3D559 | F78A3AC13BFB |
| 9 | 1 | 557F866 | 3C7AAB3 | E0DBEBEDE781 |
| 10 | 2 | 55FE199 | F1EAACC | B1F347BA464F |
| 11 | 2 | 57F8665 | C7AAB33 | 215FD3DED386 |
| 12 | 2 | 5FE1995 | 1EAACCF | 7571F59467E9 |
| 13 | 2 | 7F86655 | 7AAB33C | 97C5D1FABA41 |
| 14 | 2 | FE19955 | EAACCF1 | 5F43B7F2E73A |
| 15 | 2 | F866557 | AAB33C7 | BF918D3D3F0A |
| 16 | 1 | **F0CCAAF** | **556678F** | CB3D8B0E17F5 |

Để ý vòng 16: C16 = C0, D16 = D0. Vì tổng số bit dịch = 1+1+2·6+1+2·6+1 = **28 = độ dài mỗi nửa**, quay đủ 1 vòng. Giống TinyDES (1+2+1 = 4).

**Vào:** 8 byte khóa → **Ra:** danh sách 16 số, mỗi số 48 bit: `[K1, K2, …, K16]`.

### Code (`core/des_core.py:59-91`)

```python
def generate_subkeys(key, log=None):
    k64 = int.from_bytes(key, "big")            # ① 8 byte → số 64 bit 0x133457799BBCDFF1
    k56 = permute(k64, PC1, 64)                 # ② PC-1: → 0xF0CCAAF556678F (56 bit)
    c, d = k56 >> 28, k56 & 0x0FFFFFFF          # ③ C0 = F0CCAAF, D0 = 556678F
    subkeys = []
    for i, s in enumerate(SHIFTS, start=1):     # SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
        c, d = rotl(c, s, 28), rotl(d, s, 28)   # ④ dịch vòng trái mỗi nửa s bit
        k = permute((c << 28) | d, PC2, 56)     # ⑤ ghép C|D rồi PC-2 → Ki 48 bit
        subkeys.append(k)
    return subkeys                              # [K1, ..., K16]
```

| Slide | Code | Giải thích dòng code |
|---|---|---|
| Rút trích 64 → 56 bit | `permute(k64, PC1, 64)` | Dùng chung hàm hoán vị với bảng PC1 |
| Chia KL₀, KR₀ (28 bit) | `k56 >> 28`, `k56 & 0x0FFFFFFF` | `>> 28`: đẩy bỏ 28 bit phải, còn 28 bit trái. `& 0x0FFFFFFF` (28 số 1): chỉ giữ 28 bit phải |
| rᵢ = 1 nếu i ∈ {1,2,9,16}, còn lại 2 | `SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]` | Vị trí 1, 2, 9, 16 là số 1 |
| Dịch vòng trái | `rotl(c, s, 28)` | Xem giải thích `rotl` ngay dưới |
| Nén 56 → 48 bit | `permute((c << 28) \| d, PC2, 56)` | `c << 28` đẩy C sang trái 28 chỗ, `\| d` gắn D vào bên phải → C‖D 56 bit |

### Hai hàm dụng cụ: `permute` và `rotl` trên số nguyên

**`permute(value, table, in_bits)`** (`core/des_core.py:23`): giống `permute` của TinyDES, chỉ là làm trên số.

```python
for pos in table:
    bit = (value >> (in_bits - pos)) & 1    # lấy bit thứ pos (đếm từ 1, từ trái)
    out = (out << 1) | bit                  # gắn bit đó vào cuối kết quả
```

Ví dụ nhỏ: `permute(0b1011, [2, 4, 3, 1], 4)`, tức lấy bit 2, 4, 3, 1 của `1011`:

| pos | `value >> (4 - pos)` | `& 1` = bit | out |
|---|---|---|---|
| 2 | `1011 >> 2` = `10` | 0 | `0` |
| 4 | `1011 >> 0` = `1011` | 1 | `01` |
| 3 | `1011 >> 1` = `101` | 1 | `011` |
| 1 | `1011 >> 3` = `1` | 1 | `0111` |

Kết quả `0111` ✔. Một hàm dùng cho mọi bảng: IP, IP⁻¹ (64→64), PC-1 (64→56), PC-2 (56→48), E (32→48), P (32→32).

**`rotl(value, n, bits)`** (`core/des_core.py:43`): dịch vòng trái.

```python
return ((value << n) | (value >> (bits - n))) & mask
```

Ví dụ `rotl(0b1000, 1, 4)`:

```
value << 1          = 10000     (bit đầu bị đẩy ra ngoài 4 bit)
value >> (4 - 1)    = 00001     (lấy đúng bit đầu đó, đưa về cuối)
ghép bằng |         = 10001
& 1111 (mask)       = 0001      (cắt phần thừa bên trái)   ✔ giống "1000" → "0001"
```

---

## D3. Chuẩn bị dữ liệu: chữ → byte → các khối 8 byte (đệm PKCS#7)

### Vì sao phải "đệm"?

DES chỉ nhận **đúng 8 byte mỗi khối**. Tin nhắn thật thì dài bao nhiêu cũng có. Vậy phải **cắt thành từng khúc 8 byte**, khúc cuối thiếu thì **độn thêm**.

Giống đóng hàng vào thùng 8 ô:
- thiếu ô nào thì nhét giấy độn vào;
- **trên mỗi tờ giấy độn ghi số tờ đã độn** (độn 7 tờ thì mỗi tờ ghi số 7);
- lúc mở thùng, nhìn tờ cuối thấy số 7 là biết bỏ đi 7 tờ.

### Ví dụ: "Xin chào", khóa `nhom2026`

**① Chữ → byte (UTF-8):**

```
X   i   n   (cách)  c   h   à       o
58  69  6E  20      63  68  C3 A0   6F        → 9 byte (chữ "à" chiếm 2 byte)
```

**② Đệm:** 9 byte, chia 8 dư 1 → thiếu 7 → thêm **7 byte, mỗi byte = 07**:

```
58 69 6E 20 63 68 C3 A0 | 6F 07 07 07 07 07 07 07        → 16 byte = 2 khối
└──────── khối 1 ──────┘ └──────── khối 2 ───────┘
```

**③ Mã hóa từng khối** bằng DES (D4–D6). Ra bản mã:

```
EA 63 45 B5 94 48 F3 27 | 3B 7B 89 A3 C7 95 E4 14
```

**Trường hợp đặc biệt:** dữ liệu đã tròn 8 byte (ví dụ `ABCDEFGH`) thì **vẫn thêm nguyên 1 khối** `08 08 08 08 08 08 08 08`.
Lý do: nếu không thêm, lúc giải mã thấy byte cuối là `48` ('H') sẽ không biết đó là chữ thật hay giấy độn.

### Code (`core/utils.py:16-62`)

```python
def pkcs7_pad(data, block_size=8):
    n = block_size - len(data) % block_size   # 9 % 8 = 1 → n = 7 ;  8 % 8 = 0 → n = 8
    return data + bytes([n]) * n              # nối thêm 7 byte giá trị 7

def split_blocks(data, block_size=8):
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]
    # range(0, 16, 8) = 0, 8  →  [data[0:8], data[8:16]]
```

| Đoạn code | Nghĩa | Ví dụ |
|---|---|---|
| `len(data) % 8` | phần dư khi chia 8 | 9 % 8 = 1 |
| `8 - 1` | số byte cần độn | 7 |
| `bytes([7])` | 1 byte có giá trị 7 | `07` |
| `* 7` | lặp lại 7 lần | `07 07 07 07 07 07 07` |

---

## D4. Hoán vị khởi tạo IP và cắt đôi (slide 74–75) → `permute(b, IP, 64)`

### Slide nói

Trước vòng 1, cả 64 bit được **xếp lại chỗ** theo bảng IP (bảng trái ở slide 75). Sau đó chia làm L0 (32 bit trái) và R0 (32 bit phải).
TinyDES **không có** bước này.

### Vào gì, ra gì

**Vào:** bản rõ `0123456789ABCDEF`

```
00000001 00100011 01000101 01100111 10001001 10101011 11001101 11101111
```

**Ra:**

```
11001100 00000000 11001100 11111111 | 11110000 10101010 11110000 10101010
└────────── L0 = CC00CCFF ─────────┘   └────────── R0 = F0AAF0AA ─────────┘
```

**Cách đọc bảng IP**, ví dụ bit đầu tiên của kết quả: bảng code ghi `58`, nghĩa là "lấy bit số 58 của đầu vào".
Bit 58 nằm trong byte thứ 8 (`EF` = `11101111`), là bit thứ 2 của byte đó = **1**. Vậy bit đầu của kết quả là 1 ✔.

**IP có làm mã an toàn hơn không?** Không. IP chỉ xếp lại chỗ theo bảng ai cũng biết. Nó có từ thời phần cứng những năm 1970 (để nạp dữ liệu vào chip tiện hơn).

### Code (`core/des_core.py:154-156`)

```python
b = int.from_bytes(block, "big")                # 8 byte → số 64 bit
ip = permute(b, IP, 64)                         # → 0xCC00CCFFF0AAF0AA
left, right = ip >> 32, ip & 0xFFFFFFFF         # L0 = CC00CCFF, R0 = F0AAF0AA
```

- `ip >> 32`: bỏ 32 bit phải, còn lại 32 bit trái = L0.
- `ip & 0xFFFFFFFF` (32 số 1): chỉ giữ 32 bit phải = R0.

---

## D5. Một vòng Feistel của DES (slide 76–78) → `feistel_f()`

### Slide nói

```
Lᵢ = Rᵢ₋₁
Rᵢ = Lᵢ₋₁ ⊕ F(Rᵢ₋₁, Kᵢ)        với   F(R, K) = P-box( S-boxes( Expand(R) ⊕ K ) )
```

**Y hệt công thức TinyDES**, chỉ đổi kích thước: Expand 32 → 48, khóa con 48 bit, 8 S-box (48 → 32), P-box 32 bit.

### Vòng 1 làm từng việc: vào gì, ra gì

Vào: L0 = `CC00CCFF`, R0 = `F0AAF0AA`, K1 = `1B02EFFC7072`.

| Việc | Vào | Làm gì | Ra |
|---|---|---|---|
| a. **Expand** | R0 (32 bit) | Kéo dài thành 48 bit theo bảng E | `7A15557A1555` (48 bit) |
| b. **XOR khóa** | 48 bit trên và K1 | So từng cặp bit | `6117BA866527` |
| c. **8 S-box** | 48 bit | Cắt 8 nhóm × 6 bit, mỗi nhóm tra 1 bảng → 4 bit | `5C82B597` (32 bit) |
| d. **P-box** | 32 bit | Xếp lại chỗ theo bảng P | **F = `234AA9BB`** |
| e. **Nửa phải mới** | L0 và F | XOR | R1 = `EF4A6544` |
| f. **Nửa trái mới** | R0 | Chép y nguyên | L1 = `F0AAF0AA` |

#### a. Expand: 32 → 48 bit (slide 77)

Bảng E chia thành 8 hàng, mỗi hàng 6 bit. Mỗi hàng lấy 4 bit liền nhau **cộng thêm 1 bit hàng xóm hai bên**:

```
code (đếm từ 1):  32 1 2 3 4 5 | 4 5 6 7 8 9 | 8 9 10 11 12 13 | ... | 28 29 30 31 32 1
```

Vào R0 = `1111 0000 1010 1010 1111 0000 1010 1010`

Ví dụ nhóm đầu: lấy bit 32, 1, 2, 3, 4, 5 → bit 32 = `0`, bit 1–5 = `1 1 1 1 0` → `011110`.

```
Ra: 011110 100001 010101 010101 011110 100001 010101 010101    (7A15557A1555)
```

16 bit bị lặp lại, nên 32 → 48. Mục đích giống TinyDES: khớp độ dài với khóa con 48 bit, và mỗi bit vào ảnh hưởng tới nhiều chỗ.

#### b. XOR với khóa con K1

```
  E(R0) = 011110 100001 010101 010101 011110 100001 010101 010101
⊕ K1    = 000110 110000 001011 101111 111111 000111 000001 110010
= ─────────────────────────────────────────────────────────────────
          011000 010001 011110 111010 100001 100110 010100 100111     (6117BA866527)
```

#### c. 8 S-box: mỗi nhóm 6 bit → 4 bit (slide 77, 78, 80, 81)

Cắt 48 bit thành 8 nhóm. Nhóm 1 vào S1, nhóm 2 vào S2, …, nhóm 8 vào S8.
**Cách tra y hệt TinyDES:** hàng = bit đầu + bit cuối, cột = 4 bit giữa.

| S-box | Vào 6 bit | Hàng (đầu+cuối) | Cột (4 bit giữa) | Ô trong bảng | Ra 4 bit |
|---|---|---|---|---|---|
| S1 | `011000` | `00` = 0 | `1100` = 12 | 5 | `0101` |
| S2 | `010001` | `01` = 1 | `1000` = 8 | C (12) | `1100` |
| S3 | `011110` | `00` = 0 | `1111` = 15 | 8 | `1000` |
| S4 | `111010` | `10` = 2 | `1101` = 13 | 2 | `0010` |
| S5 | `100001` | `11` = 3 | `0000` = 0 | B (11) | `1011` |
| S6 | `100110` | `10` = 2 | `0011` = 3 | 5 | `0101` |
| S7 | `010100` | `00` = 0 | `1010` = 10 | 9 | `1001` |
| S8 | `100111` | `11` = 3 | `0011` = 3 | 7 | `0111` |

Tự kiểm tra với slide 80: bảng S1, hàng 0, cột C là **5** ✔.

Ghép 8 kết quả: `0101 1100 1000 0010 1011 0101 1001 0111` = **`5C82B597`** (32 bit).

#### d. P-box: hoán vị 32 bit (slide 78)

Bảng P (code): `16 7 20 21 29 12 28 17 …`. Nghĩa là bit 1 của kết quả lấy bit 16, bit 2 lấy bit 7, …

```
Vào:  0101 1100 1000 0010 1011 0101 1001 0111
      bit 16 = 0 (nhóm thứ 4 "0010", bit cuối) → bit 1 của kết quả = 0
      bit 7  = 0 (nhóm thứ 2 "1100", bit thứ 3) → bit 2 của kết quả = 0
      bit 20 = 1 (nhóm thứ 5 "1011", bit cuối)  → bit 3 của kết quả = 1
      ...
Ra:   0010 0011 0100 1010 1010 1001 1011 1011  = F1 = 234AA9BB
```

#### e–f. Kết thúc vòng 1

```
R1 = L0 ⊕ F1 = CC00CCFF ⊕ 234AA9BB = EF4A6544
L1 = R0                            = F0AAF0AA
```

### Code (`core/des_core.py:97-137, 160`)

```python
def feistel_f(r32, k48, detail=None):
    e = permute(r32, E, 32)     # a. 32 → 48 bit      VD 7A15557A1555
    x = e ^ k48                 # b. XOR khóa con     VD 6117BA866527
    s = sbox_sub(x)             # c. 8 S-box 48 → 32  VD 5C82B597
    f = permute(s, P, 32)       # d. P-box            VD 234AA9BB
    return f

# trong vòng lặp 16 vòng:
left, right = right, left ^ feistel_f(right, k)     # e–f. Lᵢ = Rᵢ₋₁ ; Rᵢ = Lᵢ₋₁ ⊕ F
```

Ở đây `^` là phép XOR của Python, làm luôn trên cả số 48 bit, không phải so từng ký tự như TinyDES.

**Hàm `sbox_sub`**, phần "khó đọc" nhất vì làm bằng phép toán bit:

```python
for i in range(8):                              # i = 0..7 ứng với S1..S8
    chunk = (x48 >> (42 - 6 * i)) & 0x3F        # lấy nhóm 6 bit thứ i
    row = ((chunk >> 4) & 0b10) | (chunk & 1)   # hàng = bit đầu + bit cuối
    col = (chunk >> 1) & 0xF                    # cột = 4 bit giữa
    out = (out << 4) | S_BOX[i][row][col]       # tra bảng, gắn 4 bit vào cuối
```

Giải thích với nhóm của S4 là `111010`:

| Dòng | Tính | Kết quả |
|---|---|---|
| `x48 >> (42 - 6*3)` rồi `& 0x3F` | Nhóm 4 nằm ở bit 19–24 tính từ trái. Dịch phải 24 chỗ cho nó về cuối, `& 0x3F` (= `111111`) giữ 6 bit | `111010` |
| `chunk >> 4` | Bỏ 4 bit cuối, còn 2 bit đầu | `11` |
| `& 0b10` | Chỉ giữ bit đầu, ở vị trí "số 2" | `10` |
| `chunk & 1` | Lấy bit cuối | `0` |
| `\|` ghép lại | hàng = `10` | **2** |
| `chunk >> 1` | Bỏ bit cuối | `11101` |
| `& 0xF` (= `1111`) | Giữ 4 bit cuối = 4 bit giữa ban đầu | `1101` = **13** |
| `S_BOX[3][2][13]` | Tra bảng S4 hàng 2 cột 13 | **2** = `0010` |

---

## D6. Chạy đủ 16 vòng

Mỗi vòng làm y hệt D5, chỉ đổi khóa con. **Đầu ra vòng trước là đầu vào vòng sau.**

| Vòng | Khóa con | F | L (sau vòng) | R (sau vòng) |
|---|---|---|---|---|
| IP | | | CC00CCFF | F0AAF0AA |
| 1 | K1 | 234AA9BB | F0AAF0AA | EF4A6544 |
| 2 | K2 | 3CAB87A3 | EF4A6544 | CC017709 |
| 3 | K3 | 4D166EB0 | CC017709 | A25C0BF4 |
| 4 | K4 | BB23774C | A25C0BF4 | 77220045 |
| 5 | K5 | 2813ADC3 | 77220045 | 8A4FA637 |
| 6 | K6 | 9E45CD2C | 8A4FA637 | E967CD69 |
| 7 | K7 | 8C051C27 | E967CD69 | 064ABA10 |
| 8 | K8 | 3C0E86F9 | 064ABA10 | D5694B90 |
| 9 | K9 | 22367C6A | D5694B90 | 247CC67A |
| 10 | K10 | 62BC9C22 | 247CC67A | B7D5D7B2 |
| 11 | K11 | E104FA02 | B7D5D7B2 | C5783C78 |
| 12 | K12 | C268CFEA | C5783C78 | 75BD1858 |
| 13 | K13 | DDBB2922 | 75BD1858 | 18C3155A |
| 14 | K14 | B7318E55 | 18C3155A | C28C960D |
| 15 | K15 | 5B81276E | C28C960D | 43423234 |
| 16 | K16 | C8C04F98 | **43423234** | **0A4CD995** |

Mẹo để kiểm tra bảng: **cột L của mỗi vòng = cột R của vòng ngay trên** (vì Lᵢ = Rᵢ₋₁).

---

## D7. Đổi chỗ lần cuối và IP⁻¹ (slide 74) → ra bản mã

### Slide nói

Sau vòng 16: **đổi 2 nửa đầu, cuối** rồi làm **hoán vị kết thúc** (IP⁻¹, bảng phải ở slide 75).

### Vào gì, ra gì

```
Sau vòng 16:   L16 = 43423234,  R16 = 0A4CD995
Đổi chỗ:       R16 L16 = 0A4CD995 43423234
IP⁻¹:          85E813540F0AB405      ← BẢN MÃ ✔
```

**Vì sao phải đổi chỗ lần cuối?** Để **giải mã dùng đúng thuật toán mã hóa, chỉ cần đảo thứ tự khóa con**.
Không đổi thì lúc giải mã phải viết thêm một hàm khác.

**IP⁻¹ là gì?** Là "IP ngược": IP⁻¹(IP(x)) = x. Nó trả các bit về đúng kiểu sắp xếp ban đầu.

### Code (`core/des_core.py:166`)

```python
out = permute((right << 32) | left, IP_INV, 64)
```

Vòng lặp đã lỡ tráo L/R ở vòng 16 (DES quy định vòng 16 không tráo). Nên code ghép ngược lại **R‖L** (`right` đứng trước) để hủy lần tráo đó, rồi IP⁻¹.

### Cây gọi hàm khi mã hóa 1 khối

```
encrypt_block(block, key)                       core/des_core.py:289
├─ generate_subkeys(key)          → K1..K16     (D2)
└─ crypt_block_fast(...)  (hoặc crypt_block_verbose để in log)
   ├─ IP                                         (D4)
   ├─ 16 lần: left, right = right, left ^ F(right, Ki)     (D5, D6)
   └─ IP⁻¹(R16‖L16)                              (D7)
→ 8 byte bản mã 85 E8 13 54 0F 0A B4 05
```

---

## D8. Giải mã DES → `des_decrypt_bytes()`

### Vào gì, ra gì

**Vào:** bản mã `85E813540F0AB405` + cùng khóa `133457799BBCDFF1` → **Ra:** `0123456789ABCDEF` ✔

### Làm thế nào?

**Chạy đúng thuật toán mã hóa, chỉ đổi thứ tự khóa con: K16, K15, …, K1.** Lý do giống TinyDES:
mỗi vòng chỉ XOR thêm F vào một nửa, XOR lần 2 với cùng F thì triệt tiêu. Đi ngược các vòng là gỡ được từng lớp.

```python
def decrypt_block(block, key):
    sk = prepare_keys(generate_subkeys(key)[::-1])   # [::-1]: đảo list [K1..K16] → [K16..K1]
    return crypt_block_fast(int.from_bytes(block, "big"), sk).to_bytes(8, "big")
```

So với `encrypt_block`: **chỉ khác đúng `[::-1]`**.

### Giải mã cả văn bản (`core/utils.py:105`)

```python
def des_decrypt_bytes(data, key):
    if len(data) % 8:                                     # bản mã phải là bội số 8 byte
        raise ValueError(...)
    return pkcs7_unpad(_crypt_blocks(data, des_core.generate_subkeys(key)[::-1]))
```

3 việc theo thứ tự:
1. Kiểm tra độ dài là bội số 8.
2. Giải mã từng khối với khóa con đảo ngược → `58 69 6E 20 63 68 C3 A0 | 6F 07 07 07 07 07 07 07`.
3. **Bỏ giấy độn** (`pkcs7_unpad`): byte cuối là `07` → bỏ 7 byte cuối → `58 69 6E 20 63 68 C3 A0 6F` → `"Xin chào"` ✔.

### Sai khóa thì sao?

Giải mã sai khóa ra **byte rác**, nên byte cuối gần như không bao giờ là giấy độn hợp lệ. Code phát hiện và báo lỗi:

```
khóa đúng nhom2026  → "Xin chào"
khóa sai  nhom2025  → khối 2 giải ra D2 82 E2 61 18 8D AD E0
                      byte cuối = E0 = 224, không phải số từ 1..8
                      → lỗi "Padding sai - có thể do sai khóa hoặc file không phải bản mã DES."
```

```python
def pkcs7_unpad(data, block_size=8):
    n = data[-1]                                                    # byte cuối
    if n < 1 or n > block_size or data[-n:] != bytes([n]) * n:      # phải là n byte đều bằng n
        raise ValueError("Padding sai - có thể do sai khóa ...")
    return data[:-n]                                                # bỏ n byte cuối
```

---

## D9. Toàn bộ đường đi của một tin nhắn / một tệp

### Văn bản

```
"Xin chào"
   │ .encode("utf-8")                         chữ → byte
   ▼
58 69 6E 20 63 68 C3 A0 6F                    (9 byte)
   │ pkcs7_pad                                 đệm
   ▼
58 69 6E 20 63 68 C3 A0 | 6F 07 07 07 07 07 07 07
   │ split_blocks → mỗi khối: int.from_bytes → crypt_block_fast (16 vòng) → to_bytes
   ▼
EA 63 45 B5 94 48 F3 27 | 3B 7B 89 A3 C7 95 E4 14      ← BẢN MÃ (gửi đi)
   │ giải mã từng khối với K16..K1
   ▼
58 69 6E 20 63 68 C3 A0 | 6F 07 07 07 07 07 07 07
   │ pkcs7_unpad                               bỏ đệm
   ▼
58 69 6E 20 63 68 C3 A0 6F  ── .decode("utf-8") ──►  "Xin chào" ✔
```

Code tương ứng (`core/utils.py:84-102`):

```python
def des_encrypt_bytes(data, key):
    return _crypt_blocks(pkcs7_pad(data), des_core.generate_subkeys(key))

def _crypt_blocks(data, subkeys):
    sk = des_core.prepare_keys(subkeys)                 # chuẩn bị khóa 1 lần cho cả tệp
    out = bytearray()
    for block in split_blocks(data):                    # từng khối 8 byte
        out += des_core.crypt_block_fast(int.from_bytes(block, "big"), sk).to_bytes(8, "big")
    return bytes(out)
```

### Tệp (ảnh, PDF, txt…)

Ảnh hay PDF cũng chỉ là **một dãy byte**. Đọc tệp ở chế độ nhị phân (`"rb"`), mã hóa y như văn bản, rồi ghi ra (`"wb"`):

```python
utils.des_encrypt_file("anh.png", "anh.png.enc", key)   # đọc → des_encrypt_bytes → ghi
utils.des_decrypt_file("anh.png.enc", "anh.png", key)   # đọc → des_decrypt_bytes → ghi
```

Trên web: trang DES, chọn tệp, bấm Mã hóa. Hàm `des_file()` (`app.py:410`) nhận tệp, mã hóa, rồi trả link tải `anh.png.enc`.

### Điểm yếu của chế độ ECB (mã từng khối riêng lẻ)

Giống TinyDES: **khối giống nhau thì ra bản mã giống nhau**. Ví dụ 16 chữ `A` (2 khối `AAAAAAAA` giống nhau), khóa `nhom2026`:

```
9F AE 96 E1 75 3D 8B 46 | 9F AE 96 E1 75 3D 8B 46 | EF 82 78 E7 3B 03 D0 CC
└─────── khối 1 ──────┘   └─ khối 2: GIỐNG HỆT ─┘   └── khối đệm 08×8 ──┘
```

Kẻ tấn công thấy ngay "2 khúc đầu giống nhau". Slide 84 có nhắc các chế độ khác (CBC, CTR…) để khắc phục; đồ án dùng ECB để so sánh trực tiếp được với thư viện pycryptodome.

---

## D10. Hai bản cài đặt: "dễ đọc" và "chạy nhanh"

| | `crypt_block_verbose` (dễ đọc) | `crypt_block_fast` (chạy nhanh) |
|---|---|---|
| Viết thế nào | Đúng từng bước sơ đồ: `permute` → `feistel_f` → `sbox_sub` | **Tính sẵn bảng tra** lúc khởi động, khi chạy chỉ tra bảng |
| Ghi log từng vòng | Có (web dùng để hiện 16 vòng) | Không |
| Tốc độ | Tệp 1 MB mất khoảng 20–30 giây | Khoảng 720 KB/s, tệp 1 MB khoảng 1,4 giây |
| Kết quả | **Giống hệt nhau** (`test_runner.py` kiểm tra) | |

Ý tưởng của bản nhanh, nói bằng lời thường: thay vì mỗi lần **tính** "bit này đi đâu" (lặp 64 lần), ta **tính trước một lần** cho mọi giá trị có thể của từng byte, cất vào bảng. Lúc chạy chỉ cần **tra 8 lần**.
Giống thuộc bảng cửu chương: thay vì cộng 7 + 7 + 7, ta nhớ sẵn 7 × 3 = 21.

Khi thuyết trình, **chỉ cần giải thích bản dễ đọc**. Bản nhanh chỉ để chạy tệp lớn cho nhanh.

---

## D11. Double DES, Triple DES (slide 82–83)

Slide giới thiệu thêm, code **không cài** phần này, nhưng hiểu rất đơn giản: **chạy DES nhiều lần với nhiều khóa**.

| | Mã hóa | Giải mã |
|---|---|---|
| Double DES | C = DES_K2( DES_K1(M) ) | M = DES⁻¹_K1( DES⁻¹_K2(C) ) |
| Triple DES (2 khóa) | C = DES_K1( DES⁻¹_K2( DES_K1(M) ) ) | M = DES⁻¹_K1( DES_K2( DES⁻¹_K1(C) ) ) |

Nếu muốn, với code hiện có thì Triple DES 1 khối chỉ là:

```python
c = encrypt_block(decrypt_block(encrypt_block(m, k1), k2), k1)
```

---

## D12. Bảng tra nhanh: slide ↔ code (DES)

| Bước (slide) | Vào → Ra | Bảng / Hàm | Ví dụ |
|---|---|---|---|
| Nhận khóa | chữ/hex → 8 byte | `utils.parse_des_key` | `133457799BBCDFF1` |
| PC-1 (79) | 64 → 56 bit | `PC1`, `permute` | `F0CCAAF556678F` |
| Chia KL₀, KR₀ (79) | 56 → 28 + 28 | `k56 >> 28`, `& 0x0FFFFFFF` | `F0CCAAF`, `556678F` |
| Dịch vòng trái rᵢ (79) | 28 → 28 | `SHIFTS`, `rotl` | `E19955F`, `AACCF1E` |
| PC-2 (79) | 56 → 48 bit | `PC2`, `permute` | K1 = `1B02EFFC7072` |
| Đệm | n byte → bội số 8 | `utils.pkcs7_pad` | `… 6F 07 07 07 07 07 07 07` |
| IP (75) | 64 → 64 | `IP`, `permute` | `CC00CCFF F0AAF0AA` |
| Expand (77) | 32 → 48 | `E`, `permute` | `7A15557A1555` |
| ⊕ khóa con (76) | 48 ⊕ 48 | `^` | `6117BA866527` |
| 8 S-box (77, 80, 81) | 48 → 32 | `S_BOX`, `sbox_sub` | `5C82B597` |
| P-box (78) | 32 → 32 | `P`, `permute` | F = `234AA9BB` |
| Vòng Feistel (76) | Lᵢ = Rᵢ₋₁, Rᵢ = Lᵢ₋₁ ⊕ F | `left, right = right, left ^ f` | R1 = `EF4A6544` |
| Đổi chỗ + IP⁻¹ (74–75) | R16‖L16 → 64 | `IP_INV`, `permute` | `85E813540F0AB405` |
| Giải mã | khóa con đảo ngược | `generate_subkeys(key)[::-1]` | → `0123456789ABCDEF` |
| Bỏ đệm | bội số 8 → n byte | `utils.pkcs7_unpad` | → `"Xin chào"` |

### Câu hỏi thầy hay hỏi (DES)

- **Khóa 64 bit sao nói 56?** 8 bit chẵn lẻ (bit cuối mỗi byte) bị PC-1 bỏ. Bằng chứng: khóa `nhom2026` và `nhom2027` cho cùng 16 khóa con.
- **Sao bảng trong code khác slide?** Slide đếm bit từ 0, code chép chuẩn FIPS đếm từ 1. Mỗi số lệch đúng 1.
- **IP có tăng độ an toàn không?** Không, chỉ là xếp lại chỗ theo bảng công khai.
- **Vì sao sau vòng 16 phải đổi chỗ lại?** Để giải mã dùng đúng hàm mã hóa, chỉ đảo thứ tự khóa con.
- **Đệm để làm gì, vì sao tròn 8 byte vẫn đệm?** DES chỉ nhận khối 8 byte. Luôn đệm để lúc bỏ đệm không nhầm dữ liệu thật với giấy độn.
- **Làm sao biết code đúng?** Ra đúng `85E813540F0AB405` của ví dụ kinh điển, khớp 16 ca thử NIST và khớp thư viện pycryptodome (`python test_runner.py`).

---

# 🔓 Bẻ khóa TinyDES: kẻ tấn công làm gì? (kĩ như trên)

> Code: `core/tinydes_core.py:242-311`. Web: trang **🕵️ Kẻ xấu bẻ khóa**, hoặc nút “Vét cạn khóa” trong **💬 An gửi Bình**. Console: `python cli.py`.

## B1. Vì sao bẻ được?

TinyDES chỉ có **256 khóa** (`00000000` → `11111111`). Máy tính thử hết 256 khóa mất khoảng **0,03 giây**.
Giống ổ khóa chỉ có 256 mã số: cứ vặn thử từ 000 trở đi là kiểu gì cũng mở được.

## B2. Kịch bản 1: kẻ tấn công biết cả bản rõ lẫn bản mã → `brute_force()`

**Vào:** bản rõ `"Hello"` + bản mã `43 61 DA DA C0` (do người gửi mã bằng khóa bí mật `11011010`)
**Ra:** danh sách khóa khớp = `["11011010"]`

**Làm gì:** lấy lần lượt từng khóa, **mã hóa thử** "Hello", so với bản mã:

| Khóa thử | Mã hóa "Hello" ra | Khớp `43 61 DA DA C0`? |
|---|---|---|
| `00000000` | `74 80 7E 7E 57` | ✘ |
| `00000001` | `77 8F 7D 7D 52` | ✘ |
| … | … | ✘ |
| `11011001` | `27 53 87 87 2E` | ✘ |
| **`11011010`** | **`43 61 DA DA C0`** | **✔ tìm thấy** |
| … (thử tiếp tới `11111111`) | | ✘ |

```python
def brute_force(plain_bytes, cipher_bytes):
    found = []
    for key in all_keys():                                   # "00000000" ... "11111111"
        if encrypt_bytes(plain_bytes, key) == cipher_bytes:  # mã thử, khớp thì giữ
            found.append(key)
    return found
```

## B3. Kịch bản 2: kẻ tấn công **chỉ** chặn được bản mã → `brute_force_ciphertext_only()`

Thực tế hơn: kẻ xấu **không biết** bản rõ. Vậy làm sao biết khóa nào đúng?
Ý tưởng: **giải mã thử với cả 256 khóa, xem bản nào "đọc được như chữ"**.

**Vào:** bản mã `43 56 36 88 FF 40 B2 56 36 A4 3E 40 DA B7 36 18 40 0B 3A` (người gửi mã "Hẹn gặp lúc 8h" bằng khóa `11011010`)
**Ra:** khóa đoán được + tin nhắn

| Hạng | Khóa thử | Giải mã ra | Điểm "giống chữ" |
|---|---|---|---|
| **1** | **`11011010`** | **`Hẹn gặp lúc 8h`** | **1.526** |
| 2 | `01100001` | ký tự rác, không đọc được | -985 |
| 3 | `01110100` | ký tự rác, không đọc được | -986 |

**Chấm điểm thế nào?** (`readability_score`, `core/tinydes_core.py:272`)

| Gặp ký tự | Điểm |
|---|---|
| Không đọc được bằng UTF-8 (rác) | khoảng −1000 (loại ngay) |
| Khoảng trắng | +3 |
| Chữ thường | +2 |
| Chữ hoa, chữ số, dấu câu | +1 |
| Ký tự điều khiển (không in ra được) | −5 |

Cuối cùng chia cho số byte để tin dài và tin ngắn so được với nhau. Khóa đúng ra câu toàn chữ và khoảng trắng nên điểm cao nhất.

**Khi nào thất bại?** Tin quá ngắn (ví dụ `Hi`). Trong 256 khóa sẽ có khóa sai tình cờ ra 2 ký tự "trông như chữ". Tin càng dài thì càng chắc.

**Bài học:** khóa ngắn thì **không an toàn**, dù thuật toán có phức tạp thế nào. DES có 2⁵⁶ khóa, nhiều hơn rất nhiều, nhưng năm 1998 máy chuyên dụng đã phá được trong vài ngày. Vì thế ngày nay dùng AES (khóa 128–256 bit, slide 84).

---

# ⭐ ĐỌC PHẦN NÀY TRƯỚC — giải thích bằng lời thường

> Phần này **không cần biết code**. Đọc xong phần này rồi mới xuống các phần chi tiết bên dưới.

## A. Năm từ cần biết

| Từ | Hiểu đơn giản | Ví dụ |
|---|---|---|
| **bit** | 1 ô chỉ chứa **0 hoặc 1**, giống công tắc tắt / bật | `1` |
| **byte** | **8 bit** đứng cạnh nhau. Một chữ cái = 1 byte | chữ `H` = `01001000` |
| **hex** | Cách viết **gọn**: cứ 4 bit viết thành 1 ký tự (0–9, A–F). 1 byte = 2 ký tự hex | `0100 1000` → `4 8` → `48` |
| **bản rõ / bản mã** | Dữ liệu **trước** / **sau** khi mã hóa | `01011100` / `10010010` |
| **khóa** | "Mật khẩu" dùng để mã hóa. Ai có khóa mới giải mã được | `10011010` |

TinyDES và DES là **mã hóa khối**: cắt dữ liệu thành từng khúc bằng nhau (TinyDES 8 bit, DES 64 bit) rồi xử lý từng khúc.

## B. Cả hai thuật toán chỉ dùng đúng 4 "động tác"

**1. Hoán vị = xếp lại chỗ đứng theo sơ đồ.**
Tài liệu đánh số bit **từ 0**: dãy `b0 b1 b2 b3`. P-box `b2 b0 b3 b1` nghĩa là: *"người đứng số 2 lên đầu, rồi người số 0, rồi số 3, rồi số 1"*.

```
b0 b1 b2 b3     --P-box b2 b0 b3 b1-->   b2 b0 b3 b1
1  0  0  0      --P-box-->               0  1  0  0
```

- Sơ đồ có **số lặp lại** thì một người đứng 2 chỗ, dãy **dài ra**. Đây là **mở rộng** (Expand của TinyDES, E của DES).
  `b0 b1 b2 b3` với Expand `b2 b3 b1 b2 b1 b0` → 4 bit thành 6 bit. Ví dụ `0110` → `101110`.
- Sơ đồ **thiếu số** thì có người bị bỏ, dãy **ngắn lại**. Đây là **nén** (Compress của TinyDES, PC-1, PC-2 của DES).

**2. Dịch vòng = vòng quay ngựa gỗ:** người đứng đầu chạy ra cuối. `1001` → `0011`

**3. XOR (⊕) = so từng cặp bit: giống nhau → 0, khác nhau → 1.**

```
  0 1 0 1
⊕ 0 1 0 0
= 0 0 0 1
```

Điều quan trọng nhất của XOR: **XOR 2 lần với cùng một giá trị thì trở về như cũ.**
`0101 ⊕ 0100 = 0001`, rồi `0001 ⊕ 0100 = 0101` (về lại ban đầu). **Nhờ vậy mới giải mã được.**

**4. S-box = tra bảng**, giống tra bảng cửu chương. TinyDES có **1 bảng 4 hàng × 16 cột**, nhận 6 bit `b0…b5`:
- lấy **bit đầu + bit cuối** (`b0 b5`) làm **số hàng** (0–3);
- lấy **4 bit ở giữa** (`b1 b2 b3 b4`) làm **số cột** (0–F);
- đọc con số trong ô đó (viết hệ 16), đổi ra 4 bit.

Ví dụ trong tài liệu (trang 70): `101010` → hàng = `1`+`0` = `10` = hàng 2; cột = `0101` = cột 5. Ô hàng 2 cột 5 là **6** = `0110`.
Đây là bước làm dữ liệu "rối" nhất, người ngoài khó đoán ngược.

## C. TinyDES kể như một câu chuyện (ví dụ trong tài liệu, trang 72)

> Khóa `10011010`, bản rõ `01011100` (hex 5C). Mục tiêu: ra bản mã `10010010` (hex 92).

**Bước 1: Từ 1 chìa khóa 8 bit làm ra 3 chìa nhỏ K1, K2, K3 (mỗi chìa 6 bit).** TinyDES có 3 vòng, mỗi vòng dùng 1 chìa nhỏ.

```
10011010  --cắt đôi-->                 KL0 = 1001 | KR0 = 1010
          --mỗi nửa xoay 1 bit-->      KL1 = 0011 | KR1 = 0101   --Compress-->  K1 = 101110
          --mỗi nửa xoay thêm 2 bit--> KL2 = 1100 | KR2 = 0101   --Compress-->  K2 = 110011
          --mỗi nửa xoay thêm 1 bit--> KL3 = 1001 | KR3 = 1010   --Compress-->  K3 = 001001
```

#### 🔎 Dòng "Compress → K1 = 101110" nghĩa là gì?

Compress làm 2 việc cùng lúc: **chọn ra 6 trong 8 bit** và **xếp lại thứ tự**. Công thức trong tài liệu: **`k5 k1 k3 k2 k7 k0`**.

**Đầu vào** là `KL1 KR1 = 0011 0101`, đánh số từ 0 đến 7:

```
Vị trí:  k0 k1 k2 k3 k4 k5 k6 k7
Bit:      0  0  1  1  0  1  0  1
```

| Bit thứ … của K1 | Lấy từ | Giá trị |
|---|---|---|
| 1 | k5 | **1** |
| 2 | k1 | **0** |
| 3 | k3 | **1** |
| 4 | k2 | **1** |
| 5 | k7 | **1** |
| 6 | k0 | **0** |

Ghép cột cuối từ trên xuống: **`1 0 1 1 1 0`** → **K1 = `101110`** ✔

- **Vì sao gọi là "nén"?** Công thức **không có k4 và k6**, nên 2 bit đó bị bỏ. 8 bit chỉ còn 6.
- **Vì sao cần đúng 6 bit?** Trong mỗi vòng, khóa con được **XOR với 6 bit** (kết quả Expand: nửa phải 4 bit kéo dài thành 6). Hai dãy XOR với nhau phải dài bằng nhau.

Trong code, việc này là đúng một dòng ở `core/tinydes_core.py`:

```python
k = permute(kl + kr, COMPRESS)   # COMPRESS = [5, 1, 3, 2, 7, 0]  ->  "00110101" -> "101110"
```

**Bước 2: Chia bản rõ làm 2 nửa: Trái (L0) và Phải (R0).** TinyDES **không có** hoán vị khởi tạo.

```
01011100  -->  L0 = 0101, R0 = 1100
```

**Bước 3: Vòng 1.** Quy tắc vàng của Feistel: **L mới = R cũ**, **R mới = L cũ ⊕ F(R cũ, K)**.

```
lấy R0 = 1100, kéo dài thành 6 bit (Expand b2 b3 b1 b2 b1 b0)  → 001011
trộn với chìa K1 = 101110 (XOR)                                  → 100101
tra S-box: hàng b0b5 = 11 = 3, cột b1..b4 = 0010 = 2              → 8 = 1000
xáo nhẹ (P-box b2 b0 b3 b1)                                       → 0100   ← gọi là F1
R1 = L0 ⊕ F1 = 0101 ⊕ 0100                                        → 0001
L1 = R0                                                           → 1100
Kết quả vòng 1: L1 R1 = 1100 0001
```

**Bước 4: Vòng 2**, y hệt nhưng dùng **K2 = 110011**: Expand(0001) = `010000` → ⊕K2 = `100011` → S-box = `1100` → F2 = `0101` → **L2 R2 = `0001 1001`**

**Bước 5: Vòng 3**, dùng **K3 = 001001**: Expand(1001) = `010001` → ⊕K3 = `011000` → S-box = `0101` → F3 = `0011` → **L3 R3 = `1001 0010`**

**Bước 6: Ghép L3 R3** → **`10010010`** = hex **92** = **BẢN MÃ** ✔ (đúng lời giải trang 72)

**Giải mã thế nào?** Đi **ngược** từ vòng 3 về vòng 1, dùng **K3, K2, K1** (tài liệu trang 66):
**R cũ = L mới**, **L cũ = R mới ⊕ F(L mới, K)**.
Giống cửa khóa 3 lớp: khóa lớp K1, K2, K3 thì lúc mở phải mở lớp ngoài cùng K3 trước.
Mỗi vòng chỉ XOR thêm F vào một nửa, mà XOR 2 lần thì mất, nên đi ngược là gỡ được từng vòng.

## D. DES = TinyDES phóng to

Cùng 4 động tác và cùng cấu trúc Feistel, chỉ là **to hơn** và **nhiều vòng hơn**:

| | TinyDES (đồ chơi) | DES (thật) |
|---|---|---|
| Mỗi khúc dữ liệu | 8 bit | 64 bit (8 chữ cái) |
| Chìa khóa | 8 bit | 64 bit (56 bit hiệu dụng) |
| Số vòng | 3 | **16** |
| Số chìa nhỏ | 3 (K1, K2, K3), mỗi chìa 6 bit | 16 (K1 … K16), mỗi chìa 48 bit |
| Hoán vị đầu / cuối | không có | IP, IP⁻¹ |
| Số bảng S-box | 1 (chính là hộp S1 của DES) | 8 |

DES có thêm một việc là **đệm (padding)**. Dữ liệu phải chia đủ khúc 8 byte. Giống đóng hàng vào thùng 8 ô:
- thiếu ô nào thì nhét giấy độn vào;
- **trên mỗi tờ giấy độn ghi số tờ đã độn** (độn 7 tờ thì mỗi tờ ghi số 7);
- lúc mở thùng, nhìn tờ cuối thấy số 7 là biết bỏ đi 7 tờ.

```
"Xin chào" = 9 byte → thêm 7 byte, mỗi byte = 07 → đủ 16 byte = 2 khúc
```

## E. Code chạy thế nào? Ví như một nhà hàng

| Trong nhà hàng | Trong đồ án | Việc làm |
|---|---|---|
| Khách gọi món | **Trình duyệt** | Bạn nhập dữ liệu, bấm "Mã hóa" |
| Bồi bàn | **`app.py`** | Nhận "order", đưa vào bếp, mang món ra. **Không tự nấu** |
| Đầu bếp | **`core/`** | Làm 6 bước mã hóa thật sự |
| Cái đĩa trình bày | **`templates/*.html`** + `static/style.css` | Bày kết quả cho đẹp |
| Sổ ghi chép | **`db.py`** (`history.db`) | Ghi lại đã phục vụ món gì (không ghi khóa) |

Thứ tự một lần bấm "Mã hóa":

```
1. Bấm Run app.py          → web bật lên, đứng chờ
2. Mở trang, nhập, bấm nút  → trình duyệt gửi dữ liệu cho app.py
3. app.py                  → đưa dữ liệu cho core/
4. core/                   → làm 6 bước, trả kết quả
5. app.py                  → nhét kết quả vào trang HTML, gửi về trình duyệt
```

## F. Nên đọc code theo thứ tự nào?

1. `core/tinydes_core.py`, đọc theo thứ tự: các bảng `EXPAND`, `SBOX`, `PBOX`, `COMPRESS`, `SHIFTS` → `permute` → `left_shift` → `xor` (3 động tác) → `generate_keys` (Bước 1) → `sbox_lookup` → `f_function` → `_encrypt_block` (3 vòng) → `_decrypt_block` → `encrypt` / `decrypt`. Hoặc đọc class `TinyDES` ở cuối file: cùng thuật toán, viết liền một mạch giống lời giải trang 72.
2. `core/des_core.py`: chỉ cần đọc `permute`, `generate_subkeys`, `feistel_f`, `crypt_block_verbose`. Phần "bản chạy nhanh" **có thể bỏ qua**, nó chỉ để chạy nhanh hơn, kết quả giống hệt.
3. `core/utils.py`: đệm và chia khúc.
4. `app.py`: chỉ cần hiểu một hàm, ví dụ `sdes_demo()`. Các hàm khác cùng khuôn.

## G. Câu thầy hay hỏi, trả lời ngắn

| Câu hỏi | Trả lời |
|---|---|
| Vì sao giải mã được? | Mỗi vòng chỉ làm L ⊕ F; XOR 2 lần với cùng giá trị thì về như cũ, nên đi ngược các vòng với khóa ngược (K3, K2, K1) là gỡ được từng vòng |
| Vì sao mỗi vòng chỉ một nửa bị đổi mà vẫn an toàn? | Mỗi vòng hai nửa đổi chỗ (L mới = R cũ), nên vòng sau tới lượt nửa kia. DES có 16 vòng nên mọi bit bị trộn rất nhiều lần |
| S-box để làm gì? | Là bước **không tuyến tính** (tra bảng), làm quan hệ giữa bản rõ, khóa và bản mã trở nên rối, khó đoán ngược |
| Vì sao TinyDES / DES không còn an toàn? | TinyDES chỉ có 256 khóa, thử hết chưa tới 1 giây, kể cả khi chỉ có bản mã (trang Bẻ khóa). DES có 2⁵⁶ khóa, máy chuyên dụng đã phá được từ năm 1998 |
| Làm sao biết code đúng? | TinyDES ra đúng từng giá trị trung gian của lời giải trang 72 (bản mã `10010010`); DES khớp 16 ca NIST và khớp thư viện pycryptodome (Passed 43/43) |
| Có dùng thư viện mã hóa không? | Không. Thư mục `core/` tự viết hết; thư viện chỉ dùng để **so sánh** trong phần kiểm thử |

---

## 0. Bức tranh tổng thể

```
Người dùng nhập (web / console)
        │
        ▼
GIAO DIỆN  (app.py, cli.py)          ← chỉ nhận dữ liệu và hiển thị
        │  gọi hàm
        ▼
THUẬT TOÁN (thư mục core/)           ← nơi mã hóa / giải mã thật sự
   ├── tinydes_core.py   TinyDES (bản thu nhỏ, theo tài liệu trang 67-72)
   ├── des_tables.py     các bảng chuẩn của DES
   ├── des_core.py       DES 64 bit
   └── utils.py          đệm PKCS#7, chia khối, đọc/ghi tệp
```

## 0.1. `app.py` chạy hàm nào? Điều gì xảy ra khi vào http://127.0.0.1:5000/

`app.py` **không tự chạy hàm mã hóa nào cả**. File này chỉ làm 2 việc:
(1) lúc khởi động thì chuẩn bị và **đăng ký** địa chỉ nào ứng với hàm nào;
(2) sau đó **đứng chờ**, trình duyệt gọi địa chỉ nào thì chạy hàm tương ứng.

### Giai đoạn 1 — Bấm Run `app.py` (chạy đúng 1 lần)

Python đọc `app.py` từ trên xuống dưới:

| Thứ tự | Dòng code | Làm gì |
|---|---|---|
| 1 | `from core import des_core, tinydes_core, utils` | Nạp phần thuật toán. Riêng `des_core` tính sẵn các **bảng tra** (`_IP_LUT`, `_FP_LUT`, `_SP`) ngay lúc import để mã hóa tệp nhanh |
| 2 | `app = Flask(__name__)` | Tạo ứng dụng web |
| 3 | `app.config["MAX_CONTENT_LENGTH"] = 20 MB` | Giới hạn kích thước tệp tải lên |
| 4 | `db.init_db()` | Mở `history.db`, tạo bảng `history` nếu chưa có |
| 5 | `DOWNLOADS = {}` và các hằng số | Chỗ giữ tạm tệp kết quả trong RAM, số khối in log… |
| 6 | `def render(...)`, `def parse_sdes_data(...)`… | Định nghĩa hàm phụ, **chưa chạy** |
| 7 | Các dòng `@app.get("/...")` / `@app.post("/...")` | **Đăng ký** bảng "địa chỉ → hàm", **chưa chạy** hàm nào |
| 8 | `if __name__ == "__main__": app.run(debug=True)` | Bật server ở cổng 5000 rồi **đứng chờ**. Lúc này hiện dòng `Running on http://127.0.0.1:5000` |

Bảng đăng ký sau bước 7:

| Địa chỉ | Phương thức | Hàm | Việc làm |
|---|---|---|---|
| `/` | GET | `index()` | Trang chủ |
| `/theory` | GET | `theory()` | Trang lý thuyết |
| `/flow` | GET | `flow()` | Trang luồng chạy code |
| `/sdes` | GET | `sdes_page()` | Form TinyDES trống |
| `/sdes_demo` | **POST** | `sdes_demo()` | **Mã hóa / giải mã TinyDES** |
| `/bruteforce` | GET | `bruteforce_page()` | Form bẻ khóa trống |
| `/sdes_bruteforce` | **POST** | `sdes_bruteforce()` | **Vét cạn 256 khóa** (biết trước bản rõ) |
| `/sdes_bruteforce_cipher` | **POST** | `sdes_bruteforce_cipher()` | **Kịch bản chỉ chặn được bản mã**: vét cạn + chấm điểm |
| `/des` | GET | `des_page()` | Form DES trống |
| `/des_file` | **POST** | `des_file()` | **Mã hóa / giải mã DES văn bản, tệp** |
| `/download/<token>` | GET | `download()` | Tải tệp kết quả |
| `/benchmark` | GET / **POST** | `benchmark_page()` / `benchmark()` | Đo thời gian |
| `/tests` | GET / **POST** | `tests_page()` / `tests_run()` | Chạy bộ kiểm thử |
| `/history` | GET | `history()` | Xem lịch sử |
| `/history/clear` | **POST** | `history_clear()` | Xóa lịch sử |
| `/huong-dan` | GET | `guide()` | Kịch bản thuyết trình + hướng dẫn |
| `/doc-code` | GET | `code_guide()` | Đọc code cùng thuật toán (đọc mã nguồn thật bằng `inspect`) |
| `/chat` | GET | `chat()` | Khung phòng chat An → Bình |
| `/api/chat/send` | **POST** (JSON) | `chat_send()` | **An mã hóa, Bình giải mã** |
| `/api/chat/attack` | **POST** (JSON) | `chat_attack()` | **Kẻ xấu vét cạn khóa** |
| `/api/chat/tamper` | **POST** (JSON) | `chat_tamper()` | **Kẻ xấu sửa 1 bit rồi chuyển tiếp** |

- **GET** = chỉ mở trang.
- **POST** = gửi dữ liệu từ form lên server. Chỉ các hàm POST mới thật sự gọi vào `core/` để mã hóa hay giải mã.
- **POST (JSON)** = trang chat gửi dữ liệu bằng JavaScript, nhận lại JSON, **không tải lại trang** (xem V18, V19).

### Giai đoạn 2 — Trình duyệt vào `http://127.0.0.1:5000/`

```
Trình duyệt gửi:  GET /
        │
        ▼
Flask tra bảng đăng ký:  "/" + GET  →  hàm index()
        │
        ▼
index():
  ├── from test_runner import DES_CASES        3 cặp (bản rõ, khóa) mẫu
  ├── với mỗi cặp:
  │     ├── des_core.encrypt_block(pt, key)    ← DES nhóm tự code
  │     └── LibDES.new(key).encrypt(pt)        ← thư viện, CHỈ để so sánh
  │           → ok = hai kết quả có giống nhau không
  ├── db.get_stats()                           đếm số lượt TinyDES, DES, Brute-force… trong history.db
  └── render("home.html", tests=..., stats=..., total=...)
        │
        ▼
render(template, **ctx):
  ├── form = request.form (nếu POST) hoặc request.args (nếu GET)   → điền lại ô nhập
  └── render_template("home.html", sbox=SBOX, form=form, ...)
        │
        ▼
home.html:
  ├── {% extends "base.html" %}       lấy khung chung: menu trái, tiêu đề, footer
  ├── {% set active = 'index' %}      tô sáng mục "Trang chủ" trên menu
  └── điền dữ liệu vào {{ ... }}, {% for ... %}:
        • bảng "Kiểm thử DES với pycryptodome"  ← tests
        • ô "Thống kê sử dụng"                  ← stats
        │
        ▼
Trả về trình duyệt 1 trang HTML hoàn chỉnh
  → trình duyệt thấy <link href="/static/style.css"> → gửi thêm GET /static/style.css
  → Flask tự trả tệp trong thư mục static/ → trang hiển thị có màu sắc
```

Mỗi lần vào trang, cửa sổ Run của PyCharm in ra:

```
"GET / HTTP/1.1" 200
"GET /static/style.css HTTP/1.1" 200      (hoặc 304 = trình duyệt dùng lại bản đã lưu)
```

### Giai đoạn 3 — Bấm nút trên một trang (ví dụ TinyDES từng bước → Mã hóa)

```
GET  /sdes          → sdes_page()  → render("sdes.html")                   hiện form trống
                                   │  người dùng nhập khóa, bản rõ, bấm "Mã hóa"
                                   ▼
POST /sdes_demo     → sdes_demo():
                        1. request.form.get(...)              đọc sdes_key, sdes_input, sdes_fmt, sdes_action
                        2. parse_sdes_data(...)               chuỗi nhập → danh sách khối 8 bit
                        3. tinydes_core.generate_keys(key)    ← GỌI VÀO core: B1 sinh K1, K2, K3
                        4. tinydes_core.encrypt(blk, key)     ← GỌI VÀO core: B2 mã hóa từng khối
                        5. tinydes_core.trace(...)            ← dữ liệu vẽ từng ô bit
                        6. tinydes_core.decrypt_bytes(...)    ← giải mã ngược để kiểm tra khớp
                        7. db.add_history(...)                ghi lịch sử (không ghi khóa)
                        8. render("sdes.html", sdes=kết_quả)  trả trang có kết quả
                      (nếu dữ liệu sai → ValueError → render("sdes.html", sdes_error=...))
```

Các nút khác đi theo cùng khuôn: **đọc form → gọi `core/` → ghi lịch sử → `render(...)`**:

| Nút | Hàm POST | Gọi vào `core/` |
|---|---|---|
| DES → Mã hóa / Giải mã | `des_file()` | `utils.parse_des_key` → `des_core.generate_subkeys` → `utils.des_encrypt_bytes` / `des_decrypt_bytes` → `des_core.crypt_block_verbose` (log 16 vòng) |
| Kẻ xấu bẻ khóa | `sdes_bruteforce()` | vòng `for key in all_keys()` (256 khóa): `generate_keys` + `encrypt_bytes`, so với bản mã |
| Kịch bản chỉ có bản mã | `sdes_bruteforce_cipher()` | `encrypt_bytes` (người gửi) → `brute_force_ciphertext_only` (kẻ tấn công) |
| Chạy đo thời gian | `benchmark()` | `utils.des_encrypt_bytes` / `des_decrypt_bytes` với 1 KB → 1 MB |
| Chạy kiểm thử | `tests_run()` | `test_runner.run_all()` |
| Tải về | `download(token)` (GET) | không gọi `core/`, chỉ lấy dữ liệu đã lưu trong `DOWNLOADS` |

---

## 0.2. Khuôn chung của thuật toán

Cả TinyDES và DES đều theo cùng một khuôn **3 bước lớn**:

| Bước | Việc làm | Ghi nhớ |
|---|---|---|
| **B1** | **Sinh khóa con** từ khóa gốc | Làm 1 lần, dùng cho mọi khối |
| **B2** | **Mã hóa**: các vòng Feistel (DES có thêm IP trước và IP⁻¹ sau) | Dùng khóa con theo thứ tự xuôi |
| **B3** | **Giải mã**: đi **ngược** các vòng của B2 | Dùng khóa con theo thứ tự **ngược** |

Lý do giải mã được: mỗi vòng Feistel chỉ XOR một nửa với F(nửa kia, khóa), mà XOR hai lần với cùng một giá trị
thì trở về như cũ. TinyDES viết đúng công thức giải mã trang 66: R(i-1) = L(i), L(i-1) = R(i) ⊕ F(L(i), K(i)).

---

# PHẦN 1. TinyDES — file `core/tinydes_core.py`

> Nguồn: tài liệu *Chương 2 - Mã hoá khoá đối xứng*, mục 3.2 "Hệ mã TinyDES", trang 67–72.

## 1.1. Input / Output

| | Dạng | Ví dụ (BTVD trang 72) |
|---|---|---|
| **Input 1**: bản rõ | chuỗi **8 bit** | `01011100` (hex 5C) |
| **Input 2**: khóa | chuỗi **8 bit** | `10011010` |
| **Output**: bản mã | chuỗi **8 bit** | `10010010` (hex 92) |

Code biểu diễn bit bằng chuỗi ký tự `'0'`/`'1'` để dễ in ra và dễ nhìn khi thuyết trình.
Bit đánh số **từ 0** như tài liệu: `"0110"` có `b0 = 0, b1 = 1, b2 = 1, b3 = 0`.

Các bảng (viết thẳng theo công thức trong tài liệu):

| Tên trong code | Công thức trong tài liệu | Giá trị |
|---|---|---|
| `EXPAND` | b2 b3 b1 b2 b1 b0 (4 → 6 bit) | `[2, 3, 1, 2, 1, 0]` |
| `PBOX` | b2 b0 b3 b1 | `[2, 0, 3, 1]` |
| `COMPRESS` | k5 k1 k3 k2 k7 k0 (8 → 6 bit) | `[5, 1, 3, 2, 7, 0]` |
| `SHIFTS` | dịch 1, 2, 1 bit ở vòng 1, 2, 3 | `[1, 2, 1]` |
| `SBOX` | bảng 4 × 16 trang 70 | hàng 0: `E 4 D 1 2 F B 8 3 A 6 C 5 9 0 7` … |

## 1.2. Hàm được gọi đầu tiên

```python
cipher, log = encrypt("01011100", "10011010")    # → "10010010"
```

`encrypt(plain_8bit, key_8bit)` làm lần lượt:

1. `is_bits(...)`: kiểm tra bản rõ đúng 8 bit, sai thì báo lỗi.
2. `generate_keys(key)` → sinh K1, K2, K3 (**B1**).
3. `_encrypt_block(plain, keys)` → 3 vòng Feistel (**B2**).
4. Trả về `(bản mã, log_trung_gian)`. `log_trung_gian` là danh sách mọi thanh ghi trung gian, dùng để in ra màn hình.

Cây gọi hàm:

```
encrypt(plain, key)
├── generate_keys(key)                    B1: sinh khóa
│   ├── KL0, KR0 = key[:4], key[4:]
│   └── lặp 3 lần (SHIFTS = 1, 2, 1):
│       ├── left_shift(KL, s), left_shift(KR, s)
│       └── permute(KL + KR, COMPRESS)  → Ki
└── _encrypt_block(plain, keys)           B2: mã hóa
    ├── L, R = plain[:4], plain[4:]
    └── lặp 3 vòng:
        ├── f_function(R, Ki)
        │   ├── permute(R, EXPAND)        4 → 6
        │   ├── xor(..., Ki)
        │   ├── sbox_lookup(...)          6 → 4
        │   └── permute(..., PBOX)        = F
        └── L, R = R, xor(L, F)
    → bản mã = L3 + R3
```

Các hàm tiện ích dùng xuyên suốt:

| Hàm | Làm gì | Ví dụ |
|---|---|---|
| `permute(bits, table)` | Bit thứ i của kết quả = bit `b[table[i]]` của đầu vào (đánh số từ 0) | `permute("0110", EXPAND)` = `101110` |
| `left_shift(bits, n)` | Dịch **vòng** trái n bit | `left_shift("1001", 1)` = `0011` |
| `xor(a, b)` | XOR từng bit | `xor("001011", "101110")` = `100101` |

---

## 1.3. B1 — Sinh khóa: `generate_keys(key_8bit)`

**Input:** khóa 8 bit `10011010`  **Output:** `(K1, K2, K3)` = `(101110, 110011, 001001)`

| # | Thao tác | Kết quả | Giải thích |
|---|---|---|---|
| 1 | Chia đôi khóa | KL0 = `1001`, KR0 = `1010` | 4 bit trái, 4 bit phải |
| 2 | Vòng 1: dịch vòng trái **1** bit | KL1 = `0011`, KR1 = `0101` | `1001` → `0011`, `1010` → `0101` |
| 3 | **Compress** → **K1** | **`101110`** | k5 k1 k3 k2 k7 k0 của `00110101` |
| 4 | Vòng 2: dịch vòng trái **2** bit (từ bước 2) | KL2 = `1100`, KR2 = `0101` | |
| 5 | **Compress** → **K2** | **`110011`** | |
| 6 | Vòng 3: dịch vòng trái **1** bit (từ bước 4) | KL3 = `1001`, KR3 = `1010` | |
| 7 | **Compress** → **K3** | **`001001`** | |

Lưu ý: mỗi lần dịch đều dịch **tiếp từ kết quả lần trước**. Tổng 1 + 2 + 1 = 4 bit nên KL3 KR3 quay về đúng KL0 KR0.

---

## 1.4. B2 — Mã hóa: `_encrypt_block(bits8, keys)`

**Input:** `01011100`, K1 = `101110`, K2 = `110011`, K3 = `001001`  **Output:** `10010010`

Chia đôi: **L0 = `0101`, R0 = `1100`**. Mỗi vòng: **L(i) = R(i-1)**, **R(i) = L(i-1) ⊕ F(R(i-1), K(i))**, với
**F(R, K) = P-box( S-box( Expand(R) ⊕ K ) )** (hàm `f_function`).

| | Vòng 1 (K1 = `101110`) | Vòng 2 (K2 = `110011`) | Vòng 3 (K3 = `001001`) |
|---|---|---|---|
| R(i-1) | `1100` | `0001` | `1001` |
| `permute(R, EXPAND)` | `001011` | `010000` | `010001` |
| `xor(…, Ki)` | `100101` | `100011` | `011000` |
| `sbox_lookup` (hàng, cột) | hàng 3, cột 2 → 8 = `1000` | hàng 3, cột 1 → C = `1100` | hàng 0, cột C → 5 = `0101` |
| `permute(…, PBOX)` = F | `0100` | `0101` | `0011` |
| R(i) = L(i-1) ⊕ F | `0101` ⊕ `0100` = `0001` | `1100` ⊕ `0101` = `1001` | `0001` ⊕ `0011` = `0010` |
| L(i) = R(i-1) | `1100` | `0001` | `1001` |
| **Kết quả vòng** | **`1100 0001`** | **`0001 1001`** | **`1001 0010`** |

Cách tra S-box (hàm `sbox_lookup`), ví dụ vòng 1 với `100101`:
hàng = b0 b5 = `1` `1` = 3; cột = b1 b2 b3 b4 = `0010` = 2 → `SBOX[3][2]` = 8 = `1000`.

Bảng S-box (trang 70):

```
b0b5 \ b1b2b3b4   0 1 2 3 4 5 6 7 8 9 A B C D E F
       0          E 4 D 1 2 F B 8 3 A 6 C 5 9 0 7
       1          0 F 7 4 E 2 D 1 A 6 C B 9 5 3 8
       2          4 1 E 8 D 6 2 B F C 9 7 3 A 5 0
       3          F C 8 2 4 9 1 7 5 B 3 E A 0 6 D
```

Bản mã **C = L3 R3 = `1001 0010`** = hex **92** ✔ khớp lời giải trang 72. TinyDES **không có** hoán vị khởi tạo / kết thúc.

Tóm tắt một dòng:

```
01011100 →vòng 1→ 11000001 →vòng 2→ 00011001 →vòng 3→ 10010010
```

---

## 1.5. B3 — Giải mã: `decrypt(cipher_8bit, key_8bit)`

```python
plain, log = decrypt("10010010", "10011010")   # → "01011100"
```

Hàm này gọi lại `generate_keys`, rồi `_decrypt_block` đi **ngược** vòng 3 → 1 theo công thức trang 66:
**R(i-1) = L(i)**, **L(i-1) = R(i) ⊕ F(L(i), K(i))**.

| Bước | Giá trị |
|---|---|
| Bản mã L3 R3 | `1001 0010` |
| Vòng 3 (dùng **K3**) | F(L3) = `0011`; L2 = R3 ⊕ F = `0010` ⊕ `0011` = `0001`; R2 = L3 = `1001` → `0001 1001` |
| Vòng 2 (dùng **K2**) | F(L2) = `0101`; L1 = `1001` ⊕ `0101` = `1100`; R1 = `0001` → `1100 0001` |
| Vòng 1 (dùng **K1**) | F(L1) = `0100`; L0 = `0001` ⊕ `0100` = `0101`; R0 = `1100` → `0101 1100` |
| Bản rõ L0 R0 | **`01011100`** ← đúng bản rõ ban đầu ✔ |

Thấy rõ: các giá trị khi giải mã đi **ngược lại** đúng các giá trị lúc mã hóa.

---

## 1.6. TinyDES với văn bản (ví dụ "Hello")

`encrypt_bytes(data, key)`: mỗi **byte** (8 bit) là một khối, mã hóa độc lập.

```
"Hello" → byte 48 65 6C 6C 6F → mỗi byte qua _encrypt_block → 67 B3 20 20 A2   (khóa 10011010)
'H' = 0x48 = 01001000 → 01100111 = 0x67
```

Giải mã: `decrypt_bytes` làm ngược lại từng byte.

## 1.7. Các hàm phụ cho phần hiển thị

| Hàm | Dùng để |
|---|---|
| `trace(block, key, decrypt=False)` | Trả về **toàn bộ** thanh ghi trung gian dưới dạng dữ liệu có cấu trúc. Web dùng hàm này để vẽ từng ô bit |
| `print_trace(t)` | In các bước ra console (`python core/tinydes_core.py`) |
| class `TinyDES` | Cùng thuật toán viết dạng class: `encrypt(p, k, verbose=True)` in từng bước đúng dạng lời giải trang 72. Dùng trong `python tinydes_menu.py`. `test_runner.py` kiểm tra class cho kết quả giống hệt các hàm trên cả 65 536 cặp |
| `brute_force(plain, cipher)` | Thử 256 khóa `00000000` → `11111111`, khóa nào cho đúng bản mã thì giữ lại |
| `readability_score(data)` | Chấm điểm dãy byte giống văn bản tới mức nào: không phải UTF-8 → rất âm; khoảng trắng +3, chữ thường +2, chữ hoa / số / dấu câu +1, ký tự điều khiển −5; chia cho số byte |
| `brute_force_ciphertext_only(cipher, top=5)` | Giải mã thử với 256 khóa, xếp theo `readability_score`, trả 5 ứng viên điểm cao nhất |

### 1.8. Kịch bản: kẻ tấn công chỉ chặn được bản mã

```
NGƯỜI GỬI    "Hẹn gặp ở cổng trường lúc 8h tối" + khóa 11011010 --encrypt_bytes--> bản mã 46 byte
                                         │ gửi qua mạng
KẺ TẤN CÔNG  chặn được bản mã, KHÔNG biết bản rõ, KHÔNG biết khóa
             for key in 256 khóa: giải mã thử → chấm điểm
               hạng 1: 11011010  điểm 1.5   → "Hẹn gặp ở cổng trường lúc 8h tối"
               hạng 2: 01100001  điểm -969  → "�..."   (rác, không phải UTF-8)
KẾT LUẬN     khóa hạng 1 = khóa thật → thông điệp bị lộ, mất chưa tới 1 giây
```

- **Vì sao nhận ra được khóa đúng?** Giải mã sai khóa gần như luôn ra byte rác (không đọc được bằng UTF-8, có ký tự điều khiển). Chỉ khóa đúng mới ra câu toàn chữ cái và khoảng trắng.
- **Khi nào thất bại?** Thông điệp quá ngắn (VD `Hi`, `OK`): trong 256 khóa sẽ có khóa sai tình cờ cho ra 2 chữ cái "trông như chữ", nên khóa thật có thể không đứng hạng 1. Thông điệp càng dài thì càng chắc chắn.
- Trong 256 khóa TinyDES, mỗi khóa cho một cách mã hóa byte khác nhau (đã kiểm tra), nên với bản mã đủ dài thì chỉ còn đúng 1 khóa đứng đầu.
- Chạy: trang **🕵️ Kẻ xấu bẻ khóa** → *Kịch bản 1*, nút “Vét cạn khóa” ở **💬 An gửi Bình**, hoặc `python cli.py` → mục 5.

---

# PHẦN 2. DES chuẩn — `core/des_core.py` + `core/utils.py`

## 2.1. Input / Output

| | Dạng | Ví dụ |
|---|---|---|
| **Input 1**: dữ liệu | bytes bất kỳ (văn bản, ảnh, tệp…) | `"Xin chào"` hoặc `0123456789ABCDEF` (1 khối) |
| **Input 2**: khóa | 8 ký tự hoặc 16 ký tự hex | `133457799BBCDFF1` |
| **Output**: bản mã | bytes, độ dài là bội của 8 | `85E813540F0AB405` |

Khác TinyDES: DES xử lý theo **số nguyên 64 bit** (Python `int`) thay vì chuỗi `'0'/'1'`, để chạy đủ nhanh với tệp lớn.

## 2.2. Hàm được gọi đầu tiên

```python
from core import utils
key = utils.parse_des_key("133457799BBCDFF1")     # → 8 byte
cipher = utils.des_encrypt_bytes(data, key)        # mã hóa
plain  = utils.des_decrypt_bytes(cipher, key)      # giải mã
```

Cây gọi hàm khi **mã hóa**:

```
des_encrypt_bytes(data, key)                       core/utils.py
├── pkcs7_pad(data)                                đệm cho đủ bội số 8 byte
├── des_core.generate_subkeys(key)                 B1: sinh 16 khóa con
│   ├── permute(key64, PC1, 64)     → 56 bit → C0, D0
│   └── lặp 16 lần: rotl(C), rotl(D) theo SHIFTS → permute(C‖D, PC2, 56) → Ki
└── _crypt_blocks(data, subkeys)
    ├── des_core.prepare_keys(subkeys)             tách mỗi khóa con thành 8 nhóm 6 bit
    ├── split_blocks(data)                         chia thành các khối 8 byte
    └── với mỗi khối: des_core.crypt_block_fast(block, keys)   B2
        ├── IP
        ├── lặp 16 vòng: L, R = R, L ⊕ f(R, Ki)
        │   └── _fast_f: E-mở rộng → ⊕Ki → 8 S-box → P
        ├── đổi chỗ L, R lần cuối
        └── IP⁻¹
```

## 2.3. Bước 0 — Chuẩn bị khóa: `parse_des_key(text)`

| Input | Output |
|---|---|
| `"133457799BBCDFF1"` (16 ký tự hex) | 8 byte `13 34 57 79 9B BC DF F1` |
| `"nhom2026"` (8 ký tự) | 8 byte mã ASCII của 8 ký tự |
| độ dài khác | báo lỗi |

## 2.4. B1 — Sinh 16 khóa con: `generate_subkeys(key)`

**Input:** 8 byte khóa  **Output:** danh sách **16 số nguyên 48 bit** K1…K16

| # | Thao tác | Ví dụ (khóa `133457799BBCDFF1`) |
|---|---|---|
| 1 | Đổi 8 byte → số 64 bit | `0x133457799BBCDFF1` |
| 2 | **PC-1**: 64 → 56 bit (bỏ 8 bit chẵn lẻ 8, 16, …, 64) | `F0CCAAF556678F` |
| 3 | Chia đôi | C0 = `F0CCAAF`, D0 = `556678F` (mỗi nửa 28 bit) |
| 4 | Vòng 1: dịch trái **1** (SHIFTS[0]) | C1 = `E19955F`, D1 = `AACCF1E` |
| 5 | **PC-2**: C1‖D1 (56 bit) → 48 bit | **K1 = `1B02EFFC7072`** |
| 6 | Lặp tiếp vòng 2…16, số bit dịch là `1 1 2 2 2 2 2 2 1 2 2 2 2 2 2 1` | … **K16 = `CB3D8B0E17F5`** |

Tổng số bit đã dịch qua 16 vòng = 28, nên C16 = C0 và D16 = D0.

## 2.5. Bước chuẩn bị dữ liệu: `pkcs7_pad` + `split_blocks`

DES chỉ mã hóa được khối đúng **8 byte**, nên phải đệm thêm. PKCS#7 thêm **n byte, mỗi byte có giá trị n** (n từ 1 đến 8):

```
"Xin chào" = 58 69 6E 20 63 68 C3 A0 6F           (9 byte, vì "à" chiếm 2 byte UTF-8)
sau pad    = 58 69 6E 20 63 68 C3 A0 | 6F 07 07 07 07 07 07 07   (16 byte = 2 khối)
```

Nếu dữ liệu đã tròn 8 byte thì vẫn thêm nguyên **một khối `08 08 … 08`**, để lúc giải mã luôn biết cần bỏ bao nhiêu byte.

## 2.6. B2 — Mã hóa 1 khối: `crypt_block_fast` (hoặc `crypt_block_verbose` để in log)

Ví dụ: khối `0123456789ABCDEF`, khóa `133457799BBCDFF1`.

| # | Bước | Kết quả |
|---|---|---|
| 1 | **IP** (bảng 64 phần tử trong `des_tables.IP`) | `CC00CCFFF0AAF0AA` → L0 = `CC00CCFF`, R0 = `F0AAF0AA` |
| 2 | **Vòng 1**, hàm f(R0, K1): | |
| 2a | E: mở rộng R 32 → 48 bit | `7A15557A1555` |
| 2b | ⊕ K1 | `7A15557A1555` ⊕ `1B02EFFC7072` = `6117BA866527` |
| 2c | 8 S-box: mỗi nhóm 6 bit → 4 bit (hàng = bit đầu + bit cuối, cột = 4 bit giữa) | `5C82B597` |
| 2d | Hoán vị P | f = `234AA9BB` |
| 2e | L1 = R0, R1 = L0 ⊕ f | L1 = `F0AAF0AA`, R1 = `CC00CCFF` ⊕ `234AA9BB` = `EF4A6544` |
| 3 | Lặp vòng 2 → 16 (giống hệt, mỗi vòng dùng Ki của nó) | sau vòng 16: L16 = `43423234`, R16 = `0A4CD995` |
| 4 | **Đổi chỗ lần cuối** → R16‖L16 | `0A4CD99543423234` |
| 5 | **IP⁻¹** | **`85E813540F0AB405`** ← bản mã ✔ |

So với TinyDES:

| | TinyDES | DES |
|---|---|---|
| Khối | 8 bit | 64 bit |
| Khóa | 8 bit | 64 bit (56 bit hiệu dụng) |
| Số vòng | 3 | 16 |
| Hoán vị đầu / cuối | không có | IP, IP⁻¹ |
| Mở rộng | Expand 4 → 6 | E 32 → 48 |
| S-box | 1 hộp 4×16 (6 bit → 4 bit) | 8 hộp 4×16 (6 bit → 4 bit) |
| Hoán vị sau S-box | P-box 4 bit | P (32 bit) |

**Hai bản cài đặt DES, cùng một kết quả:**
- `crypt_block_verbose`: viết đúng sơ đồ (`permute` → `feistel_f` → `sbox_sub`), có ghi log từng vòng. Web dùng bản này để hiển thị 16 vòng.
- `crypt_block_fast`: tính sẵn bảng tra (gộp S-box với P, gộp IP theo từng byte), nhanh hơn nhiều, dùng để mã hóa tệp.
- `test_runner.py` kiểm tra hai bản cho kết quả giống nhau.

## 2.7. B3 — Giải mã: `des_decrypt_bytes(cipher, key)`

```
des_decrypt_bytes(cipher, key)
├── kiểm tra độ dài là bội của 8
├── generate_subkeys(key)[::-1]        ← ĐẢO NGƯỢC: K16, K15, …, K1
├── _crypt_blocks(cipher, ...)         ← chạy y hệt lúc mã hóa
└── pkcs7_unpad(...)                   ← đọc byte cuối = n, bỏ n byte đệm
```

Ví dụ: `85E813540F0AB405` → (khóa con đảo ngược) → `0123456789ABCDEF` ✔

**Sai khóa thì sao?** Kết quả giải mã là dữ liệu rác, nên byte cuối thường không phải padding hợp lệ.
Khi đó `pkcs7_unpad` báo lỗi *"Padding sai - có thể do sai khóa"*.

## 2.8. Với tệp (ảnh, txt…)

```python
utils.des_encrypt_file("anh.png", "anh.png.enc", key)   # read_file (rb) → des_encrypt_bytes → write_file (wb)
utils.des_decrypt_file("anh.png.enc", "anh.png", key)   # read_file (rb) → des_decrypt_bytes → write_file (wb)
```

Tệp được đọc ở chế độ nhị phân (`rb`), nên ảnh, PDF hay bất kỳ loại tệp nào cũng xử lý như một dãy byte.

---

## 2.9. Giải thích chi tiết file `core/des_core.py`

> Trong code, **từng dòng đều đã có comment kèm ví dụ**. Mở `core/des_core.py` để đọc song song với mục này.

File gồm 3 phần:

| Phần | Hàm | Vai trò |
|---|---|---|
| **1. Công cụ cơ bản** | `permute`, `rotl` | Hoán vị bit, dịch vòng bit |
| **2. Bản dễ đọc** | `generate_subkeys`, `sbox_sub`, `feistel_f`, `crypt_block_verbose` | Viết **đúng sơ đồ DES trong sách**, có ghi log, dùng để hiển thị |
| **3. Bản chạy nhanh** | `_build_byte_lut`, `_apply_lut`, `_SP`, `_fast_f`, `crypt_block_fast` | Tính sẵn bảng tra để mã hóa tệp lớn nhanh. Kết quả **giống hệt** bản dễ đọc |
| **API** | `encrypt_block`, `decrypt_block` | Mã hóa / giải mã 1 khối 8 byte |

Quy ước: dữ liệu là **số nguyên** (`int`), **bit 1 = bit trái nhất**. Ví dụ khối 8 byte `01 23 … EF` ↔ số `0x0123456789ABCDEF`.

### `permute(value, table, in_bits)`: hoán vị bit

```python
for pos in table:
    out = (out << 1) | ((value >> (in_bits - pos)) & 1)
```

- `value >> (in_bits - pos)`: dịch phải để đưa bit ở vị trí `pos` về cuối.
- `& 1`: chỉ giữ đúng bit đó.
- `out << 1 | bit`: dịch `out` sang trái một chỗ rồi gắn bit mới vào cuối.

Ví dụ: `permute(0b1011, [2, 4, 3, 1], 4)`. Đầu vào b1=1, b2=0, b3=1, b4=1; lấy b2, b4, b3, b1 = **`0111`**.
Kết quả dài `len(table)` bit, nên cùng một hàm làm được IP / IP⁻¹ (64 → 64), PC-1 (64 → 56), PC-2 (56 → 48), E (32 → 48) và P (32 → 32).

### `rotl(value, n, bits)`: dịch vòng trái

`((value << n) | (value >> (bits - n))) & mask`: phần bị đẩy ra bên trái quay về bên phải.
Ví dụ `rotl(0b1000, 1, 4)` = `0001`; `rotl(0xF0CCAAF, 1, 28)` = `E19955F` (C0 → C1).

### `generate_subkeys(key)`: 16 khóa con

| Dòng code | Ví dụ |
|---|---|
| `int.from_bytes(key, "big")` | 8 byte → `0x133457799BBCDFF1` |
| `permute(k64, PC1, 64)` | `F0CCAAF556678F` |
| `k56 >> 28`, `k56 & 0x0FFFFFFF` | C0 = `F0CCAAF`, D0 = `556678F` |
| vòng i: `rotl(c, s)`, `rotl(d, s)` | C1 = `E19955F`, D1 = `AACCF1E` |
| `permute((c << 28) \| d, PC2, 56)` | K1 = `1B02EFFC7072` … K16 = `CB3D8B0E17F5` |

### `sbox_sub(x48)`: 8 S-box

- `chunk = (x48 >> (42 - 6*i)) & 0x3F`: lấy nhóm 6 bit thứ i.
- `row = ((chunk >> 4) & 0b10) | (chunk & 1)`: hàng = bit đầu + bit cuối.
- `col = (chunk >> 1) & 0xF`: cột = 4 bit giữa.

Ví dụ `6117BA866527`:
- S1 nhận `011000` → hàng 0, cột 12 → 5.
- S2 nhận `010001` → hàng 1, cột 8 → C.
- … kết quả cả 8 S-box = **`5C82B597`**.

### `feistel_f` và `crypt_block_verbose`

```
F(R, K) = P( S( E(R) ⊕ K ) )      VD: E 7A15557A1555 → ⊕K1 6117BA866527 → S 5C82B597 → P 234AA9BB

left, right = right, left ^ feistel_f(right, k)      # Python tính hết vế phải trước rồi mới gán
out = permute((right << 32) | left, IP_INV, 64)      # ghép R16‖L16 để hủy lần tráo thừa sau vòng 16
```

### Bản chạy nhanh: tính sẵn 3 loại bảng

| Bảng | Ý tưởng | Hiệu quả |
|---|---|---|
| `_IP_LUT`, `_FP_LUT` (`_build_byte_lut`) | Chia 64 bit thành 8 byte, tính sẵn "byte j có giá trị v thì bật bit nào của kết quả" (8 × 256) | 8 lần tra thay cho 64 lần lặp |
| `_SP` | **P chỉ đổi chỗ bit** nên P(a OR b) = P(a) OR P(b). Tính sẵn P của phần đóng góp từng S-box (8 × 64) | 8 lần tra ra luôn f, bỏ được `sbox_sub` và `permute(P)` |
| Mẹo E trong `_fast_f` | Các nhóm 6 bit của bảng E bắt đầu cách nhau 4 bit. Tạo chuỗi 34 bit `R32 \| R1…R32 \| R1` rồi cắt | Không cần bảng E |

- `_split_key` / `prepare_keys`: cắt sẵn mỗi Ki thành 8 nhóm 6 bit, **một lần cho cả tệp**. Ví dụ K1 → `000110 110000 001011 …`
- **Kết quả đo:** khoảng 720 KB/s, tệp 1 MB mất khoảng 1,4 giây. Bản dễ đọc mất khoảng 20–30 giây cho cùng tệp đó.

### API

```python
encrypt_block(block, key)   # prepare_keys(generate_subkeys(key))        → crypt_block_fast
decrypt_block(block, key)   # prepare_keys(generate_subkeys(key)[::-1])  → crypt_block_fast   ← chỉ khác [::-1]
```

---

# PHẦN 3. Từ giao diện đến thuật toán

## 3.1. Web (`app.py`)

Ví dụ: người dùng mở trang **TinyDES từng bước**, nhập khóa `10011010`, bản rõ `01011100`, bấm **Mã hóa**.

```
1. Trình duyệt gửi POST /sdes_demo (form: sdes_key, sdes_input, sdes_fmt, sdes_action=enc)
2. app.sdes_demo()
   ├── parse_sdes_data(...)               chuyển input → danh sách khối 8 bit
   ├── tinydes_core.generate_keys(key)    lấy K1, K2, K3 + log sinh khóa
   ├── tinydes_core.encrypt(blk, key)     với từng khối → bản mã + log
   ├── tinydes_core.decrypt_bytes(...)    giải mã ngược lại để kiểm tra khớp
   ├── tinydes_core.trace(...)            dữ liệu để vẽ từng ô bit
   └── db.add_history(...)                ghi lịch sử (không ghi khóa)
3. render_template("sdes.html", sdes=kết_quả)   → trình duyệt hiển thị
```

Trang **DES: văn bản & tệp** (POST `/des_file`):

```
parse_des_key → generate_subkeys (log 16 khóa con) → des_encrypt_bytes / des_decrypt_bytes
→ crypt_block_verbose (log 16 vòng của khối đầu) → lưu tệp kết quả vào RAM → trả link tải
```

## 3.2. Console

| Lệnh | Gọi |
|---|---|
| `python cli.py` | Menu → `tinydes_core.trace` / `utils.des_encrypt_bytes` / `utils.des_encrypt_file` / `tinydes_core.brute_force` / `test_runner.run_all` |
| `python core/tinydes_core.py` | Nhập bản rõ + khóa → `trace` → `print_trace` (mã hóa), rồi `trace(..., decrypt=True)` (giải mã) |
| `python test_runner.py` | `run_all()` → in bảng đối chiếu, `Passed 43/43` |

---

## 4. Tóm tắt cần nhớ khi thuyết trình

1. **Bắt đầu** từ `encrypt(...)` (TinyDES) hoặc `des_encrypt_bytes(...)` (DES).
2. **B1 – sinh khóa:** `generate_keys` → K1, K2, K3 (TinyDES) · `generate_subkeys` → K1…K16 (DES).
3. **B2 – mã hóa:** các vòng Feistel (mở rộng → ⊕ khóa → S-box → hoán vị → ⊕ nửa trái). TinyDES 3 vòng, ghép L3R3; DES 16 vòng, có thêm IP trước và IP⁻¹ sau.
4. **B3 – giải mã:** đi ngược các vòng với khóa con đảo ngược (TinyDES: K3, K2, K1). DES thêm bước bỏ padding.
5. **Kiểm chứng:** TinyDES ra đúng lời giải trang 72 `10010010` (92); DES ra đúng `85E813540F0AB405` và khớp 16 ca NIST SP 800-17.

---

# PHẦN 5. Cú pháp Python dùng trong code (giải thích từng dòng hay gặp)

## 5.1. Dòng `pt, key = bytes.fromhex(pt_hex), bytes.fromhex(key_hex)`

Dòng này nằm trong hàm `index()` của `app.py` và trong `test_runner.py`:

```python
for pt_hex, key_hex in DES_CASES:
    pt, key = bytes.fromhex(pt_hex), bytes.fromhex(key_hex)
```

| Thành phần | Nghĩa | Ví dụ |
|---|---|---|
| `DES_CASES` | List các tuple 2 chuỗi | `[("0123456789ABCDEF", "133457799BBCDFF1"), …]` |
| `for pt_hex, key_hex in …` | Mỗi vòng lấy 1 tuple và **tách luôn** thành 2 biến | `pt_hex = "0123456789ABCDEF"`, `key_hex = "133457799BBCDFF1"` |
| `bytes.fromhex(s)` | Chuỗi hex → bytes, cứ **2 ký tự hex = 1 byte** | `"0123456789ABCDEF"` → 8 byte `[1, 35, 69, 103, 137, 171, 205, 239]` |
| `a, b = x, y` | Gán **2 biến cùng lúc** | `pt` = 8 byte bản rõ, `key` = 8 byte khóa |

Khi in ra, Python hiển thị `b'\x01#Eg\x89\xab\xcd\xef'`. Byte `0x23`, `0x45`, `0x67` trùng mã ASCII của `#`, `E`, `g` nên Python in thành chữ, còn các byte khác in dạng `\x..`. **Giá trị vẫn là 8 byte** như trên.

Các dòng tiếp theo trong `index()`:

```python
ours = des_core.encrypt_block(pt, key)                    # 8 byte bản mã do nhóm tự code
"ct": ours.hex().upper()                                  # bytes → chuỗi hex in hoa: "85E813540F0AB405"
"ok": ours == LibDES.new(key, LibDES.MODE_ECB).encrypt(pt)  # so với thư viện → True / False
```

## 5.2. Đổi qua lại giữa chuỗi, bytes và số

| Cú pháp | Nghĩa | Ví dụ → kết quả |
|---|---|---|
| `bytes.fromhex("E0 F8")` | hex → bytes (bỏ qua dấu cách) | `b'\xe0\xf8'` |
| `b.hex()` | bytes → hex chữ thường | `0123456789abcdef` |
| `b.hex().upper()` | … in hoa | `0123456789ABCDEF` |
| `b.hex(" ")` | … có dấu cách giữa các byte | `01 23 45 67 89 AB CD EF` (sau `.upper()`) |
| `"Xin chào".encode("utf-8")` | chữ → bytes | 9 byte `58 69 6E 20 63 68 C3 A0 6F` (chữ "à" = 2 byte) |
| `b.decode("utf-8")` | bytes → chữ | `b"Hello"` → `"Hello"` |
| `b.decode("utf-8", errors="replace")` | byte không hợp lệ thành `�` thay vì báo lỗi | `b"\xe0\xf8"` → `"��"` |
| `b"nhom2026"` | viết bytes trực tiếp | 8 byte, `n` = 110, `h` = 104, … |
| `int.from_bytes(b, "big")` | bytes → số (byte đầu là phần cao) | 8 byte trên → `0x0123456789ABCDEF` |
| `n.to_bytes(8, "big")` | số → 8 byte | `0x85E8…05` → `b'\x85\xe8\x13T\x0f\n\xb4\x05'` |
| `bytes([7]) * 7` | 7 byte giá trị 7 (dùng trong PKCS#7) | `07 07 07 07 07 07 07` |
| `bytes(range(256))` | 256 byte `00` → `FF` | |
| `int("01001000", 2)` | chuỗi nhị phân → số | `72` |
| `bytes([0x48, 0x65])` | list số → bytes | `b'He'` |

## 5.3. Định dạng số: `format(...)` và f-string

| Cú pháp | Nghĩa | Ví dụ |
|---|---|---|
| `format(5, "010b")` | nhị phân, đủ 10 chữ số (thêm 0 đầu) | `0000000101` |
| `format(1023, "010b")` | | `1111111111` |
| `format(255, "08b")` | nhị phân 8 chữ số | `11111111` |
| `format(3, "02b")` | | `11` |
| `f"{k:012X}"` | hex **in hoa**, đủ 12 chữ số | `1B02EFFC7072` |
| `f"{c:07X}"` | hex in hoa, đủ 7 chữ số | `F0CCAAF` |
| `f"{x:.2f}"` | số thực làm tròn 2 chữ số | `3.14` |
| `f"{name:<16}"` | canh trái, chiếm 16 ký tự (cho thẳng cột) | `"Expand          "` |
| `f"K1={k1}"` | chèn giá trị biến vào chuỗi | `K1=10100100` |

## 5.4. Cắt chuỗi / list (slicing)

| Cú pháp | Nghĩa | Ví dụ |
|---|---|---|
| `s[:4]` | 4 phần tử đầu | `"01011100"[:4]` = `0101` (L0) |
| `s[4:]` | từ vị trí 4 đến hết | `"01011100"[4:]` = `1100` (R0) |
| `s[1:3]` | vị trí 1, 2 (không gồm 3) | `"abcdef"[1:3]` = `bc` |
| `s[-1]` | phần tử cuối | byte cuối (dùng trong `pkcs7_unpad`) |
| `s[:-n]` | bỏ n phần tử cuối | bỏ phần đệm |
| `lst[::-1]` | **đảo ngược** | `[1, 2, 3][::-1]` = `[3, 2, 1]`; `subkeys[::-1]` = K16 … K1 |
| `bits[n:] + bits[:n]` | dịch vòng trái n | `"10000"` → `"00001"` |

## 5.5. Phép toán trên bit (dùng nhiều trong DES)

| Phép | Nghĩa | Ví dụ (`0b1011` = 11) |
|---|---|---|
| `x << n` | dịch trái n bit (nhân 2ⁿ) | `1011 << 1` = `10110` (22) |
| `x >> n` | dịch phải n bit (bỏ n bit cuối) | `1011 >> 1` = `101` (5) |
| `x & y` | AND: giữ bit mà cả hai đều 1. Dùng để **lấy ra** một số bit | `1011 & 0110` = `0010` (2) |
| `x \| y` | OR: bit nào một bên là 1 thì là 1. Dùng để **ghép** | `1011 \| 0100` = `1111` (15) |
| `x ^ y` | XOR: khác nhau → 1. Dùng để **trộn với khóa** | `1011 ^ 0110` = `1101` (13) |
| `x & 0x3F` | giữ 6 bit cuối (`0x3F` = `111111`) | lấy nhóm 6 bit cho S-box |
| `x & 0xFF` | giữ 8 bit cuối (1 byte) | |
| `x & 0xFFFFFFFF` | giữ 32 bit cuối | lấy nửa R |
| `(1 << bits) - 1` | số gồm `bits` chữ số 1 | `(1 << 4) - 1` = `1111` |

## 5.6. Vòng lặp, list, dict

| Cú pháp | Nghĩa | Ví dụ |
|---|---|---|
| `for i, x in enumerate(lst, start=1)` | lấy cả **số thứ tự** lẫn phần tử | `i` = 1, 2, 3…; dùng cho "Vòng 1", "Vòng 2"… |
| `for x, y in zip(a, b)` | duyệt song song 2 dãy | `xor()` của TinyDES |
| `[f(x) for x in lst]` | **list comprehension**: tạo list mới | `[format(b, "08b") for b in data]` |
| `{k: v for …}` | tạo dict | `{r["algo"]: r["n"] for r in rows}` |
| `"".join(list_chuoi)` | nối list chuỗi thành 1 chuỗi | `"".join(["1", "0"])` = `"10"` |
| `" ".join(…)` | nối có dấu cách | `"11100000 11111000"` |
| `lst.append(x)` | thêm vào cuối list | |
| `d.get("key", mặc_định)` | lấy giá trị, không có thì lấy mặc định | `request.form.get("sdes_key", "")` |
| `d.setdefault(k, []).append(x)` | chưa có khóa thì tạo list rỗng rồi thêm | nhóm kết quả kiểm thử |
| `{**detail, "a": 1}` | trải các phần tử của dict vào dict mới | log vòng DES |
| `all(...)` / `any(...)` | tất cả đúng / có ít nhất 1 cái đúng | `all(c in "01" for c in s)` |
| `sum([True, False, True])` | True = 1, False = 0 | `2` (đếm số ca PASS) |

## 5.7. Hàm, điều kiện, lỗi

| Cú pháp | Nghĩa |
|---|---|
| `def f(a, b=None)` | `b` có giá trị mặc định, không truyền cũng được |
| `def f(**ctx)` | nhận mọi tham số `tên=giá_trị` thành 1 dict |
| `return a, b` / `x, y = f()` | trả và nhận nhiều giá trị (tuple) |
| `A if điều_kiện else B` | điều kiện viết 1 dòng: `"Mã hóa" if action == "enc" else "Giải mã"` |
| `x or mặc_định` | `x` rỗng / `None` thì lấy mặc định: `keys or generate_keys(key)` |
| `lambda: f(x)` | hàm không tên 1 dòng (truyền vào `_measure` để đo thời gian) |
| `raise ValueError("…")` | báo lỗi, dừng hàm |
| `try: … except ValueError as e:` | bắt lỗi để hiển thị thay vì sập chương trình |
| `with open(path, "rb") as f:` | mở tệp nhị phân, **tự đóng** khi xong |
| `_` | biến không dùng tới: `ct, _ = encrypt(…)` (bỏ log) |
| `if __name__ == "__main__":` | chỉ chạy khi chạy trực tiếp file, không chạy khi file khác import |

## 5.8. Riêng Flask (`app.py`)

| Cú pháp | Nghĩa |
|---|---|
| `@app.get("/sdes")` | Trình duyệt **mở** `/sdes` thì chạy hàm ngay bên dưới |
| `@app.post("/sdes_demo")` | Trình duyệt **gửi form** tới `/sdes_demo` thì chạy hàm |
| `@app.get("/download/<token>")` | Phần `<token>` của URL được truyền vào hàm làm tham số |
| `request.form.get("sdes_key")` | Lấy giá trị ô `<input name="sdes_key">` của form |
| `request.files.get("des_file")` | Lấy tệp người dùng chọn |
| `request.args` | Tham số trên URL: `/bruteforce?bf_plain=Hello` |
| `render_template("sdes.html", sdes=result)` | Mở `templates/sdes.html`, thay `{{ sdes.… }}` bằng dữ liệu, trả HTML |
| `send_file(io.BytesIO(data), as_attachment=True)` | Gửi dữ liệu trong RAM về cho trình duyệt **tải xuống** |
| `redirect(url_for("history"))` | Chuyển trình duyệt sang trang `/history` |
| `abort(404)` | Trả lỗi "không tìm thấy" |
