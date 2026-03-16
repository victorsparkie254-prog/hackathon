# Streamlit PWA Offline Support

To enable true offline access for this farmer application on Android/iOS, you can wrap this Streamlit app using a Progressive Web App (PWA) configuration or Android WebView.

### 1. Service Worker & Manifest
Since Streamlit dynamically generates HTML, you can inject a custom `manifest.json` and a `service-worker.js` by placing an `index.html` in the Streamlit static files directory (or using an NGINX reverse proxy to serve them).

**`manifest.json`**
```json
{
  "name": "Crop Disease AI",
  "short_name": "Crop AI",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0E1117",
  "theme_color": "#0E1117",
  "icons": [
    {
      "src": "/icon.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

**`service-worker.js`**
```javascript
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('farm-store').then((cache) => cache.addAll([
      '/',
      '/index.html',
    ])),
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request)),
  );
});
```

### 2. Native Wrapper (Alternative)
For immediate offline ML inference on mobile without a network connection:
- Convert the PyTorch model (`ai/train.py`) to an optimized format like **TensorFlow Lite** or **TorchScript**.
- Build a barebones Flutter or React Native app that incorporates local edge-inference directly and stores history in local SQLite or Hive.
