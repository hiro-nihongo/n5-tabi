/* にほんへの旅 Service Worker
   更新を配布するときは下の CACHE のバージョン番号を上げること(v1 → v2)*/
const CACHE = "n5tabi-v3";
const CORE = [
  "./",
  "index.html",
  "unit0.html",
  "unit1.html",
  "unit2.html",
  "fonts/KleeOne-Regular.woff2",
  "manifest.json",
  "icon-192.png",
  "icon-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* キャッシュ優先 + 取得成功したものは自動キャッシュ
   → 音声ファイルは一度再生すればオフラインでも鳴る */
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  const cacheable =
    url.origin === location.origin ||
    url.hostname === "fonts.googleapis.com" ||
    url.hostname === "fonts.gstatic.com";

  e.respondWith(
    caches.match(e.request).then(hit => {
      if (hit) return hit;
      return fetch(e.request).then(res => {
        if (res.ok && cacheable) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      }).catch(() => {
        if (e.request.mode === "navigate") return caches.match("index.html");
        return new Response("", { status: 404 });
      });
    })
  );
});
