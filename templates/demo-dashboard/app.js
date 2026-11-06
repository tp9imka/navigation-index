/* Nav demo dashboard: replays navdash/1 JSONL tracks on MapLibre. No build step. */
'use strict';

const SCHEMA = 'navdash/1';
const LINE_ROLES = new Set(['truth', 'ins', 'fused']);
const POINT_ROLES = new Set(['gnss', 'altpnt']);
const ROLE_ORDER = ['truth', 'ins', 'gnss', 'altpnt', 'fused'];
const DEFAULT_COLORS = { truth: '#e8eaed', ins: '#ffb74d', gnss: '#ef5350', altpnt: '#ba68c8', fused: '#4fc3f7' };
const FRIENDLY_UAV_SIDC = 'SFAPMFQ--------'; // 2525C: friend, air, military fixed-wing UAV (CoT a-f-A-M-F-Q)
const SYMBOL_SIZE = 26;
const POINT_TRAIL_S = 30;            // fixes older than this fade to the floor opacity
const POINT_FLOOR_OPACITY = 0.2;
const STALE_GAP_FACTOR = 3;          // a fix older than 3 median periods is "no fix now"
const INTERP_GAP_FACTOR = 5;         // do not interpolate across gaps longer than this
const CIRCLE_VERTICES = 64;
const M_PER_DEG_LAT = 111132.92;
const FIT_PADDING_PX = 60;
const OSM_TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const OSM_ATTRIB = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const EVENT_CLASS = {
  attack_onset: 'gt', gnss_lost: 'warn', gnss_restored: 'ok', spoof_suspected: 'bad', fix_excluded: 'bad',
  fix_readmitted: 'ok', alarm_raised: 'bad', alarm_cleared: 'ok', source_switched: 'info', al_exceeded: 'gt',
};
const CLASS_COLOR = { gt: '#b0bec5', warn: '#ffb300', ok: '#66bb6a', bad: '#ef5350', info: '#4fc3f7' };
const ZONE_COLORS = ['match', ['get', 'kind'], 'jamming', '#ffb300', 'spoofing', '#ef5350', '#ba68c8'];

const params = new URLSearchParams(location.search);
const S = {
  map: null, ready: null, tracks: [], zones: null, events: [], derived: [],
  T: 0, tMin: 0, tMax: 0, playing: false, speed: 5, follow: true, lastFrame: 0,
  marker: null, symbol: null, alertLimit: params.has('al') ? Number(params.get('al')) : null,
  cumErr: null, title: 'Nav demo',
};
const $ = (id) => document.getElementById(id);

/* ---------- geometry ---------- */
function distM(a, b) {
  const lat = (a.lat + b.lat) / 2 * Math.PI / 180;
  const dn = (a.lat - b.lat) * M_PER_DEG_LAT;
  const de = (a.lon - b.lon) * M_PER_DEG_LAT * Math.cos(lat);
  return Math.hypot(dn, de);
}
function circle(c, r) {
  const ring = [];
  const kLon = M_PER_DEG_LAT * Math.cos(c.lat * Math.PI / 180);
  for (let i = 0; i <= CIRCLE_VERTICES; i++) {
    const a = 2 * Math.PI * i / CIRCLE_VERTICES;
    ring.push([c.lon + r * Math.cos(a) / kLon, c.lat + r * Math.sin(a) / M_PER_DEG_LAT]);
  }
  return ring;
}
function median(xs) {
  if (!xs.length) return 1;
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.floor(s.length / 2)];
}

