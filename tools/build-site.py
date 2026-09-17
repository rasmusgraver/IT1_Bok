#!/usr/bin/env python3
"""build-site.py — IT1_Bok enkeltkilde for sidehode, sidefelt, innholdsfortegnelse,
sidefot og paginering. Genererer alle 10 publiserte HTML-sidene fra innholds-
fragmenter i tools/pages/ og én felles mal her i fila.

Kjøring:
    python3 tools/build-site.py

Endring i navigasjon = endring her (én fil), ikke 10 håndredigerte sider.
Kjør `python3 tools/check-site.py` etterpå for å verifisere lenkene.
"""

import html as htmlmod
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Bokas struktur (enkeltkilde for navigasjon)
# ---------------------------------------------------------------------------
TRACKS = [
    ("html", "// html", "dot--html"),
    ("css", "// css", "dot--css"),
    ("js", "// javascript", "dot--js"),
]

CHAPTERS = {
    "html": [
        ("Introduksjon", "html/intro.html"),
        ("Viktige tagger", "html/tagger.html"),
        ("Semantiske tagger", "html/semantikk.html"),
        ("Forms", "html/forms.html"),
    ],
    "css": [
        ("Grunnleggende", "css/grunnleggende.html"),
        ("Flexbox", "css/flexbox.html"),
        ("Grid", "css/grid.html"),
    ],
    "js": [
        ("Grunnleggende", "js/grunnleggende.html"),
        ("onclick", "js/onclick.html"),
    ],
}

# (id, fil, tittel, spor, eyebrow, h1)
PAGES = [
    ("index", "index.html", "IT1 · Nettbasert kompendium", None, "// velkommen", "IT1"),
    ("intro", "html/intro.html", "Introduksjon · IT1", "html", "// html", "Introduksjon"),
    ("tagger", "html/tagger.html", "Viktige tagger · IT1", "html", "// html", "Viktige tagger"),
    ("semantikk", "html/semantikk.html", "Semantiske tagger · IT1", "html", "// html", "Semantiske tagger"),
    ("forms", "html/forms.html", "Forms · IT1", "html", "// html", "Forms"),
    ("css_grunnleggende", "css/grunnleggende.html", "Grunnleggende · IT1", "css", "// css", "Grunnleggende"),
    ("css_flexbox", "css/flexbox.html", "Flexbox · IT1", "css", "// css", "Flexbox"),
    ("css_grid", "css/grid.html", "Grid · IT1", "css", "// css", "Grid"),
    ("js_grunnleggende", "js/grunnleggende.html", "Grunnleggende · IT1", "js", "// javascript", "Grunnleggende"),
    ("js_onclick", "js/onclick.html", "onclick · IT1", "js", "// javascript", "onclick"),
]
BY_ID = {p[0]: p for p in PAGES}
ORDER = [p[0] for p in PAGES]          # lineær leserekkefølge (R-04)

DESC = {
    "index": "Nettbasert kompendium for IT1 — lær HTML, CSS og JavaScript steg for steg.",
    "html": "Nettbasert kompendium for IT1 — HTML-siden: tagger, semantikk og skjemaer.",
    "css": "Nettbasert kompendium for IT1 — CSS-siden: selektorer, boksmodellen, flexbox og grid.",
    "js": "Nettbasert kompendium for IT1 — JavaScript-siden: variabler, funksjoner og hendelser.",
}


def page_desc(pid):
    if pid == "index":
        return DESC["index"]
    track = BY_ID[pid][3]
    return DESC.get(track, DESC["index"])


def rel_root(page_file):
    """Relativ prefix fra filas eget katalog opp til repo-rota."""
    return "../" * page_file.count("/")


