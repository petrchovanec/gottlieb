from __future__ import annotations

import argparse
import posixpath
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


BASE_PATH = "/hermann-gottlieb/"
ROOT = Path(__file__).resolve().parents[1]
DIST = (ROOT / "dist").resolve()


class SiteHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == BASE_PATH.rstrip("/"):
            self.send_response(301)
            self.send_header("Location", BASE_PATH)
            self.end_headers()
            return
        super().do_GET()

    def translate_path(self, path: str) -> str:
        clean_path = unquote(urlsplit(path).path)
        if clean_path.startswith(BASE_PATH):
            clean_path = clean_path[len(BASE_PATH) :]
        else:
            clean_path = clean_path.lstrip("/")
        clean_path = posixpath.normpath(clean_path)
        parts = [part for part in clean_path.split("/") if part not in ("", ".", "..")]
        target = DIST.joinpath(*parts)
        if target.is_dir():
            target = target / "index.html"
        resolved = target.resolve()
        if resolved != DIST and DIST not in resolved.parents:
            return str(DIST / "404.html")
        return str(resolved)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the generated site at its GitHub Pages base path.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not DIST.exists():
        raise SystemExit("dist/ does not exist. Run scripts/build_site.py first.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), SiteHandler)
    print(f"Serving http://127.0.0.1:{args.port}{BASE_PATH}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
