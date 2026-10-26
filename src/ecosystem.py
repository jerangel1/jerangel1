"""Generate the Engineering Ecosystem SVGs (animated + static, wide + narrow).

Usage: python3 -I ecosystem.py <fonts_dir> <out_dir>

The diagram reads as a blueprint. A request travels down the layer spine
(Frontend -> Backend -> Data -> Cloud); as it passes, the cross-cutting
capability it relies on lights up, and the cycle ends on SYSTEM READY.
Edit LAYERS and COPY to change the content; the rest is layout.

A box's items are either a flat list of chips or a list of (label, chips)
groups, drawn as labelled rows.
"""
import base64
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bounce import ball  # noqa: E402
from xml.sax.saxutils import escape

FONTS, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])

CHARCOAL, PANEL, LINE = "#121412", "#1a1d1a", "#2e322d"
WHITE, MUTED = "#f2efe8", "#a7a59e"
LIME, BLUE = "#c6f432", "#3d7bff"

LAYERS = [
    ("01", "Frontend", [("WEB", ["React", "Next.js", "TypeScript", "Mantine", "Radix UI", "Tailwind", "TanStack", "Astro"]),
                        ("MOBILE", ["React Native", "Expo", "Tamagui", "Reanimated", "Skia"])]),
    ("02", "Backend", [("PYTHON", ["FastAPI", "Django", "Celery", "SQLModel"]),
                       ("NODE", ["Node.js", "Fastify", "Bun"]),
                       ("GO", ["Fiber", "Huma", "Goroutines", "Channels"]),
                       ("REALTIME", ["WebSockets", "Socket.IO", "Asterisk AMI", "SIP.js"]),
                       ("JAVA", ["Spring Boot"])]),
    ("03", "Data", ["PostgreSQL", "Redis", "Valkey", "Prisma", "SQLAlchemy", "pgx", "Alembic", "MinIO"]),
    ("04", "Cloud", [("AWS", ["ECS", "RDS", "S3", "Lambda", "SQS", "SES", "CloudWatch"]),
                     ("AZURE", ["Container Apps", "Functions", "Key Vault", "Front Door", "App Service"])]),
]
AI_TOOLS = ["Claude Code", "Codex", "Azure OpenAI", "LangChain", "Ollama"]
VOICE_AI = ["Vapi", "Deepgram", "ElevenLabs", "Whisper", "Twilio"]
DEVOPS = ["Docker", "Linux", "GitHub Actions", "OpenTofu", "Sentry", "Prometheus", "OpenTelemetry", "SonarQube"]

# Per-language copy. caps: (num, title, items, index of the layer whose passage lights it up).
# notes: editorial annotations in the gap after a layer; `secure` sits under the side cards.
COPY = {
    "en": {
        "layers": LAYERS,
        "caps": [
            ("05", "AI Engineering", [("BUILD", ["Model integration", "MCP integration", "Multi-agent orchestration"]), ("VOICE", VOICE_AI), ("TOOLS", AI_TOOLS)], 1),
            ("06", "Architecture & Security", ["System Design", "API Design", "OWASP", "Observability", "Row-Level Security", "Secrets Management"], 2),
            ("07", "DevOps", DEVOPS, 3),
        ],
        "notes": [(0, "Built to evolve"), (2, "Designed for failure")],
        "secure": "Secure by default",
        "eyebrow": "02 · ENGINEERING ECOSYSTEM",
        "subtitle": "a request, from interface to infrastructure",
        "ready": "● SYSTEM READY",
        "cross": "CROSS-CUTTING",
        "label": ("Engineering ecosystem. A request flows through ", ", then ", ". Cross-cutting: "),
    },
    "es": {
        "layers": [("01", "Frontend", [("WEB", LAYERS[0][2][0][1]), ("MÓVIL", LAYERS[0][2][1][1])]),
                   ("02", "Backend", [("TIEMPO REAL", g[1]) if g[0] == "REALTIME" else g for g in LAYERS[1][2]]), ("03", "Datos", LAYERS[2][2]), ("04", "Cloud", LAYERS[3][2])],
        "caps": [
            ("05", "Ingeniería de IA", [("CREO", ["Integración de modelos", "Integración MCP", "Orquestación multiagente"]), ("VOZ", VOICE_AI), ("USO", AI_TOOLS)], 1),
            ("06", "Arquitectura y Seguridad", ["Diseño de sistemas", "Diseño de APIs", "OWASP", "Observabilidad", "Seguridad por fila", "Gestión de secretos"], 2),
            ("07", "DevOps", DEVOPS, 3),
        ],
        "notes": [(0, "Hecho para evolucionar"), (2, "Tolerante a fallos")],
        "secure": "Seguro por defecto",
        "eyebrow": "02 · ECOSISTEMA DE INGENIERÍA",
        "subtitle": "una solicitud, de la interfaz a la infraestructura",
        "ready": "● SISTEMA LISTO",
        "cross": "TRANSVERSAL",
        "label": ("Ecosistema de ingeniería. Una solicitud recorre ", ", luego ", ". Transversal: "),
    },
}