/* ---------- parsing ---------- */
function parseJsonl(text, fallbackName) {
  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  let header = null; const pts = []; const events = [];
  for (const [i, line] of lines.entries()) {
    let o;
    try { o = JSON.parse(line); } catch (e) { throw new Error(`${fallbackName}: line ${i + 1} is not JSON`); }
    if (o.meta && i === 0) throw new Error(`${fallbackName} is a raw navapp run; convert it with convert_navapp.py`);
    if (o.header) header = o.header;
    else if (o.event) events.push(o);
    else if (Number.isFinite(o.t) && Number.isFinite(o.lat) && Number.isFinite(o.lon)) pts.push(o);
  }
  header = header || {};
  if (header.schema && header.schema !== SCHEMA) console.warn(`${fallbackName}: schema ${header.schema}, expected ${SCHEMA}`);
  const role = header.role || 'fused';
  pts.sort((a, b) => a.t - b.t);
  const period = median(pts.slice(1).map((p, i) => p.t - pts[i].t));
  return {
    id: (header.track || fallbackName.replace(/\.[^.]+$/, '')).replace(/[^\w-]/g, '_'),
    role, label: header.label || header.track || fallbackName,
    color: header.color || DEFAULT_COLORS[role] || '#ffffff',
    primary: !!header.primary, header, pts, events, period, visible: true,
  };
}

async function fetchText(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return r.text();
}

function ingest(name, text) {
  let o = null;
  try { o = JSON.parse(text); } catch (e) { /* JSONL: more than one JSON value */ }
  if (o && o.type === 'FeatureCollection') { S.zones = o; return; }
  if (o && Array.isArray(o.tracks)) throw new Error(`${name} is a manifest; open it with ?manifest=`);
  const trk = parseJsonl(text, name);
  S.tracks = S.tracks.filter((t) => t.id !== trk.id).concat(trk);
}

async function loadManifest(url) {
  const base = new URL(url, location.href);
  const m = JSON.parse(await fetchText(base.href));
  S.tracks = []; S.zones = null;
  S.title = m.title || S.title;
  for (const f of m.tracks || []) ingest(f, await fetchText(new URL(f, base).href));
  if (m.zones) S.zones = JSON.parse(await fetchText(new URL(m.zones, base).href));
  await rebuild(true);
}

async function loadUrls(srcs, zonesUrl) {
  for (const u of srcs) ingest(u.split('/').pop(), await fetchText(u));
  if (zonesUrl) S.zones = JSON.parse(await fetchText(zonesUrl));
  await rebuild(true);
}

async function loadFiles(files) {
  for (const f of files) ingest(f.name, await f.text());
  await rebuild(true);
}

/* ---------- sampling ---------- */
function lastIndexAtOrBefore(pts, T) {
  let lo = 0, hi = pts.length - 1, ans = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (pts[mid].t <= T) { ans = mid; lo = mid + 1; } else hi = mid - 1;
  }
  return ans;
}
function sampleAt(trk, T) {
  const p = trk.pts; const i = lastIndexAtOrBefore(p, T);
  if (i < 0) return null;
  const a = p[i];
  if (POINT_ROLES.has(trk.role)) return T - a.t <= STALE_GAP_FACTOR * trk.period ? { ...a, i } : null;
  const b = p[i + 1];
  if (!b || b.t - a.t > INTERP_GAP_FACTOR * trk.period) return { ...a, i };
  const k = (T - a.t) / (b.t - a.t);
  return { ...a, lat: a.lat + k * (b.lat - a.lat), lon: a.lon + k * (b.lon - a.lon), i };
}
const primaryTrack = () => S.tracks.find((t) => t.role === 'fused' && t.primary)
  || S.tracks.find((t) => t.role === 'fused');
const truthTrack = () => S.tracks.find((t) => t.role === 'truth');

function precomputeErrors() {
  S.cumErr = null; S.derived = [];
  const f = primaryTrack(), tr = truthTrack();
  if (!f || !tr) return;
  const al = alertLimit();
  const cum = []; let mx = 0, over = false;
  for (const p of f.pts) {
    const q = sampleAt(tr, p.t);
    if (!q) { cum.push(mx); continue; }
    const e = distM(p, q);
    mx = Math.max(mx, e); cum.push(mx);
    if (al != null && (e > al) !== over) {
      over = e > al;
      S.derived.push({ t: p.t, event: 'al_exceeded', ground_truth: true, _track: f.label,
        text: over ? `True error > AL (${e.toFixed(1)} m), from truth` : `True error back under AL (${e.toFixed(1)} m)` });
    }
  }
  S.cumErr = cum;
}
function alertLimit() {
  if (S.alertLimit != null && Number.isFinite(S.alertLimit)) return S.alertLimit;
  const f = primaryTrack();
  return f && Number.isFinite(f.header.alert_limit_m) ? f.header.alert_limit_m : null;
}

