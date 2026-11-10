"use strict";
// Playground Advisor (loop-65). Vanilla JS, no build step, no dependencies.
// Shows the close-area-benchmark results (data/advisor.json, built by data/build_advisor.py) for the
// selected preset family and sensor, recommends a planner, and explains every option.
//   const adv = Advisor.mount(container, { getFamily, getPreset, onPick });
//   getFamily() => "maze" | { custom: true, from: "maze" | null }
//   getPreset() => "ideal" | "crazyflie" | "crazyflie_bright"
//   onPick(plannerId, { planner, filter, bench })   called by the "Use this" buttons
// Optional: getAvailable() => array of planner option ids the playground offers (others get no button),
//           dataUrl, pollMs (default 400; 0 = only adv.refresh()).
(function () {
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const SCRIPT = document.currentScript && document.currentScript.src;
  const DEFAULT_URL = SCRIPT ? new URL("data/advisor.json", SCRIPT).href : "data/advisor.json";
  const PRESET_LABEL = { ideal: "ideal: 72 rays, 360 deg, 6 m", crazyflie: "Crazyflie: 4 cone beams, 3 m", crazyflie_bright: "Crazyflie, bright light: 0.73 m" };
  const FAULT_LABEL = { truth: "off: planner sees truth", none: "VIO EKF, no fault", jump: "VIO jump 0.5 m", bias: "VIO bias 0.05 m/s, 10 s", dropout: "VIO dropout 2 s" };
  const FILTER_LABEL = { none: "none", F2: "F2: PX4-CBF on ranges" };
  const COLS = [
    ["rank", "#", "num"], ["label", "Planner", "txt"], ["map", "Map", "txt"], ["reached", "Reached", "num"],
    ["collision", "Collision", "num"], ["stuck", "Stuck", "num"], ["median_time_s", "Median time", "num"], ["bar", "", "none"],
  ];
  let cache = null;
  function load(url) {
    if (!cache) cache = fetch(url).then(r => { if (!r.ok) throw new Error(r.status + " " + url); return r.json(); });
    return cache;
  }
  const pc = v => (v == null ? "-" : Math.round(v) + " %");
  const sec = v => (v == null ? "-" : Math.round(v) + " s");

  function mount(container, opts) {
    opts = opts || {};
    const st = { data: null, err: null, sort: { key: "rank", dir: 1 }, key: "", pop: null };
    const root = document.createElement("section");
    root.className = "adv";
    root.setAttribute("aria-label", "Advisor: which planner to pick");
    container.appendChild(root);
    root.innerHTML = '<p class="small muted">Loading advisor data...</p>';

    function ctx() {
      let fam = null, custom = false, from = null;
      try {
        const f = opts.getFamily ? opts.getFamily() : null;
        if (f && typeof f === "object") { custom = !!f.custom; from = f.from || f.family || null; fam = custom ? null : f.family; }
        else fam = f || null;
      } catch (e) { fam = null; }
      let preset = "ideal";
      try { preset = (opts.getPreset && opts.getPreset()) || "ideal"; } catch (e) { /* keep ideal */ }
      let avail = null;
      try { avail = opts.getAvailable ? opts.getAvailable() : null; } catch (e) { avail = null; }
      return { fam, custom, from, preset, avail };
    }

    function pick(bench) {
      const p = st.data.planners[bench].playground;
      if (opts.onPick) opts.onPick(p.planner, { planner: p.planner, filter: p.filter, bench });
      const msg = root.querySelector(".adv-picked");
      if (msg) msg.textContent = `Set planner ${p.planner}` + (p.filter !== "none" ? ` and filter ${p.filter}` : "") + ".";
    }

    function usable(bench, c) {
      const p = st.data.planners[bench].playground.planner;
      return c.avail ? c.avail.includes(p) : true;
    }

    function useBtn(bench, c, text, cls) {
      const ok = usable(bench, c);
      return `<button type="button" class="btn sm ${cls || ""}" data-use="${esc(bench)}"${ok ? "" : ' disabled title="Not offered by this playground yet"'}>${esc(text)}</button>`;
    }

    function info(kind, id) {
      return `<button type="button" class="adv-i" data-info="${esc(kind)}:${esc(id)}" aria-label="About ${esc(id)}" aria-expanded="false">i</button>`;
    }

    function recCard(title, r, cells, c, family, preset) {
      const D = st.data;
      let w = r.winner, swapNote = "";
      if (!usable(w, c)) {             // a tied planner the playground offers is just as good by reach and collision
        const alt = r.ties.find(p => usable(p, c));
        if (alt) { swapNote = `<p class="small muted">Ties with ${esc(D.planners[w].label)} (fastest, ${sec(cells[w].median_time_s)} median), which this playground does not offer yet.</p>`; w = alt; }
      }
      const cell = cells[w];
      const why = w === r.winner ? r.reason : `${pc(cell.reached)} reached, ${pc(cell.collision)} collision, ${sec(cell.median_time_s)} median (${cell.n} layouts, seed 0, synthetic).`;
      const others = [r.winner].concat(r.ties).filter(p => p !== w && !(swapNote && p === r.winner));
      const ties = others.length ? `<p class="small muted">Tied on reached and collision: ${others.map(esc).join(", ")}.</p>` : "";
      let late = "";
      if (shorterLimit(cell, c) && cell.reached_within_60s != null && cell.reached_within_60s < cell.reached)
        late = `<p class="small adv-warn">The playground stops runs at ${pgLimitS(c.famUsed)} s here. Within 60 s this planner reached ${pc(cell.reached_within_60s)} (benchmark limit ${cell.max_time_s} s).</p>`;
      const weak = r.weak ? `<p class="small adv-warn">${esc(r.weak)}</p><p>${useBtn(r.safest, c, "Use the safest: " + D.planners[r.safest].label)}</p>` : "";
      return `<div class="adv-card"><h4>${esc(title)}</h4>
        <p class="adv-win"><strong>${esc(D.planners[w].label)}</strong> ${info("planner", w)}</p>
        <p class="small">${esc(why)}</p>${swapNote}${ties}${late}${weak}
        <p>${useBtn(w, c, "Use this", "primary")}</p></div>`;
    }

    // Run time limit the playground uses for a family: worker.js max_time_for (bench.py LONG_FAMILIES, loop-73b).
    // The "by 60 s" notes only apply when the playground limit is shorter than the benchmark cell's.
    function pgLimitS(fam) { return ({ maze: 120, warehouse: 120 })[fam] || 60; }
    function shorterLimit(cell, c) { return cell.max_time_s != null && pgLimitS(c.famUsed) < cell.max_time_s; }

    function rows(cells, c) {
      const D = st.data, rank = {};
      const ranked = D.recommend[c.famUsed][c.presetUsed].ranked;
      ranked.forEach((p, i) => { rank[p] = i + 1; });
      const list = Object.keys(cells).map(p => ({ p, rank: rank[p], label: D.planners[p].label, map: D.planners[p].needs_prior_map ? "prior" : "none", ...cells[p] }));
      const { key, dir } = st.sort;
      list.sort((a, b) => {
        let x = a[key], y = b[key];
        if (key === "median_time_s") { x = x == null ? 1e9 : x; y = y == null ? 1e9 : y; }
        if (typeof x === "string") return dir * x.localeCompare(y) || a.rank - b.rank;
        return dir * (x - y) || a.rank - b.rank;
      });
      return list.map(r => {
        const bar = `<span class="adv-bar" aria-hidden="true"><i class="r" style="width:${r.reached}%"></i><i class="c" style="width:${r.collision}%"></i><i class="s" style="width:${r.stuck}%"></i><i class="t" style="width:${r.timeout}%"></i></span>`;
        const notPg = !D.planners[r.p].in_playground_now ? ' <span class="adv-tag">new</span>' : "";
        const t60 = shorterLimit(r, c) && r.reached_within_60s != null && r.reached_within_60s < r.reached ? `<span class="adv-sub">${pc(r.reached_within_60s)} by 60 s</span>` : "";
        const ok = usable(r.p, c);
        return `<tr${r.p === D.recommend[c.famUsed][c.presetUsed].no_map.winner || r.p === D.recommend[c.famUsed][c.presetUsed].prior_map.winner ? ' class="adv-best"' : ""}>
          <td class="num">${r.rank}</td>
          <td class="adv-name">${ok ? `<button type="button" class="adv-link" data-use="${esc(r.p)}" title="Use this planner">${esc(r.label)}</button>` : `<span title="Not offered by this playground yet">${esc(r.label)}</span>`}${notPg} ${info("planner", r.p)}</td>
          <td>${r.map}</td><td class="num">${pc(r.reached)}${t60}</td><td class="num">${pc(r.collision)}</td><td class="num">${pc(r.stuck)}</td>
          <td class="num">${sec(r.median_time_s)}</td><td class="adv-barcell">${bar}</td></tr>`;
      }).join("");
    }

    function render() {
      const D = st.data;
      if (st.err) { root.innerHTML = `<p class="small bad">Advisor data did not load: ${esc(st.err)}</p>`; return; }
      if (!D) return;
      const c = ctx();
      closePop();
      const head = `<div class="adv-head"><h3>Advisor</h3><span class="badge synthetic">synthetic benchmark</span></div>`;
      let note = "";
      let fam = c.fam;
      if (c.custom || !fam || !D.families.includes(fam)) {
        const near = c.from && D.families.includes(c.from) ? c.from : null;
        if (!near) {
          root.innerHTML = head + `<p class="adv-note">No benchmark for custom worlds. Load a preset world to see measured success rates per planner.</p>` + optionsHtml(null, c);
          return;
        }
        note = `<p class="adv-note">No benchmark for custom worlds. This world was edited from the ${esc(D.family_labels[near])} preset, so the table shows that family. Your edits may change the result.</p>`;
        fam = near;
      }
      let preset = c.preset;
      if (!D.presets.includes(preset)) {
        const near = (D.not_in_benchmark.nearest_preset || {})[preset] || "ideal";
        note += `<p class="adv-note">The ${esc(PRESET_LABEL[preset] || preset)} sensor is not in the benchmark. Showing ${esc(PRESET_LABEL[near] || near)}, the nearest. ${info("preset", preset)}</p>`;
        preset = near;
      }
      c.famUsed = fam; c.presetUsed = preset;
      const cells = D.cells[fam][preset], R = D.recommend[fam][preset];
      const sub = `<p class="small muted">${esc(D.family_labels[fam])}, sensor ${esc(PRESET_LABEL[preset])} ${info("preset", preset)}. ${D.bench.layouts} layouts, seed ${D.bench.seed}, true pose, scored on truth. Not a flight result.</p>`;
      const recs = `<div class="adv-recs">${recCard("Have a map of the room", R.prior_map, cells, c, fam, preset)}${recCard("No map, build it in flight", R.no_map, cells, c, fam, preset)}</div><p class="small adv-picked" aria-live="polite"></p>`;
      const th = COLS.map(([k, t, kind]) => {
        if (kind === "none") return `<th scope="col" class="adv-barcell"><span class="adv-legend"><i class="r"></i>reached <i class="c"></i>collision <i class="s"></i>stuck <i class="t"></i>timeout</span></th>`;
        const on = st.sort.key === k, aria = on ? (st.sort.dir > 0 ? "ascending" : "descending") : "none";
        return `<th scope="col" aria-sort="${aria}"${kind === "num" ? ' class="num"' : ""}><button type="button" data-sort="${k}">${esc(t)}${on ? (st.sort.dir > 0 ? " ^" : " v") : ""}</button></th>`;
      }).join("");
      const table = `<div class="adv-scroll"><table class="adv-table"><caption class="small muted">All ${Object.keys(cells).length} benchmark planners. # = rank by the rule: reached, then collision, then time. Click a header to sort.</caption><thead><tr>${th}</tr></thead><tbody>${rows(cells, c)}</tbody></table></div>`;
      const diff = D.playground_differences, sh = diff.astar_unknown_shipped_vs_bench[fam];
      const caveats = `<details class="adv-more"><summary>Why a playground run can differ</summary><ul class="small">
        <li>${esc(diff.one_layout)}</li><li>${esc(diff.time_limit)}</li>
        <li>${esc(diff.astar_unknown_map_corner)}${sh ? ` Here: ${sh.shipped_prior} % vs ${sh.benchmark_geofence} %.` : ""}</li>
        <li>The benchmark gives every planner the true pose. VIO faults and F2 on other planners are not in it: see the option notes below.</li></ul></details>`;
      root.innerHTML = head + note + sub + recs + table + caveats + optionsHtml(fam, c);
    }

    function optionsHtml(fam, c) {
      const D = st.data, d = D.docs;
      const group = (title, kind, ids, labels) => `<div class="adv-opt"><span class="adv-opt-t">${esc(title)}</span>` +
        ids.map(id => `<span class="adv-chip">${esc(labels[id] || id)} ${info(kind, id)}</span>`).join("") + "</div>";
      return `<div class="adv-opts"><h4>What each option does</h4>
        ${group("Sensor", "preset", Object.keys(d.preset), PRESET_LABEL)}
        ${group("VIO fault", "fault", Object.keys(d.fault), FAULT_LABEL)}
        ${group("Safety filter", "filter", Object.keys(d.filter), FILTER_LABEL)}
        <p class="small muted">Planner notes: the (i) next to each planner in the table.</p></div>`;
    }

    function docHtml(kind, id) {
      const D = st.data, d = D.docs[kind] && D.docs[kind][id];
      if (!d) return `<p>No notes for ${esc(id)}.</p>`;
      const c = ctx(), fam = c.fam || c.from;
      const title = kind === "planner" ? D.planners[id].label : ({ preset: PRESET_LABEL, fault: FAULT_LABEL, filter: FILTER_LABEL }[kind][id] || id);
      const rowsOut = [];
      if (d.what) rowsOut.push(["What", d.what]);
      if (d.needs) rowsOut.push(["Needs", d.needs]);
      if (d.good) rowsOut.push(["Good at", d.good]);
      if (d.fails) rowsOut.push(["Fails", d.fails]);
      if (d.impact) rowsOut.push(["Impact", d.impact]);
      if (d.by_family && fam && d.by_family[fam]) rowsOut.push([`On ${fam}`, d.by_family[fam]]);
      let extra = "";
      if (d.matrix) extra = `<p class="adv-pop-sub">In the benchmark</p><ul>${d.matrix.map(l => `<li>${esc(l)}</li>`).join("")}</ul>`;
      const src = (d.src || []).map(s => esc(s)).join(", ");
      return `<p class="adv-pop-t">${esc(title)}</p><dl>${rowsOut.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>${extra}` +
        `<p class="adv-pop-src">Synthetic. Source: ${src || "close-area-benchmark"}</p>`;
    }

    function closePop() {
      if (!st.pop) return;
      st.pop.el.remove();
      if (st.pop.btn) st.pop.btn.setAttribute("aria-expanded", "false");
      st.pop = null;
    }

    function openPop(btn) {
      const same = st.pop && st.pop.btn === btn;
      closePop();
      if (same) return;
      const [kind, id] = btn.dataset.info.split(":");
      const el = document.createElement("div");
      el.className = "adv-pop";
      el.setAttribute("role", "dialog");
      el.setAttribute("aria-label", "About " + id);
      el.innerHTML = `<button type="button" class="adv-x" aria-label="Close">x</button>` + docHtml(kind, id);
      root.appendChild(el);
      const rb = root.getBoundingClientRect(), bb = btn.getBoundingClientRect();
      const w = Math.min(360, rb.width - 8);
      el.style.width = w + "px";
      el.style.left = Math.max(4, Math.min(bb.left - rb.left - 20, rb.width - w - 4)) + "px";
      el.style.top = (bb.bottom - rb.top + 6) + "px";
      btn.setAttribute("aria-expanded", "true");
      st.pop = { el, btn };
      el.querySelector(".adv-x").focus({ preventScroll: true });
    }

    root.addEventListener("click", ev => {
      const t = ev.target.closest("button");
      if (!t) return;
      if (t.classList.contains("adv-x")) { const b = st.pop && st.pop.btn; closePop(); if (b) b.focus(); return; }
      if (t.dataset.info) { openPop(t); return; }
      if (t.dataset.sort) {
        const k = t.dataset.sort;
        st.sort = st.sort.key === k ? { key: k, dir: -st.sort.dir } : { key: k, dir: ["reached", "label", "rank", "map"].includes(k) ? (k === "reached" ? -1 : 1) : 1 };
        render();
        const again = root.querySelector(`[data-sort="${k}"]`); if (again) again.focus();
        return;
      }
      if (t.dataset.use) pick(t.dataset.use);
    });
    document.addEventListener("click", ev => { if (st.pop && !st.pop.el.contains(ev.target) && ev.target !== st.pop.btn) closePop(); });
    document.addEventListener("keydown", ev => { if (ev.key === "Escape" && st.pop) { const b = st.pop.btn; closePop(); b.focus(); } });

    function keyNow() { const c = ctx(); return JSON.stringify([c.fam, c.custom, c.from, c.preset, c.avail]); }
    function refresh(force) {
      const k = keyNow();
      if (!force && k === st.key) return;
      st.key = k;
      render();
    }

    load(opts.dataUrl || DEFAULT_URL).then(d => { st.data = d; refresh(true); }).catch(e => { st.err = e.message; render(); });
    const poll = opts.pollMs == null ? 400 : opts.pollMs;
    const timer = poll > 0 ? setInterval(() => { if (st.data) refresh(false); }, poll) : null;
    return { refresh: () => refresh(true), destroy() { if (timer) clearInterval(timer); closePop(); root.remove(); }, get data() { return st.data; }, element: root };
  }

  window.Advisor = { mount, load: url => load(url || DEFAULT_URL) };
})();
