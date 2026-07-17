#!/usr/bin/env python3
"""Interactive verification of the Byteploy site via raw CDP (stdlib only)."""
import base64, hashlib, json, os, socket, struct, subprocess, sys, time, urllib.request

PORT = int(os.environ.get("CDP_PORT", "9223"))
BASE = os.environ.get("SITE_BASE", "http://localhost:8137")

# ---------- minimal RFC6455 client ----------
class WS:
    def __init__(self, url):
        # ws://host:port/path
        rest = url.split("://", 1)[1]
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=10)
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
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def send(self, payload: bytes, opcode=0x1):
        header = bytes([0x80 | opcode])
        mask = os.urandom(4)
        n = len(payload)
        if n < 126:
            header += bytes([0x80 | n])
        elif n < 65536:
            header += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            header += bytes([0x80 | 127]) + struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(header + mask + masked)

    def recv_msg(self):
        # returns (opcode, payload) of a complete message (handles fragmentation)
        payload = b""
        opcode = None
        while True:
            b1, b2 = self._read_exact(2)
            fin = b1 & 0x80
            op = b1 & 0x0F
            if opcode is None or op != 0:
                opcode = op if op != 0 else opcode
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read_exact(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read_exact(8))[0]
            if b2 & 0x80:  # masked (server shouldn't, but handle)
                mask = self._read_exact(4)
                data = self._read_exact(n)
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            else:
                data = self._read_exact(n)
            payload += data
            if fin:
                break
        return opcode, payload


class CDP:
    def __init__(self, ws_url):
        self.ws = WS(ws_url)
        self.id = 0
        self.events = []

    def call(self, method, params=None, timeout=20):
        self.id += 1
        mid = self.id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}).encode())
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.ws.sock.settimeout(max(0.1, deadline - time.time()))
            try:
                op, payload = self.ws.recv_msg()
            except socket.timeout:
                continue
            if op == 0x9:  # ping -> pong
                self.ws.send(payload, opcode=0xA)
                continue
            if op != 0x1:
                continue
            msg = json.loads(payload)
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
            if "method" in msg:
                self.events.append(msg)
        raise TimeoutError(method)

    def drain(self, seconds):
        deadline = time.time() + seconds
        while time.time() < deadline:
            self.ws.sock.settimeout(max(0.05, deadline - time.time()))
            try:
                op, payload = self.ws.recv_msg()
            except (socket.timeout, TimeoutError):
                break
            if op == 0x9:
                self.ws.send(payload, opcode=0xA)
                continue
            if op == 0x1:
                msg = json.loads(payload)
                if "method" in msg:
                    self.events.append(msg)

    def js(self, expr, timeout=20):
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True,
                                           "awaitPromise": True}, timeout)
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:400])
        return r["result"].get("value")


results = []
def check(name, cond, detail=""):
    results.append((bool(cond), name, str(detail)[:160]))
    print(("PASS" if cond else "FAIL"), name, detail if not cond else "")