def sidebar(page_id):
    """Sidefeltet: kommaseparerte spor; aktivt spor utfoldet med kapitler."""
    page = BY_ID[page_id]
    track = page[3]
    root = rel_root(page[1])
    r = []

    home_active = page_id == "index"
    r.append(
        f'<a class="nav-home{" is-active" if home_active else ""}"'
        f'{ " aria-current=\"page\"" if home_active else ""} href="{root}index.html">// forside</a>'
    )

    for tname, tlabel, dotcls in TRACKS:
        is_here = track == tname
        if page_id == "index":
            # Forsiden: kun spor-lenker (uten underliste)
            r.append(
                f'<a class="nav-link" href="{CHAPTERS[tname][0][1]}">'
                f'<p class="nav-group__label"><span class="dot {dotcls}"></span>{tlabel}</p></a>'
            )
            continue
        if is_here:
            r.append(
                f'<div class="nav-group">'
                f'<p class="nav-group__label"><span class="dot {dotcls}"></span>{tlabel}</p>'
                f'<ul class="nav-group__list">'
            )
            for ctitle, chref in CHAPTERS[tname]:
                active = chref == page[1]
                r.append(
                    f'<li><a class="nav-link{" is-active" if active else ""}"'
                    f'{" aria-current=\"page\"" if active else ""} href="{root}{chref}">{htmlmod.escape(ctitle)}</a></li>'
                )
            r.append("</ul></div>")
        else:
            landing = CHAPTERS[tname][0][1]
            r.append(
                f'<a class="nav-link" href="{root}{landing}">'
                f'<p class="nav-group__label"><span class="dot {dotcls}"></span>{tlabel}</p></a>'
            )
    return "\n".join(r)


def head(page_id):
    page = BY_ID[page_id]
    title = page[2]
    desc = page_desc(page_id)
    proto = "https://"
    return f"""<meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{htmlmod.escape(title)}</title>
        <meta name="description" content="{htmlmod.escape(desc)}" />
        <link rel="icon" type="image/svg+xml" href="{rel_root(page[1])}images/favicon.svg" />
        <meta property="og:title" content="{htmlmod.escape(title)}" />
        <meta property="og:description" content="{htmlmod.escape(desc)}" />
        <meta property="og:type" content="website" />
        <meta property="og:locale" content="nb_NO" />
        <link rel="stylesheet" href="{rel_root(page[1])}styles.css" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet" />"""


def toc(fragment):
    """Hent h2-overskriftene (konvertert fra block__label) → innholdsfortegnelse."""
    entries = re.findall(
        r'<h2 class="block__label" id="([^"]+)">(.*?)</h2>', fragment, re.S
    )
    if len(entries) < 3:
        return ""
    lis = "\n".join(
        f'<li><a href="#{sid}">{htmlmod.escape(re.sub(r"<[^>]+>", "", lbl).strip())}</a></li>'
        for sid, lbl in entries
    )
    return (
        f'<nav class="toc" aria-label="På denne siden">'
        f'<p class="toc__label">// på denne siden</p>'
        f'<ol class="toc__list">{lis}</ol></nav>'
    )


def upgrade_labels(fragment):
    """Seksjonsmerkene blir ekte overskrifter (h2) med anker-id (R-05).
    Nedlastingsblokkene («📥 …») beholdes som p-etiketter."""
    counter = {"n": 0}

    def repl(m):
        label = m.group(3).strip()
        if label.startswith("📥"):
            return m.group(0)
        counter["n"] += 1
        n = counter["n"]
        return (
            f'<section class="{m.group(2)}">'
            f'<h2 class="block__label" id="sec-{n}">{label}</h2>'
        )

    # <section class="block block--theory"> → <section ... id="sec-N"><h2 class="block__label" id="sec-N">…
    pattern = re.compile(r'(<section class="(block block--(?:theory|example|task))">\s*<p class="block__label">(.*?)</p>)', re.S)
    return pattern.sub(repl, fragment)


def pagination(page_id):
    idx = ORDER.index(page_id)
    page = BY_ID[page_id]
    root = rel_root(page[1])
    prev = BY_ID[ORDER[idx - 1]] if idx > 0 else None
    nxt = BY_ID[ORDER[idx + 1]] if idx < len(ORDER) - 1 else None
    home = "index.html" if page_id == "index" else root + "index.html"

    bits = ['<nav class="page-nav" aria-label="Kapittelnavigasjon">']
    if prev and prev[0] != "index":
        bits.append(f'<a class="page-nav__prev" href="{root}{prev[1]}">← {htmlmod.escape(prev[2].split(" · ")[0])}</a>')
    elif prev:
        bits.append(f'<a class="page-nav__prev" href="{root}index.html">← forside</a>')
    else:
        bits.append('<span class="page-nav__spacer"></span>')
    cur = htmlmod.escape(page[2].split(" · ")[0])
    bits.append(f'<span class="page-nav__cur">// {cur}</span>')
    if nxt:
        bits.append(f'<a class="page-nav__next" href="{root}{nxt[1]}">{htmlmod.escape(nxt[2].split(" · ")[0])} →</a>')
    else:
        bits.append('<span class="page-nav__spacer"></span>')
    bits.append('</nav>')
    bits.append('<p class="page-home"><a href="' + home + '">↑ tilbake til forsiden</a></p>')
    return "\n".join(bits)


