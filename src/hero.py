"""Generate the hero and the principles cards as SVGs (animated + static, wide + narrow).

Usage: python3 -I hero.py <fonts_dir> <out_dir>

The hero is a blueprint elevation: an arch cut into the four layers a request
crosses. A request is tossed in at the top and hops down floor by floor, each
layer's job lighting up as it lands, and leaves with a 200 OK. On load the name
rises in and the tagline types itself out, once; the static build shows
everything at rest.
"""
import base64
import pathlib
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bounce import ball  # noqa: E402

FONTS, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])

CHARCOAL, PANEL, LINE = "#121412", "#1a1d1a", "#2e322d"
WHITE, MUTED = "#f2efe8", "#a7a59e"
LIME, BLUE = "#c6f432", "#3d7bff"

NAME = ("JESÚS", "RANGEL")

# Per-language copy. jobs: what each layer does with the request.
COPY = {
    "en": {
        "role": "Software Architecture / Cloud / AI",
        "tagline": "I build the systems behind the experience.",
        "request": "REQUEST",
        "jobs": ["render", "authorize · validate", "persist", "deliver"],
        "diagram": "Diagram: a request crosses frontend, backend, data and cloud and returns 200 OK.",
        "principles_title": "WORKING PRINCIPLES",
        "principles": [
            ("System before code.", "Boundaries, data and failure modes first. Frameworks second."),
            ("AI builds, I decide.", "I lead teams of AI agents and own every decision that reaches production."),
            ("Traceable by default.", "Every requirement links to its commit, its pull request and its review."),
        ],
        "chapter": ("03 · OFF THE CLOCK", "Building systems for tomorrow.", "Building LEGO with my kids today."),
        "cta": "Connect on LinkedIn",
    },
    "es": {
        "role": "Arquitectura de Software / Cloud / IA",
        "tagline": "Construyo los sistemas detrás de la experiencia.",
        "request": "SOLICITUD",
        "jobs": ["renderiza", "autoriza · valida", "persiste", "entrega"],
        "diagram": "Diagrama: una solicitud recorre frontend, backend, datos y cloud y responde 200 OK.",
        "principles_title": "PRINCIPIOS DE TRABAJO",
        "principles": [
            ("Sistema antes que código.", "Límites, datos y modos de falla primero. Frameworks después."),
            ("La IA construye, yo decido.", "Lidero equipos de agentes de IA y respondo por cada decisión que llega a producción."),
            ("Trazable por defecto.", "Cada requisito se enlaza con su commit, su pull request y su revisión."),
        ],
        "chapter": ("03 · FUERA DE HORARIO", "Construyendo sistemas para mañana.", "Construyendo LEGO con mis hijos hoy."),
        "cta": "Conectemos en LinkedIn",
    },
}
LAYER_LABELS = ["01 FRONTEND", "02 BACKEND", "03 DATA", "04 CLOUD"]
LAYER_LABELS_ES = ["01 FRONTEND", "02 BACKEND", "03 DATOS", "04 CLOUD"]

CYCLE = 10.0
# Arch geometry, local units: 440 wide, apex at y=0, floor at y=500.
ARCH_W, ARCH_R, FLOOR = 440, 220, 500
BANDS = [(0, 170), (170, 280), (280, 390), (390, 500)]
ENTRY = -70
ARRIVE = [1.5, 3.0, 4.5, 6.0]
DWELL = 0.9
EXIT = ARRIVE[-1] + DWELL + 0.4


def font_faces():
    def face(family, file, weight):
        data = base64.b64encode((FONTS / file).read_bytes()).decode()
        return f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    return face("Archivo", "Archivo-800.woff2", "600 800") + face("Plex Mono", "IBMPlexMono-400.woff2", 400)


def kt(*seconds):
    return ";".join(f"{min(max(s / CYCLE, 0), 1):.4f}" for s in seconds)


def pulse_opacity(on, off):
    return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, on - 0.2, on, off, off + 0.3, CYCLE)}" '
            f'dur="{CYCLE}s" repeatCount="indefinite"/>')


