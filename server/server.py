#!/usr/bin/env python3
import json, subprocess, os, sys, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BUILD_SH = '/workspace/server/build_apk.sh'
OUT_DIR = '/workspace/server/output'
os.makedirs(OUT_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/generate-apk':
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get('Content-Length', 0))
        try:
            cfg = json.loads(self.rfile.read(length))
        except Exception:
            self._json(400, {'error': '无效的配置'}); return

        app_name = str(cfg.get('appName') or 'My App')[:30]
        site_url = str(cfg.get('siteUrl') or '').strip()
        package = str(cfg.get('packageName') or 'app.lumen.webapp')
        package = ''.join(c for c in package.lower() if c.isalnum() or c == '.').strip('.') or 'app.lumen.webapp'
        try:
            version_code = max(1, int(cfg.get('versionCode') or 1))
        except Exception:
            version_code = 1
        version_name = str(cfg.get('versionName') or '1.0.0')[:20]

        parsed = urlparse(site_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            self._json(400, {'error': '请输入有效的网站地址（以 http/https 开头）'}); return

        icon_path = ''
        icon_b64 = cfg.get('iconData')
        if icon_b64:
            try:
                import base64
                if ',' in icon_b64:
                    icon_b64 = icon_b64.split(',', 1)[1]
                fd, icon_path = tempfile.mkstemp(suffix='.png')
                with os.fdopen(fd, 'wb') as f:
                    f.write(base64.b64decode(icon_b64))
            except Exception:
                icon_path = ''

        config = {
            'appName': app_name,
            'siteUrl': site_url,
            'packageName': package,
            'versionName': version_name,
            'versionCode': version_code,
            'dark': bool(cfg.get('dark')),
            'fullscreen': bool(cfg.get('fullscreen')),
            'externalLinks': bool(cfg.get('externalLinks')),
            'iconPath': icon_path,
        }
        cfg_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config, cfg_file)
        cfg_file.close()

        safe_name = package.replace('.', '_')
        out_apk = os.path.join(OUT_DIR, f'{safe_name}.apk')
        try:
            r = subprocess.run(['bash', BUILD_SH, cfg_file.name, out_apk],
                               capture_output=True, text=True, timeout=300)
            if r.returncode != 0 or not os.path.exists(out_apk):
                self._json(500, {'error': '构建失败', 'detail': r.stderr[-500:]})
                return
            size_kb = os.path.getsize(out_apk) / 1024
            self._json(200, {
                'ok': True,
                'downloadUrl': f'/api/download/{safe_name}.apk',
                'packageName': package,
                'sizeKb': round(size_kb, 1),
            })
        except subprocess.TimeoutExpired:
            self._json(500, {'error': '构建超时'})
        finally:
            try: os.unlink(cfg_file.name)
            except Exception: pass
            if icon_path:
                try: os.unlink(icon_path)
                except Exception: pass

    def do_GET(self):
        if self.path.startswith('/api/download/'):
            name = os.path.basename(self.path[len('/api/download/'):])
            path = os.path.join(OUT_DIR, name)
            if not os.path.isfile(path):
                self.send_response(404); self.end_headers(); return
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.android.package-archive')
            self.send_header('Content-Disposition', f'attachment; filename="{name}"')
            self._cors()
            self.send_header('Content-Length', str(os.path.getsize(path)))
            self.end_headers()
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk: break
                    self.wfile.write(chunk)
            return
        self._serve_static()

    STATIC_DIR = '/workspace/app'

    def _serve_static(self):
        import mimetypes
        path = self.path.split('?')[0]
        if path == '/':
            path = '/index.html'
        fs_path = os.path.normpath(os.path.join(self.STATIC_DIR, path.lstrip('/')))
        if not fs_path.startswith(self.STATIC_DIR) or not os.path.isfile(fs_path):
            self.send_response(404); self.end_headers(); return
        ctype = mimetypes.guess_type(fs_path)[0] or 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(os.path.getsize(fs_path)))
        self.end_headers()
        with open(fs_path, 'rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk: break
                self.wfile.write(chunk)

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    port = 8001
    print(f'APK build server listening on {port}', flush=True)
    HTTPServer(('127.0.0.1', port), Handler).serve_forever()
