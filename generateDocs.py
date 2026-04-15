#!/usr/bin/env python3
"""
generateDocs.py
---------------
Scans every session folder (DD-MM-YYYY), parses its README.md,
and auto-generates the full VitePress documentation:

  docs/sessions/<date>.md     — one page per session
  docs/.vitepress/config.mjs  — sidebar + nav (rebuilt from all sessions)
  docs/index.md               — home page with feature cards + session table

Run locally:
  python generateDocs.py

CI/CD (GitHub Actions):
  Called automatically before `npm run docs:build` on every push to main.
  The three generated paths above are git-ignored; they are always rebuilt
  fresh from the source-of-truth README files.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

# ── Project constants ──────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
SESSIONS_OUT = DOCS / "sessions"
VITEPRESS = DOCS / ".vitepress"

REPO_BASE = "/C-DAA-Programs/"
GITHUB_REPO = "https://github.com/SpreadSheets600/C-DAA-Programs"
SITE_TITLE = "C · DAA Programs"
SITE_DESC = (
    "Design and Analysis of Algorithms — "
    "Lab programs, algorithms, and annotated C code."
)

# ── Helpers ────────────────────────────────────────────────────────────────────

DATE_RE = re.compile(r"^\d{2}-\d{2}-\d{4}$")


def parse_date(folder):
    """Parse a DD-MM-YYYY folder name → datetime, or None on failure."""
    try:
        return datetime.strptime(folder, "%d-%m-%Y")
    except ValueError:
        return None


def pretty_date(folder):
    """'10-04-2026'  →  'April 10, 2026'"""
    d = parse_date(folder)
    return d.strftime("%B %d, %Y") if d else folder


def vitepress_slug(text):
    """
    Reproduce the VitePress / GitHub heading-anchor algorithm so that
    sidebar deep-links actually point to the right section.

      'Exercise 1 : Binary Search With Iteration'
        → 'exercise-1-binary-search-with-iteration'
    """
    text = re.sub(r"<[^>]+>", "", text)  # strip HTML tags
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)  # drop punctuation
    text = re.sub(r"\s+", "-", text.strip())  # spaces → hyphens
    text = re.sub(r"-{2,}", "-", text)  # collapse double hyphens
    return text


# ── README parser ──────────────────────────────────────────────────────────────


def parse_readme(path):
    """
    Parse a session README.md into structured data.

    Returns
    -------
    {
      "title": str,
      "exercises": [
        {
          "title":     str,   # e.g. "Exercise 1 : Binary Search With Iteration"
          "slug":      str,   # VitePress anchor slug
          "algorithm": str,   # raw markdown (numbered list, bold, code ticks…)
          "code":      str,   # source code, no fences
          "lang":      str,   # "c" or "cpp"
          "output":    str,   # expected output, no fences
        },
        …
      ]
    }
    """
    text = path.read_text(encoding="utf-8")

    # ── Page title (# …) ──────────────────────────────────────────────────────
    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else path.parent.name

    # ── Split into exercise blocks on "## Exercise N : …" headings ────────────
    parts = re.split(r"^(##\s+Exercise\s+\d+\s*:.*)$", text, flags=re.M)
    # parts layout: [intro, heading1, body1, heading2, body2, …]

    exercises = []
    for i in range(1, len(parts), 2):
        ex_header = parts[i].strip()
        ex_body = parts[i + 1] if i + 1 < len(parts) else ""

        # Title = everything after the leading "## "
        ex_title = re.sub(r"^##\s+", "", ex_header).strip()

        # ── Algorithm block ───────────────────────────────────────────────────
        algo_m = re.search(
            r"###\s+Algorithm\s*:?\s*\n(.*?)(?=^###\s|\Z)",
            ex_body,
            re.M | re.S,
        )
        algorithm = algo_m.group(1).strip() if algo_m else ""

        # ── Code block (```cpp … ``` or ```c … ```) ───────────────────────────
        code_m = re.search(r"```(cpp|c)\s*\n(.*?)```", ex_body, re.S)
        code = code_m.group(2).rstrip() if code_m else ""
        lang = code_m.group(1) if code_m else "c"

        # ── Output block (```bash … ```) ──────────────────────────────────────
        out_m = re.search(r"```bash\s*\n(.*?)```", ex_body, re.S)
        output = out_m.group(1).rstrip() if out_m else ""

        exercises.append(
            {
                "title": ex_title,
                "slug": vitepress_slug(ex_title),
                "algorithm": algorithm,
                "code": code,
                "lang": lang,
                "output": output,
            }
        )

    return {"title": title, "exercises": exercises}


# ── Page renderers ─────────────────────────────────────────────────────────────


def render_session_page(folder, data):
    """
    Generate a complete VitePress Markdown page for one session.
    """
    date = pretty_date(folder)
    exs = data["exercises"]
    cpps = sorted(p.name for p in (ROOT / folder).glob("*.cpp"))
    topics = " · ".join(e["title"] for e in exs)

    L = []

    # ── Front matter ──────────────────────────────────────────────────────────
    L += [
        "---",
        f'title: "{date}"',
        f'description: "Lab exercises for {date} — {topics}"',
        "---",
        "",
    ]

    # ── Page title + overview ─────────────────────────────────────────────────
    L += [
        f"# {date}",
        "",
        "::: info Session Overview",
        topics,
        ":::",
        "",
        "---",
        "",
    ]

    # ── One section per exercise ──────────────────────────────────────────────
    for ex in exs:
        L += [f"## {ex['title']}", ""]

        if ex["algorithm"]:
            L += ["### Algorithm", "", ex["algorithm"], ""]

        if ex["code"]:
            L += [
                "### Code",
                "",
                f"```{ex['lang']}",
                ex["code"],
                "```",
                "",
            ]

        if ex["output"]:
            L += [
                "### Output",
                "",
                "```bash",
                ex["output"],
                "```",
                "",
            ]

        L += ["---", ""]

    # ── Compile & Run ─────────────────────────────────────────────────────────
    if cpps:
        L += ["## Compile & Run", "", "```bash"]
        for f in cpps:
            stem = Path(f).stem
            L.append(f"gcc {f} -o {stem} && ./{stem}")
        L += [
            "```",
            "",
            "::: details Turbo C++ Compatibility",
            "```c",
            "// Change function signature",
            "int main()  →  void main()",
            "",
            "// Change return statement",
            "return 0;  →  getch();",
            "```",
            ":::",
            "",
        ]

    return "\n".join(L)


def render_config(sessions):
    """
    Generate docs/.vitepress/config.mjs from all discovered sessions.
    `sessions` is a list of (folder_name, parsed_data) tuples.
    """

    def sidebar_item(folder, data):
        date = pretty_date(folder)
        sub_lines = "\n".join(
            f'            {{ text: "{e["title"]}", '
            f'link: "/sessions/{folder}#{e["slug"]}" }},'
            for e in data["exercises"]
        )
        return (
            f"        {{\n"
            f'          text: "{date}",\n'
            f'          link: "/sessions/{folder}",\n'
            f"          collapsed: false,\n"
            f"          items: [\n"
            f"{sub_lines}\n"
            f"          ],\n"
            f"        }}"
        )

    sidebar_str = ",\n".join(sidebar_item(f, d) for f, d in sessions)
    first_link = f"/sessions/{sessions[0][0]}" if sessions else "/"

    return (
        'import { defineConfig } from "vitepress";\n'
        "\n"
        "export default defineConfig({\n"
        f'  base: "{REPO_BASE}",\n'
        "\n"
        f'  title: "{SITE_TITLE}",\n'
        f'  description: "{SITE_DESC}",\n'
        "\n"
        "  head: [\n"
        f'    ["link", {{ rel: "icon", href: "{REPO_BASE}favicon.svg" }}],\n'
        '    ["meta", { name: "theme-color", content: "#7c3aed" }],\n'
        "  ],\n"
        "\n"
        "  lastUpdated: true,\n"
        "  cleanUrls:   true,\n"
        "\n"
        "  markdown: {\n"
        "    theme: {\n"
        '      light: "one-dark-pro",\n'
        '      dark:  "one-dark-pro",\n'
        "    },\n"
        "    lineNumbers: true,\n"
        "  },\n"
        "\n"
        "  themeConfig: {\n"
        '    logo: { src: "/favicon.svg", alt: "DAA" },\n'
        "\n"
        "    nav: [\n"
        '      { text: "Home",     link: "/" },\n'
        f'      {{ text: "Sessions", link: "{first_link}" }},\n'
        f'      {{ text: "GitHub",   link: "{GITHUB_REPO}" }},\n'
        "    ],\n"
        "\n"
        "    sidebar: [\n"
        "      {\n"
        '        text: "📁 Sessions",\n'
        "        items: [\n"
        f"{sidebar_str}\n"
        "        ],\n"
        "      },\n"
        "    ],\n"
        "\n"
        f'    socialLinks: [{{ icon: "github", link: "{GITHUB_REPO}" }}],\n'
        "\n"
        '    search: { provider: "local" },\n'
        "\n"
        "    footer: {\n"
        '      message:   "Design & Analysis of Algorithms — Lab Programs",\n'
        '      copyright: "Built with VitePress · SpreadSheets600",\n'
        "    },\n"
        "\n"
        "    editLink: {\n"
        f'      pattern: "{GITHUB_REPO}/edit/main/docs/:path",\n'
        '      text:    "Edit this page on GitHub",\n'
        "    },\n"
        "\n"
        '    outline:   { level: [2, 3], label: "On this page" },\n'
        "\n"
        "    docFooter: {\n"
        '      prev: "← Previous Session",\n'
        '      next: "Next Session →",\n'
        "    },\n"
        "  },\n"
        "});\n"
    )


def render_index(sessions):
    """
    Generate docs/index.md — the VitePress home page.
    `sessions` is a list of (folder_name, parsed_data) tuples.
    """
    first = sessions[0][0] if sessions else ""

    rows = "\n".join(
        "| [{date}](./sessions/{folder}) | {topics} |".format(
            date=pretty_date(f),
            folder=f,
            topics=" · ".join(e["title"] for e in d["exercises"]),
        )
        for f, d in sessions
    )

    # The doubled {{ / }} are literal braces inside the f-string for the
    # <style> block — they are NOT Python format placeholders.
    return f"""\
