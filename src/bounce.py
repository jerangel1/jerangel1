"""A ball that hops between landing spots: it arcs through the air, squashes on impact and kicks up a ring.

Shared by hero.py and ecosystem.py. Everything is SMIL, so it animates inside a GitHub <img>.
"""
import math

EASE_OUT = "0.25 0.46 0.45 0.94"  # rising: decelerates toward the apex
EASE_IN = "0.55 0.085 0.68 0.53"  # falling: accelerates toward the landing
HOLD = "0 0 1 1"


def ball(stops, cycle, r, color, show, hide, lift=40, ceiling=None):
    """stops: [(x, y, land, leave)] where (x, y) is the resting centre and land/leave are seconds.

    The ball rests on each stop from `land` to `leave`, then hops to the next one. It is visible
    from `show` to `hide` of every cycle. `ceiling` keeps arcs below a y (e.g. clear of a header).
    """
    def kt(*seconds):
        return ";".join(f"{min(max(s / cycle, 0), 1):.4f}" for s in seconds)

    x0, y0 = stops[0][0], stops[0][1]
    times, xs, ys, splines = [0.0], [x0], [y0], []

    def key(t, x, y, spline):
        times.append(t)
        xs.append(x)
        ys.append(y)
        splines.append(spline)

    for i, (x, y, land, leave) in enumerate(stops):
        if i:
            px, py, _, pleave = stops[i - 1]
            apex = min(py, y) - lift
            if ceiling is not None:
                apex = min(max(apex, ceiling), min(py, y) - 4)
            up, down = math.sqrt(py - apex), math.sqrt(y - apex)
            f = up / (up + down)  # share of the hop spent rising, as in a real parabola
            key(pleave + (land - pleave) * f, px + (x - px) * f, apex, EASE_OUT)
            key(land, x, y, EASE_IN)
        if leave > times[-1]:
            key(leave, x, y, HOLD)
    key(cycle, xs[-1], ys[-1], HOLD)

    timing = f'keyTimes="{kt(*times)}" dur="{cycle}s" repeatCount="indefinite"'
    moves = (f'<animate attributeName="cx" values="{";".join(f"{v:.1f}" for v in xs)}" {timing}/>'
             f'<animate attributeName="cy" values="{";".join(f"{v:.1f}" for v in ys)}" {timing} '
             f'calcMode="spline" keySplines="{";".join(splines)}"/>')

    # Squash on every landing: wider and flatter for a beat, then back to round.
    sq_t, rx, ry = [0.0], [r], [r]
    for _, _, land, _ in stops[1:]:
        for t, a, b in ((land - 0.02, r, r), (land + 0.07, r * 1.35, r * 0.7), (land + 0.24, r, r)):
            sq_t.append(t)
            rx.append(a)
            ry.append(b)
    sq_t.append(cycle)
    rx.append(r)
    ry.append(r)
    squash = (f'<animate attributeName="rx" values="{";".join(f"{v:.1f}" for v in rx)}" keyTimes="{kt(*sq_t)}" dur="{cycle}s" repeatCount="indefinite"/>'
              f'<animate attributeName="ry" values="{";".join(f"{v:.1f}" for v in ry)}" keyTimes="{kt(*sq_t)}" dur="{cycle}s" repeatCount="indefinite"/>')

    visible = (f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt(0, show - 0.2, show, hide, hide + 0.3, cycle)}" '
               f'dur="{cycle}s" repeatCount="indefinite"/>')
    out = [f'<ellipse cx="{x0:.1f}" cy="{y0:.1f}" rx="{r}" ry="{r}" fill="{color}" opacity="0">{moves}{squash}{visible}</ellipse>']

    # Impact ring: a flat ripple on the surface the ball just hit.
    for x, y, land, _ in stops[1:]:
        floor = y + r
        out.append(f'<ellipse cx="{x:.1f}" cy="{floor:.1f}" rx="0" ry="0" fill="none" stroke="{color}" stroke-width="2" opacity="0">'
                   f'<animate attributeName="rx" values="0;0;{r * 3.2:.1f};{r * 3.2:.1f}" keyTimes="{kt(0, land, land + 0.6, cycle)}" dur="{cycle}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="ry" values="0;0;{r * 0.9:.1f};{r * 0.9:.1f}" keyTimes="{kt(0, land, land + 0.6, cycle)}" dur="{cycle}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0;0.9;0;0" keyTimes="{kt(0, land - 0.01, land, land + 0.6, cycle)}" dur="{cycle}s" repeatCount="indefinite"/>'
                   f'</ellipse>')
    return "".join(out)
