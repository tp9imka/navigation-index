// Worker pool for the Solver: K ES-module workers running site/playground/worker.js unchanged.
// Each worker loads Pyodide once. Jobs wait in one FIFO queue and go to the first idle, ready worker.
// The first worker starts alone; the others start when it is ready (or fails), so a cold load
// downloads the 22 MB once and the others load from the browser cache.
// A job ends exactly once, through onDone(job, result, error): a worker error message, a worker
// crash (onerror) or a watchdog timeout all give error != null. cancel() terminates every worker;
// queued and running jobs are reported back through onCancel(jobs), not as results.

export class Pool {
  constructor({ url, size, onReady, onProgress, onDone, onFatal, onCancel, jobTimeoutS = 180, makeWorker }) {
    this.url = url; this.size = Math.max(1, size | 0);
    this.cb = { onReady, onProgress, onDone, onFatal, onCancel };
    this.jobTimeoutS = jobTimeoutS;
    this.makeWorker = makeWorker || (u => new Worker(u, { type: "module" }));
    this.slots = []; this.queue = []; this.nextId = 1; this.env = null; this.closed = false; this.readyCount = 0;
  }

  start() {
    this._spawn(0);
    return this;
  }

  _spawn(i) {
    if (this.closed) return;
    const slot = { i, w: this.makeWorker(this.url), ready: false, dead: false, job: null, timer: null, t0: performance.now() };
    this.slots[i] = slot;
    slot.w.onmessage = ev => this._msg(slot, ev.data || {});
    slot.w.onerror = ev => {
      if (ev && ev.preventDefault) ev.preventDefault();
      this._crash(slot, "worker crashed: " + ((ev && ev.message) || "unknown error"));
    };
  }

  _spawnRest() {
    if (this._restStarted) return;
    this._restStarted = true;
    for (let i = 1; i < this.size; i++) this._spawn(i);
  }

  _msg(slot, m) {
    if (slot.dead || this.closed) return;
    if (m.type === "progress" || m.type === "retry") { if (this.cb.onProgress) this.cb.onProgress(slot.i, m); return; }
    if (m.type === "ready") {
      slot.ready = true; this.readyCount++;
      slot.load_ms = Math.round(performance.now() - slot.t0);
      if (!this.env) this.env = m.env;
      if (this.cb.onReady) this.cb.onReady(slot.i, m, this.readyCount);
      this._spawnRest();
      this._pump();
      return;
    }
    if (m.type === "result" || m.type === "error") {
      if (m.fatal || m.id == null) { this._crash(slot, m.message || "load failed"); return; }
      const job = slot.job;
      if (!job || job.id !== m.id) return;
      this._finish(slot, m.type === "result" ? m.result : null, m.type === "error" ? (m.message || "error") : null);
    }
  }

  _finish(slot, result, error) {
    const job = slot.job;
    clearTimeout(slot.timer);
    slot.job = null; slot.timer = null;
    if (job) {
      job.wall_ms = Math.round(performance.now() - job.t_sent);
      if (this.cb.onDone) this.cb.onDone(job, result, error);
    }
    this._pump();
  }

  // The worker died (crash, fatal load error or watchdog): its job ends as an error; a worker that
  // was ready gets one replacement, a worker that never became ready is not restarted.
  _crash(slot, why) {
    if (slot.dead) return;
    slot.dead = true;
    clearTimeout(slot.timer);
    try { slot.w.terminate(); } catch (err) { /* already gone */ }
    const job = slot.job; slot.job = null;
    if (job) {
      job.wall_ms = Math.round(performance.now() - job.t_sent);
      if (this.cb.onDone) this.cb.onDone(job, null, why);
    }
    const wasReady = slot.ready;
    if (wasReady) this.readyCount--;
    this._spawnRest();
    if (wasReady && !this.closed) this._spawn(slot.i);
    else if (!this.slots.some(s => s && !s.dead) && this.cb.onFatal) this.cb.onFatal(why);
    this._pump();
  }

  // Add jobs ({world, cfg, ...anything}); returns them with ids. FIFO.
  add(jobs) {
    for (const j of jobs) { j.id = this.nextId++; this.queue.push(j); }
    this._pump();
    return jobs;
  }

  _pump() {
    if (this.closed) return;
    for (const slot of this.slots) {
      if (!slot || slot.dead || !slot.ready || slot.job || !this.queue.length) continue;
      const job = this.queue.shift();
      slot.job = job; job.worker = slot.i; job.t_sent = performance.now();
      slot.timer = setTimeout(() => this._crash(slot, `no result after ${this.jobTimeoutS} s (watchdog)`), this.jobTimeoutS * 1000);
      slot.w.postMessage({ type: "run", id: job.id, world: job.world, cfg: job.cfg });
    }
  }

  get busy() { return this.queue.length + this.slots.filter(s => s && s.job).length; }
  get alive() { return this.slots.filter(s => s && !s.dead).length; }

  // Stop everything: terminate the workers (a running Python call cannot be interrupted otherwise).
  cancel() {
    if (this.closed) return [];
    this.closed = true;
    const left = this.queue.splice(0);
    for (const slot of this.slots) {
      if (!slot) continue;
      clearTimeout(slot.timer);
      if (slot.job) left.unshift(slot.job);
      slot.job = null; slot.dead = true;
      try { slot.w.terminate(); } catch (err) { /* already gone */ }
    }
    if (this.cb.onCancel) this.cb.onCancel(left);
    return left;
  }
}