---
layout: home

hero:
  name: "C-DAA"
  text: "Design & Analysis of Algorithms"
  tagline: Lab programs, step-by-step algorithms, and annotated C code — organized by session date.
  image:
    src: /logo.svg
    alt: C-DAA Programs
  actions:
    - theme: brand
      text: Browse Sessions →
      link: /sessions/{first}
    - theme: alt
      text: View on GitHub
      link: {GITHUB_REPO}

features:
  - icon: 🗂️
    title: Session-Based Organization
    details: Every lab session lives in its own dated folder — easy to navigate, easy to reference during exams.

  - icon: 🔍
    title: Algorithm Walkthroughs
    details: Each exercise includes a plain-English algorithm before the code so you understand the logic, not just the syntax.

  - icon: 💡
    title: Annotated C Code
    details: One Dark Pro syntax highlighting with line numbers — easy to read, easy to review.

  - icon: ⚡
    title: GCC & Turbo C++ Ready
    details: All programs compile under GCC. Turbo C++ compatibility notes are included on every session page.
---

<style>
:root {{
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(135deg, #41d1ff 0%, #bd34fe 100%);
  --vp-home-hero-image-background-image: linear-gradient(135deg, #41d1ff22 0%, #bd34fe22 100%);
  --vp-home-hero-image-filter: blur(44px);
}}
</style>

## Sessions

| Date | Topics Covered |
|------|----------------|
{rows}
"""


# ── Entry point ────────────────────────────────────────────────────────────────


def main():
    print("\n  C-DAA · generateDocs.py")
    print("  " + "─" * 40)

    # ── Discover session folders ───────────────────────────────────────────────
    folders = sorted(
        [
            d.name
            for d in ROOT.iterdir()
            if d.is_dir() and DATE_RE.match(d.name) and (d / "README.md").exists()
        ],
        key=lambda n: parse_date(n) or datetime.min,
    )

    if not folders:
        print(
            "\n  ⚠  No session folders found.\n"
            "     Expected directories named DD-MM-YYYY containing a README.md.\n"
        )
        sys.exit(0)

    # ── Ensure output directories exist ───────────────────────────────────────
    SESSIONS_OUT.mkdir(parents=True, exist_ok=True)
    VITEPRESS.mkdir(parents=True, exist_ok=True)

    # ── Parse + generate one page per session ─────────────────────────────────
    sessions = []
    for folder in folders:
        data = parse_readme(ROOT / folder / "README.md")
        sessions.append((folder, data))

        out = SESSIONS_OUT / f"{folder}.md"
        out.write_text(render_session_page(folder, data), encoding="utf-8")
        print(f"  ✅  {out.relative_to(ROOT)}")

    # ── Generate VitePress config ──────────────────────────────────────────────
    cfg_path = VITEPRESS / "config.mjs"
    cfg_path.write_text(render_config(sessions), encoding="utf-8")
    print(f"  ✅  {cfg_path.relative_to(ROOT)}")

    # ── Generate home page ─────────────────────────────────────────────────────
    idx_path = DOCS / "index.md"
    idx_path.write_text(render_index(sessions), encoding="utf-8")
    print(f"  ✅  {idx_path.relative_to(ROOT)}")

    n = len(sessions)
    print(f"\n  🚀  Done — generated docs for {n} session{'s' if n != 1 else ''}.\n")


if __name__ == "__main__":
    main()
