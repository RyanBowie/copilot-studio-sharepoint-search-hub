"""Serve only the verified static staging tree on loopback, including a project prefix."""

import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFIX = "/copilot-studio-sharepoint-search-hub/"


def verified_staging():
    staging = ROOT / "_site"
    marker = staging / ".site-build-manifest.json"
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    expected = set(manifest["files"]) | {marker.name}
    paths = list(staging.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Do not serve symlinks.")
    actual = {p.relative_to(staging).as_posix() for p in paths if p.is_file()}
    if actual != expected:
        raise ValueError("Staging has unreviewed files; rebuild before previewing.")
    for relative, fingerprint in manifest["sha256"].items():
        path = (staging / relative).resolve()
        if not path.is_relative_to(staging.resolve()):
            raise ValueError("Unsafe staging manifest path.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != fingerprint:
            raise ValueError("Staging content changed after its allowlisted build.")
    return staging


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, prefix=DEFAULT_PREFIX, **kwargs):
        self.prefix = prefix
        super().__init__(*args, directory=directory, **kwargs)

    def send_head(self):
        path = urlsplit(self.path).path
        if path == "/":
            self.send_response(302)
            self.send_header("Location", self.prefix)
            self.end_headers()
            return None
        if not path.startswith(self.prefix):
            self.send_error(404)
            return None
        self.path = "/" + self.path[len(self.prefix):]
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, *args):
        pass


def create_server(port=0):
    staging = verified_staging()
    return ThreadingHTTPServer(("127.0.0.1", port), partial(PreviewHandler, directory=str(staging)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = create_server(args.port)
    print(f"Local-only preview: http://127.0.0.1:{server.server_address[1]}{DEFAULT_PREFIX}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
