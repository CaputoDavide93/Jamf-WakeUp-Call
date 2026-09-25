#!/usr/bin/env python3
"""Draw every diagram in this repository as SVG, one file per colour scheme.

  docs/assets/<name>-light.svg
  docs/assets/<name>-dark.svg

Drawn rather than Mermaid, because GitHub renders Mermaid on its own terms: it
picks the theme, pins the version, ignores `%%{init}%%` and decodes HTML
entities before parsing. Here the picture is exactly what is committed.

**GitHub sanitises SVG in markdown**, so no <style>, no <script>, no web font
and no <foreignObject>. Everything is a presentation attribute and the type is
a system stack. Each pair is served from one <picture>, which GitHub switches
on prefers-color-scheme.

Layout is explicit rather than solved: these diagrams are small enough that
placing them by hand is cheaper than a layout engine nobody can predict.

House rules: a slate scale, a single accent on the one thing that matters in
each picture, drawn icons rather than emoji, monospace for anything that is
literally typed, and text contrast at or above 4.5:1 in both schemes.

Needs only the standard library. Run `python3 tools/gen_diagram.py` after
editing; tests/test_diagrams.py fails if a committed SVG differs from what
this file draws.
"""
from __future__ import annotations

import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parents[1]
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

SCHEMES = {
    "light": dict(card="#ffffff", border="#d8dee4", title="#0f172a", sub="#5b6673",
                  accent="#2b59c3", on_accent="#ffffff", soft="#f1f4f9",
                  line="#94a3b8", rule="#e6e9ee", chip="#475569",
                  warn="#9a3412", warn_soft="#fff4ed", group="#f7f9fb"),
    "dark":  dict(card="#161b22", border="#30363d", title="#e6edf3", sub="#9aa4b0",
                  accent="#4c7ef3", on_accent="#ffffff", soft="#1b2230",
                  line="#6b7684", rule="#232a33", chip="#aeb7c2",
                  warn="#ffa657", warn_soft="#2a1d14", group="#11151b"),
}


# Stroked glyphs on a 24x24 grid, drawn rather than typed.
ICONS = {
    "user":     "M12 11a4 4 0 1 0 0-8 4 4 0 1 0 0 8z M5 21c0-4 3-7 7-7s7 3 7 7",
    "terminal": "M3 5h18v14H3z M7 10l3 2.5L7 15 M12.5 15h4.5",
    "server":   "M4 4h16v7H4z M4 13h16v7H4z M8 7.5h.01 M8 16.5h.01 M12 7.5h4 M12 16.5h4",
    "laptop":   "M5 5h14v10H5z M3 15h18l1.5 4h-21z",
}


