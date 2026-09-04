"""Danish Wikipedia lookup tool: search + plain-text intro extracts (MediaWiki API, no keys)."""
import hashlib, json, os, time, urllib.error, urllib.parse, urllib.request

API = "https://da.wikipedia.org/w/api.php"
UA = "daisy-tools/0.1 (research harness; contact: bolgacg1@gmail.com)"
MIN_INTERVAL = 0.6          # seconds between live requests (Wikimedia asks for serial, polite clients)
CACHE_DIR = os.environ.get("DAISY_WIKI_CACHE", os.path.join(os.path.dirname(__file__), "..", "cache", "wiki"))
_last = [0.0]

def _cache_path(url):
    return os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest() + ".json")

def _get(params, retries=6):
    params = dict(params, format="json", formatversion=2)
    url = API + "?" + urllib.parse.urlencode(params)
    cp = _cache_path(url)
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as f:
            return json.load(f)
    for i in range(retries):
        wait = MIN_INTERVAL - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
            _last[0] = time.time()
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            return data
        except urllib.error.HTTPError as e:
            _last[0] = time.time()
            if e.code == 429 and i < retries - 1:
                ra = e.headers.get("Retry-After")
                time.sleep(float(ra) if ra and ra.isdigit() else 30 * (i + 1))
                continue
            raise
        except Exception:
            _last[0] = time.time()
            if i == retries - 1:
                raise
            time.sleep(2.0 * (i + 1))

def search(query, limit=3):
    d = _get({"action": "query", "list": "search", "srsearch": query, "srlimit": limit})
    return [h["title"] for h in d.get("query", {}).get("search", [])]

def extracts(titles, chars=1200):
    if not titles:
        return {}
    d = _get({"action": "query", "prop": "extracts", "explaintext": 1, "exintro": 1,
              "exchars": chars, "redirects": 1, "titles": "|".join(titles)})
    return {p["title"]: p.get("extract", "") for p in d.get("query", {}).get("pages", [])}

def lookup(query, limit=3, chars=1200):
    """Returns list of (title, extract) for the top search hits."""
    titles = search(query, limit)
    ex = extracts(titles, chars)
    return [(t, ex.get(t, "")) for t in titles]