# ---------- launch isolated chromium ----------
proc = subprocess.Popen(
    ["chromium", "--headless=new", "--no-sandbox", f"--remote-debugging-port={PORT}",
     "--no-first-run", "--user-data-dir=" + __import__("tempfile").mkdtemp(prefix="byteploy-qa-"),
     "--window-size=1440,900", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    ws_url = None
    for _ in range(50):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?{BASE}/", method="PUT")
            with urllib.request.urlopen(req, timeout=2) as f:
                ws_url = json.load(f)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.2)
    assert ws_url, "chromium debug port never came up"

    cdp = CDP(ws_url)
    cdp.call("Runtime.enable")
    cdp.call("Log.enable")
    cdp.call("Page.enable")
    cdp.drain(2.5)  # let the page load, collect console

    # --- 1. right page, no console errors ---
    href = cdp.js("location.href")
    check("loaded ES page", href.rstrip("/") == BASE, href)

    # --- 2. typewriter animates live ---
    w1 = cdp.js("document.getElementById('typeword').textContent")
    time.sleep(1.4); cdp.drain(0.1)
    w2 = cdp.js("document.getElementById('typeword').textContent")
    check("typewriter animating", w1 != w2, f"{w1!r} -> {w2!r}")

    # --- 3. no horizontal overflow at 1440 ---
    over = cdp.js("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("no h-overflow @1440", over <= 0, f"delta={over}")

    # --- 4. FAQ accordion opens and closes on click ---
    check("faq opens", cdp.js(
        "(() => { const d=document.querySelector('.faq'); d.querySelector('summary').click(); return d.open; })()"),
        "")
    check("faq closes", cdp.js(
        "(() => { const d=document.querySelector('.faq'); d.querySelector('summary').click(); return !d.open; })()"),
        "")

    # --- 5. anchor nav scrolls to section ---
    cdp.js("document.querySelector('.nav-menu a[href=\"#servicios\"]').click()")
    time.sleep(0.9)
    check("anchor nav scrolls", cdp.js("scrollY") > 200 and cdp.js("location.hash") == "#servicios",
          f"y={cdp.js('scrollY')} hash={cdp.js('location.hash')}")

    # --- 6. EN toggle navigates to /en/ ---
    cdp.js("document.querySelector('.nav-lang').click()")
    time.sleep(1.2); cdp.drain(0.5)
    check("EN toggle -> /en/", cdp.js("location.pathname") == "/en/", cdp.js("location.href"))
    check("EN typewriter word list", "project" in (cdp.js(
        "document.getElementById('typeword')?.dataset.words || ''")), "")
    # back to ES from EN navbar language toggle (footer no longer has lang links)
    cdp.js("document.querySelector('.nav-lang').click()")
    time.sleep(1.2); cdp.drain(0.5)
    check("ES toggle from EN navbar -> /", cdp.js("location.pathname") == "/", cdp.js("location.href"))

    # --- 7. mobile metrics: overflow + hamburger menu flow ---
    cdp.call("Emulation.setDeviceMetricsOverride",
             {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True})
    cdp.call("Page.reload"); time.sleep(1.8); cdp.drain(0.7)
    over_m = cdp.js("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("no h-overflow @390 (real metrics)", over_m <= 0, f"delta={over_m}")
    check("hamburger visible @390", cdp.js(
        "getComputedStyle(document.querySelector('.nav-toggle')).display") != "none", "")
    check("menu hidden initially", cdp.js(
        "getComputedStyle(document.querySelector('#nav-menu')).display") == "none", "")
    cdp.js("document.querySelector('.nav-toggle').click()")
    check("menu opens + aria-expanded", cdp.js(
        "document.body.classList.contains('nav-open') && document.querySelector('.nav-toggle').getAttribute('aria-expanded')==='true'"), "")
    cdp.js("document.querySelector('#nav-menu a[href=\"#proceso\"]').click()")
    time.sleep(0.6)
    check("menu closes after link click", cdp.js(
        "!document.body.classList.contains('nav-open') && document.querySelector('.nav-toggle').getAttribute('aria-expanded')==='false'"), "")
    # Escape closes too
    cdp.js("document.querySelector('.nav-toggle').click()")
    cdp.js("document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}))")
    check("Escape closes menu", cdp.js("!document.body.classList.contains('nav-open')"), "")

    # --- 8. console errors across the whole session ---
    cdp.drain(0.5)
    errors = []
    for ev in cdp.events:
        if ev["method"] == "Runtime.exceptionThrown":
            errors.append(str(ev["params"].get("exceptionDetails", {}).get("text", "exception"))[:120])
        elif ev["method"] == "Log.entryAdded" and ev["params"]["entry"]["level"] == "error":
            errors.append(ev["params"]["entry"].get("text", "")[:120])
        elif ev["method"] == "Runtime.consoleAPICalled" and ev["params"]["type"] == "error":
            errors.append("console.error")
    check("zero console/page errors (ES+EN, desktop+mobile)", not errors, errors)

finally:
    proc.terminate()

fails = [r for r in results if not r[0]]
print(f"\n{len(results) - len(fails)}/{len(results)} interactive checks passed")
sys.exit(1 if fails else 0)