class Canvas:
    """Parts plus a size. No layout engine, on purpose."""

    def __init__(self, w: int, h: int, scheme: str, label: str) -> None:
        self.w, self.h, self.c, self.label = w, h, SCHEMES[scheme], label
        self.parts: list[str] = []

    def add(self, *svg: str) -> "Canvas":
        self.parts.extend(svg)
        return self

    # ── primitives ────────────────────────────────────────────────────────
    def icon(self, name, x, y, colour, size=21):
        s = size / 24
        return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" fill="none" '
                f'stroke="{colour}" stroke-width="1.7" stroke-linecap="round" '
                f'stroke-linejoin="round"><path d="{ICONS[name]}"/></g>')

    def text(self, x, y, s, *, size=13, colour=None, font=None, weight=None,
             anchor="start", opacity=None):
        c = colour or self.c["sub"]
        extra = (f' font-weight="{weight}"' if weight else "") + \
                (f' opacity="{opacity}"' if opacity else "")
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font or SANS}" '
                f'font-size="{size}" fill="{c}" text-anchor="{anchor}"{extra}>'
                f'{escape(s)}</text>')

    def box(self, x, y, w, h, title, subs=(), *, icon=None, tone="plain", rx=10):
        c = self.c
        fill, edge, tt = c["card"], c["border"], c["title"]
        st, op = c["sub"], ""
        if tone == "accent":
            fill = edge = c["accent"]; tt = st = c["on_accent"]; op = "0.85"
        elif tone == "soft":
            fill = c["soft"]
        elif tone == "warn":
            fill, edge, tt, st = c["warn_soft"], c["warn"], c["warn"], c["warn"]
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
               f'stroke="{edge}" stroke-width="1"/>']
        tx = x + 16
        ty = y + (28 if subs else h / 2 + 5)
        if icon:
            out.append(self.icon(icon, x + 16, y + (13 if subs else h / 2 - 10), tt))
            tx = x + 47
        out.append(self.text(tx, ty, title, size=15 if subs else 14,
                             colour=tt, weight="600"))
        for i, s in enumerate(subs):
            out.append(self.text(x + 16, y + 52 + i * 18, s, size=12.5,
                                 colour=st, opacity=op or None))
        return "".join(out)

    def diamond(self, cx, cy, w, h, lines):
        c = self.c
        pts = f"{cx},{cy - h/2} {cx + w/2},{cy} {cx},{cy + h/2} {cx - w/2},{cy}"
        out = [f'<polygon points="{pts}" fill="{c["soft"]}" stroke="{c["border"]}" '
               f'stroke-width="1"/>']
        n = len(lines)
        for i, s in enumerate(lines):
            out.append(self.text(cx, cy - (n - 1) * 7 + i * 14 + 4, s, size=12,
                                 colour=c["title"], anchor="middle"))
        return "".join(out)

    def pill(self, cx, cy, text, *, tone="plain", pad=16, size=13):
        c = self.c
        w = len(text) * size * 0.58 + pad * 2
        h = 32
        fill, edge, col = c["card"], c["border"], c["title"]
        if tone == "accent":
            fill = edge = c["accent"]; col = c["on_accent"]
        elif tone == "soft":
            fill = c["soft"]
        return (f'<rect x="{cx - w/2:.1f}" y="{cy - h/2}" width="{w:.1f}" height="{h}" '
                f'rx="{h/2}" fill="{fill}" stroke="{edge}" stroke-width="1"/>'
                + self.text(cx, cy + 4.5, text, size=size, colour=col, anchor="middle",
                            weight="500")), w

    def edge(self, pts, *, label=None, dash=False, both=False, label_at=0.5,
             label_dy=-9, label_anchor="middle", mono=True):
        c = self.c
        d = ' stroke-dasharray="5 4"' if dash else ""
        path = " ".join(f"{x},{y}" for x, y in pts)
        out = [f'<polyline points="{path}" fill="none" stroke="{c["line"]}" '
               f'stroke-width="1.5"{d} marker-end="url(#a)"'
               + (' marker-start="url(#a)"' if both else "") + "/>"]
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            lx = x1 + (x2 - x1) * label_at
            ly = y1 + (y2 - y1) * label_at
            out.append(self.text(lx, ly + label_dy, label, size=11.5,
                                 colour=c["chip"], font=MONO if mono else SANS,
                                 anchor=label_anchor))
        return "".join(out)

    def group(self, x, y, w, h, title):
        c = self.c
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
                f'fill="{c["group"]}" stroke="{c["border"]}" stroke-width="1" '
                f'stroke-dasharray="6 5"/>'
                + self.text(x + 18, y + 24, title, size=12, colour=c["sub"],
                            weight="600"))

    def footer(self, note):
        return (f'<line x1="24" y1="{self.h - 52}" x2="{self.w - 24}" y2="{self.h - 52}" '
                f'stroke="{self.c["rule"]}" stroke-width="1"/>'
                + self.text(24, self.h - 26, note, size=12.5, colour=self.c["sub"]))

    def render(self) -> str:
        c = self.c
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-label="{escape(self.label)}">'
            f'<defs>'
            f'<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 10 5 0 10z" fill="{c["line"]}"/></marker>'
            f'</defs>' + "".join(self.parts) + "</svg>"
        )


