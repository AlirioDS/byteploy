#!/usr/bin/env python3
"""Captura pantallas de Makundal (staging acme) via CDP puro para armar el demo GIF."""
import base64, hashlib, json, os, socket, struct, subprocess, sys, time, urllib.request, tempfile

PORT = 9236
BASE = "http://acme.staging.example:3000"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/mkframes"
os.makedirs(OUT, exist_ok=True)

class WS:
    def __init__(self, url):
        rest = url.split("://", 1)[1]
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=15)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            resp += self.sock.recv(4096)
        assert b"101" in resp.split(b"\r\n")[0], resp[:200]
        self.buf = b""
    def _read_exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(262144)
            if not chunk: raise ConnectionError("closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out
    def send(self, payload, opcode=0x1):
        header = bytes([0x80 | opcode]); mask = os.urandom(4); n = len(payload)
        if n < 126: header += bytes([0x80 | n])
        elif n < 65536: header += bytes([0x80 | 126]) + struct.pack(">H", n)
        else: header += bytes([0x80 | 127]) + struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(header + mask + masked)
    def recv_msg(self):
        payload = b""; opcode = None
        while True:
            b1, b2 = self._read_exact(2)
            fin = b1 & 0x80; op = b1 & 0x0F
            if opcode is None or op != 0: opcode = op if op != 0 else opcode
            n = b2 & 0x7F
            if n == 126: n = struct.unpack(">H", self._read_exact(2))[0]
            elif n == 127: n = struct.unpack(">Q", self._read_exact(8))[0]
            if b2 & 0x80:
                mask = self._read_exact(4); data = self._read_exact(n)
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            else: data = self._read_exact(n)
            payload += data
            if fin: break
        return opcode, payload

class CDP:
    def __init__(self, ws_url):
        self.ws = WS(ws_url); self.id = 0
    def call(self, method, params=None, timeout=30):
        self.id += 1; mid = self.id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}).encode())
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.ws.sock.settimeout(max(0.1, deadline - time.time()))
            try: op, payload = self.ws.recv_msg()
            except socket.timeout: continue
            if op == 0x9: self.ws.send(payload, opcode=0xA); continue
            if op != 0x1: continue
            msg = json.loads(payload)
            if msg.get("id") == mid:
                if "error" in msg: raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(method)
    def js(self, expr, timeout=30):
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, timeout)
        if r.get("exceptionDetails"): raise RuntimeError(json.dumps(r["exceptionDetails"])[:300])
        return r["result"].get("value")
    def shot(self, name):
        data = self.call("Page.captureScreenshot", {"format": "png"})["data"]
        p = os.path.join(OUT, name)
        open(p, "wb").write(base64.b64decode(data))
        print("frame:", name, os.path.getsize(p), "bytes")
    def goto(self, url, settle=2.2):
        self.call("Page.navigate", {"url": url}); time.sleep(settle)

proc = subprocess.Popen(
    ["chromium", "--headless=new", "--no-sandbox", f"--remote-debugging-port={PORT}",
     "--no-first-run", "--user-data-dir=" + tempfile.mkdtemp(prefix="mk-demo-"),
     "--window-size=1280,800", "--hide-scrollbars", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    ws_url = None
    for _ in range(50):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?about:blank", method="PUT")
            with urllib.request.urlopen(req, timeout=2) as f:
                ws_url = json.load(f)["webSocketDebuggerUrl"]
            break
        except Exception: time.sleep(0.2)
    assert ws_url, "no debug port"
    cdp = CDP(ws_url)
    cdp.call("Runtime.enable"); cdp.call("Page.enable")
    cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1280, "height": 800, "deviceScaleFactor": 1, "mobile": False})

    # 1. login
    cdp.goto(BASE + "/sign_in", 2.5)
    print("at:", cdp.js("location.href"))
    ok = cdp.js("""(() => {
      const email = document.querySelector('input[type=email], input[name*="email"]');
      const pass  = document.querySelector('input[type=password]');
      if (!email || !pass) return 'no-fields';
      const set = (el, v) => { const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; s.call(el, v); el.dispatchEvent(new Event('input', {bubbles: true})); };
      set(email, 'admin@example.com'); set(pass, 'CHANGEME');
      (email.closest('form')).requestSubmit();
      return 'submitted';
    })()""")
    print("login:", ok)
    time.sleep(3)
    print("after login:", cdp.js("location.href"))

    # 2. descubrir links de navegación
    links = cdp.js("JSON.stringify(Array.from(document.querySelectorAll('nav a, aside a, header a')).map(a => a.getAttribute('href')).filter(h => h && h.startsWith('/')))")
    print("nav links:", links)

    # 3. frames
    cdp.shot("01-dashboard.png")
    cdp.goto(BASE + "/items", 2.5); cdp.shot("02-items.png")
    # detalle del primer item con receta si existe
    first = cdp.js("JSON.stringify((Array.from(document.querySelectorAll('a[href^=\"/items/\"]')).map(a=>a.getAttribute('href')).filter(h=>/\\/items\\/\\d+/.test(h))[0]) || null)")
    print("first item:", first)
    if first and first != "null":
        href = json.loads(first)
        cdp.goto(BASE + href, 2.5); cdp.shot("03-item.png")
        cdp.goto(BASE + href.split("?")[0].rstrip("/") + "/recipe", 2.5)
        if "recipe" in (cdp.js("location.pathname") or ""):
            cdp.shot("04-recipe.png")
    print("done. url final:", cdp.js("location.href"))
finally:
    proc.terminate()