/* ---------- map ---------- */
async function baseStyle() {
  const bg = { id: 'bg', type: 'background', paint: { 'background-color': '#0b0f14' } };
  const basemap = params.get('basemap') || (params.has('pmtiles') ? 'pmtiles' : 'osm');
  const dim = { 'raster-saturation': -0.7, 'raster-brightness-max': 0.4, 'raster-contrast': 0.15 };
  if (basemap === 'none') return { version: 8, sources: {}, layers: [bg] };
  if (basemap === 'pmtiles') {
    const url = new URL(params.get('pmtiles'), location.href).href;
    const protocol = new pmtiles.Protocol();
    maplibregl.addProtocol('pmtiles', protocol.tile);
    const pm = new pmtiles.PMTiles(url);
    protocol.add(pm);
    const h = await pm.getHeader();
    const src = `pmtiles://${url}`;
    if (h.tileType !== pmtiles.TileType.Mvt) {
      return { version: 8, sources: { base: { type: 'raster', url: src, tileSize: 256 } },
        layers: [bg, { id: 'base', type: 'raster', source: 'base', paint: dim }] };
    }
    // Protomaps basemap schema (earth, water, landuse, roads, buildings); no labels, so no glyphs needed.
    const v = (id, type, layer, paint, extra = {}) => ({ id, type, source: 'base', 'source-layer': layer, paint, ...extra });
    return { version: 8, sources: { base: { type: 'vector', url: src, attribution: OSM_ATTRIB } },
      layers: [bg,
        v('earth', 'fill', 'earth', { 'fill-color': '#151c24' }),
        v('landuse', 'fill', 'landuse', { 'fill-color': '#18222b', 'fill-opacity': 0.6 }),
        v('water', 'fill', 'water', { 'fill-color': '#0d2233' }),
        v('buildings', 'fill', 'buildings', { 'fill-color': '#202a35' }),
        v('roads', 'line', 'roads', { 'line-color': '#3a4757', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 16, 3] }),
      ] };
  }
  const tiles = params.get('tiles') || OSM_TILES;
  return { version: 8,
    sources: { base: { type: 'raster', tiles: [tiles], tileSize: 256, maxzoom: 19, attribution: params.get('tiles') ? '' : OSM_ATTRIB } },
    layers: [bg, { id: 'base', type: 'raster', source: 'base', paint: dim }] };
}

async function initMap() {
  S.map = new maplibregl.Map({
    container: 'map', style: await baseStyle(), center: [10, 59], zoom: 3,
    preserveDrawingBuffer: true, attributionControl: { compact: true },
  });
  S.map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-left');
  S.map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
  S.map.on('dragstart', (e) => { if (e.originalEvent) setFollow(false); });
  // style.load, not load: load also waits for basemap tiles, which may be slow or offline.
  S.ready = new Promise((res) => (S.map.isStyleLoaded() ? res() : S.map.once('style.load', res)));
  await S.ready;
  const empty = { type: 'FeatureCollection', features: [] };
  S.map.addSource('zones', { type: 'geojson', data: empty });
  S.map.addLayer({ id: 'zones-fill', type: 'fill', source: 'zones',
    paint: { 'fill-color': ZONE_COLORS, 'fill-opacity': ['case', ['get', '_active'], 0.14, 0.05] } });
  S.map.addLayer({ id: 'zones-line', type: 'line', source: 'zones',
    paint: { 'line-color': ZONE_COLORS, 'line-width': 2, 'line-dasharray': [3, 2], 'line-opacity': ['case', ['get', '_active'], 1, 0.4] } });
  S.map.addSource('rings', { type: 'geojson', data: empty });
  S.map.addSource('heads', { type: 'geojson', data: empty });
}

