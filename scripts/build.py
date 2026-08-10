#!/usr/bin/env python3
"""Regenerate every SVG on the profile from live GitHub data.

Run locally with a token that can read public data:

    GITHUB_TOKEN=$(gh auth token) python scripts/build.py

In CI the workflow passes the job's GITHUB_TOKEN. Note the query asks for
user(login:...) and not viewer — inside Actions `viewer` is the bot, not Berkay.

Design rule for everything in here: the *static* frame must already be correct.
Animation is decoration only. A bar whose width animates from zero renders as an
empty bar wherever animation does not run, which is worse than no animation.
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime

USER = "KaramelliS"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

BG, PANEL, PANEL2 = "#0f1216", "#171b21", "#121519"
LINE, LINE2 = "#2b323d", "#242a33"
TEXT, DIM, FAINT = "#e6edf3", "#adbac7", "#5b6572"
GREEN, GREEN2 = "#22c55e", "#16a34a"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, Segoe UI, Inter, Helvetica, Arial, sans-serif"

LANG_COLORS = {
    "Python": "#3572A5", "Rust": "#dea584", "JavaScript": "#f1e05a",
    "HTML": "#e34c26", "CSS": "#8b6fc4", "PowerShell": "#2f6fbd",
    "Shell": "#89e051", "Dockerfile": "#5c7d8a", "TypeScript": "#3178c6",
    "Go": "#00ADD8", "C": "#555555", "C++": "#f34b7d", "Java": "#b07219",
}
HEAT = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
PRE_ACCOUNT = "#0c0f13"          # days before the account existed

QUERY = """
query($login: String!) {
  user(login: $login) {
    login createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: CREATED_AT, direction: ASC}) {
      totalCount
      nodes {
        name createdAt stargazerCount isFork
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set. Try: GITHUB_TOKEN=$(gh auth token) python scripts/build.py")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": "bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": USER + "-profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit("GraphQL error: " + json.dumps(payload["errors"])[:400])
    return payload["data"]["user"]


def card(w, h, title):
    """Shared card chrome: border, faint grid, small caps title."""
    return [
        '<defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
        '<path d="M32 0H0V32" fill="none" stroke="#1c222a" stroke-width="1"/></pattern>'
        '<clipPath id="cardclip"><rect x="1" y="1" width="%d" height="%d" rx="16"/></clipPath>'
        '<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#fff" stop-opacity="0.13"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
        % (w - 2, h - 2),
        '<rect x="1" y="1" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (w - 2, h - 2, BG, LINE),
        '<g clip-path="url(#cardclip)"><rect width="%d" height="%d" fill="url(#grid)" opacity="0.45"/></g>' % (w, h),
        '<text x="40" y="38" font-family="%s" font-size="12" fill="#8b949e" letter-spacing="1.6">%s</text>'
        % (MONO, esc(title)),
    ]


# --------------------------------------------------------------------------- header

def build_header(u, repos, stars):
    since = datetime.strptime(u["createdAt"][:10], "%Y-%m-%d").strftime("%b %Y")
    taglines = [
        "Rust · Go · Node · Python — whatever the problem wants.",
        "I reverse-engineer protocols so software needs no browser.",
        "From Tokat, Türkiye. Still just getting started.",
    ]
    keys = [
        "0;1;1;0;0;0;0;0;0;0",
        "0;0;0;0;1;1;0;0;0;0",
        "0;0;0;0;0;0;0;1;1;0",
    ]
    times = [
        "0;0.03;0.28;0.33;0.36;0.63;0.66;0.96;0.99;1",
        "0;0.03;0.30;0.36;0.39;0.61;0.66;0.96;0.99;1",
        "0;0.03;0.30;0.36;0.39;0.63;0.69;0.72;0.94;1",
    ]
    chips = [
        ("%d public projects" % repos, False),
        ("Go · Node · Rust · Python", False),
        ("shipping since %s" % since, True),
    ]

    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300" '
         'role="img" aria-label="Berkay (KaramelliS) — 18, Tokat, Türkiye">']
    p.append('<defs>'
             '<linearGradient id="cardg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="#0b0d10"/></linearGradient>'
             '<linearGradient id="grn" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
             '<radialGradient id="glow" cx="0.16" cy="0.28" r="0.72">'
             '<stop offset="0" stop-color="%s" stop-opacity="0.16"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
             '<pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse">'
             '<path d="M32 0H0V32" fill="none" stroke="#1c222a" stroke-width="1"/></pattern>'
             '<clipPath id="cc"><rect x="1" y="1" width="1198" height="298" rx="16"/></clipPath>'
             '</defs>' % (PANEL2, GREEN, GREEN2, GREEN2, GREEN2))
    p.append('<rect x="1" y="1" width="1198" height="298" rx="16" fill="url(#cardg)" stroke="%s"/>' % LINE)
    p.append('<g clip-path="url(#cc)"><rect width="1200" height="300" fill="url(#g)" opacity="0.5"/>'
             '<rect width="1200" height="300" fill="url(#glow)"/>'
             '<rect width="1200" height="3" fill="url(#grn)"/></g>')

    p.append('<text x="48" y="76" font-family="%s" font-size="14" fill="#8b949e" letter-spacing="1.5">$ whoami</text>' % MONO)
    p.append('<text x="48" y="128" font-family="%s" font-size="46" font-weight="700" fill="%s" letter-spacing="-0.5">Berkay</text>' % (SANS, TEXT))
    p.append('<text x="212" y="128" font-family="%s" font-size="15" fill="#6e7681">@%s · 18</text>' % (MONO, USER))

    p.append('<g font-family="%s" font-size="16">' % MONO)
    for t, k, tm in zip(taglines, keys, times):
        p.append('<text x="70" y="172" fill="%s" opacity="0">%s'
                 '<animate attributeName="opacity" values="%s" keyTimes="%s" dur="15s" repeatCount="indefinite"/>'
                 '</text>' % (GREEN, esc(t), k, tm))
    p.append('</g>')
    p.append('<rect x="48" y="155" width="9" height="19" fill="%s" opacity="0.9">'
             '<animate attributeName="opacity" values="0.9;0.9;0;0;0.9" keyTimes="0;0.4;0.5;0.9;1" '
             'dur="1.1s" repeatCount="indefinite"/></rect>' % GREEN)

    x = 48
    p.append('<g font-family="%s" font-size="12.5">' % MONO)
    for label, dot in chips:
        w = int(len(label) * 7.35) + (46 if dot else 38)
        p.append('<rect x="%d" y="212" width="%d" height="30" rx="15" fill="%s" stroke="%s"/>' % (x, w, PANEL, LINE))
        tx = x + 19
        if dot:
            p.append('<circle cx="%d" cy="227" r="4" fill="%s">'
                     '<animate attributeName="opacity" values="1;0.25;1" dur="2.2s" repeatCount="indefinite"/>'
                     '</circle>' % (x + 20, GREEN))
            tx = x + 32
        p.append('<text x="%d" y="231" fill="%s">%s</text>' % (tx, DIM, esc(label)))
        x += w + 10
    p.append('</g>')

    # right: request log
    p.append('<rect x="740" y="44" width="412" height="212" rx="10" fill="#0b0d10" stroke="%s"/>' % LINE2)
    p.append('<path d="M740 54a10 10 0 0 1 10-10h392a10 10 0 0 1 10 10v24H740z" fill="%s"/>' % PANEL)
    p.append('<line x1="740" y1="78" x2="1152" y2="78" stroke="%s"/>' % LINE2)
    for i, cx in enumerate((760, 776, 792)):
        p.append('<circle cx="%d" cy="61" r="4.5" fill="#3a434f"/>' % cx)
    p.append('<text x="814" y="65" font-family="%s" font-size="11.5" fill="#8b949e">no browser · no driver · just sockets</text>' % MONO)

    rows = [("POST", "/ajax/account/login", "200", 106, "0;0.10;0.85;0.95;1", "0;1;1;1;0"),
            ("GET", "/ajax/server", "200", 134, "0;0.16;0.26;0.95;1", "0;0;1;1;0"),
            ("WS", "/hermes", "101", 162, "0;0.32;0.42;0.95;1", "0;0;1;1;0"),
            ("TCP", "minecraft handshake", "0x00", 190, "0;0.48;0.58;0.95;1", "0;0;1;1;0"),
            ("·", "queue confirmed automatically", "", 218, "0;0.64;0.74;0.95;1", "0;0;1;1;0")]
    p.append('<g font-family="%s" font-size="12.5">' % MONO)
    for meth, path, code, y, kt, vals in rows:
        p.append('<g opacity="0"><animate attributeName="opacity" values="%s" keyTimes="%s" dur="7s" repeatCount="indefinite"/>' % (vals, kt))
        p.append('<text x="762" y="%d" fill="#6e7681">%s</text>' % (y, meth))
        colour = GREEN if not code else DIM
        p.append('<text x="806" y="%d" fill="%s">%s</text>' % (y, colour, esc(path)))
        if code:
            p.append('<text x="1128" y="%d" fill="%s" text-anchor="end">%s</text>' % (y, GREEN, code))
        p.append('</g>')
    p.append('</g>')
    p.append('<rect x="740" y="248" width="0" height="2" fill="url(#grn)">'
             '<animate attributeName="width" values="0;412;412;0" keyTimes="0;0.74;0.92;1" dur="7s" repeatCount="indefinite"/></rect>')
    p.append('</svg>')
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------------- stats

def build_stats(cc, repo_count, stars, busiest):
    cal = cc["contributionCalendar"]
    # A token that is not Berkay's own can only count public contributions.
    # In CI that is the case, so say "public" rather than quietly showing a
    # smaller number under a label that claims to be the total.
    hidden = cc.get("restrictedContributionsCount") or 0
    pub = " public" if hidden else ""
    note = "%d private not shown" % hidden if hidden else "last 12 months"
    items = [
        (cal["totalContributions"], "%scontributions" % (pub.strip() + " " if pub else ""), note),
        (cc["totalCommitContributions"], "commits", "authored"),
        (repo_count, "public repos", "all mine, no forks"),
        (stars, "stars earned", "across every repo"),
        (busiest, "busiest day", "commits in 24h"),
    ]
    W, H = 1200, 168
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="GitHub activity: %d contributions, %d commits, %d repositories, %d stars">'
         % (W, H, W, H, cal["totalContributions"], cc["totalCommitContributions"], repo_count, stars)]
    p += card(W, H, "ACTIVITY · REFRESHED AUTOMATICALLY BY GITHUB ACTIONS" + (" · PUBLIC ONLY" if hidden else ""))

    n = len(items)
    gap, x0 = 14, 40
    cw = (1120 - gap * (n - 1)) / n
    for i, (value, label, sub) in enumerate(items):
        x = x0 + i * (cw + gap)
        p.append('<rect x="%.1f" y="60" width="%.1f" height="82" rx="12" fill="%s" stroke="%s"/>' % (x, cw, PANEL, LINE2))
        p.append('<rect x="%.1f" y="60" width="%.1f" height="2" rx="1" fill="%s" opacity="0.55"/>' % (x + cw * 0.18, cw * 0.64, GREEN))
        p.append('<text x="%.1f" y="103" font-family="%s" font-size="30" font-weight="700" fill="%s" text-anchor="middle">%s</text>'
                 % (x + cw / 2, SANS, TEXT, value))
        p.append('<text x="%.1f" y="121" font-family="%s" font-size="11.5" fill="%s" text-anchor="middle">%s</text>'
                 % (x + cw / 2, MONO, GREEN, esc(label)))
        p.append('<text x="%.1f" y="135" font-family="%s" font-size="10" fill="%s" text-anchor="middle">%s</text>'
                 % (x + cw / 2, MONO, FAINT, esc(sub)))
    p.append('<rect x="-180" y="60" width="180" height="82" fill="url(#sheen)" opacity="0.9">'
             '<animate attributeName="x" values="-180;1200" dur="6s" repeatCount="indefinite"/></rect>')
    p.append('</svg>')
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------------- contributions

