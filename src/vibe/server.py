"""vibe serve: tiny local API + static page. Local only (binds 127.0.0.1).

  GET /                 docs/index.html (and docs/data.js)
  GET /health           {"ok": true}
  GET /search?q=...     {"parsed", "score": [...all segments], "top": [...]}
  GET /like?id=...      {"ids": [...]}
  GET /near?q=...       {"idx": [...]}  the 25 clips whose audio embedding is closest to the text
  GET /audio/<seg>.mp3  that segment's 20 s clip from the local cache (fallback when the publisher URL is blocked)
  POST /rate            save listening-test ratings to reports/listening_test.json
"""
import json
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pandas as pd

from . import rank
from .audio import raw_file
from .config import ROOT

PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT / "docs"), **kw)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        qs = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/health":
                return self._json({"ok": True})
            if u.path == "/search":
                p, score, *_ = rank.score_all(qs["q"])
                _, top = rank.search(qs["q"], k=10, parsed=p)
                return self._json({"parsed": {k: p[k] for k in ("vibe_text", "targets", "topic", "avoid")},
                                   "source": p.get("source"), "score": [round(float(v), 3) for v in score],
                                   "top": [{"id": r["segment_id"], "parts": r["parts"], "why": r["why"]} for r in top]})
            if u.path == "/near":
                return self._json({"idx": rank.nearest_clips(qs["q"])})
            if u.path == "/like":
                return self._json({"ids": [r["segment_id"] for r in rank.like(qs["id"], k=5, max_per_show=2)]})
            if u.path.startswith("/audio/"):
                return self._clip(u.path.rsplit("/", 1)[1].removesuffix(".mp3"))
        except Exception as e:
            return self._json({"error": str(e)}, 500)
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/rate":
            return self._json({"error": "not found"}, 404)
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            # ?name=study -> reports/listening_study.json; default -> reports/listening_test.json
            name = parse_qs(u.query).get("name", ["test"])[0]
            if not name.isalnum():
                return self._json({"error": "bad name"}, 400)
            (ROOT / "reports" / f"listening_{name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
            return self._json({"ok": True, "saved": len(data.get("ratings", {}))})
        except Exception as e:
            return self._json({"error": str(e)}, 400)

    def _clip(self, seg_id):
        df, _, _ = rank.index()
        row = df[df.segment_id == seg_id]
        if row.empty:
            return self._json({"error": "unknown segment"}, 404)
        r = row.iloc[0]
        eps = pd.read_parquet(ROOT / "data" / "episodes.parquet").set_index("episode_id")
        mp3 = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(r.start_s), "-i",
                              str(raw_file(eps.loc[r.episode_id, "audio_file"])), "-t", str(r.end_s - r.start_s),
                              "-ac", "1", "-b:a", "96k", "-f", "mp3", "-"], capture_output=True, check=True).stdout
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(mp3)))
        self.end_headers()
        self.wfile.write(mp3)

    def log_message(self, *a):
        pass


def serve(port=PORT):
    rank.index()
    rank.encoder()  # warm up so the first search is fast
    print(f"Vibe Search on http://127.0.0.1:{port}/  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
