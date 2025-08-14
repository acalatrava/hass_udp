import json, socket, base64, time, urllib.request, sys, os

# Lee opciones del add-on
with open("/data/options.json", "r") as f:
    OPT = json.load(f)

PORT = int(OPT.get("port", 9999))
WEBHOOK_ID = OPT.get("webhook_id", "udp_9999")
DEDUP_S = float(OPT.get("dedup_seconds", 2))
REQ_BITS = OPT.get("require_bitlength", 24)
BASE64_IN = bool(OPT.get("base64_input", True))

WEBHOOK_URL = f"http://127.0.0.1:8123/api/webhook/{WEBHOOK_ID}"

last = {}  # code -> ts

def send_to_webhook(payload: dict):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(WEBHOOK_URL, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=3).read()

def decode_packet(data: bytes) -> str:
    if BASE64_IN:
        try:
            return base64.b64decode(data).decode("ascii")
        except Exception:
            # si falla base64, intenta texto directo
            return data.decode("ascii", errors="ignore")
    return data.decode("ascii", errors="ignore")

def main():
    print(f"[udp2ha] Listening UDP on 0.0.0.0:{PORT} → webhook {WEBHOOK_ID}", flush=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # reuse por si reinicias rápido
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", PORT))
    sock.settimeout(1.0)

    while True:
        try:
            try:
                data, addr = sock.recvfrom(65535)
            except socket.timeout:
                continue
            s = decode_packet(data)
            # JSON con fallback de "}"
            try:
                payload = json.loads(s)
            except Exception:
                try:
                    payload = json.loads(s + "}")
                except Exception:
                    print(f"[udp2ha] Bad JSON from {addr}: {s[:120]}...", flush=True)
                    continue

            # filtro bitlength
            if REQ_BITS is not None:
                try:
                    if int(payload.get("bitlength", -1)) != int(REQ_BITS):
                        continue
                except Exception:
                    continue

            # dedup por code
            code = str(payload.get("code"))
            if not code or code == "None":
                # si alguna vez quieres derivar code de 'raw', hazlo aquí
                pass
            now = time.time()
            last_ts = last.get(code, 0.0)
            if now - last_ts < DEDUP_S:
                continue
            last[code] = now

            # envía a webhook
            try:
                send_to_webhook(payload)
                print(f"[udp2ha] → {WEBHOOK_ID} sent: {payload}", flush=True)
            except Exception as e:
                print(f"[udp2ha] Webhook error: {e}", flush=True)

        except Exception as e:
            print(f"[udp2ha] Loop error: {e}", flush=True)
            time.sleep(0.2)

if __name__ == "__main__":
    main()
