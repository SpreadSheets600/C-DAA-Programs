import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
EXERCISES_OUT = DOCS / "exercises"
PDF_SECTIONS_OUT = DOCS / "pdfs"
VITEPRESS = DOCS / ".vitepress"
GENERATED_PUBLIC = DOCS / "public" / "generated"

REPO_BASE = "/C-DAA-Programs/"
GITHUB_REPO = "https://github.com/SpreadSheets600/C-DAA-Programs"
SITE_URL = f"https://spreadsheets600.github.io{REPO_BASE}"
SITE_TITLE = "C-DAA Programs"
SITE_DESC = "Design And Analysis Of Algorithms lab programs, notes, and reference materials."

DATE_RE = re.compile(r"^\d{2}-\d{2}-\d{4}$")
SOURCE_EXTENSIONS = (".c", ".cc", ".cpp", ".cxx")
PDF_EXTENSIONS = (".pdf",)
SKIP_TOP_LEVEL_DIRS = {
    ".git",
    ".github",
    ".omx",
    "docs",
    "node_modules",
    "__pycache__",
}


def parse_date(folder):
    try:
        return datetime.strptime(folder, "%d-%m-%Y")
    except ValueError:
        return None


def pretty_date(folder):
    parsed = parse_date(folder)
    return parsed.strftime("%B %d, %Y") if parsed else folder


def prettify_name(text):
    return re.sub(r"[-_]+", " ", text).strip().title()


