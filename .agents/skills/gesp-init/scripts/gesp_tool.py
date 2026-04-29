#!/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "raw"
RAW_SYL = RAW / "syl"
RAW_PP = RAW / "pp"
RAW_ARCHIVE = RAW / "09-archive"
WIKI = ROOT / "wiki"
STATE = ROOT / "state"
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


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\u3000", " ").replace("\xa0", " ")
    lines = []
    for raw in text.splitlines():
        line = raw.rstrip()
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def markdown_text(path: Path) -> str:
    return normalize_markdown(read_text(path))


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
        if path.suffix.lower() != ".md":
            raise ValueError(f"unsupported input file {path}; only Markdown (.md) files are supported")
        return [path]
    if kind == "outline":
        directory = RAW_SYL
    else:
        directory = RAW_PP
    return sorted(directory.glob("*.md"))


def heading_pattern(title: str) -> re.Pattern[str]:
    return re.compile(rf"^#{{1,6}}\s*{re.escape(title)}\s*$", re.M)


def markdown_section(text: str, title: str) -> str:
    match = heading_pattern(title).search(text)
    if not match:
        return ""
    start = match.end()
    rest = text[start:]
    current_level = len(match.group(0)) - len(match.group(0).lstrip("#"))
    next_heading = re.search(rf"^#{{1,{current_level}}}\s+", rest, re.M)
    section_text = rest[: next_heading.start()] if next_heading else rest
    return normalize_markdown(section_text)


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
        print(json.dumps({"status": "no_input", "kind": "outline", "directory": str(RAW_SYL), "expected_extension": ".md"}, ensure_ascii=False))
        return
    for path in paths:
        text = markdown_text(path)
        level = slug_level(path, text)
        overview = markdown_section(text, "考核目标") or "未可靠提取考核目标。"
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
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月", text)
    if not m:
        m = re.search(r"(\d{4})[_ -](\d{1,2})", path.stem)
    if not m:
        raise ValueError(f"missing exam year/month in markdown content: {path}")
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
    if m:
        return re.findall(r"[A-D]", m.group(1))
    table = re.search(r"^\|\s*答案\s*\|(.+?)\|\s*$", text, re.M)
    if not table:
        return []
    return [token.strip() for token in table.group(1).split("|") if token.strip() in {"A", "B", "C", "D"}]


def tf_answer_key(text: str) -> List[str]:
    table = re.search(r"^\|\s*答案\s*\|(.+?)\|\s*$", text, re.M)
    if not table:
        return []
    return [token.strip().upper() for token in table.group(1).split("|") if token.strip().upper() in {"T", "F"}]


def require_section(text: str, title: str, path: Path) -> str:
    section_text = markdown_section(text, title)
    if not section_text:
        raise ValueError(f"missing markdown heading '{title}' in {path}")
    return section_text


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
        if re.match(r"^#{2,6}\s*3\.\d+\s*编程题", line):
            continue
        line = re.sub(r"^- \[ \] ", "", line)
        line = re.sub(r"^- ", "", line, count=1)
        line = re.sub(r"^#{2,6}\s+", "", line)
        if re.fullmatch(r"#{2,6}", line.strip()):
            continue
        lines.append(line)
    text = "\n".join(lines).strip()
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
        match = re.match(r"^([A-D])\.(?:\s+.*)?$", line)
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


def question_page_content(meta: Dict[str, int | str], qno: int, qtype: str, stem: str, answer: str, concept_refs: List[str], extraction_status: str) -> str:
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
analysis: ""
concept_refs: {json.dumps(concept_refs, ensure_ascii=False)}
difficulty: "unknown"
extraction_status: {extraction_status}
---

## Stem

{stem}

## Answer

{answer or "未可靠提取。"}

## Analysis

首版未生成解析。

## Links

{chr(10).join(links)}
"""


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
        print(json.dumps({"status": "no_input", "kind": "paper", "directory": str(RAW_PP), "expected_extension": ".md"}, ensure_ascii=False))
        return
    blueprint = load_jsonish(STATE / "catalog" / "blueprint.yaml", {})
    for path in paths:
        text = markdown_text(path)
        meta = exam_meta(path, text)
        single = require_section(text, "单选题", path)
        judge = require_section(text, "判断题", path)
        programming = require_section(text, "编程题", path)
        key = answer_key(single)
        judge_key = tf_answer_key(judge)
        question_pages = []
        single_blocks = parse_question_blocks(single)
        for idx, match in enumerate(single_blocks):
            local_no = int(match.group(1))
            start = match.start()
            end = single_blocks[idx + 1].start() if idx + 1 < len(single_blocks) else len(single)
            stem = cleanup_question_markdown(single[start:end])
            qno = local_no
            qpage = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
            refs = map_concepts(stem)
            answer = key[local_no - 1] if local_no - 1 < len(key) else ""
            status = single_choice_extraction_status(stem, answer)
            write_text(WIKI / "questions" / f"{qpage}.md", question_page_content(meta, qno, "single_choice", stem, answer, refs, status))
            question_pages.append(qpage)
            for ref in refs:
                update_concept_question_refs(ref, qpage)
        judge_blocks = parse_question_blocks(judge)
        for idx, match in enumerate(judge_blocks):
            local_no = int(match.group(1))
            start = match.start()
            end = judge_blocks[idx + 1].start() if idx + 1 < len(judge_blocks) else len(judge)
            stem = cleanup_question_markdown(judge[start:end])
            qno = 15 + local_no
            qpage = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
            refs = map_concepts(stem)
            answer = judge_key[local_no - 1] if local_no - 1 < len(judge_key) else ""
            status = "ok" if answer else "needs_review"
            write_text(WIKI / "questions" / f"{qpage}.md", question_page_content(meta, qno, "true_false", stem, answer, refs, status))
            question_pages.append(qpage)
            for ref in refs:
                update_concept_question_refs(ref, qpage)
        prog_matches = list(re.finditer(r"3\.(\d+)\s*编程题\s*(\d+)", programming))
        for idx, match in enumerate(prog_matches):
            local_no = int(match.group(2))
            start = match.start()
            end = prog_matches[idx + 1].start() if idx + 1 < len(prog_matches) else len(programming)
            stem = cleanup_question_markdown(programming[start:end])
            qno = 25 + local_no
            qpage = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
            refs = map_concepts(stem)
            write_text(WIKI / "questions" / f"{qpage}.md", question_page_content(meta, qno, "programming", stem, "", refs, "needs_review"))
            question_pages.append(qpage)
            for ref in refs:
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
        print(json.dumps({"status": "ok", "source_file": path.name, "engine": "markdown", "exam_page": exam_page}, ensure_ascii=False))
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