# ── the diagrams ──────────────────────────────────────────────────────────

def architecture(scheme):
    """One wake-up, end to end. A sequence, so it gets lifelines."""
    k = Canvas(1180, 690, scheme,
               "The operator runs main.py, which gets a bearer token from Jamf Pro when it has "
               "no API token, resolves the dynamic group, serial or serial file to computer "
               "records, and asks for confirmation. Unless --dry-run is set it then posts one "
               "management-framework redeploy per computer; Jamf Pro sends the MDM command "
               "over APNs and the Mac reinstalls the Jamf framework.")
    c = k.c
    O, P, J, D = 116, 340, 820, 1064
    lanes = [("Operator", O, "user", "plain"), ("main.py", P, "terminal", "accent"),
             ("Jamf Pro", J, "server", "plain"), ("Mac", D, "laptop", "plain")]
    top, bottom = 84, 616
    for name, x, icon, tone in lanes:
        w = 176
        k.add(k.box(x - w / 2, 26, w, 44, name, icon=icon, tone=tone),
              f'<line x1="{x}" y1="{top - 14}" x2="{x}" y2="{bottom}" stroke="{c["border"]}" '
              f'stroke-width="1" stroke-dasharray="4 5"/>')

    def msg(y, x1, x2, text, *, dash=False):
        step = 8 if x2 > x1 else -8
        return k.edge([(x1 + step, y), (x2 - step, y)], label=text, dash=dash)

    def note(y, x1, x2, text, *, mono=False):
        return k.text((x1 + x2) / 2, y + 19, text, size=11.5, anchor="middle",
                      colour=c["chip"] if mono else c["sub"], font=MONO if mono else None)

    # The block the whole tool exists for: one redeploy per computer.
    k.add(f'<rect x="{P - 130}" y="380" width="{J - P + 260}" height="106" rx="8" fill="none" '
          f'stroke="{c["border"]}" stroke-width="1" stroke-dasharray="5 4"/>',
          k.text(P - 116, 398, "for each computer, unless --dry-run", size=11.5,
                 colour=c["sub"], weight="600"))
    k.add(
        msg(100, O, P, "python3 main.py"),
        note(100, O, P, "group, one serial or a file"),
        msg(146, P, J, "POST /api/v1/auth/token"),
        note(146, P, J, "skipped when an API token is set"),
        msg(200, J, P, "bearer token", dash=True),
        msg(246, P, J, "GET /JSSResource/computergroups/id/{id}"),
        note(246, P, J, "or /JSSResource/computers/serialnumber/{sn}", mono=True),
        msg(300, J, P, "computer records", dash=True),
        msg(334, P, O, "Do you want to proceed?", dash=True),
        msg(364, O, P, "yes"),
        msg(430, P, J, "POST /api/v1/jamf-management-framework/redeploy/{id}"),
        msg(466, J, P, "deviceId, commandUuid", dash=True),
        msg(518, J, D, "MDM command via APNs"),
        # The last step is the Mac's own, so it is a note on its lane, not a message.
        k.box(D - 88, 540, 176, 64, "Jamf framework", ["reinstalled"], tone="soft"),
        k.footer("Superseded by the wakeup module in Jamf-SnipeIT-Suite. Reads are retried "
                 "on 429 and 5xx; a redeploy is sent once, never retried."),
    )
    return k.render()


DIAGRAMS = {
    "architecture": architecture,
}


def main() -> None:
    out = ROOT / "docs" / "assets"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in DIAGRAMS.items():
        for scheme in SCHEMES:
            path = out / f"{name}-{scheme}.svg"
            path.write_text(fn(scheme), encoding="utf-8")
    print(f"{len(DIAGRAMS)} diagrams x {len(SCHEMES)} schemes -> docs/assets/")


if __name__ == "__main__":
    main()
