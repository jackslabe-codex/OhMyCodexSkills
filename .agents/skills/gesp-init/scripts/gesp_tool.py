#!/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "raw"
RAW_SYL = RAW / "syl"
RAW_PP = RAW / "pp"
RAW_ARCHIVE = RAW / "09-archive"
WIKI = ROOT / "wiki"
STATE = ROOT / "state"
DOCLING_BIN = Path("/Users/mao3/.local/opt/docling/bin/docling")
PDFTOTEXT_BIN = Path("/opt/homebrew/bin/pdftotext")
PDFTOPPM_BIN = Path("/opt/homebrew/bin/pdftoppm")

DIRS = [
    RAW_SYL,
    RAW_PP,
    RAW_ARCHIVE / "syl",
    RAW_ARCHIVE / "pp",
    WIKI / "concepts",
    WIKI / "syntheses",
    WIKI / "questions",
    WIKI / "exams",
    STATE / "candidates",
    STATE / "attempts",
    STATE / "catalog",
]

LEVEL5_CONCEPTS = [
    {
        "slug": "concept-number-theory",
        "title": "concept-number-theory",
        "name": "初等数论",
        "module": "初等数论",
        "summary": "覆盖素数与合数、最大公约数与最小公倍数、同余与模运算、约数与倍数、质因数分解、奇偶性、欧几里得算法、唯一分解定理以及素数筛法。",
        "prerequisites": [],
        "keywords": ["素数", "合数", "最大公约数", "最小公倍数", "同余", "模运算", "质因数", "奇偶", "欧几里得", "gcd", "lcm", "筛法"],
    },
    {
        "slug": "concept-complexity",
        "title": "concept-complexity",
        "name": "算法复杂度估算方法",
        "module": "算法复杂度估算方法",
        "summary": "覆盖多项式复杂度、对数复杂度以及时间复杂度和空间复杂度的基本判断。",
        "prerequisites": [],
        "keywords": ["复杂度", "时间复杂度", "空间复杂度", "对数", "多项式"],
    },
    {
        "slug": "concept-cpp-high-precision",
        "title": "concept-cpp-high-precision",
        "name": "C++高精度运算",
        "module": "C++高精度运算",
        "summary": "覆盖使用数组或序列模拟高精度加法、减法、乘法和除法。",
        "prerequisites": [],
        "keywords": ["高精度", "carry", "rem", "vector<int>", "大整数", "进位", "借位"],
    },
    {
        "slug": "concept-linked-list",
        "title": "concept-linked-list",
        "name": "链表",
        "module": "链表",
        "summary": "覆盖单链表、双链表、循环链表的创建、插入、删除、遍历、查找等基本操作。",
        "prerequisites": [],
        "keywords": ["链表", "单链表", "双链表", "循环链表", "结点", "Node", "prev", "next", "哑结点"],
    },
    {
        "slug": "concept-binary-search",
        "title": "concept-binary-search",
        "name": "二分算法",
        "module": "二分算法",
        "summary": "覆盖二分查找和二分答案算法，强调有序条件和边界控制。",
        "prerequisites": ["concept-complexity"],
        "keywords": ["二分", "二分查找", "二分答案", "mid", "有序"],
    },
    {
        "slug": "concept-recursion",
        "title": "concept-recursion",
        "name": "递归算法",
        "module": "递归算法",
        "summary": "覆盖递归基本概念、复杂度分析和递归优化策略。",
        "prerequisites": ["concept-complexity"],
        "keywords": ["递归", "fib", "递归函数"],
    },
    {
        "slug": "concept-divide-and-conquer",
        "title": "concept-divide-and-conquer",
        "name": "分治算法",
        "module": "分治算法",
        "summary": "覆盖归并排序和快速排序等典型分治算法。",
        "prerequisites": ["concept-recursion", "concept-complexity"],
        "keywords": ["分治", "归并排序", "快速排序", "pivot", "枢轴"],
    },
    {
        "slug": "concept-greedy",
        "title": "concept-greedy",
        "name": "贪心算法",
        "module": "贪心算法",
        "summary": "覆盖贪心算法的基本思想和最优子结构。",
        "prerequisites": ["concept-complexity"],
        "keywords": ["贪心", "最优子结构"],
    },
]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_jsonish(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_jsonish(path: Path, obj) -> None:
    write_text(path, json.dumps(obj, ensure_ascii=False, indent=2))


def normalize(text: str) -> str:
    text = text.replace("\u3000", " ").replace("\xa0", " ")
    text = re.sub(r"第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", "", text)
    text = re.sub(r"页\s*\d+\s*共\s*/\s*页\s*\d+\s*第", "", text)
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if not line:
            lines.append("")
            continue
        if re.fullmatch(r"\d+", line):
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return normalize("\n".join((page.extract_text() or "") for page in reader.pages))


def pdftotext_bin() -> str | None:
    if PDFTOTEXT_BIN.exists():
        return str(PDFTOTEXT_BIN)
    return shutil.which("pdftotext")


def pdftoppm_bin() -> str | None:
    if PDFTOPPM_BIN.exists():
        return str(PDFTOPPM_BIN)
    return shutil.which("pdftoppm")


def normalize_layout_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\f", "\n")
    lines = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if re.fullmatch(r"\s*", line):
            lines.append("")
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_text_via_pdftotext_layout(path: Path) -> str | None:
    binary = pdftotext_bin()
    if not binary:
        return None
    result = subprocess.run([binary, "-layout", str(path), "-"], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    text = normalize_layout_text(result.stdout)
    if "第 1 题" not in text or "答案" not in text:
        return None
    return text


def docling_bin() -> str | None:
    if DOCLING_BIN.exists():
        return str(DOCLING_BIN)
    return shutil.which("docling")


def normalize_docling_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\u3000", " ").replace("\xa0", " ")
    lines = []
    in_code = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            lines.append(line.strip())
            continue
        if re.fullmatch(r"\d+", line.strip()):
            continue
        if in_code:
            line = re.sub(r"(?:\s+\d+){2,}\s*$", "", line)
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_text_via_docling(path: Path) -> str | None:
    binary = docling_bin()
    if not binary:
        return None
    with tempfile.TemporaryDirectory(prefix="gesp-docling-") as tmpdir:
        env = os.environ.copy()
        env.setdefault("PATH", f"/Users/mao3/.local/opt/docling/bin:/opt/homebrew/bin:{env.get('PATH', '')}")
        env.setdefault("TESSDATA_PREFIX", "/opt/homebrew/share/tessdata/")
        cmd = [
            binary,
            str(path),
            "--to",
            "md",
            "--ocr",
            "--ocr-engine",
            "tesseract",
            "--output",
            tmpdir,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            return None
        md_path = Path(tmpdir) / f"{path.stem}.md"
        if not md_path.exists():
            return None
        return normalize_docling_markdown(md_path.read_text(encoding="utf-8"))


def paper_text(path: Path) -> tuple[str, str]:
    layout_text = pdf_text_via_pdftotext_layout(path)
    if layout_text:
        return layout_text, "pdftotext_layout"
    docling_text = pdf_text_via_docling(path)
    if docling_text:
        return docling_text, "docling"
    return pdf_text(path), "pypdf"


def ensure_index() -> None:
    index_path = WIKI / "index.md"
    if index_path.exists():
        text = read_text(index_path)
    else:
        text = "# Wiki Index\n\n## Concepts\n\n## Syntheses\n"
    lines = text.splitlines()
    filtered = []
    skip_section = False
    for line in lines:
        if line in {"## Entities", "## Sources"}:
            skip_section = True
            continue
        if skip_section and line.startswith("## "):
            skip_section = False
        if skip_section:
            continue
        filtered.append(line)
    text = "\n".join(filtered).strip() + "\n"
    for heading in ["## Concepts", "## Syntheses", "## Questions", "## Exams"]:
        if heading not in text:
            text = text.rstrip() + f"\n\n{heading}\n"
    write_text(index_path, text)


def init_state() -> None:
    blueprint_path = STATE / "catalog" / "blueprint.yaml"
    if not blueprint_path.exists():
        blueprint = {
            "exam": "gesp",
            "subject": "cpp",
            "levels": {},
            "papers": {},
            "concepts": {},
            "question_types": ["single_choice", "true_false", "programming"],
            "naming": {
                "exam_page": "wiki/exams/exam-<year>-<month>.md",
                "question_page": "wiki/questions/question-<year>-<month>-<no>.md",
            },
        }
        dump_jsonish(blueprint_path, blueprint)
    candidate_path = STATE / "candidates" / "default.yaml"
    if not candidate_path.exists():
        candidate = {
            "exam": "gesp",
            "subject": "cpp",
            "candidate_id": "default",
            "concepts": [],
        }
        dump_jsonish(candidate_path, candidate)


def init_repo() -> None:
    for directory in DIRS:
        directory.mkdir(parents=True, exist_ok=True)
    for keep in [
        RAW_SYL / ".gitkeep",
        RAW_PP / ".gitkeep",
        RAW_ARCHIVE / ".gitkeep",
        RAW_ARCHIVE / "syl" / ".gitkeep",
        RAW_ARCHIVE / "pp" / ".gitkeep",
        STATE / "attempts" / ".gitkeep",
    ]:
        if not keep.exists():
            write_text(keep, "")
    ensure_index()
    if not (WIKI / "log.md").exists():
        write_text(WIKI / "log.md", "")
    init_state()


def update_index(section: str, page: str, summary: str) -> None:
    text = read_text(WIKI / "index.md")
    lines = text.splitlines()
    heading = f"## {section}"
    if heading not in lines:
        lines.extend(["", heading, ""])
    idx = lines.index(heading)
    insert_at = idx + 1
    while insert_at < len(lines) and lines[insert_at].startswith("- [["):
        if lines[insert_at].startswith(f"- [[{page}]]"):
            lines[insert_at] = f"- [[{page}]] — {summary}"
            write_text(WIKI / "index.md", "\n".join(lines))
            return
        insert_at += 1
    lines.insert(insert_at, f"- [[{page}]] — {summary}")
    write_text(WIKI / "index.md", "\n".join(lines))


def append_log(kind: str, summary: str, output: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"## [{stamp}] {kind}\n- **summary**: {summary}\n- **output**: {output}\n"
    existing = read_text(WIKI / "log.md").strip()
    write_text(WIKI / "log.md", (existing + "\n\n" + block).strip() if existing else block)


def slug_level(path: Path, text: str) -> int:
    if "五级" in text or "level5" in path.name.lower():
        return 5
    raise ValueError(f"unsupported level for {path}")


def resolve_input_paths(path_str: str | None, kind: str) -> List[Path]:
    if path_str:
        path = (ROOT / path_str).resolve() if not Path(path_str).is_absolute() else Path(path_str)
        return [path]
    if kind == "outline":
        directory = RAW_SYL
    else:
        directory = RAW_PP
    return sorted(directory.glob("*.pdf"))


def archive_source(path: Path, kind: str) -> None:
    if kind == "outline":
        src_dir = RAW_SYL.resolve()
        archive_dir = RAW_ARCHIVE / "syl"
    else:
        src_dir = RAW_PP.resolve()
        archive_dir = RAW_ARCHIVE / "pp"
    try:
        relative_parent = path.resolve().parent
    except FileNotFoundError:
        return
    if relative_parent != src_dir:
        return
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / path.name
    if target.exists():
        stem = path.stem
        suffix = path.suffix
        target = archive_dir / f"{stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}{suffix}"
    shutil.move(str(path), str(target))


def ingest_outline(path_str: str | None) -> None:
    init_repo()
    paths = resolve_input_paths(path_str, "outline")
    if not paths:
        print(json.dumps({"status": "no_input", "kind": "outline", "directory": str(RAW_SYL)}, ensure_ascii=False))
        return
    for path in paths:
        text = pdf_text(path)
        level = slug_level(path, text)
        overview_match = re.search(r"（二）\s*考核目标(.*?)(?:（三）|知识块)", text, re.S)
        overview = normalize(overview_match.group(1)) if overview_match else "未可靠提取考核目标。"
        blueprint = load_jsonish(STATE / "catalog" / "blueprint.yaml", {})
        blueprint.setdefault("levels", {})[str(level)] = {
            "outline_source": path.name,
            "modules": [{"slug": item["slug"], "name": item["name"], "prerequisites": item["prerequisites"]} for item in LEVEL5_CONCEPTS],
        }
        for item in LEVEL5_CONCEPTS:
            blueprint.setdefault("concepts", {})[item["slug"]] = {
                "exam": "gesp",
                "level": level,
                "module": item["module"],
                "prerequisites": item["prerequisites"],
            }
            concept_path = WIKI / "concepts" / f"{item['slug']}.md"
            write_text(
                concept_path,
                f"""---
title: "{item['title']}"
type: concept
exam: gesp
subject: cpp
level: {level}
module: "{item['module']}"
prerequisites: {json.dumps(item['prerequisites'], ensure_ascii=False)}
question_refs: []
---

## Definition

{item['summary']}

## Notes

- 来源：{path.name}
""",
            )
            update_index("Concepts", item["slug"], f"GESP C++ 五级考点：{item['name']}")
        dump_jsonish(STATE / "catalog" / "blueprint.yaml", blueprint)
        candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
        existing = {entry["concept_id"]: entry for entry in candidate.get("concepts", [])}
        for item in LEVEL5_CONCEPTS:
            existing.setdefault(
                item["slug"],
                {
                    "concept_id": item["slug"],
                    "mastery_level": "unknown",
                    "attempt_count": 0,
                    "correct_count": 0,
                    "last_attempt_at": "",
                    "last_question_ids": [],
                },
            )
        candidate["concepts"] = list(existing.values())
        dump_jsonish(STATE / "candidates" / "default.yaml", candidate)
        append_log("gesp-ingest-outline", f"摄入大纲 {path.name}", "[[concept-number-theory]] 等 concept 页面")
        archive_source(path, "outline")


def exam_meta(path: Path, text: str) -> Dict[str, int | str]:
    m = re.search(r"(\d{4})[_ ](\d{1,2})", path.stem)
    if not m:
        m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月", text)
    year = int(m.group(1))
    month = int(m.group(2))
    level = slug_level(path, text)
    return {
        "year": year,
        "month": month,
        "level": level,
        "exam_page": f"exam-{year:04d}-{month:02d}",
        "paper_id": f"{year:04d}-{month:02d}",
    }


def answer_key(text: str) -> List[str]:
    m = re.search(r"答案\s+([A-D](?:\s+[A-D]){14})", text)
    return re.findall(r"[A-D]", m.group(1)) if m else []


def section(text: str, start: str, end: str | None) -> str:
    s = text.find(start)
    if s == -1:
        return ""
    s += len(start)
    e = text.find(end, s) if end else -1
    return text[s:] if e == -1 else text[s:e]


def parse_question_blocks(section_text: str) -> List[re.Match]:
    return list(re.finditer(r"第\s*(\d+)\s*题", section_text))


def rewrite_compact_option_fence(block: str) -> str:
    pattern = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.S)

    def repl(match: re.Match) -> str:
        content = match.group(1).strip()
        if "A. B. C. D." not in content:
            return match.group(0)
        body = content.split("A. B. C. D.", 1)[1].strip()
        chunks = [
            part.strip()
            for part in re.split(r"\s+1(?:\s+2(?:\s+3)?)?\s+", body)
            if part.strip()
        ]
        if len(chunks) != 4:
            return match.group(0)
        labels = ["A", "B", "C", "D"]
        parts = []
        for label, chunk in zip(labels, chunks):
            parts.append(f"{label}.\n\n```cpp\n{chunk}\n```")
        return "\n\n".join(parts)

    return pattern.sub(repl, block)


def cleanup_question_markdown(block: str) -> str:
    block = rewrite_compact_option_fence(block)
    block = block.strip()
    lines = []
    for raw in block.splitlines():
        line = raw.rstrip()
        if re.match(r"^- \d+ 单选题", line):
            continue
        if re.match(r"^## 3\.\d+ 编程题", line):
            continue
        line = re.sub(r"^- \[ \] ", "", line)
        line = re.sub(r"^- ", "", line, count=1)
        line = re.sub(r"^##\s+", "", line)
        line = re.sub(r"(?:\s+\d+){2,}\s*$", "", line)
        lines.append(line)
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def format_layout_question_block(block: str) -> str:
    lines = block.strip().splitlines()
    out = []
    in_code = False

    def flush_code() -> None:
        nonlocal in_code
        if in_code:
            out.append("```")
            out.append("")
            in_code = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            if in_code:
                continue
            if out and out[-1] != "":
                out.append("")
            continue
        if re.fullmatch(r"\d+", stripped):
            continue
        if re.fullmatch(r"[A-D]\.", stripped):
            flush_code()
            out.append(stripped)
            out.append("")
            continue
        m = re.match(r"^\s*\d+(.*)$", line)
        if m:
            code = m.group(1).rstrip()
            if not code.strip():
                continue
            if not in_code:
                out.append("```cpp")
                in_code = True
            out.append(code[1:] if code.startswith(" ") else code)
            continue
        flush_code()
        out.append(stripped)
    flush_code()
    text = "\n".join(out).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def has_layout_code_lines(block: str) -> bool:
    for raw in block.splitlines():
        if re.match(r"^\s*\d+\s+\S", raw):
            return True
    return False


def extract_plain_question_parts(block: str) -> tuple[str, Dict[str, str]]:
    text = normalize(block)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    intro_lines: List[str] = []
    options: Dict[str, str] = {}
    current_label = ""

    def looks_code_like(line: str) -> bool:
        return bool(
            re.search(r"[{};]|//|vector<|int\s+\w+\s*\(|return\b|while\s*\(|for\s*\(|if\s*\(|\belse\b", line)
        )

    def compact_cjk_spaces(value: str) -> str:
        value = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)
        value = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[，。；：？！）】])", "", value)
        value = re.sub(r"(?<=[（【])\s+(?=[\u4e00-\u9fff])", "", value)
        return value

    for line in lines:
        match = re.match(r"^([A-D])\.\s*(.*)$", line)
        if match:
            current_label = match.group(1)
            tail = match.group(2).strip()
            options[current_label] = compact_cjk_spaces(f"{current_label}. {tail}".strip())
            continue
        if current_label:
            if looks_code_like(line):
                continue
            options[current_label] = compact_cjk_spaces(f"{options[current_label]} {line}".strip())
        else:
            if looks_code_like(line):
                continue
            intro_lines.append(line)
    return compact_cjk_spaces(" ".join(intro_lines).strip()), options


def rebuild_hybrid_code_question(layout_block: str, plain_block: str) -> str:
    layout_stem = format_layout_question_block(layout_block)
    plain_intro, plain_options = extract_plain_question_parts(plain_block)
    lines = layout_stem.splitlines()
    first_special = 0
    while first_special < len(lines):
        stripped = lines[first_special].strip()
        if stripped.startswith("```") or re.fullmatch(r"[A-D]\.", stripped):
            break
        first_special += 1

    out: List[str] = []
    if plain_intro:
        out.append(plain_intro)
    else:
        out.extend(line for line in lines[:first_special] if line.strip())
    if out and out[-1] != "":
        out.append("")

    i = first_special
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        label_match = re.match(r"^([A-D])\.(?:\s+.*)?$", stripped)
        if label_match:
            label = label_match.group(1)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if re.fullmatch(r"[A-D]\.", stripped) and j < len(lines) and lines[j].startswith("```"):
                out.append(f"{label}.")
                out.append("")
                while j < len(lines):
                    if re.match(r"^([A-D])\.(?:\s+.*)?$", lines[j].strip()):
                        break
                    out.append(lines[j])
                    j += 1
                if out and out[-1] != "":
                    out.append("")
                i = j
                continue
            option_text = plain_options.get(label, f"{label}.")
            out.append(option_text)
            while j < len(lines) and not re.match(r"^([A-D])\.(?:\s+.*)?$", lines[j].strip()):
                j += 1
            i = j
            continue
        out.append(lines[i])
        i += 1

    text = "\n".join(out).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def top_level_option_labels(stem: str) -> List[str]:
    labels = []
    in_code = False
    for raw in stem.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        match = re.fullmatch(r"([A-D])\.", line)
        if match:
            labels.append(match.group(1))
    return labels


def single_choice_extraction_status(stem: str, answer: str) -> str:
    if not answer:
        return "needs_review"
    if "A. B. C. D." in stem or "## " in stem:
        return "needs_review"
    labels = top_level_option_labels(stem)
    if labels != ["A", "B", "C", "D"]:
        return "needs_review"
    if stem.count("```") % 2 != 0:
        return "needs_review"
    return "ok"


def map_concepts(stem: str) -> List[str]:
    haystack = stem.lower()
    refs = []
    for item in LEVEL5_CONCEPTS:
        if any(keyword.lower() in haystack for keyword in item["keywords"]):
            refs.append(item["slug"])
    return refs


def question_page_content(
    meta: Dict[str, int | str],
    qno: int,
    qtype: str,
    stem: str,
    answer: str,
    concept_refs: List[str],
    extraction_status: str,
    analysis: str = "",
    difficulty: str = "unknown",
    source: str = "",
) -> str:
    qid = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
    links = [f"- [[exam-{meta['year']:04d}-{meta['month']:02d}]]"] + [f"- [[{ref}]]" for ref in concept_refs]
    return f"""---
title: "{qid}"
type: question
question_id: "{qid}"
year: {meta['year']}
month: {meta['month']}
no: {qno}
level: {meta['level']}
subject: cpp
question_type: {qtype}
answer: {json.dumps(answer, ensure_ascii=False)}
analysis: {json.dumps(analysis, ensure_ascii=False)}
concept_refs: {json.dumps(concept_refs, ensure_ascii=False)}
difficulty: {json.dumps(difficulty, ensure_ascii=False)}
extraction_status: {extraction_status}
source: {json.dumps(source, ensure_ascii=False)}
---

## Stem

{stem}

## Answer

{answer or "未可靠提取。"}

## Analysis

{analysis or "首版未生成解析。"}

## Links

{chr(10).join(links)}
"""


def pdf_page_texts(path: Path) -> List[str]:
    binary = pdftotext_bin()
    reader = PdfReader(str(path))
    pages: List[str] = []
    for page_no in range(1, len(reader.pages) + 1):
        if binary:
            result = subprocess.run(
                [binary, "-layout", "-f", str(page_no), "-l", str(page_no), str(path), "-"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                pages.append(normalize_layout_text(result.stdout))
                continue
        page = reader.pages[page_no - 1]
        pages.append(normalize(page.extract_text() or ""))
    return pages


def render_pdf_pages(path: Path, output_dir: Path, dpi: int = 120) -> List[Path]:
    binary = pdftoppm_bin()
    if not binary:
        raise RuntimeError("pdftoppm is required to render PDF pages for GLM visual extraction")
    prefix = output_dir / "page"
    result = subprocess.run(
        [binary, "-png", "-r", str(dpi), str(path), str(prefix)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {result.stderr.strip() or result.stdout.strip()}")
    images = sorted(output_dir.glob("page-*.png"))
    if not images:
        raise RuntimeError("pdftoppm did not produce any page images")
    return images


def render_pdf_page(path: Path, output_dir: Path, page_no: int, dpi: int = 200) -> Path:
    binary = pdftoppm_bin()
    if not binary:
        raise RuntimeError("pdftoppm is required to render PDF pages")
    prefix = output_dir / "page"
    result = subprocess.run(
        [binary, "-png", "-r", str(dpi), "-f", str(page_no), "-l", str(page_no), str(path), str(prefix)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {result.stderr.strip() or result.stdout.strip()}")
    images = sorted(output_dir.glob("page-*.png"))
    if not images:
        raise RuntimeError(f"pdftoppm did not produce page {page_no}")
    return images[0]


def image_data_url(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def concept_candidates(blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
    concepts = blueprint.get("concepts", {})
    items = []
    for slug in sorted(concepts):
        entry = concepts[slug]
        items.append(
            {
                "slug": slug,
                "module": entry.get("module", ""),
                "prerequisites": entry.get("prerequisites", []),
            }
        )
    if items:
        return items
    return [
        {"slug": item["slug"], "module": item["module"], "prerequisites": item["prerequisites"]}
        for item in LEVEL5_CONCEPTS
    ]


def build_glm_paper_prompt(meta: Dict[str, int | str], page_texts: List[str], concepts: List[Dict[str, Any]]) -> str:
    text_pages = "\n\n".join(
        f"===== PAGE {idx} TEXT LAYER =====\n{text}" for idx, text in enumerate(page_texts, start=1)
    )
    schema = {
        "paper": {"year": meta["year"], "month": meta["month"], "level": meta["level"]},
        "questions": [
            {
                "no": 1,
                "question_type": "single_choice",
                "answer": "A",
                "analysis": "",
                "difficulty": "unknown",
                "concept_refs": ["concept-linked-list"],
                "extraction_status": "ok",
                "stem_markdown": "题面 Markdown",
            }
        ],
    }
    return f"""你是 GESP C++ 五级真题结构化助手。请结合后续按顺序提供的 PDF 页面截图和下面的文本层粗抽取结果，重建一份适合题库使用的严格 JSON。

必须遵守：
1. 只输出 JSON 对象，不要输出 Markdown code fence，不要解释。
2. 输出 schema 必须与示例一致：{json.dumps(schema, ensure_ascii=False)}
3. paper.year={meta['year']}，paper.month={meta['month']}，paper.level={meta['level']}。
4. questions 必须包含 27 题：单选题全局编号 1-15，判断题全局编号 16-25，编程题全局编号 26-27。
5. question_type 只能是 single_choice、true_false、programming。
6. 单选题 answer 使用答案表中的 A/B/C/D；判断题如果答案表没有可靠答案，answer 置空并标记 extraction_status 为 needs_review；编程题 answer 置空。
7. stem_markdown 要按题目逻辑重建，不要照搬 PDF 物理版面；去掉页眉、页脚、页码和 PDF 行号。
8. 代码必须用 fenced block，C++ 使用 ```cpp，样例使用 ```text。
9. 编程题必须包含题目描述、输入格式、输出格式、样例、样例解释、数据范围、参考程序；样例和参考程序必须去掉 PDF 行号。
10. 公式、变量、复杂度、上下标、样例内容以页面截图为准补全；文本层缺字或乱序时以截图为准。
11. concept_refs 只能从给定候选 concept slug 中选择；不确定可留空，并把 extraction_status 设为 needs_review。
12. difficulty 没有可靠依据时填 unknown；analysis 没有解析时填空字符串。

concept 候选：
{json.dumps(concepts, ensure_ascii=False, indent=2)}

文本层粗抽取：
{text_pages}
"""


def build_glm_question_group_prompt(
    meta: Dict[str, int | str],
    page_texts: List[tuple[int, str]],
    concepts: List[Dict[str, Any]],
    qtype: str,
    expected_nos: List[int],
) -> str:
    text_pages = "\n\n".join(f"===== PAGE {idx} TEXT LAYER =====\n{text}" for idx, text in page_texts)
    return f"""你是 GESP C++ 五级真题结构化助手。请只处理本次指定的题目编号，结合前面页面截图和下面文本层粗抽取，输出严格 JSON。

必须只输出 JSON 对象，不要 Markdown code fence，不要解释。
输出格式：
{{
  "questions": [
    {{
      "no": {expected_nos[0]},
      "question_type": "{qtype}",
      "answer": "",
      "analysis": "",
      "difficulty": "unknown",
      "concept_refs": [],
      "extraction_status": "ok",
      "stem_markdown": "题面 Markdown"
    }}
  ]
}}

硬性规则：
1. 只输出这些全局题号：{expected_nos}。
2. question_type 必须全部是 {qtype}。
3. 单选题全局编号为 1-15；判断题全局编号为 16-25；编程题全局编号为 26-27。
4. stem_markdown 要按题目逻辑重建，去掉页眉、页脚、页码和 PDF 行号。
5. 代码必须用 fenced block，C++ 使用 ```cpp，样例使用 ```text。
6. 编程题必须包含题目描述、输入格式、输出格式、样例、样例解释、数据范围、参考程序；样例和参考程序必须去掉 PDF 行号。
7. 公式、变量、复杂度、上下标、样例内容以页面截图为准补全；文本层缺字或乱序时以截图为准。
8. concept_refs 只能从给定候选 concept slug 中选择；不确定可留空，并把 extraction_status 设为 needs_review。
9. difficulty 没有可靠依据时填 unknown；analysis 没有解析时填空字符串。

paper 元信息：year={meta['year']} month={meta['month']} level={meta['level']}

concept 候选：
{json.dumps(concepts, ensure_ascii=False, indent=2)}

文本层粗抽取：
{text_pages}
"""


def glm_chat_completion(content: List[Dict[str, Any]]) -> str:
    api_key = os.environ.get("GLM_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GLM_API_KEY is required for GLM-5V-Turbo paper ingestion")
    base = os.environ.get("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
    model = os.environ.get("GLM_VISION_MODEL", "glm-5v-turbo")
    thinking = os.environ.get("GLM_THINKING", "enabled")
    timeout = int(os.environ.get("GLM_TIMEOUT_SECONDS", "300"))
    payload: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "thinking": {"type": thinking},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GLM API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GLM API request failed: {exc.reason}") from exc

    payload = json.loads(raw)
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"unexpected GLM API response: {raw[:1000]}") from exc


def extract_json_object(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.S)
        if fence:
            cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        preview = cleaned[:800].replace("\n", "\\n")
        raise RuntimeError(f"GLM response did not contain a JSON object: {preview}")
    return json.loads(cleaned[start : end + 1])


def strip_markdown_code_line_numbers(markdown: str) -> str:
    lines = []
    in_fence = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        if in_fence:
            if re.fullmatch(r"\s*\d+\s*", line):
                continue
            match = re.match(r"^(\s*)\d+\s{2,}(.*)$", line)
            if match:
                line = match.group(1) + match.group(2)
        lines.append(line)
    return "\n".join(lines).strip()


def numbered_block_after_heading(text: str, heading_pattern: str) -> str:
    match = re.search(heading_pattern + r"\s*\n(?P<body>(?:\s*\d+\s+\S.*(?:\n|$))+)", text)
    if not match:
        return ""
    values = []
    for raw in match.group("body").splitlines():
        line_match = re.match(r"^\s*\d+\s+(.*\S)\s*$", raw)
        if line_match:
            values.append(line_match.group(1).strip())
    return "\n".join(values).strip()


def repair_programming_samples(stem: str, qno: int, layout_text: str) -> str:
    if qno not in {26, 27}:
        return stem
    local_no = qno - 25
    input_sample = numbered_block_after_heading(layout_text, rf"3\.{local_no}\.4\.1\s+输入样例")
    output = numbered_block_after_heading(layout_text, rf"3\.{local_no}\.4\.2\s+输出样例")

    def replace_sample(markdown: str, label: str, value: str) -> str:
        if not value:
            return markdown
        pattern = rf"(####[^\n]*{label}[^\n]*\n\s*```text\n).*?(\n```)"
        return re.sub(pattern, rf"\g<1>{value}\2", markdown, flags=re.S)

    stem = replace_sample(stem, "输入样例", input_sample)
    stem = replace_sample(stem, "输出样例", output)
    return stem


def normalize_true_false_answer(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "1", "√", "✓", "对", "正确"}:
        return "true"
    if text in {"false", "f", "no", "n", "0", "×", "x", "错", "错误"}:
        return "false"
    return ""


def classify_red_judge_mark(width: int, height: int) -> str:
    if height >= 20 and width >= 16:
        return "true"
    if height <= 18 and width <= 18:
        return "false"
    return ""


def extract_true_false_answer_key_from_image(image_path: Path) -> List[str]:
    try:
        from PIL import Image
    except ImportError:
        return []
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pix = img.load()
    red_pixels: set[tuple[int, int]] = set()
    for y in range(height):
        for x in range(width):
            r, g, b = pix[x, y]
            if r > 170 and g < 100 and b < 100:
                red_pixels.add((x, y))

    seen: set[tuple[int, int]] = set()
    components = []
    for pixel in list(red_pixels):
        if pixel in seen:
            continue
        stack = [pixel]
        seen.add(pixel)
        xs = []
        ys = []
        for x, y in stack:
            xs.append(x)
            ys.append(y)
            for nx in (x - 1, x, x + 1):
                for ny in (y - 1, y, y + 1):
                    if (nx, ny) in red_pixels and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
        if len(xs) < 20:
            continue
        x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
        box_w = x2 - x1 + 1
        box_h = y2 - y1 + 1
        answer = classify_red_judge_mark(box_w, box_h)
        if answer:
            components.append({"x": (x1 + x2) / 2, "y": (y1 + y2) / 2, "answer": answer})

    best_row: List[Dict[str, Any]] = []
    for component in components:
        row = [item for item in components if abs(item["y"] - component["y"]) <= 18]
        if len(row) > len(best_row):
            best_row = row
    best_row = sorted(best_row, key=lambda item: item["x"])
    if len(best_row) < 10:
        return []
    return [item["answer"] for item in best_row[:10]]


def extract_true_false_answer_key(path: Path, page_texts: List[str] | None = None) -> List[str]:
    if page_texts is None:
        page_texts = pdf_page_texts(path)
    judge_page = first_page_containing(page_texts, r"判断题")
    if judge_page is None:
        return []
    with tempfile.TemporaryDirectory(prefix="gesp-judge-key-") as tmpdir:
        image = render_pdf_page(path, Path(tmpdir), judge_page)
        normalized = extract_true_false_answer_key_from_image(image)
    if len(normalized) != 10 or any(not item for item in normalized):
        raise RuntimeError(f"could not extract true/false answer key from {path.name}: {normalized}")
    return normalized


def normalize_question_no(question: Dict[str, Any]) -> int:
    raw_no = int(question.get("no", 0))
    qtype = question.get("question_type", "")
    if qtype == "true_false" and 1 <= raw_no <= 10:
        return 15 + raw_no
    if qtype == "programming" and 1 <= raw_no <= 2:
        return 25 + raw_no
    return raw_no


def validate_glm_paper_payload(payload: Dict[str, Any], meta: Dict[str, int | str], known_concepts: set[str]) -> List[Dict[str, Any]]:
    paper = payload.get("paper", {})
    if int(paper.get("year", 0)) != meta["year"] or int(paper.get("month", 0)) != meta["month"]:
        raise RuntimeError("GLM paper metadata does not match the source PDF")
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise RuntimeError("GLM response missing questions list")

    normalized: List[Dict[str, Any]] = []
    seen: set[int] = set()
    expected_types = {
        **{no: "single_choice" for no in range(1, 16)},
        **{no: "true_false" for no in range(16, 26)},
        **{no: "programming" for no in range(26, 28)},
    }
    for raw in questions:
        if not isinstance(raw, dict):
            raise RuntimeError("GLM question item is not an object")
        qtype = str(raw.get("question_type", "")).strip()
        qno = normalize_question_no(raw)
        if qno not in expected_types:
            raise RuntimeError(f"unexpected question no: {qno}")
        if expected_types[qno] != qtype:
            raise RuntimeError(f"question {qno} has type {qtype}, expected {expected_types[qno]}")
        if qno in seen:
            raise RuntimeError(f"duplicate question no: {qno}")
        seen.add(qno)

        stem = str(raw.get("stem_markdown", "")).strip()
        if not stem:
            raise RuntimeError(f"question {qno} has empty stem_markdown")
        refs = [ref for ref in raw.get("concept_refs", []) if isinstance(ref, str) and ref in known_concepts]
        status = str(raw.get("extraction_status", "ok") or "ok").strip()
        if len(refs) != len(raw.get("concept_refs", [])):
            status = "needs_review"
        if status not in {"ok", "needs_review"}:
            status = "needs_review"
        answer = str(raw.get("answer", "") or "").strip()
        if qtype == "true_false":
            answer = ""
            status = "needs_review"

        normalized.append(
            {
                "no": qno,
                "question_type": qtype,
                "answer": answer,
                "analysis": str(raw.get("analysis", "") or "").strip(),
                "difficulty": str(raw.get("difficulty", "unknown") or "unknown").strip(),
                "concept_refs": refs,
                "extraction_status": status,
                "stem_markdown": strip_markdown_code_line_numbers(stem),
            }
        )
    missing = sorted(set(expected_types) - seen)
    if missing:
        raise RuntimeError(f"GLM response missing questions: {missing}")
    return sorted(normalized, key=lambda item: item["no"])


def validate_glm_question_group(
    payload: Dict[str, Any],
    expected_nos: List[int],
    qtype: str,
    known_concepts: set[str],
) -> List[Dict[str, Any]]:
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise RuntimeError("GLM group response missing questions list")
    expected = set(expected_nos)
    normalized: List[Dict[str, Any]] = []
    seen: set[int] = set()
    for raw in questions:
        if not isinstance(raw, dict):
            raise RuntimeError("GLM group question item is not an object")
        qno = normalize_question_no(raw)
        if qno not in expected:
            raise RuntimeError(f"unexpected question no in group: {qno}; expected {expected_nos}")
        if qno in seen:
            raise RuntimeError(f"duplicate question no in group: {qno}")
        seen.add(qno)
        actual_type = str(raw.get("question_type", "")).strip()
        if actual_type != qtype:
            raise RuntimeError(f"question {qno} has type {actual_type}, expected {qtype}")
        stem = str(raw.get("stem_markdown", "")).strip()
        if not stem:
            raise RuntimeError(f"question {qno} has empty stem_markdown")
        raw_refs = raw.get("concept_refs", [])
        refs = [ref for ref in raw_refs if isinstance(ref, str) and ref in known_concepts]
        status = str(raw.get("extraction_status", "ok") or "ok").strip()
        if len(refs) != len(raw_refs):
            status = "needs_review"
        if status not in {"ok", "needs_review"}:
            status = "needs_review"
        answer = str(raw.get("answer", "") or "").strip()
        if qtype == "true_false":
            answer = ""
            status = "needs_review"
        normalized.append(
            {
                "no": qno,
                "question_type": qtype,
                "answer": answer,
                "analysis": str(raw.get("analysis", "") or "").strip(),
                "difficulty": str(raw.get("difficulty", "unknown") or "unknown").strip(),
                "concept_refs": refs,
                "extraction_status": status,
                "stem_markdown": strip_markdown_code_line_numbers(stem),
            }
        )
    missing = sorted(expected - seen)
    if missing:
        raise RuntimeError(f"GLM group response missing questions: {missing}")
    return sorted(normalized, key=lambda item: item["no"])


def extract_question_group_with_glm(
    images: List[Path],
    page_texts: List[str],
    concepts: List[Dict[str, Any]],
    known_concepts: set[str],
    meta: Dict[str, int | str],
    page_numbers: List[int],
    qtype: str,
    expected_nos: List[int],
) -> List[Dict[str, Any]]:
    content: List[Dict[str, Any]] = []
    for page_no in page_numbers:
        content.append({"type": "image_url", "image_url": {"url": image_data_url(images[page_no - 1])}})
    prompt_pages = [(page_no, page_texts[page_no - 1]) for page_no in page_numbers]
    content.append({"type": "text", "text": build_glm_question_group_prompt(meta, prompt_pages, concepts, qtype, expected_nos)})
    response_text = glm_chat_completion(content)
    payload = extract_json_object(response_text)
    return validate_glm_question_group(payload, expected_nos, qtype, known_concepts)


def question_numbers_on_page(text: str) -> List[int]:
    return [int(value) for value in re.findall(r"第\s*(\d+)\s*题", text)]


def first_page_containing(page_texts: List[str], pattern: str, start: int = 1) -> int | None:
    regex = re.compile(pattern)
    for idx, text in enumerate(page_texts, start=1):
        if idx < start:
            continue
        if regex.search(text):
            return idx
    return None


def pages_for_expected_questions(page_texts: List[str], qtype: str, expected_nos: List[int]) -> List[int]:
    expected = set(expected_nos)
    first_judge = first_page_containing(page_texts, r"判断题")
    first_programming = first_page_containing(page_texts, r"编程题")
    pages: List[int] = []
    for idx, text in enumerate(page_texts, start=1):
        if qtype == "single_choice":
            if first_judge and idx >= first_judge:
                continue
            local_numbers = question_numbers_on_page(text)
        elif qtype == "true_false":
            if first_judge and idx < first_judge:
                continue
            if first_programming and idx > first_programming:
                continue
            local_numbers = question_numbers_on_page(text)
            local_numbers = [number + 15 for number in local_numbers]
        else:
            raise ValueError(f"unsupported qtype for page inference: {qtype}")
        if expected.intersection(local_numbers):
            pages.append(idx)
    return pages


def programming_pages(page_texts: List[str], local_no: int) -> List[int]:
    start = first_page_containing(page_texts, rf"3\.{local_no}\s+编程题\s+{local_no}")
    if start is None:
        raise RuntimeError(f"could not locate programming question {local_no}")
    next_start = first_page_containing(page_texts, rf"3\.{local_no + 1}\s+编程题\s+{local_no + 1}", start + 1)
    end = (next_start - 1) if next_start else len(page_texts)
    return list(range(start, end + 1))


def infer_glm_question_groups(page_texts: List[str]) -> List[tuple[List[int], str, List[int]]]:
    groups = [
        (pages_for_expected_questions(page_texts, "single_choice", list(range(1, 9))), "single_choice", list(range(1, 9))),
        (pages_for_expected_questions(page_texts, "single_choice", list(range(9, 16))), "single_choice", list(range(9, 16))),
        (pages_for_expected_questions(page_texts, "true_false", list(range(16, 26))), "true_false", list(range(16, 26))),
        (programming_pages(page_texts, 1), "programming", [26]),
        (programming_pages(page_texts, 2), "programming", [27]),
    ]
    for page_numbers, qtype, expected_nos in groups:
        if not page_numbers:
            raise RuntimeError(f"could not infer pages for {qtype} questions {expected_nos}")
    return groups


def extract_paper_with_glm(path: Path, meta: Dict[str, int | str], blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not os.environ.get("GLM_API_KEY", "").strip():
        raise RuntimeError("GLM_API_KEY is required for GLM-5V-Turbo paper ingestion")
    page_texts = pdf_page_texts(path)
    concepts = concept_candidates(blueprint)
    known_concepts = {item["slug"] for item in concepts}
    with tempfile.TemporaryDirectory(prefix="gesp-glm-pages-") as tmpdir:
        images = render_pdf_pages(path, Path(tmpdir))
        if len(images) != len(page_texts):
            raise RuntimeError(f"rendered page count {len(images)} does not match text page count {len(page_texts)}")
        groups = infer_glm_question_groups(page_texts)
        questions: List[Dict[str, Any]] = []
        for page_numbers, qtype, expected_nos in groups:
            questions.extend(
                extract_question_group_with_glm(
                    images,
                    page_texts,
                    concepts,
                    known_concepts,
                    meta,
                    page_numbers,
                    qtype,
                    expected_nos,
                )
            )
    return validate_glm_paper_payload(
        {"paper": {"year": meta["year"], "month": meta["month"], "level": meta["level"]}, "questions": questions},
        meta,
        known_concepts,
    )


def update_concept_question_refs(concept_slug: str, question_page: str) -> None:
    path = WIKI / "concepts" / f"{concept_slug}.md"
    text = read_text(path)
    m = re.search(r"question_refs: (\[.*?\])", text)
    refs = json.loads(m.group(1)) if m else []
    if question_page not in refs:
        refs.append(question_page)
    text = re.sub(r"question_refs: (\[.*?\])", f"question_refs: {json.dumps(refs, ensure_ascii=False)}", text)
    if "## Links" in text and f"[[{question_page}]]" not in text:
        text = text.rstrip() + f"\n- [[{question_page}]]\n"
    write_text(path, text)


def ingest_paper(path_str: str | None) -> None:
    init_repo()
    paths = resolve_input_paths(path_str, "paper")
    if not paths:
        print(json.dumps({"status": "no_input", "kind": "paper", "directory": str(RAW_PP)}, ensure_ascii=False))
        return
    blueprint = load_jsonish(STATE / "catalog" / "blueprint.yaml", {})
    for path in paths:
        text = pdf_text_via_pdftotext_layout(path) or pdf_text(path)
        meta = exam_meta(path, text)
        questions = extract_paper_with_glm(path, meta, blueprint)
        key = answer_key(text)
        if len(key) == 15:
            for question in questions:
                if question["question_type"] == "single_choice" and 1 <= question["no"] <= 15:
                    question["answer"] = key[question["no"] - 1]
        judge_key = extract_true_false_answer_key(path, pdf_page_texts(path))
        if len(judge_key) == 10:
            for question in questions:
                if question["question_type"] == "true_false" and 16 <= question["no"] <= 25:
                    question["answer"] = judge_key[question["no"] - 16]
                    if question["extraction_status"] == "needs_review":
                        question["extraction_status"] = "ok"
        for question in questions:
            if question["question_type"] == "programming":
                question["stem_markdown"] = repair_programming_samples(question["stem_markdown"], question["no"], text)
        question_pages = []
        for question in questions:
            qno = question["no"]
            qpage = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
            write_text(
                WIKI / "questions" / f"{qpage}.md",
                question_page_content(
                    meta,
                    qno,
                    question["question_type"],
                    question["stem_markdown"],
                    question["answer"],
                    question["concept_refs"],
                    question["extraction_status"],
                    question["analysis"],
                    question["difficulty"],
                    path.name,
                ),
            )
            question_pages.append(qpage)
            for ref in question["concept_refs"]:
                update_concept_question_refs(ref, qpage)
        exam_page = meta["exam_page"]
        write_text(
            WIKI / "exams" / f"{exam_page}.md",
            f"""---
title: "{exam_page}"
type: exam
exam: gesp
subject: cpp
level: {meta['level']}
year: {meta['year']}
month: {meta['month']}
question_refs: {json.dumps(question_pages, ensure_ascii=False)}
source: "{path.name}"
---

## Summary

GESP C++ 五级 {meta['year']} 年 {meta['month']:02d} 月真题，共 {len(question_pages)} 题，题型包含单选、判断和编程。

## Questions

{chr(10).join(f"- [[{page}]]" for page in question_pages)}
""",
        )
        blueprint.setdefault("papers", {})[meta["paper_id"]] = {
            "level": meta["level"],
            "source_file": path.name,
            "exam_page": exam_page,
            "question_count": len(question_pages),
        }
        update_index("Exams", exam_page, f"GESP C++ 五级 {meta['year']} 年 {meta['month']:02d} 月真题")
        for page in question_pages:
            update_index("Questions", page, f"{page} | {meta['year']}-{meta['month']:02d}")
        append_log("gesp-ingest-paper", f"摄入试卷 {path.name}", f"[[{exam_page}]]")
        archive_source(path, "paper")
        print(json.dumps({"status": "ok", "source_file": path.name, "engine": os.environ.get("GLM_VISION_MODEL", "glm-5v-turbo"), "exam_page": exam_page}, ensure_ascii=False))
    dump_jsonish(STATE / "catalog" / "blueprint.yaml", blueprint)


def parse_frontmatter(path: Path) -> Dict[str, str]:
    text = read_text(path)
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()[1:]
    data = {}
    for line in lines:
        if line == "---":
            break
        if ": " in line:
            k, v = line.split(": ", 1)
            data[k] = v.strip()
    return data


def extract_markdown_section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.M | re.S)
    return match.group(1).strip() if match else ""


def all_questions() -> List[Dict[str, str]]:
    items = []
    for path in sorted((WIKI / "questions").glob("question-*.md")):
        fm = parse_frontmatter(path)
        fm["path"] = str(path)
        body = read_text(path)
        fm["stem_text"] = extract_markdown_section(body, "Stem")
        items.append(fm)
    return items


def create_attempt(filters: Dict[str, object], selected: List[Dict[str, str]]) -> str:
    attempt_id = datetime.now().strftime("attempt-%Y%m%d-%H%M%S")
    payload = {
        "attempt_id": attempt_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filters": filters,
        "questions": [
            {
                "question_id": item["question_id"].strip('"'),
                "concept_refs": json.loads(item.get("concept_refs", "[]")),
                "question_type": item.get("question_type", ""),
                "correct_answer": json.loads(item.get("answer", '""')),
                "stem_text": item.get("stem_text", ""),
            }
            for item in selected
        ],
        "answers": {},
        "grading": [],
    }
    dump_jsonish(STATE / "attempts" / f"{attempt_id}.yaml", payload)
    return attempt_id


def practice(args) -> None:
    questions = all_questions()
    if args.paper:
        year, month = args.paper.split("-")
        questions = [q for q in questions if q.get("year") == year and int(q.get("month", 0)) == int(month)]
    if args.concepts:
        wanted = set(args.concepts.split(","))
        questions = [q for q in questions if wanted.intersection(set(json.loads(q.get("concept_refs", "[]"))))]
    if args.wrong_only:
        candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
        weak = {c["concept_id"] for c in candidate.get("concepts", []) if c["mastery_level"] == "weak"}
        questions = [q for q in questions if weak.intersection(set(json.loads(q.get("concept_refs", "[]"))))]
    count = min(args.count, len(questions))
    selected = questions[:count]
    attempt_id = create_attempt({"concepts": args.concepts, "paper": args.paper, "wrong_only": args.wrong_only, "count": count}, selected)
    lines = [f"# GESP Practice", "", f"attempt_id: {attempt_id}", ""]
    for idx, q in enumerate(selected, start=1):
        qid = q["question_id"].strip('"')
        qtype = q.get("question_type", "")
        refs = ", ".join(json.loads(q.get("concept_refs", "[]"))) or "N/A"
        lines.extend(
            [
                f"## {idx}. {qid}",
                f"- question_type: {qtype}",
                f"- concept_refs: {refs}",
                "",
                q.get("stem_text", "未找到题面。"),
                "",
            ]
        )
    print("\n".join(lines))


def grade(args) -> None:
    path = STATE / "attempts" / f"{args.attempt_id}.yaml"
    attempt = load_jsonish(path, {})
    answers = {}
    for pair in args.answers:
        if "=" in pair:
            k, v = pair.split("=", 1)
            answers[k] = v
    attempt["answers"].update(answers)
    grading = []
    candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
    concept_map = {entry["concept_id"]: entry for entry in candidate.get("concepts", [])}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in attempt.get("questions", []):
        qid = item["question_id"]
        qtype = item["question_type"]
        expected = item.get("correct_answer", "")
        given = answers.get(qid, "")
        if qtype == "single_choice" and expected:
            correct = given == expected
            score = 1 if correct else 0
            review_status = "auto"
            reason = "客观题自动判分。"
            confidence = 1.0
        elif qtype == "true_false" and expected:
            correct = given.lower() == expected.lower()
            score = 1 if correct else 0
            review_status = "auto"
            reason = "判断题按标准答案自动判分。"
            confidence = 1.0
        else:
            correct = False
            score = 0
            review_status = "needs_manual_review"
            reason = "缺少可靠标准答案或属于编程题，仅提供待复核记录。"
            confidence = 0.2
        grading.append(
            {
                "question_id": qid,
                "concept_refs": item.get("concept_refs", []),
                "result": "correct" if correct else "incorrect",
                "score": score,
                "confidence": confidence,
                "judgement_reason": reason,
                "review_status": review_status,
            }
        )
        for ref in item.get("concept_refs", []):
            entry = concept_map.setdefault(ref, {"concept_id": ref, "mastery_level": "unknown", "attempt_count": 0, "correct_count": 0, "last_attempt_at": "", "last_question_ids": []})
            entry["attempt_count"] += 1
            entry["correct_count"] += score
            entry["last_attempt_at"] = now
            entry["last_question_ids"] = [qid] + entry.get("last_question_ids", [])[:4]
            ratio = entry["correct_count"] / max(entry["attempt_count"], 1)
            if ratio == 0:
                entry["mastery_level"] = "weak"
            elif ratio < 0.6:
                entry["mastery_level"] = "developing"
            else:
                entry["mastery_level"] = "solid"
    attempt["grading"] = grading
    dump_jsonish(path, attempt)
    candidate["concepts"] = list(concept_map.values())
    dump_jsonish(STATE / "candidates" / "default.yaml", candidate)
    print(json.dumps({"attempt_id": args.attempt_id, "graded": len(grading)}, ensure_ascii=False, indent=2))


def report(args) -> None:
    candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
    concepts = candidate.get("concepts", [])
    if args.concept:
        concepts = [c for c in concepts if c["concept_id"] == args.concept]
    if args.weak_only:
        concepts = [c for c in concepts if c["mastery_level"] in {"unknown", "weak", "developing"}]
    concepts.sort(key=lambda x: (x["mastery_level"], x["attempt_count"]))
    lines = ["# GESP Report", ""]
    for item in concepts:
        ratio = f"{item['correct_count']}/{item['attempt_count']}" if item["attempt_count"] else "0/0"
        lines.extend(
            [
                f"## {item['concept_id']}",
                f"- mastery_level: {item['mastery_level']}",
                f"- recent_attempt_count: {item['attempt_count']}",
                f"- recent_correct_rate: {ratio}",
                f"- last_attempt_at: {item['last_attempt_at'] or 'N/A'}",
                f"- last_question_ids: {', '.join(item['last_question_ids']) if item['last_question_ids'] else 'N/A'}",
                "",
            ]
        )
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p_outline = sub.add_parser("ingest-outline")
    p_outline.add_argument("path", nargs="?")
    p_paper = sub.add_parser("ingest-paper")
    p_paper.add_argument("path", nargs="?")
    p_practice = sub.add_parser("practice")
    p_practice.add_argument("--concepts", default="")
    p_practice.add_argument("--count", type=int, default=5)
    p_practice.add_argument("--paper", default="")
    p_practice.add_argument("--wrong-only", action="store_true")
    p_grade = sub.add_parser("grade")
    p_grade.add_argument("attempt_id")
    p_grade.add_argument("--answers", nargs="*", default=[])
    p_report = sub.add_parser("report")
    p_report.add_argument("--concept", default="")
    p_report.add_argument("--weak-only", action="store_true")
    args = parser.parse_args()
    if args.cmd == "init":
        init_repo()
    elif args.cmd == "ingest-outline":
        ingest_outline(args.path)
    elif args.cmd == "ingest-paper":
        ingest_paper(args.path)
    elif args.cmd == "practice":
        practice(args)
    elif args.cmd == "grade":
        grade(args)
    elif args.cmd == "report":
        report(args)


if __name__ == "__main__":
    main()