def blueprint(ox, oy, s, fs, animated, uid, c, labels):
    """The arch elevation at (ox, oy), scaled by s. fs is the label size in local units."""
    arch = f"M0 {FLOOR}V{ARCH_R}A{ARCH_R} {ARCH_R} 0 0 1 {ARCH_W} {ARCH_R}V{FLOOR}Z"
    cx = ARCH_W * 0.7  # request lane, right of the layer labels
    out = [f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s})">',
           f'<defs><clipPath id="arch{uid}"><path d="{arch}"/></clipPath></defs>',
           f'<path d="M22 {FLOOR + 22}V{ARCH_R + 22}A{ARCH_R} {ARCH_R} 0 0 1 {ARCH_W + 22} {ARCH_R + 22}V{FLOOR + 22}" fill="none" stroke="{BLUE}" stroke-width="2"/>',
           f'<g clip-path="url(#arch{uid})"><rect width="{ARCH_W}" height="{FLOOR}" fill="{PANEL}"/>']
    grid = "".join(f"M0 {y}H{ARCH_W}" for y in range(40, FLOOR, 40)) + "".join(f"M{x} 0V{FLOOR}" for x in range(40, ARCH_W, 40))
    out.append(f'<path d="{grid}" stroke="{LINE}" stroke-width="1"/>')
    for i, (top, bottom) in enumerate(BANDS):
        if animated:
            a = ARRIVE[i]
            out.append(f'<rect y="{top}" width="{ARCH_W}" height="{bottom - top}" fill="{LIME}" opacity="0">'
                       f'<animate attributeName="opacity" values="0;0;0.13;0.13;0;0" keyTimes="{kt(0, a - 0.25, a, a + DWELL, a + DWELL + 0.4, CYCLE)}" '
                       f'dur="{CYCLE}s" repeatCount="indefinite"/></rect>')
        if i:
            out.append(f'<path d="M0 {top}H{ARCH_W}" stroke="{WHITE}" stroke-opacity=".85" stroke-width="1.5"/>')
    out.append(f'<path d="M{cx} 60V{FLOOR - 30}" stroke="{LIME}" stroke-width="2" stroke-dasharray="3 7" stroke-linecap="round"/></g>')
    out.append(f'<path d="{arch}" fill="none" stroke="{WHITE}" stroke-opacity=".9" stroke-width="2"/>')

    for i, ((label, job), (top, bottom)) in enumerate(zip(zip(labels, c["jobs"]), BANDS)):
        mid = (top + bottom) / 2 + (40 if i == 0 else 0)
        lx = 64 if i == 0 else 24  # clear of the dome's curve
        out.append(f'<text x="{lx}" y="{mid + fs*0.35:.1f}" class="lbl" font-size="{fs}">{escape(label)}</text>')
        out.append(f'<path d="M{ARCH_W} {mid:.1f}H{ARCH_W + 44}" stroke="{LINE}" stroke-width="1.5"/>')
        job_svg = f'<text x="{ARCH_W + 54}" y="{mid + fs*0.35:.1f}" class="job" font-size="{fs}">{escape(job)}</text>'
        out.append(job_svg)
        if animated:
            a = ARRIVE[i]
            out.append(f'<g opacity="0">{pulse_opacity(a - 0.1, a + DWELL + 0.2)}'
                       f'<path d="M{ARCH_W} {mid:.1f}H{ARCH_W + 44}" stroke="{LIME}" stroke-width="2"/>'
                       f'<text x="{ARCH_W + 54}" y="{mid + fs*0.35:.1f}" class="job on" font-size="{fs}">{escape(job)}</text></g>')

    # Incoming request label, the response, and the drafting marks.
    out.append(f'<text x="{cx}" y="{ENTRY - 14}" text-anchor="middle" class="lbl dim" font-size="{fs*0.85:.1f}">{c["request"]}</text>')
    out.append(f'<path d="M{cx} {ENTRY - 4}V{ENTRY + 40}" stroke="{MUTED}" stroke-width="1.5"/>')
    ok = f'<text x="{ARCH_W + 54}" y="{FLOOR + 44}" class="job on" font-size="{fs}">● 200 OK</text>'
    out.append(f'<g opacity="0">{pulse_opacity(EXIT - 0.2, CYCLE - 0.5)}{ok}</g>' if animated else ok)
    out.append(f'<path d="M-30 -10H-2M-30 -10V18" fill="none" stroke="{LIME}" stroke-width="3"/>')

    if animated:
        # The request itself: tossed in, hops down landing on each floor, leaves after the last.
        r = 8
        stops = [(cx, ENTRY + 40, 0.6, 0.6)]
        for i, (a, (_, bottom)) in enumerate(zip(ARRIVE, BANDS)):
            stops.append((ARCH_W * (0.7 if i % 2 else 0.52), bottom - r, a, a + DWELL * 0.6))
        out.append(ball(stops, CYCLE, r, LIME, 0.6, EXIT - 0.2, lift=36))
    out.append("</g>")
    return "".join(out)