MONO_ADV = 0.6  # IBM Plex Mono advance width, in em
CYCLE = 16.0
APPEAR, TRAVEL_START, TRAVEL_END, READY_END = 0.3, 2.8, 11.0, 15.2


def font_face(family, file, weight):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}"


def kt(*seconds):
    return ";".join(f"{min(max(s / CYCLE, 0), 1):.4f}" for s in seconds)


def groups_of(items):
    return items if items and isinstance(items[0], tuple) else [(None, items)]


def describe(items):
    return "; ".join(f"{label}: {', '.join(chips)}" if label else ", ".join(chips) for label, chips in groups_of(items))


def fade(content, start, end, animated):
    """Visible from `start` to `end` of each cycle; always visible in static builds."""
    if not animated:
        return content
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, start, start + 0.6, end - 0.4, end, CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>{content}</g>')


def chip_row(items, x0, y0, width, fs, label=None, label_w=0):
    """Chips left to right, wrapping inside `width`; an optional label leads the first row."""
    h, padx, gap = fs * 1.9, fs * 0.8, fs * 0.45
    x, y, out = x0, y0, []
    if label:
        out.append(f'<text x="{x0:.1f}" y="{y0 + h*0.64:.1f}" class="glabel">{escape(label)}</text>')
        x = x0 + label_w
    indent = x
    for t in items:
        w = len(t) * fs * MONO_ADV + padx * 2
        if x + w > x0 + width and x > indent:
            x, y = indent, y + h + gap
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
            f'<text x="{x + w/2:.1f}" y="{y + h*0.66:.1f}" text-anchor="middle" class="chip">{escape(t)}</text>'
        )
        x += w + gap
    return "".join(out), (y + h) - y0


def box(num, title, items, x, y, w, fs, accent=LIME):
    pad, head, row_gap = fs * 1.1, fs * 2.3, fs * 0.45
    body, cy = [], y + pad + head
    labels = [label for label, _ in groups_of(items) if label]
    label_w = max((len(t) for t in labels), default=0) * fs * 0.8 * 0.74 + fs * 1.2
    for label, chips in groups_of(items):
        svg, gh = chip_row(chips, x + pad, cy, w - pad * 2, fs, label, label_w)
        body.append(svg)
        cy += gh + row_gap
    h = cy - row_gap - y + pad
    svg = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{fs*0.8:.1f}" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>'
           f'<path d="M{x:.1f} {y + fs*1.8:.1f}V{y:.1f}H{x + fs*1.8:.1f}" fill="none" stroke="{accent}" stroke-width="3"/>'
           f'<text x="{x + pad:.1f}" y="{y + pad + fs*0.85:.1f}" class="num">{num}</text>'
           f'<text x="{x + pad + fs*2.3:.1f}" y="{y + pad + fs*1.0:.1f}" class="title">{escape(title)}</text>' + "".join(body))
    return svg, h


def glow(x, y, w, h, fs, at, color, animated):
    """Outline that lights up when the request reaches this box, then settles."""
    if not animated:
        return ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{fs*0.8:.1f}" fill="none" stroke="{color}" stroke-width="2" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0.35;0.35;0;0" '
            f'keyTimes="{kt(0, at - 0.3, at, at + 1.0, at + 1.6, READY_END - 0.4, READY_END, CYCLE)}" dur="{CYCLE}s" repeatCount="indefinite"/></rect>')


