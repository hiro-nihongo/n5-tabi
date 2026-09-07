/* ===== 日本語さくらんぼ 専用サービスワーカー =====
   「にほんへの旅」の sw.js とは完全に別。
   このファイルは /cherry/ の中だけを見る。

   ▼ 中身を直したら、必ず下の数字を1つ上げる
------------------------------------------------ */
const VERSION = 2;

const CORE_CACHE  = `cherry-core-v${VERSION}`;
const AUDIO_CACHE = "cherry-audio-v1";   // 音声は内容が変わらないので据え置き

/* 最初に必ず取っておくもの（HTMLだけ。軽い） */
const CORE = [
  "./",
  "./index.html",
  "./pea_dou.html",
  "./pea_gin.html",
  "./pea_kin.html"
];

/* ---- インストール：HTMLだけ先に取る ---- */
self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CORE_CACHE)
      .then(c => c.addAll(CORE))
      .then(() => self.skipWaiting())
  );
});

/* ---- 有効化：古い版のキャッシュを捨てる ---- */
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k.startsWith("cherry-core-") && k !== CORE_CACHE)
          .map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

/* ---- 取り出し方 ---- */
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  /* ① 音声：一度聞いたものは貯めて、次からは取りに行かない */
  if (url.pathname.includes("/cherry/audio/")) {
    e.respondWith(
      caches.open(AUDIO_CACHE).then(async cache => {
        const hit = await cache.match(req);
        if (hit) return hit;
        try {
          const res = await fetch(req);
          if (res.ok) cache.put(req, res.clone());
          return res;
        } catch (err) {
          return new Response("", { status: 504 });
        }
      })
    );
    return;
  }

  /* ② HTML：まず新しいものを見に行き、だめならキャッシュ */
  if (req.mode === "navigate" || req.destination === "document") {
    e.respondWith(
      fetch(req)
        .then(res => {
          const copy = res.clone();
          caches.open(CORE_CACHE).then(c => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then(r => r || caches.match("./index.html")))
    );
    return;
  }

  /* ③ その他：キャッシュ優先 */
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req))
  );
});