def styles():
    return (font_faces() +
            f".name{{font:800 112px Archivo,'Helvetica Neue',Arial,sans-serif;fill:{WHITE};letter-spacing:-.02em}}"
            f".eyebrow{{font:400 15px 'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.22em;fill:{LIME}}}"
            f".role{{font:400 24px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{WHITE}}} .role tspan{{fill:{LIME}}}"
            f".tag{{font:400 21px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{MUTED}}}"
            f".lbl{{font-family:'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.14em;fill:{WHITE}}}"
            f".job{{font-family:'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.06em;fill:{MUTED}}}"
            f".dim{{fill:{MUTED}}} .on{{fill:{LIME}}}")


def role_svg(role, x, y, size=None):
    parts = role.split(" / ")
    sep = '<tspan> / </tspan>'
    style = f' style="font-size:{size}px"' if size else ""
    return f'<text x="{x}" y="{y}" class="role"{style}>{sep.join(escape(p) for p in parts)}</text>'


def rise(content, delay, animated):
    """Fades and slides `content` up into place once, `delay` seconds after load."""
    if not animated:
        return content
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.7s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 28" to="0 0" begin="{delay}s" dur="0.7s" '
            f'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1" fill="freeze"/>{content}</g>')


def typed(text, x, y, size, animated, uid, begin=1.4, per_char=0.045):
    """The tagline types itself out once, then a cursor keeps blinking after it."""
    line = f'<text x="{x}" y="{y}" class="tag" style="font-size:{size}px">{escape(text)}</text>'
    if not animated:
        return line
    adv = size * 0.6  # IBM Plex Mono advance
    widths = ";".join(f"{adv * n:.1f}" for n in range(len(text) + 1))
    xs = ";".join(f"{x + adv * n + 4:.1f}" for n in range(len(text) + 1))
    dur = per_char * len(text)
    return (f'<clipPath id="type{uid}"><rect x="{x - 4}" y="{y - size}" height="{size * 1.6:.0f}" width="0">'
            f'<animate attributeName="width" values="{widths}" calcMode="discrete" begin="{begin}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<g clip-path="url(#type{uid})">{line}</g>'
            f'<rect x="{x + 4}" y="{y - size * 0.82:.1f}" width="{adv * 0.55:.1f}" height="{size:.0f}" fill="{LIME}">'
            f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="{begin}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect>')


def hero(layout, animated, c, labels):
    wide = layout == "wide"
    if wide:
        W, H = 1600, 560
        text = (rise('<text x="96" y="118" class="eyebrow">01 · JERANGEL1</text>', 0.1, animated)
                + rise(f'<text x="90" y="232" class="name">{NAME[0]}</text>', 0.25, animated)
                + rise(f'<text x="90" y="334" class="name">{NAME[1]}</text>', 0.45, animated)
                + rise(role_svg(c["role"], 96, 400), 0.75, animated)
                + typed(c["tagline"], 96, 450, 21, animated, "w"))
        plan = blueprint(900, 104, 0.8, 18, animated, "w", c, labels)
    else:
        W, H = 800, 1040
        text = (rise('<text x="60" y="80" class="eyebrow" style="font-size:20px">01 · JERANGEL1</text>', 0.1, animated)
                + rise(f'<text x="54" y="196" class="name" style="font-size:118px">{NAME[0]}</text>', 0.25, animated)
                + rise(f'<text x="54" y="304" class="name" style="font-size:118px">{NAME[1]}</text>', 0.45, animated)
                + rise(role_svg(c["role"], 60, 372, 30), 0.75, animated)
                + typed(c["tagline"], 60, 420, 24, animated, "n"))
        plan = blueprint(110, 556, 0.8, 24, animated, "n", c, labels)
    grid = (f'<path d="{"".join(f"M{x} 0V{H}" for x in range(0, W, 40))}{"".join(f"M0 {y}H{W}" for y in range(0, H, 40))}" '
            f'stroke="{WHITE}" stroke-opacity="0.035"/>')
    label = f"{' '.join(NAME).title()}. {c['role']}. {c['tagline']} {c['diagram']}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><style>{styles()}</style>'
            f'<rect width="{W}" height="{H}" rx="18" fill="{CHARCOAL}"/>{grid}{text}{plan}</svg>')


