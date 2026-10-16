"""Regenerate the "Amazing Lectures about Technology" table in README.md.

The catalogue lives in scripts/catalog.json. New YouTube links posted to the
Discord channel since `last_synced` are fetched, titled via YouTube oEmbed,
auto-categorised by keyword, appended to the catalogue and rendered into the
README between the catalog:start / catalog:end markers.

Usage:
    python scripts/update_catalog.py init                 # one-off: build catalog.json from README
    DISCORD_TOKEN=... python scripts/update_catalog.py sync [--channel NAME]
    python scripts/update_catalog.py sync --export messages.json
    python scripts/update_catalog.py render               # README from catalog.json only

`sync` also renders. Edit catalog.json by hand to fix a category or title,
then run `render`. Delete a video's entry and add its id to "ignored" to keep
it out permanently.
"""
import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CATALOG = Path(__file__).resolve().parent / "catalog.json"
START, END = "<!-- catalog:start -->", "<!-- catalog:end -->"
COLUMNS = 3
FALLBACK = "Miscellaneous"

YT_URL = re.compile(
    r"https?://(?:www\.|m\.)?(?:youtu\.be/|youtube\.com/(?:watch\?\S*?v=|shorts/|live/|embed/))"
    r"([A-Za-z0-9_-]{11})\S*"
)

# First matching category wins, so order matters: specific before general.
# Keywords are matched as whole words against "channel title", lowercased.
RULES = {
    "Space": [
        "spacex", "starship", "nasa", "jwst", "webb", "telescope", "galaxy", "galaxies",
        "planets", "mars", "lunar", "orbit", "orbital", "astronaut", "black hole", "universe",
        "cosmic", "cosmology", "solar system", "asteroid", "scott manley", "dr becky",
        "satellite", "everyday astronaut", "space travel", "eclipse", "gravitational",
    ],
    "Cybersecurity": [
        "hack", "hacker", "hacking", "exploit", "vulnerability", "malware", "security", "cve",
        "backdoor", "ransomware", "zero-day", "0day", "liveoverflow", "low level learning", "pwn",
        "reverse engineering", "xz", "jailbreak",
    ],
    "Artifical Intelligence": [
        "ai", "a.i.", "gpt", "chatgpt", "llm", "llms", "neural", "machine learning", "deep learning",
        "transformer", "transformers", "openai", "anthropic", "claude", "deepmind", "alphago",
        "alphafold", "agi", "diffusion", "reinforcement learning", "3blue1brown", "two minute papers",
        "karpathy", "gemini", "agent", "agents",
    ],
    "Computing Hardware": [
        "cpu", "gpu", "chip", "chips", "transistor", "transistors", "silicon", "semiconductor",
        "tsmc", "intel", "amd", "nvidia", "asml", "lithography", "jim keller", "risc-v", "arm",
        "fpga", "hardware", "asianometry", "high yield", "branch education",
    ],
    "High Performance Computing": [
        "performance", "optimization", "optimisation", "optimizing", "simd", "cache", "cppcon",
        "c++", "molly rocket", "mollyrocket", "casey muratori", "jonathan blow", "johnathan blow",
        "compiler", "compilers", "assembly", "zig", "jai", "latency", "fps",
        "multithreading", "parallel", "data oriented", "jonathan blow", "cppcon",
    ],
    "Simulation Science": [
        "simulation", "simulating", "simulate", "physics", "fluid", "particle", "particles",
        "sebastian lague", "procedural", "erosion", "cellular automata", "ray tracing", "raytracing",
        "rendering", "shader", "shaders", "voxel", "voxels",
    ],
    "Science & Engineering": [
        "electronics", "engine", "airplane", "aircraft", "radio", "physics", "maglev", "steve mould",
        "electroboom", "thought emporium", "math", "maths", "mathematics", "fractal", "fractals",
    ],
    "Corporate Secrets": [
        "outage", "went down", "scaled", "scale", "cloud", "pricing",
        "company", "companies", "business", "ceo", "billion", "startup", "industry", "market",
        "economy", "economics", "bankrupt", "monopoly", "corporate", "corporation",
    ],
    "Computer Science": [
        "algorithm", "algorithms", "programming", "programmer", "code", "coding", "software",
        "computer science", "data structure", "linux", "rust", "go", "golang", "c++", "c",
        "operating system", "kernel", "database", "network", "internet", "computerphile",
    ],
    "Fun Projects": [
        "i built", "i made", "building", "made a", "built a", "project", "minecraft", "factorio",
        "game", "games", "redstone", "diy", "robot",
    ],
}