function addOverlayLayers() {
  const m = S.map;
  for (const id of ['ring-r95', 'ring-al', 'ring-pl', 'err-line', 'heads']) if (m.getLayer(id)) m.removeLayer(id);
  m.addLayer({ id: 'ring-r95', type: 'fill', source: 'rings', filter: ['==', ['get', 'kind'], 'r95'],
    paint: { 'fill-color': '#4fc3f7', 'fill-opacity': 0.18 } });
  m.addLayer({ id: 'ring-al', type: 'line', source: 'rings', filter: ['==', ['get', 'kind'], 'al'],
    paint: { 'line-color': '#e6edf3', 'line-width': 1.5, 'line-dasharray': [2, 2], 'line-opacity': 0.7 } });
  m.addLayer({ id: 'ring-pl', type: 'line', source: 'rings', filter: ['==', ['get', 'kind'], 'pl'],
    paint: { 'line-color': ['get', 'color'], 'line-width': 2.5 } });
  m.addLayer({ id: 'err-line', type: 'line', source: 'rings', filter: ['==', ['get', 'kind'], 'err'],
    paint: { 'line-color': '#ffffff', 'line-width': 1.5, 'line-dasharray': [1, 1.5] } });
  m.addLayer({ id: 'heads', type: 'circle', source: 'heads',
    paint: { 'circle-radius': 6, 'circle-color': ['get', 'color'], 'circle-stroke-color': '#0b0f14', 'circle-stroke-width': 2 } });
}

function trackLayerIds(t) { return [`${t.id}-full`, `${t.id}-prog`, `${t.id}-pts`]; }

function clearTrackLayers() {
  const m = S.map;
  for (const l of m.getStyle().layers) if (l.source && l.source.startsWith('trk-')) m.removeLayer(l.id);
  for (const s of Object.keys(m.getStyle().sources)) if (s.startsWith('trk-')) m.removeSource(s);
}

function addTrackLayers(t) {
  const m = S.map;
  const coords = t.pts.map((p) => [p.lon, p.lat]);
  if (LINE_ROLES.has(t.role)) {
    m.addSource(`trk-${t.id}-full`, { type: 'geojson', data: { type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: coords } } });
    m.addSource(`trk-${t.id}-prog`, { type: 'geojson', data: { type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: [] } } });
    const width = t.role === 'fused' ? 4 : 3;
    m.addLayer({ id: `${t.id}-full`, type: 'line', source: `trk-${t.id}-full`,
      paint: { 'line-color': t.color, 'line-width': width - 1, 'line-opacity': 0.25 }, layout: { 'line-join': 'round' } });
    m.addLayer({ id: `${t.id}-prog`, type: 'line', source: `trk-${t.id}-prog`,
      paint: { 'line-color': t.color, 'line-width': width, ...(t.role === 'ins' ? { 'line-dasharray': [2, 1] } : {}) },
      layout: { 'line-join': 'round', 'line-cap': 'round' } });
  } else {
    m.addSource(`trk-${t.id}-pts`, { type: 'geojson', data: { type: 'FeatureCollection',
      features: t.pts.map((p) => ({ type: 'Feature', properties: { t: p.t }, geometry: { type: 'Point', coordinates: [p.lon, p.lat] } })) } });
    m.addLayer({ id: `${t.id}-pts`, type: 'circle', source: `trk-${t.id}-pts`, filter: ['<=', ['get', 't'], 0],
      paint: { 'circle-radius': 3.5, 'circle-color': t.color, 'circle-opacity': 0.6 } });
  }
}

function applyVisibility(t) {
  for (const id of trackLayerIds(t)) if (S.map.getLayer(id)) S.map.setLayoutProperty(id, 'visibility', t.visible ? 'visible' : 'none');
}

function setTrackColor(t, color) {
  t.color = color;
  for (const id of trackLayerIds(t)) {
    if (!S.map.getLayer(id)) continue;
    S.map.setPaintProperty(id, S.map.getLayer(id).type === 'circle' ? 'circle-color' : 'line-color', color);
  }
  render();
}

/* ---------- vehicle symbol ---------- */
function makeMarker() {
  if (S.marker) return;
  S.symbol = new ms.Symbol(FRIENDLY_UAV_SIDC, { size: SYMBOL_SIZE });
  const el = document.createElement('div');
  el.className = 'vehicle-marker';
  el.innerHTML = S.symbol.asSVG();
  const a = S.symbol.getAnchor();
  S.marker = new maplibregl.Marker({ element: el, anchor: 'top-left', offset: [-a.x, -a.y] });
}

