// Bump VERSION when this file's caching logic changes. Old caches are deleted on activate.
const VERSION = 'v2';
const PAGES = `pages-${VERSION}`;
const ASSETS = `assets-${VERSION}`;
const PRECACHE_URLS = ['index.html', '404.html'];

self.addEventListener('install', (event) => {
	event.waitUntil(
		caches.open(PAGES)
			.then((cache) => cache.addAll(PRECACHE_URLS))
			.then(() => self.skipWaiting())
	);
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys()
			.then((names) => Promise.all(
				names.filter((name) => name !== PAGES && name !== ASSETS).map((name) => caches.delete(name))
			))
			.then(() => self.clients.claim())
	);
});

self.addEventListener('fetch', (event) => {
	const { request } = event;
	if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
	event.respondWith(request.mode === 'navigate' ? networkFirst(request) : staleWhileRevalidate(event));
});

// Pages: always try the network so content changes (like pricing) show up immediately;
// fall back to the cache only when offline.
async function networkFirst(request) {
	const cache = await caches.open(PAGES);
	try {
		const response = await fetch(request);
		if (response.status === 200) cache.put(request, response.clone());
		return response;
	} catch (err) {
		return (await cache.match(request)) || (await cache.match('index.html')) || Response.error();
	}
}

// Assets: serve from cache for speed, refresh the cache in the background.
async function staleWhileRevalidate(event) {
	const cache = await caches.open(ASSETS);
	const cached = await cache.match(event.request);
	const refresh = fetch(event.request)
		.then((response) => {
			if (response.status === 200) cache.put(event.request, response.clone());
			return response;
		})
		.catch(() => cached || Response.error());
	event.waitUntil(refresh);
	return cached || refresh;
}
