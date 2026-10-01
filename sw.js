// Cache léger : la page marche hors ligne, les médias lourds restent en ligne.
const C='hermes-v1';
const CORE=['./','index.html','manifest.webmanifest','icons/icon-192.png','media/video-poster.webp','media/schema-equipe-hermes.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(CORE)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim()});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
 if(/status\.(svg|json)$/.test(r.url)||r.mode==='navigate'){e.respondWith(fetch(r).then(x=>{const y=x.clone();caches.open(C).then(c=>c.put(r,y));return x}).catch(()=>caches.match(r).then(x=>x||caches.match('./'))));return}
 if(/\.mp4$/.test(r.url))return;
 e.respondWith(caches.match(r).then(x=>x||fetch(r)))});