/* ---------- rebuild + render ---------- */
async function rebuild(fit) {
  await S.ready;
  S.tracks.sort((a, b) => ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role));
  if (!S.tracks.some((t) => t.primary) && primaryTrack()) primaryTrack().primary = true;
  clearTrackLayers();
  for (const t of S.tracks) { addTrackLayers(t); applyVisibility(t); }
  addOverlayLayers();
  const all = S.tracks.flatMap((t) => t.pts);
  S.tMin = all.length ? Math.min(...S.tracks.filter((t) => t.pts.length).map((t) => t.pts[0].t)) : 0;
  S.tMax = all.length ? Math.max(...S.tracks.filter((t) => t.pts.length).map((t) => t.pts[t.pts.length - 1].t)) : 0;
  S.T = S.tMin;
  precomputeErrors();
  S.events = S.tracks.flatMap((t) => t.events.map((e) => ({ ...e, _track: t.label, _tid: t.id })))
    .concat(S.derived.map((e) => ({ ...e, _tid: primaryTrack().id }))).sort((a, b) => a.t - b.t);
  $('scrub').min = S.tMin; $('scrub').max = S.tMax;
  $('title').textContent = S.title;
  document.title = S.title;
  makeMarker();
  if (primaryTrack()) S.marker.setLngLat([primaryTrack().pts[0].lon, primaryTrack().pts[0].lat]).addTo(S.map);
  renderTrackList(); renderEvents(); renderTicks();
  if (fit && all.length) {
    const b = new maplibregl.LngLatBounds();
    all.forEach((p) => b.extend([p.lon, p.lat]));
    S.map.fitBounds(b, { padding: FIT_PADDING_PX, duration: 0, maxZoom: 18 });
  }
  render();
}

function render() {
  const m = S.map, T = S.T;
  if (!m || !m.getSource('rings')) return;
  const heads = [];
  for (const t of S.tracks) {
    const cur = sampleAt(t, T);
    if (LINE_ROLES.has(t.role)) {
      const i = lastIndexAtOrBefore(t.pts, T);
      const coords = t.pts.slice(0, i + 1).map((p) => [p.lon, p.lat]);
      if (cur && i >= 0) coords.push([cur.lon, cur.lat]);
      m.getSource(`trk-${t.id}-prog`).setData({ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: coords } });
    } else {
      m.setFilter(`${t.id}-pts`, ['<=', ['get', 't'], T]);
      m.setPaintProperty(`${t.id}-pts`, 'circle-opacity',
        ['interpolate', ['linear'], ['-', T, ['get', 't']], 0, 0.9, POINT_TRAIL_S, POINT_FLOOR_OPACITY]);
    }
    if (cur && t.visible && !(t.role === 'fused' && t === primaryTrack())) {
      heads.push({ type: 'Feature', properties: { color: t.color }, geometry: { type: 'Point', coordinates: [cur.lon, cur.lat] } });
    }
  }
  m.getSource('heads').setData({ type: 'FeatureCollection', features: heads });

  if (S.zones) {
    m.getSource('zones').setData({ ...S.zones, features: S.zones.features.map((f) => {
      const p = f.properties || {};
      const active = (p.t_start == null || T >= p.t_start) && (p.t_end == null || T <= p.t_end);
      return { ...f, properties: { ...p, _active: active } };
    }) });
  }

  const f = primaryTrack(), tr = truthTrack();
  const fc = f ? sampleAt(f, T) : null;
  const tc = tr ? sampleAt(tr, T) : null;
  const al = alertLimit();
  const rings = [];
  let err = null;
  if (fc && f.visible) {
    if (Number.isFinite(fc.r95_m)) rings.push(poly('r95', circle(fc, fc.r95_m)));
    if (al != null) rings.push(poly('al', circle(fc, al)));
    if (Number.isFinite(fc.pl_m)) rings.push(poly('pl', circle(fc, fc.pl_m), al != null && fc.pl_m > al ? '#ef5350' : '#66bb6a'));
    if (tc && tr.visible) rings.push({ type: 'Feature', properties: { kind: 'err' }, geometry: { type: 'LineString', coordinates: [[fc.lon, fc.lat], [tc.lon, tc.lat]] } });
    S.marker.setLngLat([fc.lon, fc.lat]);
    S.marker.getElement().style.display = '';
    if (S.follow) m.jumpTo({ center: [fc.lon, fc.lat] });
  } else if (S.marker) {
    S.marker.getElement().style.display = 'none';
  }
  if (fc && tc) err = distM(fc, tc);
  m.getSource('rings').setData({ type: 'FeatureCollection', features: rings });
  renderMetrics(f, fc, err, al);
  renderEventState();
  $('scrub').value = T;
  $('clock').textContent = `${T.toFixed(1)} / ${S.tMax.toFixed(1)} s`;
}

