import html
import json
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
SITE_URL = f"https://spreadsheets600.github.io{REPO_BASE}"
SITE_TITLE = "C-DAA Programs"
SITE_DESC = "Design And Analysis Of Algorithms lab programs, notes, and reference implementations."

DATE_RE = re.compile(r"^\d{2}-\d{2}-\d{4}$")
SOURCE_EXTENSIONS = (".c", ".cc", ".cpp", ".cxx")


def parse_date(folder):
    try:
        return datetime.strptime(folder, "%d-%m-%Y")
    except ValueError:
        return None


def pretty_date(folder):
    parsed = parse_date(folder)
    return parsed.strftime("%B %d, %Y") if parsed else folder


def vitepress_slug(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-{2,}", "-", text)
    return text


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def normalize_code(text):
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def compile_command(path):
    compiler = "gcc" if path.suffix == ".c" else "g++"
    stem = path.stem
    return f"{compiler} {path.name} -o {stem} && ./{stem}"


def github_blob(path):
    return f"{GITHUB_REPO}/blob/main/{path.as_posix()}"


def github_tree(path):
    return f"{GITHUB_REPO}/tree/main/{path.as_posix()}"


def site_page(path=""):
    clean_path = path.lstrip("/")
    return f"{SITE_URL}{clean_path}"


def extract_section(body, heading):
    match = re.search(
        rf"^###\s+{heading}\s*:?\s*\n(.*?)(?=^###\s|\Z)",
        body,
        re.M | re.S,
    )
    return match.group(1).strip() if match else ""


def clean_exercise_title(title):
    return re.sub(r"^Exercise\s+\d+\s*:\s*", "", title, flags=re.I).strip()


def infer_topic(exercises):
    stems = []
    for ex in exercises:
        title = clean_exercise_title(ex["title"])
        stem = re.split(r"\bwith\b", title, maxsplit=1, flags=re.I)[0].strip(" :-")
        stem = re.sub(r"\s{2,}", " ", stem)
        if stem and stem not in stems:
            stems.append(stem)

    if not stems:
        return "Algorithms Practice"
    if len(stems) == 1:
        return stems[0]
    return ", ".join(stems[:2])


def summary_text(exercises):
    titles = [clean_exercise_title(ex["title"]) for ex in exercises]
    if not titles:
        return "Session notes and reference implementations."
    if len(titles) == 1:
        return titles[0]
    if len(titles) == 2:
        return f"{titles[0]} and {titles[1]}"
    return f"{titles[0]}, {titles[1]}, and {len(titles) - 2} more"


def find_source_files(folder):
    session_dir = ROOT / folder
    return sorted(
        [
            path
            for path in session_dir.iterdir()
            if path.is_file() and path.suffix in SOURCE_EXTENSIONS
        ],
        key=lambda path: path.name.lower(),
    )


def match_source_files(folder, exercises):
    source_files = find_source_files(folder)
    by_code = {}

    for path in source_files:
        content = normalize_code(path.read_text(encoding="utf-8"))
        if content:
            by_code.setdefault(content, []).append(path)

    used = set()
    matched = []

    for index, exercise in enumerate(exercises):
        path = None
        code = normalize_code(exercise["code"])

        if code and code in by_code:
            for candidate in by_code[code]:
                if candidate not in used:
                    path = candidate
                    break

        if path is None and index < len(source_files):
            candidate = source_files[index]
            if candidate not in used:
                path = candidate

        if path is not None:
            used.add(path)

        matched.append(path)

    return matched, source_files


def parse_readme(path):
    text = path.read_text(encoding="utf-8")

    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else path.parent.name

    parts = re.split(r"^(##\s+Exercise\s+\d+\s*:.*)$", text, flags=re.M)
    exercises = []

    for index in range(1, len(parts), 2):
        header = parts[index].strip()
        body = parts[index + 1] if index + 1 < len(parts) else ""
        code_match = re.search(r"```(cpp|c)\s*\n(.*?)```", body, re.S)
        output_match = re.search(r"```bash\s*\n(.*?)```", body, re.S)

        exercise = {
            "title": re.sub(r"^##\s+", "", header).strip(),
            "slug": vitepress_slug(header),
            "algorithm": extract_section(body, "Algorithm"),
            "code": code_match.group(2).rstrip() if code_match else "",
            "lang": code_match.group(1) if code_match else "c",
            "output": output_match.group(1).rstrip() if output_match else "",
        }
        exercises.append(exercise)

    matched_sources, source_files = match_source_files(path.parent.name, exercises)
    for exercise, source_file in zip(exercises, matched_sources):
        if source_file is None:
            continue
        exercise["source_file"] = source_file.name
        exercise["source_link"] = github_blob(source_file.relative_to(ROOT))
        exercise["compile_command"] = compile_command(source_file)

    return {
        "title": title,
        "topic": infer_topic(exercises),
        "summary": summary_text(exercises),
        "exercises": exercises,
        "source_files": source_files,
        "source_readme_link": github_blob(path.relative_to(ROOT)),
        "source_folder_link": github_tree(path.parent.relative_to(ROOT)),
    }


def render_readme(sessions):
    total_exercises = sum(len(data["exercises"]) for _, data in sessions)
    total_files = sum(len(data["source_files"]) for _, data in sessions)

    session_rows = "\n".join(
        (
            f"| {pretty_date(folder)} | {data['topic']} | {len(data['exercises'])} | "
            f"[Session README](./{folder}/README.md) | [Docs Page]({site_page(f'exercises/{folder}')}) |"
        )
        for folder, data in sessions
    )

    return (
        f"# {SITE_TITLE}\n\n"
        "> This README is generated by `generateDocs.py`. Add or update dated lab folders, "
        "then run `npm run docs:sync`.\n\n"
        "A clean archive of Design and Analysis of Algorithms lab work for:\n"
        "- quick revision before exams\n"
        "- copying algorithms into your notebook without hunting through files\n"
        "- keeping source code, explanation, and output together for later reference\n\n"
        "## Snapshot\n\n"
        f"- Sessions Archived : **{len(sessions)}**\n"
        f"- Programs Documented : **{total_exercises}**\n"
        f"- Source Files Tracked : **{total_files}**\n"
        f"- Docs Site : [View the generated VitePress pages]({SITE_URL})\n\n"
        "## Session Index\n\n"
        "| Date | Topic | Programs | Source | Docs |\n"
        "|------|-------|----------|--------|------|\n"
        f"{session_rows}\n\n"
    )


def render_exercise_page(folder, data):
    session_label = pretty_date(folder)
    exercises = data["exercises"]
    source_readme_rel = Path(folder) / "README.md"
    generator_rel = Path("generateDocs.py")

    jump_rows = "\n".join(
        (
            "| "
            f"[{ex['title']}](#{ex['slug']}) | "
            f"{ex.get('source_file', 'Generated from README only')} | "
            f"{'[Open on GitHub](' + ex['source_link'] + ')' if ex.get('source_link') else 'Source file not matched'} |"
        )
        for ex in exercises
    )

    lines = [
        "---",
        f"title: {js_string(data['title'])}",
        "titleTemplate: false",
        "---",
        "",
        f"# {data['title']}",
        "",
        '<div class="session-hero">',
        '  <div class="session-hero__copy">',
        '    <p class="session-hero__eyebrow">Lab Reference</p>',
        f"    <p>{html.escape(data['topic'])} collected as revision-friendly notes, runnable source code, and sample output.</p>",
        "  </div>",
        '  <div class="session-hero__stats">',
        f"    <div><strong>{html.escape(session_label)}</strong><span>session date</span></div>",
        f"    <div><strong>{len(exercises)}</strong><span>programs</span></div>",
        f"    <div><strong>{len(data['source_files'])}</strong><span>source files</span></div>",
        "  </div>",
        "</div>",
        "",
        "::: tip Study flow",
        "Read the algorithm first, write the steps in your notebook, then compare the implementation and output with the original program file.",
        ":::",
        "",
        "## Session Resources",
        "",
        f"- [Open source session folder]({data['source_folder_link']})",
        f"- [Open original session README]({data['source_readme_link']})",
        f"- [Open docs generator]({github_blob(generator_rel)})",
        "",
        "## Quick Jump",
        "",
        "| Program | File | Link |",
        "|---------|------|------|",
        jump_rows,
        "",
    ]

    for index, ex in enumerate(exercises, start=1):
        lines += [
            f"## {ex['title']}",
            "",
            '<div class="exercise-meta">',
            f"  <span>Program {index} of {len(exercises)}</span>",
            f"  <span>{ex.get('source_file', 'Source file not matched')}</span>",
            f"  <span>{ex['lang'].upper()}</span>",
            "</div>",
            "",
        ]

        if ex.get("source_link"):
            lines += [
                f"[Open original file on GitHub]({ex['source_link']})",
                "",
            ]

        if ex["algorithm"]:
            lines += [
                "### Algorithm",
                "",
                ex["algorithm"],
                "",
            ]

        if ex["code"]:
            lines += [
                "### Code",
                "",
                f"```{ex['lang']}",
                ex["code"],
                "```",
                "",
            ]

        if ex.get("compile_command"):
            lines += [
                "::: details Compile command",
                "```bash",
                ex["compile_command"],
                "```",
                ":::",
                "",
            ]

        if ex["output"]:
            lines += [
                "### Output",
                "",
                "```bash",
                ex["output"],
                "```",
                "",
            ]

        lines += ["---", ""]

    if data["source_files"]:
        lines += [
            "## Compile All Files",
            "",
            "```bash",
        ]
        for path in data["source_files"]:
            lines.append(compile_command(path))
        lines += [
            "```",
            "",
            "::: details Turbo C++ compatibility notes",
            "```c",
            "// Change function signature",
            "int main()  ->  void main()",
            "",
            "// Change the final line",
            "return 0;  ->  getch();",
            "```",
            ":::",
            "",
        ]

    lines += [
        "## Maintainer Note",
        "",
        f"This page is generated from [{source_readme_rel.as_posix()}]({data['source_readme_link']}) by "
        f"[{generator_rel.as_posix()}]({github_blob(generator_rel)}).",
        "",
    ]

    return "\n".join(lines)


def sidebar_item(folder, data, collapsed):
    child_items = "\n".join(
        (
            "            { "
            f"text: {js_string(ex['title'])}, "
            f"link: {js_string(f'/exercises/{folder}#{ex["slug"]}')} "
            "},"
        )
        for ex in data["exercises"]
    )

    return (
        "        {\n"
        f"          text: {js_string(pretty_date(folder))},\n"
        f"          link: {js_string(f'/exercises/{folder}')},\n"
        f"          collapsed: {'true' if collapsed else 'false'},\n"
        "          items: [\n"
        f"{child_items}\n"
        "          ],\n"
        "        }"
    )


def render_config(sessions):
    first_link = f"/exercises/{sessions[0][0]}" if sessions else "/"
    sidebar_str = ",\n".join(
        sidebar_item(folder, data, collapsed=index > 0)
        for index, (folder, data) in enumerate(sessions)
    )

    return (
        'import { defineConfig } from "vitepress";\n'
        "import {\n"
        "  transformerNotationDiff,\n"
        "  transformerNotationFocus,\n"
        "  transformerNotationHighlight,\n"
        '} from "@shikijs/transformers";\n'
        "\n"
        "export default defineConfig({\n"
        f"  base: {js_string(REPO_BASE)},\n"
        f"  title: {js_string(SITE_TITLE)},\n"
        f"  description: {js_string(SITE_DESC)},\n"
        "  cleanUrls: true,\n"
        "  lastUpdated: true,\n"
        "\n"
        "  head: [\n"
        '    ["link", { rel: "preconnect", href: "https://fonts.googleapis.com" }],\n'
        '    ["link", { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" }],\n'
        '    ["link", { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap" }],\n'
        f'    ["link", {{ rel: "icon", href: "{REPO_BASE}favicon.svg" }}],\n'
        '    ["meta", { name: "theme-color", content: "#0f766e" }],\n'
        "  ],\n"
        "\n"
        "  markdown: {\n"
        "    theme: {\n"
        '      light: "github-light-default",\n'
        '      dark: "github-dark-default",\n'
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
        '    logo: { src: "/favicon.svg", alt: "C-DAA Programs" },\n'
        "    nav: [\n"
        '      { text: "Home", link: "/" },\n'
        f'      {{ text: "Latest Session", link: "{first_link}" }},\n'
        f'      {{ text: "GitHub", link: "{GITHUB_REPO}" }},\n'
        "    ],\n"
        "    sidebar: [\n"
        "      {\n"
        '        text: "Lab Sessions",\n'
        "        items: [\n"
        f"{sidebar_str}\n"
        "        ],\n"
        "      },\n"
        "    ],\n"
        f'    socialLinks: [{{ icon: "github", link: "{GITHUB_REPO}" }}],\n'
        '    search: { provider: "local" },\n'
        "    footer: {\n"
        '      message: "Built for revision, notebook writing, and quick code lookup.",\n'
        '      copyright: "C-DAA Programs · SpreadSheets600",\n'
        "    },\n"
        '    outline: { level: [2, 3], label: "On this page" },\n'
        "    docFooter: {\n"
        '      prev: "Previous session",\n'
        '      next: "Next session",\n'
        "    },\n"
        "  },\n"
        "});\n"
    )


def render_index(sessions):
    first_link = f"/exercises/{sessions[0][0]}" if sessions else "/"
    latest_folder, latest_data = sessions[0]

    total_sessions = len(sessions)
    total_exercises = sum(len(data["exercises"]) for _, data in sessions)
    total_files = sum(len(data["source_files"]) for _, data in sessions)

    timeline_cards = "\n".join(
        [
            (
                '<article class="session-card">'
                f'<p class="session-card__date">{html.escape(pretty_date(folder))}</p>'
                f'<h3><a href="./exercises/{folder}">{html.escape(data["topic"])}</a></h3>'
                f"<p>{html.escape(data['summary'])}</p>"
                f'<p class="session-card__meta">{len(data["exercises"])} programs · {len(data["source_files"])} files</p>'
                "</article>"
            )
            for folder, data in sessions
        ]
    )

    session_rows = "\n".join(
        (
            f"| [{pretty_date(folder)}](./exercises/{folder}) | {data['topic']} | "
            f"{len(data['exercises'])} | "
            f"[Folder]({data['source_folder_link']}) |"
        )
        for folder, data in sessions
    )

    latest_programs = "\n".join(
        f'<li><a href="./exercises/{latest_folder}#{ex["slug"]}">{html.escape(ex["title"])}</a></li>'
        for ex in latest_data["exercises"]
    )

    return (
        "---\n"
        "layout: home\n"
        "\n"
        "hero:\n"
        f"  name: {js_string(SITE_TITLE)}\n"
        '  text: "DAA lab work, organized for fast revision."\n'
        "  tagline: Keep each lab session in one place with algorithm steps, source code, and sample output that stay easy to revisit later.\n"
        "  actions:\n"
        "    - theme: brand\n"
        "      text: Open Latest Session\n"
        f"      link: {first_link}\n"
        "    - theme: alt\n"
        "      text: View on GitHub\n"
        f"      link: {GITHUB_REPO}\n"
        "features:\n"
        "  - title: Session-wise archive\n"
        "    details: Each lab date gets its own generated page with linked programs and clean navigation.\n"
        "  - title: Notebook-friendly structure\n"
        "    details: Algorithms, code, and outputs are kept in the same order you need when revising or writing in your copy.\n"
        "  - title: Single-source workflow\n"
        "    details: Update the dated session folder once, then regenerate the README and docs site together.\n"
        "---\n"
        "\n"
        '<div class="landing-metrics">\n'
        f"  <div><strong>{total_sessions}</strong><span>sessions</span></div>\n"
        f"  <div><strong>{total_exercises}</strong><span>programs</span></div>\n"
        f"  <div><strong>{total_files}</strong><span>source files</span></div>\n"
        f"  <div><strong>{html.escape(pretty_date(latest_folder))}</strong><span>latest lab</span></div>\n"
        "</div>\n"
        "\n"
        "## Latest Session\n"
        "\n"
        '<div class="latest-session">\n'
        '  <div class="latest-session__copy">\n'
        f'    <p class="latest-session__eyebrow">{html.escape(pretty_date(latest_folder))}</p>\n'
        f'    <h3><a href="./exercises/{latest_folder}">{html.escape(latest_data["topic"])}</a></h3>\n'
        f"    <p>{html.escape(latest_data['summary'])}</p>\n"
        "  </div>\n"
        '  <ul class="latest-session__list">\n'
        f"{latest_programs}\n"
        "  </ul>\n"
        "</div>\n"
        "\n"
        "## Study Workflow\n"
        "\n"
        '<div class="workflow-grid">\n'
        "  <article><strong>1.</strong><p>Write the lab solution in the dated folder with its source file and session README.</p></article>\n"
        "  <article><strong>2.</strong><p>Run <code>npm run docs:sync</code> to regenerate the GitHub README and VitePress docs.</p></article>\n"
        "  <article><strong>3.</strong><p>Use the generated site later to revise algorithms, compare outputs, and copy notes into your notebook faster.</p></article>\n"
        "</div>\n"
        "\n"
        "## Session Timeline\n"
        "\n"
        f'<div class="timeline-grid">\n{timeline_cards}\n</div>\n'
        "\n"
        "## All Sessions\n"
        "\n"
        "| Date | Topic | Programs | Source |\n"
        "|------|-------|----------|--------|\n"
        f"{session_rows}\n"
    )


def main():
    folders = sorted(
        [
            item.name
            for item in ROOT.iterdir()
            if item.is_dir()
            and DATE_RE.match(item.name)
            and (item / "README.md").exists()
        ],
        key=lambda name: parse_date(name) or datetime.min,
    )

    if not folders:
        print("No exercise folders found.")
        sys.exit(0)

    EXERCISES_OUT.mkdir(parents=True, exist_ok=True)
    VITEPRESS.mkdir(parents=True, exist_ok=True)

    sessions_chronological = []
    for folder in folders:
        data = parse_readme(ROOT / folder / "README.md")
        sessions_chronological.append((folder, data))

        out_path = EXERCISES_OUT / f"{folder}.md"
        out_path.write_text(render_exercise_page(folder, data), encoding="utf-8")
        print(f"generated  {out_path.relative_to(ROOT)}")

    sessions_display = list(reversed(sessions_chronological))

    config_path = VITEPRESS / "config.mjs"
    config_path.write_text(render_config(sessions_display), encoding="utf-8")
    print(f"generated  {config_path.relative_to(ROOT)}")

    index_path = DOCS / "index.md"
    index_path.write_text(render_index(sessions_display), encoding="utf-8")
    print(f"generated  {index_path.relative_to(ROOT)}")

    readme_path = ROOT / "README.md"
    readme_path.write_text(render_readme(sessions_display), encoding="utf-8")
    print(f"generated  {readme_path.relative_to(ROOT)}")

    print(f"done - {len(sessions_display)} folder(s) processed.")


if __name__ == "__main__":
    main()
