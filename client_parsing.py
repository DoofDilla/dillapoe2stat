import re,os

# passt auf die von dir gezeigte Zeile
GEN_RE = re.compile(
    r'^(?P<ts>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}).*?Generating level (?P<lvl>\d+) area "(?P<code>[^"]+)" with seed (?P<seed>\d+)',
    re.IGNORECASE
)

def code_to_title(code: str) -> str:
    # "MapAzmerianRanges" -> "Azmerian Ranges"
    if code.startswith("Map"):
        code = code[3:]
    out = []
    for i, ch in enumerate(code):
        if i and ch.isupper() and (not code[i-1].isupper()):
            out.append(" ")
        out.append(ch)
    return "".join(out).strip()

def get_last_map_from_client(client_path, scan_bytes=1_500_000):
    size = os.path.getsize(client_path)
    with open(client_path, "rb") as f:
        f.seek(max(0, size - scan_bytes))
        buf = f.read()
    text = buf.decode("utf-8", errors="ignore")
    for line in reversed(text.splitlines()):
        m = GEN_RE.search(line)
        if m:
            ts  = m.group("ts")
            lvl = int(m.group("lvl"))
            code = m.group("code")
            seed = int(m.group("seed"))
            return {
                "timestamp": ts,
                "level": lvl,
                "map_code": code,
                "map_name": code_to_title(code),
                "seed": seed,
                "raw": line
            }
    return None