function poly(kind, ring, color) {
  return { type: 'Feature', properties: { kind, color: color || '#66bb6a' }, geometry: { type: 'Polygon', coordinates: [ring] } };
}

/* ---------- panels ---------- */
function setV(id, text, cls) { const el = $(id); el.textContent = text; el.className = `v ${cls || ''}`; }

function renderMetrics(f, fc, err, al) {
  const pill = $('status-pill');
  $('metric-ref').textContent = f ? `(${f.label})` : '';
  setV('m-time', `${S.T.toFixed(1)} s`);
  if (!f || !fc) {
    pill.textContent = f ? 'NO SOLUTION' : 'NO DATA'; pill.className = 'pill';
    for (const id of ['m-health', 'm-err', 'm-maxerr', 'm-r95', 'm-pl', 'm-alarms', 'm-src']) setV(id, '-');
    $('m-flag').textContent = ''; return;
  }
  const health = fc.health || 'n/a';
  const hcls = { trusted: 'ok', suspect: 'warn', excluded: 'bad', unavailable: 'warn' }[health] || '';
  pill.textContent = health.toUpperCase() + (fc.alarm ? ' + ALARM' : '');
  pill.className = `pill ${fc.alarm ? 'bad' : hcls}`;
  setV('m-health', health, hcls);
  setV('m-err', err == null ? 'not measured' : `${err.toFixed(1)} m`, err == null ? '' : (al != null && err > al ? 'bad' : 'ok'));
  if (S.cumErr && err != null) {
    const i = lastIndexAtOrBefore(f.pts, S.T);
    setV('m-maxerr', `${Math.max(i >= 0 ? S.cumErr[i] : 0, err).toFixed(1)} m`);
  } else setV('m-maxerr', 'not measured');
  setV('m-r95', Number.isFinite(fc.r95_m) ? `${fc.r95_m.toFixed(1)} m` : 'not stated');
  const pl = Number.isFinite(fc.pl_m) ? fc.pl_m : null;
  setV('m-pl', `${pl == null ? 'n/a' : pl.toFixed(1)} / ${al == null ? 'n/a' : al.toFixed(0)} m`,
    pl != null && al != null ? (pl > al ? 'bad' : 'ok') : '');
  const i = lastIndexAtOrBefore(f.pts, S.T);
  let raised = 0;
  for (let k = 0; k <= i; k++) if (f.pts[k].alarm && !(k > 0 && f.pts[k - 1].alarm)) raised++;
  setV('m-alarms', fc.alarm == null ? 'n/a' : `${raised}${fc.alarm ? ' (active)' : ''}`, fc.alarm ? 'bad' : '');
  setV('m-src', (fc.sources || []).join('+') || 'none');

  const flag = $('m-flag');
  let msg = '', cls = '';
  if (err != null && al != null && err > al && !fc.alarm) { msg = 'HAZARDOUSLY MISLEADING: true error > AL, no alarm'; cls = 'bad'; }
  else if (err != null && pl != null && err > pl && !fc.alarm) { msg = 'MISLEADING: true error > PL, no alarm'; cls = 'bad'; }
  else if (fc.alarm) { msg = 'ALARM: integrity monitor flagged the solution'; cls = 'warn'; }
  else if (pl != null && al != null && pl > al) { msg = 'PL > AL: integrity not available'; cls = 'warn'; }
  flag.textContent = msg; flag.className = `flag ${cls}`;
}