def build_contributions(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    created = u["createdAt"][:10]
    weeks = cal["weeks"]
    peak = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=0)

    CELL, GAP = 16, 4
    PITCH = CELL + GAP
    GX, GY = 78, 76
    W, H = 1200, 258

    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="Contribution calendar: %d contributions in the last year">'
         % (W, H, W, H, cal["totalContributions"])]
    hidden = u["contributionsCollection"].get("restrictedContributionsCount") or 0
    p += card(W, H, "CONTRIBUTIONS · %d%s IN THE LAST YEAR"
              % (cal["totalContributions"], " PUBLIC" if hidden else ""))

    # month labels
    seen = set()
    p.append('<g font-family="%s" font-size="10.5" fill="%s">' % (MONO, FAINT))
    for wi, w in enumerate(weeks):
        d0 = w["contributionDays"][0]["date"]
        mon = d0[:7]
        if mon not in seen and int(d0[8:10]) <= 7:
            seen.add(mon)
            label = datetime.strptime(d0, "%Y-%m-%d").strftime("%b")
            p.append('<text x="%d" y="66">%s</text>' % (GX + wi * PITCH, label))
    p.append('</g>')

    p.append('<g font-family="%s" font-size="10" fill="%s">' % (MONO, FAINT))
    for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append('<text x="66" y="%d" text-anchor="end">%s</text>' % (GY + wd * PITCH + 12, name))
    p.append('</g>')

    peak_xy = None
    p.append("<g>")
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            c, wd = d["contributionCount"], d["weekday"]
            x, y = GX + wi * PITCH, GY + wd * PITCH
            if d["date"] < created:
                fill = PRE_ACCOUNT                    # before the account existed
            elif c == 0:
                fill = HEAT[0]
            else:
                q = c / peak if peak else 0
                fill = HEAT[1] if q <= 0.25 else HEAT[2] if q <= 0.5 else HEAT[3] if q <= 0.75 else HEAT[4]
            p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s"><title>%s: %d</title></rect>'
                     % (x, y, CELL, CELL, fill, d["date"], c))
            if c == peak and peak and peak_xy is None:
                peak_xy = (x, y)
    p.append("</g>")

    if peak_xy:
        px, py = peak_xy
        p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="none" stroke="%s" stroke-width="2">'
                 '<animate attributeName="opacity" values="1;0.15;1" dur="2.4s" repeatCount="indefinite"/></rect>'
                 % (px - 2, py - 2, CELL + 4, CELL + 4, GREEN))

    gw = len(weeks) * PITCH
    p.append('<clipPath id="gridclip"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath>'
             % (GX, GY, gw, 7 * PITCH))
    p.append('<g clip-path="url(#gridclip)">'
             '<rect x="-150" y="%d" width="150" height="%d" fill="url(#sheen)" opacity="0.7">'
             '<animate attributeName="x" values="%d;%d" dur="7s" repeatCount="indefinite"/></rect></g>'
             % (GY, 7 * PITCH, GX - 150, GX + gw))

    ly = GY + 7 * PITCH + 22
    p.append('<text x="%d" y="%d" font-family="%s" font-size="10.5" fill="%s">Dimmed cells predate the account (created %s).</text>'
             % (GX, ly, MONO, FAINT, datetime.strptime(created, "%Y-%m-%d").strftime("%d %b %Y")))
    lx = GX + gw - 210
    p.append('<text x="%d" y="%d" font-family="%s" font-size="10.5" fill="%s">Less</text>' % (lx, ly, MONO, FAINT))
    for i, col in enumerate(HEAT):
        p.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (lx + 36 + i * 16, ly - 10, col))
    p.append('<text x="%d" y="%d" font-family="%s" font-size="10.5" fill="%s">More</text>' % (lx + 36 + len(HEAT) * 16 + 6, ly, MONO, FAINT))
    p.append('</svg>')
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------------- timeline

