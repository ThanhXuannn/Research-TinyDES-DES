/*
  PHÒNG CHAT An -> Bình (trang /chat, templates/chat.html).
  File này chỉ VẼ giao diện. Việc mã hóa / giải mã / vét cạn đều do server làm (app.py gọi core/):
    POST /api/chat/send    {algo, key, text}        -> {cipher_hex, bob_text, weak, ...}
    POST /api/chat/attack  {algo, key, cipher_hex}  -> TinyDES: {top, success, elapsed}; DES: {per_sec, years}
    POST /api/chat/chosen  {algo, key, cipher_hex}  -> TinyDES: {calls, rows, text}; DES: không lập được bảng
    POST /api/chat/tamper  {algo, key, cipher_hex, index} -> {cipher_hex (đã sửa), bob_text hoặc bob_error}
  `key` gửi kèm attack chỉ để kiểm chứng "kẻ xấu đoán đúng chưa", server không dùng nó để tìm khóa.
*/
(function () {
  var DEFAULT_KEY = { tinydes: "11011010", des: "nhom2026" };   // khóa mẫu cho mỗi thuật toán
  var NAME = { tinydes: "TinyDES", des: "DES" };
  var packets = [];        // mọi gói tin đã gửi: {n, algo, key, text, hex}
  var lastText = "";       // tin An gửi gần nhất (cho nút "Gửi lại")

  function $(id) { return document.getElementById(id); }
  function algo() { return document.querySelector('input[name="chatAlgo"]:checked').value; }

  // tạo 1 thẻ HTML; text đi qua textContent nên chữ người dùng gõ không bao giờ thành mã HTML
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function clearEmpty(box) { var p = box.querySelector(".msgs-empty"); if (p) p.remove(); }
  function scrollEnd(box) { box.scrollTop = box.scrollHeight; }
  function showError(msg) { $("chatError").textContent = msg; $("chatError").hidden = !msg; }

  // gửi JSON lên server, nhận JSON về
  function api(path, body) { return window.LOCAL_API(path, body); }   // bản tĩnh


  // số lớn -> chữ dễ đọc kiểu Việt Nam. VD 690000 -> "690.000"
  function vn(n) { return Math.round(n).toLocaleString("vi-VN"); }
  function years(y) {
    if (y >= 1e9) return vn(y / 1e9) + " tỷ năm";
    if (y >= 1e6) return vn(y / 1e6) + " triệu năm";
    if (y >= 1e3) return vn(y / 1e3) + " nghìn năm";
    return vn(y) + " năm";
  }

  // ---------------- An gửi tin ----------------
  function send(text) {
    var a = algo(), key = $("chatKey").value.trim();
    showError("");
    $("anSend").disabled = true;
    return api("/api/chat/send", { algo: a, key: key, text: text }).then(function (d) {
      var n = packets.length + 1;
      var dup = packets.filter(function (p) { return p.hex === d.cipher_hex; })[0];  // gói cũ giống hệt?
      var p = { n: n, algo: a, key: key, text: text, hex: d.cipher_hex };
      packets.push(p);
      lastText = text;
      addAn(p, d);
      addPacket(p, d, dup);
      addBinh(d.bob_text, "Giải mã bằng khóa chung · tin #" + n, "");
      $("keyWarn").hidden = !d.weak;
      if (d.weak) $("keyWarn").textContent = "Khóa " + key + " là khóa yếu: 3 chìa con K1, K2, K3 không khác nhau hết. Nên chọn khóa có 0 và 1 lẫn lộn.";
    }).catch(function (e) { showError(e.message); })
      .finally(function () { $("anSend").disabled = false; });
  }

  function addAn(p, d) {
    var box = $("anMsgs"); clearEmpty(box);
    var b = el("div", "bubble an");
    b.appendChild(el("p", null, p.text));
    b.appendChild(el("small", null, "" + NAME[p.algo] + " · khóa " + p.key + " · " + d.n_plain + " byte → " + d.n_bytes + " byte mã"));
    box.appendChild(b); scrollEnd(box);
  }

  function addBinh(text, meta, extra) {
    var box = $("binhMsgs"); clearEmpty(box);
    var b = el("div", "bubble binh " + extra);
    b.appendChild(el("p", null, text));
    b.appendChild(el("small", null, meta));
    box.appendChild(b); scrollEnd(box);
  }

  // ---------------- Đường truyền: gói tin kẻ xấu nhìn thấy ----------------
  function hexView(hex, mark) {
    // mỗi byte 1 ô; byte bị sửa (mark) được tô đỏ
    var wrap = el("div", "hex");
    hex.split(" ").forEach(function (h, i) { wrap.appendChild(el("span", i === mark ? "changed" : null, h)); });
    return wrap;
  }

  function addPacket(p, d, dup) {
    var box = $("packets"); clearEmpty(box);
    var card = el("div", "packet");
    var head = el("div", "packet-head");
    head.appendChild(el("b", null, "Gói tin #" + p.n));
    head.appendChild(el("span", "chip algo", NAME[p.algo] + " · " + d.n_bytes + " byte"));
    card.appendChild(head);
    card.appendChild(hexView(p.hex));
    if (dup) card.appendChild(el("p", "eve-note leak", "Giống hệt gói #" + dup.n + ". Kẻ xấu không đọc được, nhưng biết An vừa gửi lại đúng tin cũ."));
    var acts = el("div", "packet-acts");
    var atk = el("button", "btn small danger", "Vét cạn khóa");
    var cho = el("button", "btn small danger", "Tấn công chọn bản rõ");
    var tmp = el("button", "btn small", "Sửa 1 bit rồi chuyển");
    atk.type = cho.type = tmp.type = "button";
    atk.onclick = function () { attack(p, card, atk); };
    cho.onclick = function () { chosen(p, card, cho); };
    tmp.onclick = function () { tamper(p, card, tmp); };
    acts.appendChild(atk); acts.appendChild(cho); acts.appendChild(tmp);
    card.appendChild(acts);
    box.appendChild(card); scrollEnd(box);
  }

  // ---------------- Kẻ xấu vét cạn khóa ----------------
  function attack(p, card, btn) {
    btn.disabled = true; btn.textContent = "Đang thử khóa…";
    api("/api/chat/attack", { algo: p.algo, key: p.key, cipher_hex: p.hex }).then(function (d) {
      var note;
      if (d.algo === "tinydes") {
        var g = d.top[0];
        note = el("div", "eve-note " + (d.success ? "leak" : "safe"));
        note.appendChild(el("p", null, "Thử đủ " + d.tried + " khóa trong " + d.elapsed + " ms. Khóa “giống chữ” nhất: " + g.key +
          (d.success ? " đúng khóa thật của An và Bình." : " đoán sai (tin quá ngắn).")));
        var read = el("p", "eve-read");
        read.appendChild(el("span", null, d.success ? "Kẻ xấu đọc được: " : "Kẻ xấu đọc ra: "));
        read.appendChild(el("b", null, "“" + g.text + "”"));
        note.appendChild(read);
        var list = el("ol", "eve-top");
        d.top.slice(1).forEach(function (c) { list.appendChild(el("li", null, c.key + " · điểm " + c.score + " · rác, không đọc được")); });
        note.appendChild(el("small", null, "Các khóa xếp hạng sau:"));
        note.appendChild(list);
        btn.textContent = d.success ? "Đã bẻ được khóa" : "Đoán sai";
      } else {
        note = el("div", "eve-note safe");
        note.appendChild(el("p", null, "Thử " + vn(d.tried) + " khóa mất " + d.elapsed + " ms, không khóa nào đúng. Tốc độ khoảng " + vn(d.per_sec) + " khóa/giây."));
        var big = el("p", "eve-read");
        big.appendChild(el("span", null, "Thử hết 2⁵⁶ khóa với tốc độ này cần khoảng "));
        big.appendChild(el("b", null, years(d.years)));
        note.appendChild(big);
        note.appendChild(el("small", null, "Kẻ xấu đành bỏ cuộc. Tin của An an toàn trước máy tính thường."));
        btn.textContent = "Bỏ cuộc";
      }
      card.appendChild(note); scrollEnd($("packets"));
    }).catch(function (e) { btn.disabled = false; btn.textContent = "Vét cạn khóa"; showError(e.message); });
  }

  // ---------------- Kẻ xấu tấn công chọn bản rõ ----------------
  // Mượn hộp đen mã hóa của An (có khóa bên trong), đưa 256 bản rõ vào để lập bảng tra, rồi tra bảng.
  function chosen(p, card, btn) {
    btn.disabled = true; btn.textContent = "Đang lập bảng tra…";
    api("/api/chat/chosen", { algo: p.algo, key: p.key, cipher_hex: p.hex }).then(function (d) {
      var note;
      if (d.algo === "tinydes") {
        note = el("div", "eve-note leak");
        note.appendChild(el("p", null, "Kẻ xấu mượn hộp đen mã hóa của An, đưa vào " + d.calls + " bản rõ (00000000 … 11111111), lập bảng tra " +
          d.rows + " dòng trong " + d.elapsed + " ms. Không tìm khóa, chỉ tra bảng từng byte."));
        var read = el("p", "eve-read");
        read.appendChild(el("span", null, "Kẻ xấu đọc được: "));
        read.appendChild(el("b", null, "“" + d.text + "”"));
        note.appendChild(read);
        btn.textContent = "Đã dịch bằng bảng tra";
      } else {
        note = el("div", "eve-note safe");
        note.appendChild(el("p", null, "DES mã từng khối 64 bit. Muốn lập bảng tra phải đưa 2⁶⁴ ≈ 18 tỷ tỷ bản rõ vào hộp đen, không thể làm được."));
        btn.textContent = "Bỏ cuộc";
      }
      card.appendChild(note); scrollEnd($("packets"));
    }).catch(function (e) { btn.disabled = false; btn.textContent = "Tấn công chọn bản rõ"; showError(e.message); });
  }

  // ---------------- Kẻ xấu sửa tin rồi chuyển tiếp ----------------
  function tamper(p, card, btn) {
    btn.disabled = true;
    api("/api/chat/tamper", { algo: p.algo, key: p.key, cipher_hex: p.hex, index: 0 }).then(function (d) {
      var note = el("div", "eve-note leak");
      note.appendChild(el("p", null, "Kẻ xấu đổi 1 bit ở byte đầu tiên rồi chuyển tiếp cho Bình:"));
      note.appendChild(hexView(d.cipher_hex, d.index));
      card.appendChild(note);
      if (d.bob_error) {
        addBinh("Không đọc được tin #" + p.n + ": " + d.bob_error, "Bản mã đã bị kẻ xấu sửa", "tampered");
      } else {
        addBinh(d.bob_text, "Tin #" + p.n + " đã bị sửa trên đường truyền. Gốc: “" + p.text + "”", "tampered");
      }
      btn.textContent = "Đã sửa";
      scrollEnd($("packets"));
    }).catch(function (e) { btn.disabled = false; showError(e.message); });
  }

  // ---------------- Nút điều khiển ----------------
  $("anForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var t = $("anText").value.trim();
    if (t) send(t);
  });

  // đổi thuật toán: nếu khóa đang gõ không hợp với thuật toán mới thì điền khóa mẫu
  document.querySelectorAll('input[name="chatAlgo"]').forEach(function (r) {
    r.addEventListener("change", function () {
      var k = $("chatKey").value.trim();
      var okTiny = /^[01]{8}$/.test(k);
      var okDes = new TextEncoder().encode(k).length === 8 || /^[0-9a-fA-F]{16}$/.test(k);
      if (algo() === "tinydes" ? !okTiny : !okDes || okTiny) $("chatKey").value = DEFAULT_KEY[algo()];
      $("keyWarn").hidden = true;
    });
  });

  document.querySelectorAll("[data-def]").forEach(function (b) {
    b.addEventListener("click", function () {
      var what = b.dataset.def;
      if (what === "des" || what === "weak") {
        var target = what === "des" ? "des" : "tinydes";
        document.querySelector('input[name="chatAlgo"][value="' + target + '"]').checked = true;
        $("chatKey").value = what === "des" ? DEFAULT_KEY.des : "11110000";
        send($("anText").value.trim() || "Hẹn gặp ở cổng trường lúc 8h tối");
      } else if (what === "repeat") {
        send(lastText || $("anText").value.trim() || "Hẹn gặp ở cổng trường lúc 8h tối");
      }
      document.querySelector(".chat-stage").scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
})();
