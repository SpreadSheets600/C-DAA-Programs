#!/usr/bin/env python3

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
EXERCISES_OUT = DOCS / "exercises"
VITEPRESS = DOCS / ".vitepress"

REPO_BASE = "/C-DAA-Programs/"
GITHUB_REPO = "https://github.com/SpreadSheets600/C-DAA-Programs"
SITE_TITLE = "C-DAA Programs"
SITE_DESC = "Design and Analysis of Algorithms — Lab programs, algorithms, and annotated C code."

DATE_RE = re.compile(r"^\d{2}-\d{2}-\d{4}$")


def parse_date(folder):
    try:
        return datetime.strptime(folder, "%d-%m-%Y")
    except ValueError:
        return None


def pretty_date(folder):
    d = parse_date(folder)
    return d.strftime("%B %d, %Y") if d else folder


def vitepress_slug(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-{2,}", "-", text)
    return text


def parse_readme(path):
    text = path.read_text(encoding="utf-8")

    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else path.parent.name

    parts = re.split(r"^(##\s+Exercise\s+\d+\s*:.*)$", text, flags=re.M)

    exercises = []
    for i in range(1, len(parts), 2):
        ex_header = parts[i].strip()
        ex_body = parts[i + 1] if i + 1 < len(parts) else ""

        ex_title = re.sub(r"^##\s+", "", ex_header).strip()

        algo_m = re.search(
            r"###\s+Algorithm\s*:?\s*\n(.*?)(?=^###\s|\Z)",
            ex_body,
            re.M | re.S,
        )
        algorithm = algo_m.group(1).strip() if algo_m else ""

        code_m = re.search(r"```(cpp|c)\s*\n(.*?)```", ex_body, re.S)
        code = code_m.group(2).rstrip() if code_m else ""
        lang = code_m.group(1) if code_m else "c"

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


def parse_root_readme():
    path = ROOT / "README.md"
    if not path.exists():
        return SITE_TITLE, {}
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else SITE_TITLE
    topics = {}
    for m in re.finditer(r"\[.*?\]\(\./(\d{2}-\d{2}-\d{4})/.*?\)\s*\[([^\]]+)\]", text):
        topics[m.group(1)] = m.group(2).strip()
    return title, topics


def render_exercise_page(folder, data):
    title = data["title"]
    exs = data["exercises"]
    cpps = sorted(p.name for p in (ROOT / folder).glob("*.cpp"))

    L = []
    L += ["---", f'title: "{title}"', "---", "", f"# {title}", ""]

    for ex in exs:
        L += [f"## {ex['title']}", ""]

        if ex["algorithm"]:
            L += ["### Algorithm", "", ex["algorithm"], ""]

        if ex["code"]:
            L += ["### Code", "", f"```{ex['lang']}", ex["code"], "```", ""]

        if ex["output"]:
            L += ["### Output", "", "```bash", ex["output"], "```", ""]

        L += ["---", ""]

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
            "int main()  ->  void main()",
            "",
            "// Change return statement",
            "return 0;  ->  getch();",
            "```",
            ":::",
            "",
        ]

    return "\n".join(L)


def render_config(sessions):
    def sidebar_item(folder, data):
        date = pretty_date(folder)
        sub_lines = "\n".join(
            f'            {{ text: "{e["title"]}", link: "/exercises/{folder}#{e["slug"]}" }},'
            for e in data["exercises"]
        )
        return (
            f"        {{\n"
            f'          text: "{date}",\n'
            f'          link: "/exercises/{folder}",\n'
            f"          collapsed: false,\n"
            f"          items: [\n"
            f"{sub_lines}\n"
            f"          ],\n"
            f"        }}"
        )

    sidebar_str = ",\n".join(sidebar_item(f, d) for f, d in sessions)
    first_link = f"/exercises/{sessions[0][0]}" if sessions else "/"

    return (
        'import { defineConfig } from "vitepress";\n'
        "import {\n"
        "  transformerNotationHighlight,\n"
        "  transformerNotationFocus,\n"
        "  transformerNotationDiff,\n"
        '} from "@shikijs/transformers";\n'
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
        "  cleanUrls: true,\n"
        "\n"
        "  markdown: {\n"
        "    theme: {\n"
        '      light: "one-dark-pro",\n'
        '      dark:  "one-dark-pro",\n'
        "    },\n"
        "    lineNumbers: true,\n"
        "    codeTransformers: [\n"
        '      transformerNotationHighlight({ matchAlgorithm: "v3" }),\n'
        '      transformerNotationFocus({ matchAlgorithm: "v3" }),\n'
        '      transformerNotationDiff({ matchAlgorithm: "v3" }),\n'
        "    ],\n"
        "  },\n"
        "\n"
        "  themeConfig: {\n"
        '    logo: { src: "/favicon.svg", alt: "DAA" },\n'
        "\n"
        "    nav: [\n"
        '      { text: "Home", link: "/" },\n'
        f'      {{ text: "Exercises", link: "{first_link}" }},\n'
        f'      {{ text: "GitHub", link: "{GITHUB_REPO}" }},\n'
        "    ],\n"
        "\n"
        "    sidebar: [\n"
        "      {\n"
        '        text: "Exercises",\n'
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
        '      message: "Design & Analysis of Algorithms — Lab Programs",\n'
        '      copyright: "Built with VitePress · SpreadSheets600",\n'
        "    },\n"
        "\n"
        "    editLink: {\n"
        f'      pattern: "{GITHUB_REPO}/edit/main/docs/:path",\n'
        '      text: "Edit this page on GitHub",\n'
        "    },\n"
        "\n"
        '    outline: { level: [2, 3], label: "On this page" },\n'
        "\n"
        "    docFooter: {\n"
        '      prev: "Previous",\n'
        '      next: "Next",\n'
        "    },\n"
        "  },\n"
        "});\n"
    )


def render_index(sessions):
    title, topics = parse_root_readme()

    rows = "\n".join(
        f"| [{pretty_date(f)}](./exercises/{f}) | {topics.get(f, '')} |"
        for f, d in sessions
    )

    return (
        "---\n"
        f"title: {title}\n"
        "---\n"
        "\n"
        f"# {title}\n"
        "\n"
        "| Date | Topic |\n"
        "|------|-------|\n"
        f"{rows}\n"
    )


def main():
    folders = sorted(
        [
            d.name
            for d in ROOT.iterdir()
            if d.is_dir() and DATE_RE.match(d.name) and (d / "README.md").exists()
        ],
        key=lambda n: parse_date(n) or datetime.min,
    )

    if not folders:
        print("No exercise folders found.")
        sys.exit(0)

    EXERCISES_OUT.mkdir(parents=True, exist_ok=True)
    VITEPRESS.mkdir(parents=True, exist_ok=True)

    sessions = []
    for folder in folders:
        data = parse_readme(ROOT / folder / "README.md")
        sessions.append((folder, data))

        out = EXERCISES_OUT / f"{folder}.md"
        out.write_text(render_exercise_page(folder, data), encoding="utf-8")
        print(f"generated  {out.relative_to(ROOT)}")

    cfg_path = VITEPRESS / "config.mjs"
    cfg_path.write_text(render_config(sessions), encoding="utf-8")
    print(f"generated  {cfg_path.relative_to(ROOT)}")

    idx_path = DOCS / "index.md"
    idx_path.write_text(render_index(sessions), encoding="utf-8")
    print(f"generated  {idx_path.relative_to(ROOT)}")

    print(f"done — {len(sessions)} folder(s) processed.")


if __name__ == "__main__":
    main()
