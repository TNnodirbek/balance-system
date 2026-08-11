const CACHE_NAME = 'balance-static-v1';

const PRECACHE_URLS = [
    '/static/manifest.json',
    '/static/offline.html',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/icons/icon-maskable-512.png',
    '/static/js/koz_yashirish.js',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const request = event.request;

    // Faqat GET so'rovlari bilan ishlaymiz - POST/API/buyurtma amallariga tegmaymiz
    if (request.method !== 'GET') {
        return;
    }

    const url = new URL(request.url);
    if (url.origin !== self.location.origin) {
        return;
    }

    // Sahifa navigatsiyasi: tarmoqni birinchi urinib ko'ramiz, faqat aloqa
    // bo'lmaganda oflayn sahifani ko'rsatamiz - hech qachon sahifa
    // kontentini o'zini keshlamaymiz (ma'lumot eskirib qolmasligi uchun)
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(() => caches.match('/static/offline.html'))
        );
        return;
    }

    // Statik resurslar (rasm, manifest, ikonkalar): kesh-birinchi
    if (PRECACHE_URLS.includes(url.pathname)) {
        event.respondWith(
            caches.match(request).then((cached) => {
                if (cached) {
                    return cached;
                }
                return fetch(request).then((response) => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    return response;
                });
            })
        );
    }
});