def build_timeline(repos):
    repos = sorted(repos, key=lambda r: r["createdAt"])
    d0 = datetime.strptime(repos[0]["createdAt"][:10], "%Y-%m-%d").date()
    d1 = datetime.strptime(repos[-1]["createdAt"][:10], "%Y-%m-%d").date()
    span = max((d1 - d0).days, 1)
    X0, X1 = 110, 1100
    W, H = 1200, 230

    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="Shipping log: %d public repositories over %d days">'
         % (W, H, W, H, len(repos), span)]
    p += card(W, H, "SHIPPING LOG · %d PUBLIC PROJECTS IN %d DAYS" % (len(repos), span))
    p.append('<defs><linearGradient id="ax" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="%s" stop-opacity="0.35"/>'
             '<stop offset="0.5" stop-color="%s" stop-opacity="0.9"/>'
             '<stop offset="1" stop-color="%s" stop-opacity="0.35"/></linearGradient></defs>' % (GREEN, GREEN, GREEN))
    p.append('<line x1="%d" y1="130" x2="%d" y2="130" stroke="%s" stroke-width="2"/>' % (X0, X1, LINE))
    p.append('<line x1="%d" y1="130" x2="%d" y2="130" stroke="url(#ax)" stroke-width="2"/>' % (X0, X1))

    newest = repos[-1]["name"]
    p.append('<g font-family="%s" font-size="11.5">' % MONO)
    for i, r in enumerate(repos):
        d = datetime.strptime(r["createdAt"][:10], "%Y-%m-%d").date()
        x = X0 + int((X1 - X0) * ((d - d0).days / span))
        up = (i % 2 == 0)
        lang = (r["primaryLanguage"] or {}).get("name") or "docs"
        col = LANG_COLORS.get(lang, "#8b949e")
        star = " · ★%d" % r["stargazerCount"] if r["stargazerCount"] else ""
        if up:
            p.append('<line x1="%d" y1="130" x2="%d" y2="90" stroke="%s"/>' % (x, x, LINE))
            p.append('<text x="%d" y="82" text-anchor="middle" fill="%s"%s>%s</text>'
                     % (x, TEXT if r["name"] == newest else DIM,
                        ' font-weight="600"' if r["name"] == newest else "", esc(r["name"])))
            p.append('<text x="%d" y="68" text-anchor="middle" fill="%s">%s%s</text>' % (x, FAINT, esc(lang), star))
        else:
            p.append('<line x1="%d" y1="130" x2="%d" y2="172" stroke="%s"/>' % (x, x, LINE))
            p.append('<text x="%d" y="188" text-anchor="middle" fill="%s"%s>%s</text>'
                     % (x, TEXT if r["name"] == newest else DIM,
                        ' font-weight="600"' if r["name"] == newest else "", esc(r["name"])))
            p.append('<text x="%d" y="202" text-anchor="middle" fill="%s">%s%s</text>' % (x, FAINT, esc(lang), star))
        p.append('<circle cx="%d" cy="130" r="5.5" fill="%s" stroke="%s" stroke-width="2.5"/>' % (x, BG, col))
        if r["name"] == newest:
            p.append('<circle cx="%d" cy="130" r="9" fill="%s" opacity="0.2">'
                     '<animate attributeName="r" values="7;15;7" dur="2.8s" repeatCount="indefinite"/>'
                     '<animate attributeName="opacity" values="0.3;0;0.3" dur="2.8s" repeatCount="indefinite"/></circle>' % (x, GREEN))
    p.append('</g>')
    p.append('<g font-family="%s" font-size="10.5" fill="%s">' % (MONO, FAINT))
    p.append('<text x="%d" y="152" text-anchor="start">%s</text>' % (X0 + 16, d0.strftime("%d %b")))
    p.append('<text x="%d" y="152" text-anchor="end">%s</text>' % (X1 - 16, d1.strftime("%d %b")))
    p.append('</g></svg>')
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------------- languages

