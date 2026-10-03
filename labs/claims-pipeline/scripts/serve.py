"""Local read-only report server with byte ranges for timestamped audio playback."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from common import ROOT

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = Path(self.translate_path(self.path)).resolve()
        if path.suffix.lower() != '.mp3' or not self.headers.get('Range'):
            return super().do_GET()
        if not path.is_relative_to(ROOT) or not path.is_file():
            return self.send_error(404)
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', self.headers['Range'])
        size = path.stat().st_size
        if not match or not any(match.groups()):
            return self.send_error(416)
        if match[1]:
            start = int(match[1])
            end = min(int(match[2]), size - 1) if match[2] else size - 1
        else:
            start, end = max(0, size - int(match[2])), size - 1
        if start > end or start >= size:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            return
        self.send_response(206)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        with path.open('rb') as file:
            file.seek(start)
            remaining = end - start + 1
            try:
                while remaining:
                    data = file.read(min(65536, remaining))
                    if not data:
                        break
                    self.wfile.write(data)
                    remaining -= len(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

if __name__ == '__main__':
    print('Local report: http://127.0.0.1:8767/reports/explorador.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8767), Handler).serve_forever()