def keyword_pattern(words):
    return re.compile(r"(?<![\w])(?:" + "|".join(re.escape(w) for w in words) + r")(?![\w])")


RULE_PATTERNS = {cat: keyword_pattern(words) for cat, words in RULES.items()}


def categorise(author, title, videos):
    """Reuse the category this channel is most often filed under, else match keywords."""
    previous = [v["category"] for v in videos if v["title"].split(" - ", 1)[0].lower() == author.lower()]
    if previous:
        return max(set(previous), key=previous.count)
    text = f"{author} {title}".lower()
    for cat, pattern in RULE_PATTERNS.items():
        if pattern.search(text):
            return cat
    return FALLBACK


def parse_url(url):
    """Return (video_id, start_seconds) for a YouTube URL, or None."""
    m = YT_URL.match(url)
    if not m:
        return None
    query = urllib.parse.parse_qs(urllib.parse.urlparse(m.group(0)).query)
    t = query.get("t", [None])[0]
    seconds = None
    if t:
        parts = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s?)?", t)
        if parts and any(parts.groups()):
            h, mi, s = (int(x or 0) for x in parts.groups())
            seconds = h * 3600 + mi * 60 + s
    return m.group(1), seconds


def load_catalog():
    return json.loads(CATALOG.read_text())


def save_catalog(cat):
    CATALOG.write_text(json.dumps(cat, indent=2, ensure_ascii=False) + "\n")


# ---------- init: bootstrap catalog.json from the existing README ----------

def cmd_init(_args):
    if CATALOG.exists():
        sys.exit(f"{CATALOG} already exists; delete it first to re-import from README.")
    lines = README.read_text().splitlines()
    categories, videos, category, titles = [], [], None, None
    for line in lines:
        if "<h2>" in line and line.startswith("|"):
            category = re.search(r"<h2>(.*?)</h2>", line).group(1)
            categories.append(category)
        elif "<h4>" in line and line.startswith("|"):
            titles = [html.unescape(t) for t in re.findall(r"<h4>(.*?)</h4>", line)]
        elif titles is not None and "<a href=" in line:
            urls = re.findall(r'<a href="([^"]+)">', line)
            for title, url in zip(titles, urls):
                vid, t = parse_url(url)
                videos.append({"id": vid, "t": t, "title": title, "category": category})
            titles = None
    save_catalog({
        "last_synced": "2023-09-08T00:00:00+00:00",
        "categories": categories,
        "videos": videos,
        "ignored": [],
    })
    print(f"Imported {len(videos)} videos in {len(categories)} categories into {CATALOG}")


# ---------- sync: pull new videos from Discord ----------

def fetch_discord_messages(channel_name):
    import asyncio
    import os

    import discord

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        sys.exit("Set DISCORD_TOKEN, or pass --export with a JSON export of the channel.")
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    result = []

    @client.event
    async def on_ready():
        try:
            channels = [c for g in client.guilds for c in g.text_channels if c.name == channel_name]
            if not channels:
                print(f"Bot can't see a channel named #{channel_name}", file=sys.stderr)
                return
            async for m in channels[0].history(limit=None, oldest_first=True):
                result.append({"time": m.created_at.isoformat(), "content": m.content})
        finally:
            await client.close()

    asyncio.run(client.start(token))
    if not result:
        sys.exit("No messages fetched.")
    return result