def build_langs(repos):
    agg = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            agg[e["node"]["name"]] = agg.get(e["node"]["name"], 0) + e["size"]
    data = sorted(agg.items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in data) or 1

    W, H = 1200, 176
    X0, BW, Y, BH = 40, 1120, 70, 26
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'role="img" aria-label="Language distribution across public repositories">' % (W, H, W, H)]
    p += card(W, H, "LANGUAGES · MEASURED ACROSS PUBLIC REPOSITORIES · %d KB" % (total // 1024))
    p.append('<defs><clipPath id="barclip"><rect x="%d" y="%d" width="%d" height="%d" rx="13"/></clipPath></defs>'
             % (X0, Y, BW, BH))
    p.append('<g clip-path="url(#barclip)">')
    p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (X0, Y, BW, BH, PANEL))
    x = X0
    for name, size in data:
        w = BW * size / total
        p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s"/>'
                 % (x, Y, w, BH, LANG_COLORS.get(name, "#8b949e")))
        x += w
    x = X0
    for name, size in data[:-1]:
        x += BW * size / total
        p.append('<rect x="%.1f" y="%d" width="1.5" height="%d" fill="%s" opacity="0.55"/>' % (x, Y, BH, BG))
    p.append('<rect x="-260" y="%d" width="260" height="%d" fill="url(#sheen)">'
             '<animate attributeName="x" values="-260;1200" dur="4.5s" repeatCount="indefinite"/></rect>' % (Y, BH))
    p.append('</g>')
    p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="13" fill="none" stroke="%s"/>' % (X0, Y, BW, BH, LINE))

    lx = 40
    p.append('<g font-family="%s" font-size="11.5">' % MONO)
    for name, size in data:
        pct = 100.0 * size / total
        p.append('<circle cx="%d" cy="129" r="4.5" fill="%s"/>' % (lx + 5, LANG_COLORS.get(name, "#8b949e")))
        p.append('<text x="%d" y="133" fill="%s">%s</text>' % (lx + 18, DIM, esc(name)))
        p.append('<text x="%.0f" y="133" fill="%s">%.1f%%</text>' % (lx + 18 + len(name) * 7.1 + 8, FAINT, pct))
        lx += 18 + len(name) * 7.1 + 8 + len("%.1f%%" % pct) * 7.1 + 26
    p.append('</g>')
    p.append('<text x="40" y="160" font-family="%s" font-size="11" fill="%s">'
             'Go is in the toolkit but not represented here yet — nothing public in it so far.</text>' % (MONO, FAINT))
    p.append('</svg>')
    return "\n".join(p) + "\n"


