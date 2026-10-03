// Cache léger v2 : la page marche hors ligne, les images se mettent à jour seules, les médias lourds restent en ligne.
const C='hermes-v2';
const CORE=['./','index.html','manifest.webmanifest','icons/icon-192.png','media/video-poster.webp','media/schema-equipe-hermes.svg'];
const MAX=40; // nombre maximal de fichiers gardés en cache
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(CORE)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
function garder(r,x){if(!x||!x.ok||x.type!=='basic')return;const y=x.clone();caches.open(C).then(c=>c.put(r,y).then(()=>c.keys()).then(k=>{if(k.length>MAX)c.delete(k[0])}))}
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);if(r.method!=='GET'||u.origin!==location.origin)return;
 // Gros fichiers (vidéo, images 4K) : jamais en cache, directement en ligne.
 if(/\.mp4$|-4k\.webp$/.test(u.pathname))return;
 // Page et état du service : réseau d'abord (toujours frais), cache si hors ligne.
 if(r.mode==='navigate'||/status\.(svg|json)$/.test(u.pathname)){e.respondWith(fetch(r).then(x=>{garder(r,x);return x}).catch(()=>caches.match(r).then(x=>x||caches.match('./'))));return}
 // Le reste (images, icônes) : réponse immédiate depuis le cache, mise à jour en arrière-plan.
 e.respondWith(caches.match(r).then(x=>{const f=fetch(r).then(y=>{garder(r,y);return y}).catch(()=>x);return x||f}))});