def oembed(video_id):
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(
        f"https://www.youtube.com/watch?v={video_id}"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.load(resp)
    except Exception:
        return None  # private, deleted or age-restricted


def cmd_sync(args):
    cat = load_catalog()
    if args.export:
        messages = json.loads(Path(args.export).read_text())
    else:
        messages = fetch_discord_messages(args.channel)

    known = {v["id"] for v in cat["videos"]} | set(cat["ignored"])
    since = cat["last_synced"]
    new = {}
    for m in sorted(messages, key=lambda m: m["time"]):
        if m["time"] <= since:
            continue
        for url in re.findall(r"https?://\S+", m["content"]):
            parsed = parse_url(url.rstrip(">)"))
            if parsed and parsed[0] not in known and parsed[0] not in new:
                new[parsed[0]] = (parsed[1], m["time"])

    print(f"{len(new)} new videos posted since {since}")
    unavailable = []
    for i, (vid, (t, posted)) in enumerate(new.items(), 1):
        meta = oembed(vid)
        if not meta:
            unavailable.append(vid)
            continue
        author, title = meta["author_name"].strip(), meta["title"].strip()
        category = categorise(author, title, cat["videos"])
        cat["videos"].append({
            "id": vid, "t": t, "title": f"{author} - {title}", "category": category, "posted": posted,
        })
        print(f"  [{i}/{len(new)}] {category:<28} {author} - {title}")

    if unavailable:
        print(f"Skipped {len(unavailable)} unavailable videos: {', '.join(unavailable)}")
        cat["ignored"].extend(unavailable)
    if FALLBACK in {v["category"] for v in cat["videos"]} and FALLBACK not in cat["categories"]:
        cat["categories"].append(FALLBACK)
    if messages:
        cat["last_synced"] = max(m["time"] for m in messages)
    save_catalog(cat)
    cmd_render(args)


# ---------- render: write the README table ----------

def cell_title(title):
    return f"<h4>{html.escape(title, quote=False).replace('|', '&#124;')}</h4>"


def cell_link(video):
    url = f"https://youtu.be/{video['id']}" + (f"?t={video['t']}" if video.get("t") else "")
    return f'<a href="{url}"><img src="https://img.youtube.com/vi/{video["id"]}/0.jpg"/></a>'


def row(cells):
    cells = cells + [""] * (COLUMNS - len(cells))
    return "| " + " | ".join(cells) + " |"


def slug(name):
    return re.sub(r"[^a-z0-9 -]", "", name.lower()).replace(" ", "-")


def render_section(cat):
    by_cat = {c: [] for c in cat["categories"]}
    for v in cat["videos"]:
        by_cat.setdefault(v["category"], []).append(v)
    used = [c for c, vids in by_cat.items() if vids]

    out = ["## Contents"]
    out += [f"- [{c}](#{slug(c)})" for c in used]
    out += ["", "", "| " * COLUMNS + "|", "| - " * COLUMNS + "|"]
    for c in used:
        out.append(row([f"<h2>{c}</h2>"]).replace("|  |  |", "| | |"))
        vids = by_cat[c]
        for i in range(0, len(vids), COLUMNS):
            chunk = vids[i:i + COLUMNS]
            out.append(row([cell_title(v["title"]) for v in chunk]))
            out.append(row([cell_link(v) for v in chunk]))
    return "\n".join(out)


def cmd_render(_args):
    cat = load_catalog()
    text = README.read_text()
    if START not in text:
        # First run: wrap the existing hand-written section in markers.
        begin = text.index("## Contents")
        end = text.index("</details>", begin)
        text = text[:begin] + START + "\n" + text[begin:end].rstrip("\n") + "\n" + END + "\n" + text[end:]
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    text = before + START + "\n" + render_section(cat) + "\n" + END + after
    text = re.sub(
        r"\(Updated [^)]*\)",
        lambda _: f"(Updated {ordinal_date(datetime.now(timezone.utc))})",
        text,
        count=1,
    )
    README.write_text(text)
    print(f"Rendered {len(cat['videos'])} videos into {README.name}")


def ordinal_date(d):
    day = d.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix} {d:%B %Y}"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(func=cmd_init)
    s = sub.add_parser("sync")
    s.add_argument("--channel", default="interesting-resources")
    s.add_argument("--export", help="Use a JSON export of the channel instead of fetching live")
    s.set_defaults(func=cmd_sync)
    sub.add_parser("render").set_defaults(func=cmd_render)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