def main():
    u = fetch()
    repos = [r for r in u["repositories"]["nodes"] if not r["isFork"]]
    projects = [r for r in repos if r["name"].lower() != USER.lower()]   # the profile repo is not a project
    stars = sum(r["stargazerCount"] for r in repos)
    cc = u["contributionsCollection"]
    peak = max((d["contributionCount"] for w in cc["contributionCalendar"]["weeks"]
                for d in w["contributionDays"]), default=0)

    files = {
        "header.svg": build_header(u, len(projects), stars),
        "stats.svg": build_stats(cc, len(repos), stars, peak),
        "contributions.svg": build_contributions(u),
        "timeline.svg": build_timeline(projects),
        "langs.svg": build_langs(repos),
    }
    os.makedirs(OUT, exist_ok=True)
    for name, body in files.items():
        path = os.path.join(OUT, name)
        old = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = f.read()
        if old != body:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            print("updated %s" % name)
        else:
            print("unchanged %s" % name)
    print("contributions=%d commits=%d repos=%d stars=%d peak=%d hidden=%d"
          % (cc["contributionCalendar"]["totalContributions"],
             cc["totalCommitContributions"], len(repos), stars, peak,
             cc.get("restrictedContributionsCount") or 0))


if __name__ == "__main__":
    main()
