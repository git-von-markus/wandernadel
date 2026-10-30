/* Harzer Stempelkarte – Offline-Unterstützung
   - Seite selbst: erst Netz, sonst Zwischenspeicher (Updates kommen sofort an)
   - Bibliotheken & Schriften: Zwischenspeicher zuerst
   - Kartenkacheln: nur bereits angesehene werden gespeichert (max. MAX_TILES) */
const SHELL = "hwn-shell-v3";
const LIBS = "hwn-libs-v1";
const TILES = "hwn-tiles-v1";
const MAX_TILES = 4000;
const SHELL_FILES = [
  "./",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png"
];
const LIB_HOSTS = ["cdnjs.cloudflare.com", "fonts.googleapis.com", "fonts.gstatic.com"];
const TILE_HOSTS = /(^|\.)tile\.openstreetmap\.org$|(^|\.)tile\.opentopomap\.org$/;

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_FILES)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  const keep = [SHELL, LIBS, TILES];
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => !keep.includes(k)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* Fremde Dateien möglichst als CORS-Antwort holen: die lassen sich sparsam speichern */
async function fetchCors(req) {
  try {
    const r = await fetch(req.url, { mode: "cors", credentials: "omit" });
    if (r.ok) return r;
  } catch (e) { /* Server erlaubt kein CORS – normal laden */ }
  return fetch(req);
}

let putCount = 0;
async function trimTiles() {
  const c = await caches.open(TILES);
  const keys = await c.keys();
  if (keys.length > MAX_TILES) await Promise.all(keys.slice(0, keys.length - MAX_TILES).map((k) => c.delete(k)));
}

async function cacheFirst(req, cacheName, isTile) {
  const c = await caches.open(cacheName);
  const hit = await c.match(req.url);
  if (hit) return hit;
  const r = await fetchCors(req);
  if (r.ok && r.type !== "opaque") {
    c.put(req.url, r.clone()).catch(() => {});
    if (isTile && ++putCount % 100 === 0) trimTiles();
  }
  return r;
}

/* Bei schwachem Netz nicht ewig warten: nach 4 s gespeicherte Version zeigen, im Hintergrund weiter aktualisieren */
async function networkFirst(req) {
  const c = await caches.open(SHELL);
  const net = fetch(req).then((r) => { if (r.ok) c.put(req, r.clone()).catch(() => {}); return r; });
  const cached = () => c.match(req, { ignoreSearch: true }).then((h) => h || c.match("./"));
  try {
    return await Promise.race([
      net,
      new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 4000))
    ]);
  } catch (e) {
    const h = await cached();
    if (h) { net.catch(() => {}); return h; }
    return net.catch(() => Response.error());
  }
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;               // Overpass-Abfragen (POST) gehen direkt ins Netz
  const url = new URL(req.url);
  if (url.origin === self.location.origin) { e.respondWith(networkFirst(req)); return; }
  if (TILE_HOSTS.test(url.hostname)) { e.respondWith(cacheFirst(req, TILES, true)); return; }
  if (LIB_HOSTS.includes(url.hostname)) { e.respondWith(cacheFirst(req, LIBS, false)); return; }
});