def wrap(text, chars):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def principles(layout, c):
    wide = layout == "wide"
    W = 1000 if wide else 600
    m, gap = 28, 16
    fs = 14 if wide else 19
    cols = 3 if wide else 1
    card_w = (W - m * 2 - gap * (cols - 1)) / cols
    pad = fs * 1.3
    body_chars = int((card_w - pad * 2) / (fs * 0.6))
    title_size = fs * 1.45
    title_chars = int((card_w - pad * 2) / (title_size * 0.6))
    cards, heights = [], []
    for title, body in c["principles"]:
        t_lines, b_lines = wrap(title, title_chars), wrap(body, body_chars)
        heights.append(pad * 2 + fs * 2.2 + len(t_lines) * title_size * 1.15 + fs * 0.6 + len(b_lines) * fs * 1.5)
        cards.append((t_lines, b_lines))
    card_h = max(heights)
    y0 = m + fs * 2.2
    out = []
    for i, (t_lines, b_lines) in enumerate(cards):
        x = m + (i % cols) * (card_w + gap)
        y = y0 + (i // cols) * (card_h + gap) if not wide else y0
        h = card_h if wide else heights[i]
        if not wide:
            y = y0 + sum(heights[:i]) + gap * i
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{card_w:.1f}" height="{h:.1f}" rx="{fs*0.8:.1f}" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>'
                   f'<path d="M{x:.1f} {y + fs*1.8:.1f}V{y:.1f}H{x + fs*1.8:.1f}" fill="none" stroke="{LIME}" stroke-width="3"/>'
                   f'<text x="{x + pad:.1f}" y="{y + pad + fs*0.8:.1f}" class="num">P/0{i + 1}</text>')
        ty = y + pad + fs * 2.2 + title_size * 0.8
        for line in t_lines:
            out.append(f'<text x="{x + pad:.1f}" y="{ty:.1f}" class="ptitle">{escape(line)}</text>')
            ty += title_size * 1.15
        by = ty - title_size * 1.15 + fs * 0.6 + fs * 1.5
        for line in b_lines:
            out.append(f'<text x="{x + pad:.1f}" y="{by:.1f}" class="pbody">{escape(line)}</text>')
            by += fs * 1.5
    H = (y0 + card_h if wide else y0 + sum(heights) + gap * (len(heights) - 1)) + m
    style = (font_faces() +
             f".num{{font:400 {fs*0.85:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.12em;fill:{LIME}}}"
             f".eyebrow{{font:400 {fs*0.85:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.18em;fill:{LIME}}}"
             f".ptitle{{font:700 {title_size:.1f}px Archivo,'Helvetica Neue',Arial,sans-serif;fill:{WHITE}}}"
             f".pbody{{font:400 {fs:.1f}px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{MUTED}}}")
    label = c["principles_title"].capitalize() + ". " + " ".join(f"{t} {b}" for t, b in c["principles"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><style>{style}</style>'
            f'<rect width="{W}" height="{H:.0f}" rx="18" fill="{CHARCOAL}"/>'
            f'<text x="{m}" y="{m + fs*1.1:.1f}" class="eyebrow">{c["principles_title"]}</text>{"".join(out)}</svg>')


def chapter(c):
    eyebrow, line1, line2 = c["chapter"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="124" viewBox="0 0 640 124" role="img" aria-label="{escape(f"{eyebrow}: {line1} {line2}")}">
  <title>{escape(f"{eyebrow}: {line1} {line2}")}</title>
  <style>{font_faces()}.e{{font:400 12px 'Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.18em;fill:{LIME}}}
  .q{{font:400 15px 'Plex Mono',ui-monospace,Menlo,monospace;fill:{WHITE}}}</style>
  <rect width="640" height="124" rx="16" fill="{CHARCOAL}"/>
  <path d="M28 28V18H38" fill="none" stroke="{BLUE}" stroke-width="3"/>
  <text x="28" y="46" class="e">{escape(eyebrow)}</text>
  <text x="28" y="78" class="q">{escape(line1)}</text>
  <text x="28" y="100" class="q">{escape(line2)}</text>
</svg>'''


# LinkedIn "in" mark (Simple Icons, CC0), 24x24 units.
LINKEDIN = ("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046"
            "c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 "
            "2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 "
            "0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z")


def cta(c):
    """The LinkedIn button: logo, label, arrow. Width follows the label so the arrow never collides with it."""
    text_w = len(c["cta"]) * 11.6
    w = text_w + 144
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="64" viewBox="0 0 {w:.0f} 64" role="img" aria-label="{escape(c["cta"])}">'
            f'<title>{escape(c["cta"])}</title><style>{font_faces()}</style>'
            f'<rect width="{w:.0f}" height="64" rx="32" fill="{LIME}"/>'
            f'<path transform="translate(28,18) scale({28 / 24:.4f})" d="{LINKEDIN}" fill="{CHARCOAL}"/>'
            f'<text x="70" y="40" font-family="Archivo, \'Helvetica Neue\', Arial, sans-serif" font-size="20" font-weight="700" fill="{CHARCOAL}">{escape(c["cta"])}</text>'
            f'<path d="M{w - 58:.0f} 32h22m-8-8 8 8-8 8" fill="none" stroke="{CHARCOAL}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def language_switch(active):
    """EN | ES pill; the active language is filled. The README wraps it in a link to the other language."""
    cells = []
    for i, code in enumerate(("EN", "ES")):
        x = 2 + i * 50
        on = code.lower() == active
        cells.append(f'<rect x="{x}" y="2" width="50" height="28" rx="14" fill="{LIME if on else "none"}"/>'
                     f'<text x="{x + 25}" y="21" text-anchor="middle" fill="{CHARCOAL if on else WHITE}">{code}</text>')
    other = "Leer en español" if active == "en" else "Read in English"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="104" height="32" viewBox="0 0 104 32" role="img" aria-label="{other}">'
            f'<title>{other}</title><style>{font_faces()}text{{font:400 13px \'Plex Mono\',ui-monospace,Menlo,monospace;letter-spacing:.12em}}</style>'
            f'<rect x="1" y="1" width="102" height="30" rx="15" fill="{CHARCOAL}" stroke="{LINE}" stroke-width="1.5"/>{"".join(cells)}</svg>')


OUT.mkdir(parents=True, exist_ok=True)
for lang, c in COPY.items():
    tag = "" if lang == "en" else f".{lang}"
    labels = LAYER_LABELS if lang == "en" else LAYER_LABELS_ES
    for layout, suffix in (("wide", ""), ("narrow", "-mobile")):
        (OUT / f"hero{suffix}{tag}.svg").write_text(hero(layout, True, c, labels))
        (OUT / f"hero{suffix}-static{tag}.svg").write_text(hero(layout, False, c, labels))
        (OUT / f"principles{suffix}{tag}.svg").write_text(principles(layout, c))
    (OUT / f"chapter-off-the-clock{tag}.svg").write_text(chapter(c))
    (OUT / f"connect-linkedin{tag}.svg").write_text(cta(c))
    (OUT / f"language-{lang}.svg").write_text(language_switch(lang))
print(sorted(p.name for p in OUT.glob("*.svg")))