def vitepress_slug(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower()
    text = re.sub(r"[^\w\s/-]", "", text)
    text = text.replace("/", " ")
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-{2,}", "-", text)
    return text


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def normalize_code(text):
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def compile_command(path):
    compiler = "gcc" if path.suffix == ".c" else "g++"
    return f"{compiler} {path.name} -o {path.stem} && ./{path.stem}"


def github_blob(path):
    return f"{GITHUB_REPO}/blob/main/{path.as_posix()}"


def github_tree(path):
    return f"{GITHUB_REPO}/tree/main/{path.as_posix()}"


def site_page(path=""):
    clean_path = path.lstrip("/")
    return f"{SITE_URL}{clean_path}"


def public_asset_path(*parts):
    return "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))


def public_asset_url(*parts):
    path = public_asset_path(*parts)
    return f"{REPO_BASE}{path}" if path else REPO_BASE


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


def reset_generated_dir(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


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


def find_pdf_sections():
    sections = []

    for item in sorted(ROOT.iterdir(), key=lambda path: path.name.lower()):
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name in SKIP_TOP_LEVEL_DIRS:
            continue
        if DATE_RE.match(item.name):
            continue

        pdf_files = sorted(
            [
                path
                for path in item.rglob("*")
                if path.is_file() and path.suffix.lower() in PDF_EXTENSIONS
            ],
            key=lambda path: path.relative_to(item).as_posix().lower(),
        )

        if not pdf_files:
            continue

        section_slug = vitepress_slug(item.name)
        files = []

        for pdf_file in pdf_files:
            relative_path = pdf_file.relative_to(item)
            public_path = (
                Path("generated") / "pdfs" / item.name / relative_path
            ).as_posix()
            files.append(
                {
                    "name": relative_path.name,
                    "display_name": relative_path.as_posix(),
                    "slug": vitepress_slug(relative_path.as_posix()),
                    "source_path": pdf_file,
                    "source_link": github_blob(pdf_file.relative_to(ROOT)),
                    "public_path": public_path,
                    "public_url": public_asset_url(public_path),
                }
            )

        sections.append(
            (
                item.name,
                {
                    "title": prettify_name(item.name),
                    "slug": section_slug,
                    "files": files,
                    "source_folder_link": github_tree(item.relative_to(ROOT)),
                    "doc_link": f"/pdfs/{section_slug}",
                },
            )
        )

    return sections


def render_readme(sessions, pdf_sections):
    total_exercises = sum(len(data["exercises"]) for _, data in sessions)
    total_files = sum(len(data["source_files"]) for _, data in sessions)
    total_pdfs = sum(len(data["files"]) for _, data in pdf_sections)

    session_rows = "\n".join(
        (
            f"| {pretty_date(folder)} | {data['topic']} | {len(data['exercises'])} | "
            f"[Session README](./{folder}/README.md) | [Docs Page]({site_page(f'exercises/{folder}')}) |"
        )
        for folder, data in sessions
    )

    pdf_rows = "\n".join(
        (
            f"| {data['title']} | {len(data['files'])} | "
            f"[Folder](./{folder}) | [Docs Page]({site_page(f'pdfs/{data['slug']}')}) |"
        )
        for folder, data in pdf_sections
    )

    lines = [
        f"# {SITE_TITLE}",
        "",
        "> This README is generated by `generateDocs.py`. Update your source folders and let the workflow regenerate the repo docs.",
        "",
        "## Snapshot",
        "",
        f"- Sessions Archived : **{len(sessions)}**",
        f"- Programs Documented : **{total_exercises}**",
        f"- Source Files Tracked : **{total_files}**",
        f"- PDF Sections Tracked : **{len(pdf_sections)}**",
        f"- PDFs Tracked : **{total_pdfs}**",
        f"- Docs Site : [Programs Site]({SITE_URL})",
        "",
        "## Session Index",
        "",
        "| Date | Topic | Programs | Source | Docs |",
        "|------|-------|----------|--------|------|",
        session_rows or "| No sessions yet | - | - | - | - |",
        "",
    ]

    if pdf_sections:
        lines += [
            "## PDF Library",
            "",
            "| Section | PDFs | Source | Docs |",
            "|---------|------|--------|------|",
            pdf_rows,
            "",
        ]

    return "\n".join(lines)


def render_exercise_page(folder, data):
    session_label = pretty_date(folder)
    exercises = data["exercises"]
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
        f"> Topic: **{data['topic']}**  ",
        f"> Session Date: **{session_label}**  ",
        f"> Programs: **{len(exercises)}**  ",
        f"> Source Files: **{len(data['source_files'])}**",
        "",
        "::: tip Study flow",
        "Read the algorithm first, write the steps in your notebook, then compare the implementation and output with the original program file.",
        ":::",
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

    return "\n".join(lines)


def render_pdf_section_page(folder, data):
    file_rows = "\n".join(
        (
            f"| [{pdf['display_name']}](#{pdf['slug']}) | "
            f"[Preview]({pdf['public_url']}) | [GitHub]({pdf['source_link']}) |"
        )
        for pdf in data["files"]
    )

    lines = [
        "---",
        f"title: {js_string(data['title'])}",
        "titleTemplate: false",
        "---",
        "",
        f"# {data['title']}",
        "",
        f"> Section: **{data['title']}**  ",
        f"> PDFs: **{len(data['files'])}**",
        "",
        "## Files",
        "",
        "| PDF | Preview | Source |",
        "|-----|---------|--------|",
        file_rows,
        "",
    ]

    for pdf in data["files"]:
        lines += [
            f"## {pdf['display_name']}",
            "",
            f"- [Preview in browser]({pdf['public_url']})",
            f"- [Open original file on GitHub]({pdf['source_link']})",
            "",
            f'<iframe src="{pdf["public_url"]}" title="{html.escape(pdf["display_name"])}" width="100%" height="720"></iframe>',
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


def sidebar_session_item(folder, data, collapsed):
    child_items = "\n".join(
        (
            "            { "
            f"text: {js_string(ex['title'])}, "
            f"link: {js_string(f'/exercises/{folder}#{ex['slug']}')} "
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


def sidebar_pdf_item(section):
    folder, data = section
    child_items = "\n".join(
        (
            "            { "
            f"text: {js_string(pdf['display_name'])}, "
            f"link: {js_string(f'/pdfs/{data['slug']}#{pdf['slug']}')} "
            "},"
        )
        for pdf in data["files"]
    )

    return (
        "        {\n"
        f"          text: {js_string(data['title'])},\n"
        f"          link: {js_string(f'/pdfs/{data['slug']}')},\n"
        "          collapsed: true,\n"
        "          items: [\n"
        f"{child_items}\n"
        "          ],\n"
        "        }"
    )


def render_config(sessions, pdf_sections):
    first_session_link = f"/exercises/{sessions[0][0]}" if sessions else "/"
    first_pdf_link = f"/pdfs/{pdf_sections[0][1]['slug']}" if pdf_sections else "/"

    session_sidebar = ",\n".join(
        sidebar_session_item(folder, data, collapsed=index > 0)
        for index, (folder, data) in enumerate(sessions)
    )

    sidebar_groups = [
        "      {\n"
        '        text: "Lab Sessions",\n'
        "        items: [\n"
        f"{session_sidebar}\n"
        "        ],\n"
        "      }"
    ]

    if pdf_sections:
        pdf_sidebar = ",\n".join(sidebar_pdf_item(section) for section in pdf_sections)
        sidebar_groups.append(
            "      {\n"
            '        text: "PDF Library",\n'
            "        items: [\n"
            f"{pdf_sidebar}\n"
            "        ],\n"
            "      }"
        )

    nav_items = [
        '      { text: "Home", link: "/" },',
        f'      {{ text: "Latest Session", link: "{first_session_link}" }},',
    ]
    if pdf_sections:
        nav_items.append(f'      {{ text: "PDF Library", link: "{first_pdf_link}" }},')
    nav_items.append(f'      {{ text: "GitHub", link: "{GITHUB_REPO}" }},')

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
        f"{chr(10).join(nav_items)}\n"
        "    ],\n"
        "    sidebar: [\n"
        f"{',\n'.join(sidebar_groups)}\n"
        "    ],\n"
        f'    socialLinks: [{{ icon: "github", link: "{GITHUB_REPO}" }}],\n'
        '    search: { provider: "local" },\n'
        "    footer: {\n"
        '      message: "Built for revision, notebook writing, and quick code lookup.",\n'
        '      copyright: "C-DAA Programs · SpreadSheets600",\n'
        "    },\n"
        '    outline: { level: [2, 3], label: "On this page" },\n'
        "    docFooter: {\n"
        '      prev: "Previous",\n'
        '      next: "Next",\n'
        "    },\n"
        "  },\n"
        "});\n"
    )


def render_index(sessions, pdf_sections):
    first_session_link = f"/exercises/{sessions[0][0]}" if sessions else "/"
    latest_folder = sessions[0][0] if sessions else None
    latest_data = sessions[0][1] if sessions else None

    total_sessions = len(sessions)
    total_exercises = sum(len(data["exercises"]) for _, data in sessions)
    total_files = sum(len(data["source_files"]) for _, data in sessions)
    total_pdf_sections = len(pdf_sections)
    total_pdfs = sum(len(data["files"]) for _, data in pdf_sections)

    session_rows = "\n".join(
        (
            f"| [{pretty_date(folder)}](./exercises/{folder}) | {data['topic']} | "
            f"{len(data['exercises'])} | [Folder]({data['source_folder_link']}) |"
        )
        for folder, data in sessions
    )

    pdf_rows = "\n".join(
        (
            f"| [{data['title']}](./pdfs/{data['slug']}) | {len(data['files'])} | "
            f"[Folder]({data['source_folder_link']}) |"
        )
        for _, data in pdf_sections
    )

    lines = [
        "---",
        "layout: home",
        "",
        "hero:",
        f"  name: {js_string(SITE_TITLE)}",
        '  text: "DAA lab work, organized for fast revision."',
        "  tagline: Keep each lab session, note set, and question bank easy to revisit later.",
        "  actions:",
        "    - theme: brand",
        "      text: Open Latest Session",
        f"      link: {first_session_link}",
        "    - theme: alt",
        "      text: View on GitHub",
        f"      link: {GITHUB_REPO}",
        "features:",
        f'  - title: "{total_sessions}"',
        '    details: Sessions',
        f'  - title: "{total_exercises}"',
        '    details: Programs',
        f'  - title: "{total_files}"',
        '    details: Source Files',
        f'  - title: "{total_pdfs}"',
        '    details: PDFs',
        "---",
        "",
    ]

    if latest_folder and latest_data:
        latest_programs = "\n".join(
            f"- [{ex['title']}](./exercises/{latest_folder}#{ex['slug']})"
            for ex in latest_data["exercises"]
        )
        lines += [
            "## Latest Session",
            "",
            f"- Date: **{pretty_date(latest_folder)}**",
            f"- Topic: **[{latest_data['topic']}](./exercises/{latest_folder})**",
            f"- Summary: {latest_data['summary']}",
            "",
            "### Programs In Latest Session",
            "",
            latest_programs,
            "",
        ]

    lines += [
        "## PDF Library",
        "",
        "| Section | PDFs | Source |",
        "|---------|------|--------|",
        pdf_rows or "| No PDF sections yet | 0 | - |",
        "",
        "## All Sessions",
        "",
        "| Date | Topic | Programs | Source |",
        "|------|-------|----------|--------|",
        session_rows or "| No sessions yet | - | - | - |",
        "",
    ]

    return "\n".join(lines)


def sync_public_assets(pdf_sections):
    reset_generated_dir(GENERATED_PUBLIC)

    for folder, data in pdf_sections:
        for pdf in data["files"]:
            destination = DOCS / "public" / Path(pdf["public_path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf["source_path"], destination)
            print(f"generated  {destination.relative_to(ROOT)}")


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

    reset_generated_dir(EXERCISES_OUT)
    reset_generated_dir(PDF_SECTIONS_OUT)
    VITEPRESS.mkdir(parents=True, exist_ok=True)

    sessions_chronological = []
    for folder in folders:
        data = parse_readme(ROOT / folder / "README.md")
        sessions_chronological.append((folder, data))

        out_path = EXERCISES_OUT / f"{folder}.md"
        out_path.write_text(render_exercise_page(folder, data), encoding="utf-8")
        print(f"generated  {out_path.relative_to(ROOT)}")

    sessions_display = list(reversed(sessions_chronological))
    pdf_sections = find_pdf_sections()

    for folder, data in pdf_sections:
        out_path = PDF_SECTIONS_OUT / f"{data['slug']}.md"
        out_path.write_text(render_pdf_section_page(folder, data), encoding="utf-8")
        print(f"generated  {out_path.relative_to(ROOT)}")

    sync_public_assets(pdf_sections)

    config_path = VITEPRESS / "config.mjs"
    config_path.write_text(
        render_config(sessions_display, pdf_sections), encoding="utf-8"
    )
    print(f"generated  {config_path.relative_to(ROOT)}")

    index_path = DOCS / "index.md"
    index_path.write_text(
        render_index(sessions_display, pdf_sections), encoding="utf-8"
    )
    print(f"generated  {index_path.relative_to(ROOT)}")

    readme_path = ROOT / "README.md"
    readme_path.write_text(
        render_readme(sessions_display, pdf_sections), encoding="utf-8"
    )
    print(f"generated  {readme_path.relative_to(ROOT)}")

    print(
        f"done - {len(sessions_display)} session(s) and {len(pdf_sections)} pdf section(s) processed."
    )


if __name__ == "__main__":
    main()
