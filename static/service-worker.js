self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('obra-cache').then(cache => {
      return cache.addAll([
        '/listar.html',
        '/static/manifest.json',
        '/static/icon-192.png',
        '/static/icon-512.png'
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(resp => {
      return resp || fetch(event.request);
    })
  );
});
