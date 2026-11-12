/*
  BẢN WEB TĨNH: thay cho 4 API /api/chat/... của app.py (không có server Python).
  Viết lại đúng thuật toán của core/tinydes_core.py, core/des_core.py, core/utils.py bằng JavaScript,
  trả về dữ liệu y hệt app.py để static/chat.js dùng nguyên như cũ.
*/
(function () {
  // ===================== TinyDES (giống core/tinydes_core.py) =====================
  var EXPAND = [2, 3, 1, 2, 1, 0], PBOX = [2, 0, 3, 1], COMPRESS = [5, 1, 3, 2, 7, 0], SHIFTS = [1, 2, 1];
  var SBOX = [
    [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8, 0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7],
    [0x0, 0xF, 0x7, 0x4, 0xE, 0x2, 0xD, 0x1, 0xA, 0x6, 0xC, 0xB, 0x9, 0x5, 0x3, 0x8],
    [0x4, 0x1, 0xE, 0x8, 0xD, 0x6, 0x2, 0xB, 0xF, 0xC, 0x9, 0x7, 0x3, 0xA, 0x5, 0x0],
    [0xF, 0xC, 0x8, 0x2, 0x4, 0x9, 0x1, 0x7, 0x5, 0xB, 0x3, 0xE, 0xA, 0x0, 0x6, 0xD]
  ];
  function permute(b, t) { return t.map(function (i) { return b[i]; }).join(""); }
  function rot(b, n) { return b.slice(n) + b.slice(0, n); }
  function xor(a, b) { var s = ""; for (var i = 0; i < a.length; i++) s += a[i] === b[i] ? "0" : "1"; return s; }
  function bin(n, w) { var s = n.toString(2); while (s.length < w) s = "0" + s; return s; }
  function isBits(s, n) { return s.length === n && /^[01]+$/.test(s); }

  function genKeys(key) {
    var kl = key.slice(0, 4), kr = key.slice(4), keys = [];
    SHIFTS.forEach(function (s) { kl = rot(kl, s); kr = rot(kr, s); keys.push(permute(kl + kr, COMPRESS)); });
    return keys;
  }
  function fF(half, k) {
    var x = xor(permute(half, EXPAND), k);
    return permute(bin(SBOX[parseInt(x[0] + x[5], 2)][parseInt(x.slice(1, 5), 2)], 4), PBOX);
  }
  function encBlock(b, keys) {
    var L = b.slice(0, 4), R = b.slice(4);
    keys.forEach(function (k) { var nR = xor(L, fF(R, k)); L = R; R = nR; });
    return L + R;
  }
  function decBlock(b, keys) {
    var L = b.slice(0, 4), R = b.slice(4);
    for (var i = 2; i >= 0; i--) { var nL = xor(R, fF(L, keys[i])); R = L; L = nL; }
    return L + R;
  }
  function tinyBytes(data, keys, fn) { return data.map(function (x) { return parseInt(fn(bin(x, 8), keys), 2); }); }

  var PUNCT = ".,!?:;'\"-()\n";
  function readability(data) {       // giống readability_score
    var text;
    try { text = new TextDecoder("utf-8", { fatal: true }).decode(new Uint8Array(data)); }
    catch (e) { return -1000 + data.filter(function (b) { return b >= 32 && b < 127; }).length; }
    var score = 0;
    Array.from(text).forEach(function (ch) {
      if (ch === " ") score += 3;
      else if (/\p{L}/u.test(ch)) score += (ch === ch.toLowerCase() && ch !== ch.toUpperCase()) ? 2 : 1;
      else if (/\p{Nd}/u.test(ch) || PUNCT.indexOf(ch) >= 0) score += 1;
      else if (/[\p{C}\p{Z}]/u.test(ch)) score -= 5;
    });
    return Math.round(score / data.length * 1000) / 1000;
  }

  // ===================== DES (giống core/des_core.py, đánh số bit từ 1) =====================
  var IP = [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7];
  var IP_INV = [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25];
  var E = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,16,17,18,19,20,21,20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1];
  var P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25];
  var PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4];
  var PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32];
  var DSHIFT = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1];
  var S = [
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],[0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],[4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],[15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],[3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],[0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],[13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],[13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],[13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],[1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],[13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],[10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],[3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],[14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],[4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],[11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],[10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],[9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],[4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],[13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],[1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],[6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],[1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],[7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],[2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
  ];
  function perm1(b, t) { var s = ""; for (var i = 0; i < t.length; i++) s += b[t[i] - 1]; return s; }
  function toBits(arr) { return arr.map(function (x) { return bin(x, 8); }).join(""); }
  function toBytes(b) { var a = []; for (var i = 0; i < b.length; i += 8) a.push(parseInt(b.slice(i, i + 8), 2)); return a; }

  function desKeys(key8) {
    var k = perm1(toBits(key8), PC1), c = k.slice(0, 28), d = k.slice(28), out = [];
    DSHIFT.forEach(function (s) { c = rot(c, s); d = rot(d, s); out.push(perm1(c + d, PC2)); });
    return out;
  }
  function desF(r, k) {
    var x = xor(perm1(r, E), k), s = "";
    for (var i = 0; i < 8; i++) {
      var g = x.slice(6 * i, 6 * i + 6);
      s += bin(S[i][parseInt(g[0] + g[5], 2)][parseInt(g.slice(1, 5), 2)], 4);
    }
    return perm1(s, P);
  }
  function desBlock(block8, keys) {
    var ip = perm1(toBits(block8), IP), L = ip.slice(0, 32), R = ip.slice(32);
    keys.forEach(function (k) { var nR = xor(L, desF(R, k)); L = R; R = nR; });
    return toBytes(perm1(R + L, IP_INV));
  }
  function desAll(data, keys) { var out = []; for (var i = 0; i < data.length; i += 8) out = out.concat(desBlock(data.slice(i, i + 8), keys)); return out; }
  function pad(data) { var n = 8 - data.length % 8; return data.concat(Array(n).fill(n)); }
  function unpad(data) {
    var n = data[data.length - 1];
    var ok = n >= 1 && n <= 8 && data.slice(-n).every(function (x) { return x === n; });
    if (!ok) throw new Error("Padding sai - có thể do sai khóa hoặc file không phải bản mã DES.");
    return data.slice(0, -n);
  }
  function parseDesKey(text) {   // giống utils.parse_des_key
    text = text.trim();
    if (text.length === 16 && /^[0-9a-fA-F]+$/.test(text)) {
      var a = []; for (var i = 0; i < 16; i += 2) a.push(parseInt(text.slice(i, i + 2), 16)); return a;
    }
    var raw = Array.from(new TextEncoder().encode(text));
    if (raw.length === 8) return raw;
    throw new Error("Khóa DES phải là 8 ký tự hoặc 16 ký tự hex (VD: 133457799BBCDFF1).");
  }

  // ===================== 3 "API" giống app.py =====================
  function utf8(s) { return Array.from(new TextEncoder().encode(s)); }
  function text(b) { return new TextDecoder("utf-8").decode(new Uint8Array(b)); }
  function hex(b) { return b.map(function (x) { return x.toString(16).toUpperCase().padStart(2, "0"); }).join(" "); }
  function unhex(s) { return String(s || "").trim().split(/\s+/).filter(Boolean).map(function (h) { return parseInt(h, 16); }); }

  function cipherFor(algo, key) {     // giống chat_cipher
    if (algo === "tinydes") {
      if (!isBits(key, 8)) throw new Error("Khóa TinyDES phải gồm đúng 8 bit 0/1, VD 11011010.");
      var ks = genKeys(key);
      return { enc: function (d) { return tinyBytes(d, ks, encBlock); }, dec: function (d) { return tinyBytes(d, ks, decBlock); }, keys: ks };
    }
    var dk = desKeys(parseDesKey(key)), rk = dk.slice().reverse();
    return { enc: function (d) { return desAll(pad(d), dk); }, dec: function (d) { return unpad(desAll(d, rk)); } };
  }

  var routes = {
    "/api/chat/send": function (b) {
      if (!b.text) throw new Error("An chưa gõ tin nhắn.");
      var c = cipherFor(b.algo, b.key), t0 = performance.now();
      var cipher = c.enc(utf8(b.text)), bob = text(c.dec(cipher));
      return { ok: true, cipher_hex: hex(cipher), n_bytes: cipher.length, n_plain: utf8(b.text).length, bob_text: bob,
               elapsed: Math.round((performance.now() - t0) * 100) / 100,
               weak: b.algo === "tinydes" && new Set(c.keys).size < 3 };
    },
    "/api/chat/attack": function (b) {
      var cipher = unhex(b.cipher_hex), t0 = performance.now();
      if (!cipher.length) throw new Error("Không có bản mã để tấn công.");
      if (b.algo === "tinydes") {
        var cands = [];
        for (var k = 0; k < 256; k++) {
          var key = bin(k, 8), plain = tinyBytes(cipher, genKeys(key), decBlock);
          cands.push({ key: key, score: readability(plain), text: text(plain) });
        }
        cands.sort(function (x, y) { return y.score - x.score; });   // điểm cao nhất lên đầu
        return { ok: true, algo: "tinydes", tried: 256, elapsed: Math.round((performance.now() - t0) * 100) / 100,
                 success: cands[0].key === b.key, top: cands.slice(0, 3) };
      }
      var first = cipher.slice(0, 8), TRY = 2000;
      for (var i = 0; i < TRY; i++) desBlock(first, desKeys([0, 0, 0, 0, 0, 0, i >> 8, i & 255]).reverse());
      var ms = performance.now() - t0, perSec = TRY / (ms / 1000);
      return { ok: true, algo: "des", tried: TRY, elapsed: Math.round(ms * 100) / 100, success: false,
               per_sec: Math.round(perSec), years: Math.pow(2, 56) / perSec / (3600 * 24 * 365) };
    },
    "/api/chat/chosen": function (b) {   // giống chat_chosen: lập bảng tra 256 dòng bằng hộp đen, rồi tra bảng
      var cipher = unhex(b.cipher_hex), t0 = performance.now();
      if (!cipher.length) throw new Error("Không có bản mã để tấn công.");
      if (b.algo === "des") return { ok: true, algo: "des", rows: Math.pow(2, 64), success: false };
      var box = cipherFor(b.algo, b.key), book = {};
      for (var p = 0; p < 256; p++) book[box.enc([p])[0]] = p;        // hộp đen chỉ cho mã hóa, không cho xem khóa
      var plain = cipher.map(function (c) { return book[c]; });
      return { ok: true, algo: "tinydes", calls: 256, rows: Object.keys(book).length,
               elapsed: Math.round((performance.now() - t0) * 100) / 100, success: true, text: text(plain) };
    },
    "/api/chat/tamper": function (b) {
      var cipher = unhex(b.cipher_hex);
      if (!cipher.length) throw new Error("Không có bản mã để sửa.");
      var index = (b.index || 0) % cipher.length;
      cipher[index] ^= 0x01;                       // đổi đúng 1 bit
      var c = cipherFor(b.algo, b.key), bob = null, err = null;
      try { bob = text(c.dec(cipher)); } catch (e) { err = e.message; }
      return { ok: true, cipher_hex: hex(cipher), index: index, bob_text: bob, bob_error: err };
    }
  };

  // chat.js gọi window.LOCAL_API(path, body) thay cho fetch tới server
  window.LOCAL_API = function (path, body) {
    return new Promise(function (resolve, reject) {
      setTimeout(function () {          // nhường trình duyệt vẽ chữ "Đang thử khóa…" trước khi tính
        try { resolve(routes[path](body)); } catch (e) { reject(e); }
      }, 20);
    });
  };
})();
