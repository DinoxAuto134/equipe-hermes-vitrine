#!/usr/bin/env python3
"""Contrôle avant publication : liens, images, médias, manifeste et vie privée.
Code de sortie 1 = la publication est bloquée."""
import json, os, re, sys, urllib.request
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
INTERDITS = ["jhoned880", "1903895", "srv1903895", "hstgr", "sslip", "186-241", "186.241",
             "C:/Users", "C:\\Users", "AppData", "kanban", "t_"+"[0-9a-f]{8}"]
erreurs = []

class P(HTMLParser):
    def __init__(s): super().__init__(); s.refs=[]; s.ids=set(); s.imgs=[]
    def handle_starttag(s, tag, a):
        a = dict(a)
        if "id" in a: s.ids.add(a["id"])
        if tag == "link" and a.get("rel") in ("preconnect", "dns-prefetch"): return
        for k in ("href", "src", "poster"):
            if a.get(k): s.refs.append((tag, a[k]))
        for k in ("srcset",):
            if a.get(k):
                for part in a[k].split(","):
                    s.refs.append((tag, part.strip().split(" ")[0]))
        if tag == "img": s.imgs.append(a)

html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
p = P(); p.feed(html)

for tag, r in p.refs:
    if r.startswith("#"):
        if r != "#" and r[1:] not in p.ids: erreurs.append(f"ancre absente : {r}")
    elif r.startswith(("http://", "https://")):
        try:
            req = urllib.request.Request(r, method="GET", headers={"User-Agent": "Mozilla/5.0 (vitrine-ci)"})
            code = urllib.request.urlopen(req, timeout=20).status
            if code >= 400: erreurs.append(f"lien externe {r} -> {code}")
        except Exception as e:
            erreurs.append(f"lien externe {r} -> {e}")
    elif not r.startswith(("mailto:", "tel:", "data:")):
        f = os.path.join(ROOT, r.split("#")[0].split("?")[0])
        if not os.path.isfile(f): erreurs.append(f"fichier absent : {r}")

for a in p.imgs:
    if "alt" not in a: erreurs.append(f"image sans alt : {a.get('src')}")
    if not (a.get("width") and a.get("height")): erreurs.append(f"image sans taille : {a.get('src')}")

man = json.load(open(os.path.join(ROOT, "manifest.webmanifest"), encoding="utf-8"))
tailles = {i["sizes"] for i in man["icons"]}
if not {"192x192", "512x512"} <= tailles: erreurs.append("manifeste : icônes 192 et 512 requises")
for i in man["icons"]:
    if not os.path.isfile(os.path.join(ROOT, i["src"])): erreurs.append(f"icône absente : {i['src']}")

# Poids max pour la 4G : rien de ce qui se charge d'office ne dépasse 300 Ko
for tag, r in p.refs:
    f = os.path.join(ROOT, r)
    if tag in ("img", "link") and os.path.isfile(f) and os.path.getsize(f) > 300_000 and not r.endswith(".webmanifest"):
        erreurs.append(f"trop lourd pour la 4G : {r} ({os.path.getsize(f)//1000} Ko)")

for dp, dn, fn in os.walk(ROOT):
    if ".git" in dp or "scripts" in dp or ".github" in dp: continue
    for n in fn:
        if not n.endswith((".html", ".svg", ".json", ".webmanifest", ".js", ".vtt", ".md")): continue
        t = open(os.path.join(dp, n), encoding="utf-8", errors="ignore").read()
        for mot in INTERDITS:
            if re.search(mot if "[" in mot else re.escape(mot), t, re.I):
                erreurs.append(f"vie privée : « {mot} » trouvé dans {n}")

if erreurs:
    print("ÉCHEC :"); [print(" -", e) for e in erreurs]; sys.exit(1)
print(f"OK : {len(p.refs)} liens/médias, {len(p.imgs)} images, manifeste valide, aucune donnée privée.")
