// Draws a compact close-area-world preset top-down on every canvas[data-world]. Data: real presets from
// site/playground/presets (synthetic layouts), rounded. o = [kind, ...geometry, glass]: w = wall x0 y0 x1 y1, b = box cx cy hx hy.
(function () {
  function css(el, name, fb) { var v = getComputedStyle(el).getPropertyValue(name).trim(); return v || fb; }
  function extent(w) {
    var xs = [w.a[0], w.b[0]], ys = [w.a[1], w.b[1]];
    w.o.forEach(function (o) { if (o[0] === "w") { xs.push(o[1], o[3]); ys.push(o[2], o[4]); } else { xs.push(o[1] - o[3], o[1] + o[3]); ys.push(o[2] - o[4], o[2] + o[4]); } });
    var m = 1;
    return [Math.min.apply(0, xs) - m, Math.min.apply(0, ys) - m, Math.max.apply(0, xs) + m, Math.max.apply(0, ys) + m];
  }
  function draw(cv) {
    var w = (window.NAV_WORLDS || {})[cv.dataset.world]; if (!w) return;
    var dpr = window.devicePixelRatio || 1, W = cv.clientWidth, H = cv.clientHeight;
    if (!W || !H) return;
    cv.width = W * dpr; cv.height = H * dpr;
    var g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0);
    var b = extent(w), pad = 12, s = Math.min((W - 2 * pad) / (b[2] - b[0]), (H - 2 * pad) / (b[3] - b[1]));
    var ox = (W - s * (b[2] - b[0])) / 2, oy = (H - s * (b[3] - b[1])) / 2;
    function X(x) { return ox + (x - b[0]) * s; } function Y(y) { return H - (oy + (y - b[1]) * s); }
    var obst = css(cv, "--obst", "#3c3c38"), glass = css(cv, "--glass", "#3d9cc4"), grid = css(cv, "--line", "#deded8");
    g.clearRect(0, 0, W, H);
    g.strokeStyle = grid; g.lineWidth = 1;
    for (var gx = Math.ceil(b[0]); gx <= b[2]; gx++) { g.beginPath(); g.moveTo(X(gx), Y(b[1])); g.lineTo(X(gx), Y(b[3])); g.stroke(); }
    for (var gy = Math.ceil(b[1]); gy <= b[3]; gy++) { g.beginPath(); g.moveTo(X(b[0]), Y(gy)); g.lineTo(X(b[2]), Y(gy)); g.stroke(); }
    w.o.forEach(function (o) {
      var c = o[5] ? glass : obst; g.fillStyle = c; g.strokeStyle = c;
      if (o[0] === "w") { g.lineWidth = Math.max(o[5] ? 3 : 2.5, 0.1 * s); g.lineCap = "square"; g.beginPath(); g.moveTo(X(o[1]), Y(o[2])); g.lineTo(X(o[3]), Y(o[4])); g.stroke(); }
      else { g.fillRect(X(o[1] - o[3]), Y(o[2] + o[4]), 2 * o[3] * s, 2 * o[4] * s); }
    });
    function mark(p, label, col) {
      g.fillStyle = col; g.beginPath(); g.arc(X(p[0]), Y(p[1]), 8, 0, 7); g.fill();
      g.fillStyle = "#fff"; g.font = "700 10px system-ui"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(label, X(p[0]), Y(p[1]) + 0.5);
    }
    mark(w.a, "A", css(cv, "--accent", "#1f5fbf")); mark(w.b, "B", css(cv, "--ok", "#1d7a3a"));
  }
  window.drawArenas = function (root) { (root || document).querySelectorAll("canvas[data-world]").forEach(draw); };
})();
