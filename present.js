// =============================================================================
// present.js — chế độ "TRÌNH CHIẾU TỪNG BƯỚC" (dùng chung cho trang TinyDES Demo và trang Kiểm thử)
//
// Ý tưởng: trên trang có nhiều ô "bước" (mỗi ô có class "step-unit").
//   - Bấm "Trình chiếu từng bước": làm MỜ hết các bước, chỉ hiện bước 1.
//   - Bấm "Bước tiếp →" (hoặc phím → / Space): hiện thêm 1 bước và cuộn tới bước đó.
//   - Bấm "Hiện tất cả" (hoặc phím Esc): thoát chế độ trình chiếu, hiện lại mọi bước.
// Việc làm mờ do CSS đảm nhận (style.css):
//   .trace.presenting .step-unit:not(.shown) { opacity: .08 }
//   -> trong khung đang trình chiếu, bước nào CHƯA có class "shown" thì gần như trong suốt.
// File này chỉ việc thêm / bỏ 2 class: "presenting" (trên khung) và "shown" (trên từng bước).
// =============================================================================

// (() => { ... })(); : tạo 1 hàm rồi gọi ngay. Các biến bên trong không "rò" ra ngoài,
// tránh trùng tên với code JavaScript khác trên trang.
(() => {
  // --- Tìm các phần tử cần dùng trên trang ---------------------------------
  // document.querySelectorAll('.trace'): mọi khung có class "trace" (mỗi khối dữ liệu 1 khung)
  // [...x]: đổi kết quả thành mảng thường để dùng được .find, .forEach
  const traces = [...document.querySelectorAll('.trace')];
  // document.getElementById('x'): tìm phần tử có id="x" (các nút nằm trong sdes.html / tests.html)
  const btnPresent = document.getElementById('btn-present');   // nút "Trình chiếu từng bước"
  const btnNext = document.getElementById('btn-next');         // nút "Bước tiếp →"
  const btnAll = document.getElementById('btn-all');           // nút "Hiện tất cả"
  const counter = document.getElementById('step-count');       // chữ "Bước 3/12"
  // Trang không có khung nào hoặc không có nút (VD chưa bấm Mã hóa) -> không làm gì cả
  if (!traces.length || !btnPresent) return;

  let presenting = false;   // đang ở chế độ trình chiếu hay không (let: biến có thể gán lại)

  // Khung đang hiển thị (trang TinyDES có thể có nhiều khung, mỗi khối 1 khung; các khung khác bị ẩn)
  // .find(t => !t.hidden): lấy khung ĐẦU TIÊN không bị ẩn
  const current = () => traces.find(t => !t.hidden);
  // Danh sách các bước trong khung đang hiển thị
  const steps = () => [...current().querySelectorAll('.step-unit')];

  // --- Cập nhật chữ "Bước x/y" và khóa nút "Bước tiếp" khi đã hết -----------
  function update() {
    const all = steps();
    // .filter(...): giữ các bước đã có class "shown"; .length: đếm số lượng
    const shown = all.filter(s => s.classList.contains('shown')).length;
    // `Bước ${shown}/${all.length}`: chuỗi có chèn biến (giống f-string của Python)
    counter.textContent = presenting ? `Bước ${shown}/${all.length}` : '';
    btnNext.disabled = shown >= all.length;      // hiện hết rồi thì làm mờ nút "Bước tiếp"
  }

  // --- Bắt đầu (hoặc bắt đầu lại) trình chiếu -------------------------------
  function start() {
    presenting = true;
    traces.forEach(t => t.classList.add('presenting'));        // bật chế độ làm mờ cho mọi khung
    steps().forEach(s => s.classList.remove('shown'));         // ẩn lại mọi bước
    btnPresent.textContent = '↺ Bắt đầu lại';                  // đổi chữ trên nút
    btnNext.hidden = btnAll.hidden = false;                    // hiện 2 nút "Bước tiếp" và "Hiện tất cả"
    next();                                                    // hiện luôn bước đầu tiên
  }

  // --- Hiện thêm 1 bước -------------------------------------------------------
  function next() {
    // tìm bước ĐẦU TIÊN chưa được hiện
    const s = steps().find(s => !s.classList.contains('shown'));
    if (s) {
      s.classList.add('shown');                                        // hiện bước đó (CSS bỏ làm mờ)
      s.scrollIntoView({behavior: 'smooth', block: 'center'});         // cuộn mượt để bước đó ra giữa màn hình
    }
    update();
  }

  // --- Thoát trình chiếu, hiện mọi bước --------------------------------------
  function showAll() {
    presenting = false;
    traces.forEach(t => t.classList.remove('presenting'));     // tắt làm mờ -> mọi bước hiện rõ
    btnPresent.textContent = 'Trình chiếu từng bước';
    btnNext.hidden = btnAll.hidden = true;                     // ẩn 2 nút phụ
    update();
  }

  // --- Gắn sự kiện: bấm nút nào thì chạy hàm nào -----------------------------
  btnPresent.addEventListener('click', start);
  btnNext.addEventListener('click', next);
  btnAll.addEventListener('click', showAll);

  // Điều khiển bằng bàn phím khi thuyết trình: → hoặc Space = bước tiếp, Esc = hiện tất cả
  document.addEventListener('keydown', e => {
    // Không xử lý nếu chưa trình chiếu, hoặc đang gõ trong ô nhập (để Space vẫn gõ được dấu cách)
    if (!presenting || ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
    if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault();      // chặn hành vi mặc định của Space (cuộn trang xuống)
      next();
    }
    if (e.key === 'Escape') showAll();
  });

  // --- Tab chọn khối (trang TinyDES khi nhập nhiều byte, VD "Hello" = 5 khối) ----
  // Mỗi tab có data-block="0", "1"...; mỗi khung .trace cũng có data-block tương ứng.
  document.querySelectorAll('#block-tabs .tab').forEach(tab => tab.addEventListener('click', () => {
    // tô sáng tab vừa bấm, bỏ tô các tab còn lại (toggle(class, điều_kiện): điều kiện đúng thì thêm, sai thì bỏ)
    document.querySelectorAll('#block-tabs .tab').forEach(t => t.classList.toggle('active', t === tab));
    // chỉ hiện khung có cùng data-block với tab, ẩn các khung khác
    traces.forEach(t => t.hidden = t.dataset.block !== tab.dataset.block);
    if (presenting) start();   // đang trình chiếu thì bắt đầu lại từ bước 1 của khối mới
  }));
})();