def front_main():
    """Forsiden: kort med bokas innholdsfortegnelse under hvert fagkort (R-09)."""
    cards = []
    intro = {
        "html": ("Struktur", "HTML - Innholdet på siden.", "Tagger, semantikk og skjemaer."),
        "css": ("Stil", "CSS - Hvordan siden ser ut!", "Og etterhvert: Boksmodell, flexbox og grid."),
        "js": ("Oppførsel", "JS - Gi \"liv\" til siden!", "Variabler, funksjoner og hendelser. Hva siden gjør."),
    }
    for tname, tlabel, dotcls in TRACKS:
        heading, p1, p2 = intro[tname]
        chap_lis = "\n".join(
            f'<li><a href="{href}">{htmlmod.escape(ct)}</a></li>' for ct, href in CHAPTERS[tname]
        )
        # Merk: kortet er en div – ikke et <a>-element – fordi kapitlene inni
        # også er lenker (a-inne-i-a ville ødelagt DOM-en i HTML-parseren).
        cards.append(
            f'<div class="track-card track-card--{tname}">'
            f'<a class="track-card__head" href="{CHAPTERS[tname][0][1]}">'
            f'<p class="track-card__eyebrow"><span class="dot {dotcls}"></span>{tlabel}</p>'
            f'<h2>{heading}</h2>'
            f'</a>'
            f'<p>{p1}</p>'
            f'<p>{p2}</p>'
            f'<ul class="track-card__list">{chap_lis}</ul>'
            f'</div>'
        )
    return f"""<p class="eyebrow">// velkommen</p>
        <h1>IT1</h1>
        <p class="lede">Dette er det digitale kompendiet for faget. Gjennom året bygger vi det opp
        steg for steg — fra de første HTML-taggene til at siden du navigerer i akkurat nå kan style
        seg selv og reagere på klikk. Bruk menyen til venstre for å hoppe mellom temaene.</p>
        <div class="track-grid">
        {''.join(cards)}
        </div>"""


def render_page(page_id):
    page = BY_ID[page_id]
    file = page[1]
    root = rel_root(file)

    if page_id == "index":
        main_body = front_main()
        content_class = "content"
    else:
        frag = open(os.path.join(ROOT, "tools", "pages", page_id + ".html")).read()
        frag = upgrade_labels(frag)
        main_body = (
            f'<p class="eyebrow">{page[4]}</p>'
            f'<h1>{htmlmod.escape(page[5])}</h1>'
            + toc(frag)
            + frag
            + pagination(page_id)
        )
        content_class = "content"

    return f"""<!doctype html>
<html lang="no">
  <head>
        {head(page_id)}
  </head>
  <body>
    <div class="layout">
      <a class="skip-link" href="#main">Hopp til innhold</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="sidebar">
        <span></span><span></span><span></span>
        <span class="sr-only">Åpne meny</span>
      </button>
      <aside class="sidebar" id="sidebar">
        <a class="brand" href="{root}index.html">IT1<span class="brand__cursor" aria-hidden="true">▍</span></a>
        <nav class="sidebar__nav" aria-label="Faginnhold">
        {sidebar(page_id)}
        </nav>
      </aside>
      <main class="{content_class}" id="main">
        {main_body}
      </main>
    </div>
    <script src="{root}script.js"></script>
  </body>
</html>"""


def main():
    for pid in ORDER:
        out = os.path.join(ROOT, BY_ID[pid][1])
        with open(out, "w") as fh:
            fh.write(render_page(pid))
        print("wrote", out)


if __name__ == "__main__":
    main()