function renderTrackList() {
  const ul = $('tracks'); ul.innerHTML = '';
  for (const t of S.tracks) {
    const li = document.createElement('li');
    const cb = Object.assign(document.createElement('input'), { type: 'checkbox', checked: t.visible, title: 'Show / hide' });
    cb.onchange = () => { t.visible = cb.checked; applyVisibility(t); renderEvents(); render(); };
    const col = Object.assign(document.createElement('input'), { type: 'color', value: t.color, title: 'Colour' });
    col.oninput = () => setTrackColor(t, col.value);
    const name = Object.assign(document.createElement('span'), { textContent: t.label + (t.primary && t.role === 'fused' ? ' *' : '') });
    const role = Object.assign(document.createElement('span'), { className: 'role', textContent: t.role });
    li.append(cb, col, name, role);
    ul.append(li);
  }
}

function visibleEvents() {
  const vis = new Set(S.tracks.filter((t) => t.visible).map((t) => t.id));
  return S.events.filter((e) => vis.has(e._tid));
}

function renderEvents() {
  const ul = $('events'); ul.innerHTML = '';
  for (const e of visibleEvents()) {
    const cls = EVENT_CLASS[e.event] || 'info';
    const li = document.createElement('li');
    li.dataset.t = e.t;
    li.innerHTML = `<span class="et">${e.t.toFixed(1)}s</span><span><span style="color:${CLASS_COLOR[cls]}"></span>
      <span class="${e.ground_truth ? 'gt' : ''}"></span><span class="src"></span></span>`;
    const spans = li.querySelectorAll('span span');
    spans[0].textContent = e.event.replace(/_/g, ' ') + ': ';
    spans[1].textContent = e.text || '';
    spans[2].textContent = e._track + (e.ground_truth ? ' (ground truth)' : '');
    li.onclick = () => seek(e.t);
    ul.append(li);
  }
  renderTicks();
  renderEventState(true);
}

function renderTicks() {
  const box = $('ticks'); box.innerHTML = '';
  const span = S.tMax - S.tMin;
  if (span <= 0) return;
  for (const e of visibleEvents()) {
    const d = document.createElement('div');
    d.className = 'tick';
    d.style.left = `${(100 * (e.t - S.tMin)) / span}%`;
    d.style.background = CLASS_COLOR[EVENT_CLASS[e.event] || 'info'];
    d.title = `${e.t.toFixed(1)} s ${e.event}`;
    d.onclick = () => seek(e.t);
    box.append(d);
  }
}

let lastEventMark = null;
function renderEventState(force) {
  const items = [...$('events').children];
  let cur = -1;
  items.forEach((li, k) => { if (Number(li.dataset.t) <= S.T) cur = k; });
  if (!force && cur === lastEventMark) return;
  lastEventMark = cur;
  items.forEach((li, k) => {
    li.classList.toggle('past', k < cur);
    li.classList.toggle('current', k === cur);
  });
  if (cur >= 0) items[cur].scrollIntoView({ block: 'nearest' });
}

/* ---------- transport ---------- */
function seek(t) { S.T = Math.min(Math.max(t, S.tMin), S.tMax); render(); }
function setPlaying(on) {
  S.playing = on && S.tMax > S.tMin;
  if (S.playing && S.T >= S.tMax) S.T = S.tMin;
  $('btn-play').textContent = S.playing ? 'Pause' : 'Play';
  S.lastFrame = performance.now();
  if (S.playing) requestAnimationFrame(tick);
}
function tick(now) {
  if (!S.playing) return;
  S.T += ((now - S.lastFrame) / 1000) * S.speed;
  S.lastFrame = now;
  if (S.T >= S.tMax) { S.T = S.tMax; render(); setPlaying(false); return; }
  render();
  requestAnimationFrame(tick);
}
function setFollow(on) { S.follow = on; $('btn-follow').classList.toggle('on', on); if (on) render(); }