def note(x, y, text, at, animated, anchor="start"):
    return fade(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="note">{escape(text)}</text>', at, READY_END, animated)


def request(boxes, cards, caps, x0, col, fs, wide):
    """The request hops from box to box, landing on each top edge; every box glows as it lands.

    Wide: it zigzags between the spine and the capability each layer leans on.
    Narrow: everything is stacked, so it hops straight down, alternating sides.
    """
    spine = [(x0, by, col, bh, LIME) for by, bh in boxes]
    side = [(cx, cy, cw, ch, BLUE) for cx, cy, cw, ch in cards]
    if wide:
        order = []
        for k, layer in enumerate(spine):
            order.append(layer)
            order += [side[i] for i, cap in enumerate(caps) if cap[3] == k]
    else:
        order = spine + side
    r = fs * 0.5
    slot = (TRAVEL_END - TRAVEL_START) / (len(order) - 1)
    stops, out = [], []
    for i, (bx, by, bw, bh, color) in enumerate(order):
        land = TRAVEL_START + i * slot
        spot = 0.78 if wide or i % 2 == 0 else 0.5
        stops.append((bx + bw * spot, by - r, land, land + slot * 0.4))
        out.append(glow(bx, by, bw, bh, fs, land, color, True))
    return "".join(out) + ball(stops, CYCLE, r, LIME, TRAVEL_START - 0.4, TRAVEL_END + 0.8, lift=fs * 3,
                                ceiling=boxes[0][0] - fs)


def build(layout, animated, c):
    wide = layout == "wide"
    W = 1000 if wide else 600
    fs = 14 if wide else 18
    m, gap = 28, 40
    inner = W - m * 2
    side_w = 330 if wide else inner
    col = inner - side_w - 48 if wide else inner
    x0 = m
    y = m + fs * (2.8 if wide else 4.0)
    parts, under = [], []

    # Spine: the four layers a request crosses, top to bottom.
    boxes = []
    for i, (num, title, items) in enumerate(c["layers"]):
        g, h = box(num, title, items, x0, y, col, fs)
        boxes.append((y, h))
        parts.append(fade(g, APPEAR + i * 0.3, READY_END, animated))
        y += h + gap
    spine_top, spine_bottom = boxes[0][0], boxes[-1][0] + boxes[-1][1]
    cx = x0 + col / 2

    for i in range(len(boxes) - 1):
        a, b = boxes[i][0] + boxes[i][1], boxes[i + 1][0]
        under.append(fade(f'<path d="M{cx:.1f} {a:.1f}V{b:.1f}" stroke="{BLUE}" stroke-width="2"/>'
                          f'<path d="M{cx - 5:.1f} {b - 9:.1f}L{cx:.1f} {b - 2:.1f}L{cx + 5:.1f} {b - 9:.1f}" fill="none" stroke="{BLUE}" stroke-width="2"/>',
                          APPEAR + i * 0.3 + 0.3, READY_END, animated))
    for after, text in c["notes"]:
        gy = boxes[after][0] + boxes[after][1] + gap / 2 + fs * 0.35
        under.append(note(cx + fs * 1.1, gy, text, 1.8, animated))

    # Cross-cutting capabilities sit beside the spine (wide) or below it (narrow).
    cards = []  # (x, y, w, h) of each capability card
    if wide:
        sx = x0 + col + 48
        rail_x = sx - 24
        cy = spine_top
        side = []
        for i, (num, title, items, layer) in enumerate(c["caps"]):
            g, h = box(num, title, items, sx, cy, side_w, fs, accent=BLUE)
            side.append((cy, h))
            parts.append(fade(g, APPEAR + 1.2 + i * 0.3, READY_END, animated))
            cards.append((sx, cy, side_w, h))
            cy += h + 16
        rail_bottom = max(spine_bottom, cy - 16)
        under.append(fade(
            f'<path d="M{rail_x:.1f} {spine_top:.1f}V{rail_bottom:.1f}" stroke="{LIME}" stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round"/>'
            + "".join(f'<path d="M{x0 + col:.1f} {by + bh/2:.1f}H{rail_x:.1f}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 6"/>' for by, bh in boxes),
            APPEAR + 1.0, READY_END, animated))
        foot = rail_bottom + fs * 1.9
        under.append(fade(f'<text x="{rail_x:.1f}" y="{foot:.1f}" text-anchor="middle" class="eyebrow dim">{c["cross"]}</text>', APPEAR + 1.0, READY_END, animated))
        under.append(note(sx + side_w, foot, c["secure"], 1.8, animated, anchor="end"))
        bottom = foot + fs * 0.6
    else:
        y += fs * 0.6 - gap
        parts.append(fade(f'<path d="M{x0} {y:.1f}H{W - m}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 6"/>'
                          f'<text x="{x0}" y="{y + fs*2:.1f}" class="eyebrow">{c["cross"]}</text>', APPEAR + 1.0, READY_END, animated))
        y += fs * 3.0
        for i, (num, title, items, layer) in enumerate(c["caps"]):
            g, h = box(num, title, items, x0, y, inner, fs, accent=BLUE)
            parts.append(fade(g, APPEAR + 1.2 + i * 0.3, READY_END, animated))
            cards.append((x0, y, inner, h))
            y += h + 16
        under.append(note(W - m, y + fs * 0.9, c["secure"], 1.8, animated, anchor="end"))
        bottom = y + fs * 1.3

    if animated:
        parts.append(request(boxes, cards, c["caps"], x0, col, fs, wide))

    H = bottom + m
    # Header: the subtitle gives way to SYSTEM READY once the request has crossed every layer.
    hx, hy = (W - m, m + fs * 1.2) if wide else (x0, m + fs * 2.6)
    anchor = "end" if wide else "start"
    subtitle = f'<text x="{hx}" y="{hy:.1f}" text-anchor="{anchor}" class="eyebrow dim">{escape(c["subtitle"])}</text>'
    ready = f'<text x="{hx}" y="{hy:.1f}" text-anchor="{anchor}" class="eyebrow ready">{c["ready"]}</text>'
    header = fade(subtitle, 0, TRAVEL_END + 0.8, True) + fade(ready, TRAVEL_END + 1.0, READY_END, True) if animated else subtitle
    title = f'<text x="{x0}" y="{m + fs*1.2:.1f}" class="eyebrow">{c["eyebrow"]}</text>' + header
    grid = "".join(f'<path d="M{gx} 0V{H:.0f}" stroke="{WHITE}" stroke-opacity="0.035"/>' for gx in range(0, W, 40))
    style = (font_face("Archivo", "Archivo-800.woff2", "600 800") + font_face("Plex Mono", "IBMPlexMono-400.woff2", 400) +
             f".title{{font:700 {fs*1.3:.1f}px Archivo,'Helvetica Neue',Arial,sans-serif;fill:{WHITE}}}"
             f".num{{font:400 {fs*0.85:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{LIME}}}"
             f".chip{{font:400 {fs:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{WHITE}}}"
             f".glabel{{font:400 {fs*0.8:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.14em;fill:{MUTED}}}"
             f".note{{font:400 {fs*0.95:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{LIME};letter-spacing:.04em}}"
             f".eyebrow{{font:400 {fs*0.85:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.18em;fill:{LIME}}}"
             f".dim{{fill:{MUTED};letter-spacing:.06em}} .ready{{letter-spacing:.22em}}")
    intro, then, cross = c["label"]
    label = (intro + then.join(f"{t} ({describe(i)})" for _, t, i in c["layers"]) +
             cross + "; ".join(f"{t} ({describe(i)})" for _, t, i, _layer in c["caps"]) + ".")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><style>{style}</style>'
            f'<rect width="{W}" height="{H:.0f}" rx="18" fill="{CHARCOAL}"/>{grid}{title}{"".join(under)}{"".join(parts)}</svg>')


OUT.mkdir(parents=True, exist_ok=True)
for lang, c in COPY.items():
    tag = "" if lang == "en" else f".{lang}"
    for layout, suffix in (("wide", ""), ("narrow", "-mobile")):
        (OUT / f"engineering-ecosystem{suffix}{tag}.svg").write_text(build(layout, True, c))
        (OUT / f"engineering-ecosystem{suffix}-static{tag}.svg").write_text(build(layout, False, c))
print(sorted((p.name, p.stat().st_size) for p in OUT.glob("engineering-ecosystem*.svg")))
