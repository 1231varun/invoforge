/**
 * Service Worker for InvoForge PWA
 * 
 * Provides offline support with intelligent caching strategies:
 * - Static assets: Cache-first (CSS, JS, images)
 * - API calls: Network-first with cache fallback
 * - Pages: Stale-while-revalidate
 */

// App version - update this when releasing new versions
const APP_VERSION = '0.1.0';
const CACHE_VERSION = 'v1';
const STATIC_CACHE = `invoforge-static-${CACHE_VERSION}`;
const DYNAMIC_CACHE = `invoforge-dynamic-${CACHE_VERSION}`;
const API_CACHE = `invoforge-api-${CACHE_VERSION}`;

// Static assets to pre-cache on install
const STATIC_ASSETS = [
  '/',
  '/dashboard',
  '/invoice',
  '/leaves',
  '/history',
  '/settings',
  '/static/css/styles.css',
  '/static/js/app.js',
  '/static/favicon/site.webmanifest',
  '/static/favicon/favicon.svg',
  '/static/favicon/logo.png',
  '/static/favicon/favicon.ico',
];

// API endpoints that can be cached for offline use
const CACHEABLE_API_PATTERNS = [
  /\/api\/settings$/,
  /\/api\/dashboard$/,
  /\/api\/leaves$/,
  /\/api\/invoices$/,
  /\/api\/working-days/,
  /\/api\/next-invoice-number$/,
];

/**
 * Install event - Pre-cache static assets
 */
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Pre-caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((error) => {
        console.error('[SW] Pre-cache failed:', error);
      })
  );
});

/**
 * Activate event - Clean up old caches and notify clients
 */
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys()
      .then((keys) => {
        return Promise.all(
          keys
            .filter((key) => (key.startsWith('invoice-gen-') || key.startsWith('invoforge-')) && 
                           !key.includes(CACHE_VERSION))
            .map((key) => {
              console.log('[SW] Removing old cache:', key);
              return caches.delete(key);
            })
        );
      })
      .then(() => self.clients.claim())
      .then(() => {
        // Notify all clients that a new version is active
        self.clients.matchAll().then(clients => {
          clients.forEach(client => {
            client.postMessage({
              type: 'SW_UPDATED',
              version: APP_VERSION
            });
          });
        });
      })
  );
});

/**
 * Message event - Handle messages from clients
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: APP_VERSION });
  }
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

/**
 * Fetch event - Handle requests with appropriate caching strategy
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other protocols
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // Determine caching strategy based on request type
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  } else if (isApiRequest(url)) {
    event.respondWith(networkFirstWithCache(request, API_CACHE));
  } else {
    event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
  }
});

/**
 * Check if URL is a static asset
 */
function isStaticAsset(url) {
  return url.pathname.startsWith('/static/') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.png') ||
         url.pathname.endsWith('.jpg') ||
         url.pathname.endsWith('.svg') ||
         url.pathname.endsWith('.woff2');
}

/**
 * Check if URL is an API request
 */
function isApiRequest(url) {
  return url.pathname.startsWith('/api/');
}

/**
 * Check if API endpoint is cacheable
 */
function isCacheableApi(url) {
  return CACHEABLE_API_PATTERNS.some(pattern => pattern.test(url.pathname));
}

/**
 * Cache-first strategy
 * Best for: Static assets that rarely change
 */
async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[SW] Cache-first fetch failed:', error);
    return new Response('Offline - Asset not available', { status: 503 });
  }
}

/**
 * Network-first with cache fallback
 * Best for: API calls where fresh data is preferred
 */
async function networkFirstWithCache(request, cacheName) {
  const url = new URL(request.url);
  
  try {
    const response = await fetch(request);
    
    // Cache successful GET responses for cacheable endpoints
    if (response.ok && isCacheableApi(url)) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    
    const cached = await caches.match(request);
    if (cached) {
      // Add header to indicate cached response
      const headers = new Headers(cached.headers);
      headers.set('X-From-Cache', 'true');
      return new Response(cached.body, {
        status: cached.status,
        statusText: cached.statusText,
        headers
      });
    }
    
    // Return offline-friendly error for API
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: 'You are offline. Please check your connection.',
        offline: true 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

/**
 * Stale-while-revalidate strategy
 * Best for: Pages where showing something quickly is important
 */
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  
  // Fetch in background to update cache
  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch(() => null);
  
  // Return cached version immediately, or wait for network
  if (cached) {
    fetchPromise; // Fire and forget
    return cached;
  }
  
  const response = await fetchPromise;
  if (response) {
    return response;
  }
  
  // Offline fallback
  return new Response(
    `<!DOCTYPE html>
    <html>
    <head>
      <title>Offline - Invoice Generator</title>
      <style>
        body { 
          font-family: system-ui, sans-serif; 
          display: flex; 
          align-items: center; 
          justify-content: center; 
          min-height: 100vh; 
          margin: 0;
          background: #0f172a;
          color: #e2e8f0;
        }
        .offline-message {
          text-align: center;
          padding: 2rem;
        }
        h1 { color: #8b5cf6; }
        button {
          background: #8b5cf6;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 1rem;
          margin-top: 1rem;
        }
      </style>
    </head>
    <body>
      <div class="offline-message">
        <h1>📴 You're Offline</h1>
        <p>Please check your internet connection and try again.</p>
        <button onclick="location.reload()">Retry</button>
      </div>
    </body>
    </html>`,
    { 
      status: 503, 
      headers: { 'Content-Type': 'text/html' } 
    }
  );
}

/**
 * Message handler for cache management
 */
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  
  if (event.data === 'clearCache') {
    caches.keys().then((keys) => {
      keys.forEach((key) => caches.delete(key));
    });
  }
});