/* ---------- screenshot ---------- */
function screenshot() {
  const mc = S.map.getCanvas();
  const dpr = mc.width / mc.clientWidth;
  const out = document.createElement('canvas');
  out.width = mc.width; out.height = mc.height;
  const g = out.getContext('2d');
  try {
    g.drawImage(mc, 0, 0);
    const f = primaryTrack(); const fc = f && sampleAt(f, S.T);
    if (fc && S.symbol) {
      const p = S.map.project([fc.lon, fc.lat]);
      const sym = new ms.Symbol(FRIENDLY_UAV_SIDC, { size: SYMBOL_SIZE * dpr });
      const a = sym.getAnchor();
      g.drawImage(sym.asCanvas(), p.x * dpr - a.x, p.y * dpr - a.y);
    }
    const lines = [S.title, `t = ${S.T.toFixed(1)} s   ${$('status-pill').textContent}`,
      `error ${$('m-err').textContent}   max ${$('m-maxerr').textContent}`,
      `PL/AL ${$('m-pl').textContent}   alarms ${$('m-alarms').textContent}`, $('m-flag').textContent].filter(Boolean);
    const fs = 14 * dpr, pad = 8 * dpr;
    g.font = `600 ${fs}px system-ui, sans-serif`;
    const w = Math.max(...lines.map((l) => g.measureText(l).width)) + 2 * pad;
    g.fillStyle = 'rgba(11,15,20,0.85)';
    g.fillRect(pad, pad, w, lines.length * fs * 1.35 + pad);
    g.fillStyle = '#e6edf3';
    lines.forEach((l, k) => g.fillText(l, 2 * pad, pad + fs * (1 + 1.35 * k)));
    out.toBlob((blob) => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `navdemo-t${S.T.toFixed(1)}.png`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    });
  } catch (e) {
    alert(`Screenshot failed (${e.message}). A tile server without CORS taints the canvas; use basemap=none or local PMTiles.`);
  }
}

/* ---------- wiring ---------- */
function toast(msg) { console.error(msg); const f = $('m-flag'); f.textContent = msg; f.className = 'flag bad'; }
const guard = (p) => p.catch((e) => toast(e.message));

function wire() {
  $('file-input').onchange = (e) => guard(loadFiles([...e.target.files]));
  $('btn-sample').onclick = () => guard(loadManifest('sample/spoof/manifest.json'));
  $('btn-sample-jam').onclick = () => guard(loadManifest('sample/jam/manifest.json'));
  $('btn-play').onclick = () => setPlaying(!S.playing);
  $('btn-follow').onclick = () => setFollow(!S.follow);
  $('btn-shot').onclick = screenshot;
  $('speed').value = params.get('speed') || '5';
  S.speed = Number($('speed').value);
  $('speed').onchange = (e) => { S.speed = Number(e.target.value); };
  $('scrub').oninput = (e) => seek(Number(e.target.value));
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' && e.target.type !== 'range') return;
    if (e.code === 'Space') { e.preventDefault(); setPlaying(!S.playing); }
    else if (e.code === 'ArrowRight') seek(S.T + (e.shiftKey ? 10 : 1));
    else if (e.code === 'ArrowLeft') seek(S.T - (e.shiftKey ? 10 : 1));
    else if (e.code === 'Home') seek(S.tMin);
    else if (e.code === 'KeyF') setFollow(!S.follow);
    else if (e.code === 'KeyS') screenshot();
  });
  const hint = $('drop-hint');
  window.addEventListener('dragover', (e) => { e.preventDefault(); hint.classList.add('show'); });
  window.addEventListener('dragleave', (e) => { if (!e.relatedTarget) hint.classList.remove('show'); });
  window.addEventListener('drop', (e) => {
    e.preventDefault(); hint.classList.remove('show');
    guard(loadFiles([...e.dataTransfer.files]));
  });
}

async function main() {
  wire();
  if (params.has('follow')) setFollow(params.get('follow') !== '0');
  await initMap();
  if (params.has('manifest')) await loadManifest(params.get('manifest'));
  else if (params.has('src')) await loadUrls(params.getAll('src'), params.get('zones'));
  if (params.has('t')) seek(Number(params.get('t')));
  if (params.get('autoplay') === '1') setPlaying(true);
  window.navdash = S;  // for console poking and headless checks
}
guard(main());
