#!/Users/mao3/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from urllib import error, request
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "raw"
RAW_SYL = RAW / "syl"
RAW_PP = RAW / "pp"
RAW_ARCHIVE = RAW / "09-archive"
WIKI = ROOT / "wiki"
STATE = ROOT / "state"
CATALOG = STATE / "catalog"
PAPER_INGEST = CATALOG / "paper_ingest"
PAPER_REQUESTS = PAPER_INGEST / "requests"
PAPER_RESULTS = PAPER_INGEST / "results"
PAPER_REVIEWS = PAPER_INGEST / "reviews"
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_OUTLINE_MODEL = "deepseek-v4-flash"
DEFAULT_PAPER_MODEL = "deepseek-v4-flash"
PAPER_CLASSIFICATION_BATCH_SIZE = 50
LEGACY_CONCEPT_ALIASES = {
    "concept-number-theory": "concept-elementary-number-theory",
    "concept-number-theory-primes": "concept-elementary-number-theory",
    "concept-number-theory-gcd-lcm": "concept-elementary-number-theory",
    "concept-number-theory-mod": "concept-elementary-number-theory",
    "concept-number-theory-factorization": "concept-elementary-number-theory",
    "concept-number-theory-sieve": "concept-elementary-number-theory",
    "concept-complexity": "concept-algorithm-complexity",
    "concept-complexity-time": "concept-algorithm-complexity",
    "concept-complexity-space": "concept-algorithm-complexity",
    "concept-complexity-orders": "concept-algorithm-complexity",
    "concept-cpp-high-precision": "concept-high-precision-cpp",
    "concept-cpp-high-precision-add-sub": "concept-high-precision-cpp",
    "concept-cpp-high-precision-mul": "concept-high-precision-cpp",
    "concept-cpp-high-precision-div": "concept-high-precision-cpp",
    "concept-linked-list-singly": "concept-linked-list",
    "concept-linked-list-doubly": "concept-linked-list",
    "concept-linked-list-circular": "concept-linked-list",
    "concept-binary-search-index": "concept-binary-algorithm",
    "concept-binary-search-answer": "concept-binary-algorithm",
    "concept-binary-search": "concept-binary-algorithm",
    "concept-recursion-basics": "concept-recursion",
    "concept-recursion-backtracking": "concept-recursion",
    "concept-divide-and-conquer": "concept-divide-conquer",
    "concept-divide-and-conquer-merge": "concept-divide-conquer",
    "concept-divide-and-conquer-quick": "concept-divide-conquer",
    "concept-greedy-strategy": "concept-greedy",
    "concept-greedy-proof": "concept-greedy",
}
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
    CATALOG,
    PAPER_REQUESTS,
    PAPER_RESULTS,
    PAPER_REVIEWS,
]

LEVEL5_CONCEPTS = [
    {
        "slug": "concept-number-theory",
        "title": "concept-number-theory",
        "name": "初等数论",
        "module": "初等数论",
        "summary": "覆盖 GESP 五级中的初等数论总览，包含素数、最大公约数、模运算、质因数分解与筛法等子主题。",
        "prerequisites": [],
        "parent_concept": "",
        "keywords": ["数论", "质数", "素数", "合数", "公约数", "同余", "模", "筛法"],
    },
    {
        "slug": "concept-number-theory-primes",
        "title": "concept-number-theory-primes",
        "name": "素数与合数",
        "module": "初等数论",
        "summary": "覆盖素数、合数、素性判定与约数个数等基础性质。",
        "prerequisites": [],
        "parent_concept": "concept-number-theory",
        "keywords": ["素数", "质数", "合数", "素性", "约数个数", "prime"],
    },
    {
        "slug": "concept-number-theory-gcd-lcm",
        "title": "concept-number-theory-gcd-lcm",
        "name": "最大公约数与最小公倍数",
        "module": "初等数论",
        "summary": "覆盖欧几里得算法、gcd/lcm、互质及相关构造。",
        "prerequisites": [],
        "parent_concept": "concept-number-theory",
        "keywords": ["最大公约数", "最小公倍数", "公约数", "公倍数", "互质", "欧几里得", "gcd", "lcm"],
    },
    {
        "slug": "concept-number-theory-mod",
        "title": "concept-number-theory-mod",
        "name": "同余与模运算",
        "module": "初等数论",
        "summary": "覆盖同余、模运算、余数性质与循环节等常见题型。",
        "prerequisites": [],
        "parent_concept": "concept-number-theory",
        "keywords": ["同余", "模运算", "取模", "余数", "mod", "%", "循环节"],
    },
    {
        "slug": "concept-number-theory-factorization",
        "title": "concept-number-theory-factorization",
        "name": "质因数分解",
        "module": "初等数论",
        "summary": "覆盖质因数分解、唯一分解定理以及由分解推导约数和倍数性质。",
        "prerequisites": ["concept-number-theory-primes"],
        "parent_concept": "concept-number-theory",
        "keywords": ["质因数分解", "唯一分解定理", "因数分解", "factor"],
    },
    {
        "slug": "concept-number-theory-sieve",
        "title": "concept-number-theory-sieve",
        "name": "素数筛法",
        "module": "初等数论",
        "summary": "覆盖埃氏筛、线性筛及基于筛法的计数和预处理题。",
        "prerequisites": ["concept-number-theory-primes"],
        "parent_concept": "concept-number-theory",
        "keywords": ["筛法", "埃氏筛", "线性筛", "筛素数"],
    },
    {
        "slug": "concept-complexity",
        "title": "concept-complexity",
        "name": "算法复杂度估算方法",
        "module": "算法复杂度估算方法",
        "summary": "覆盖时间复杂度、空间复杂度及常见复杂度量级判断。",
        "prerequisites": [],
        "parent_concept": "",
        "keywords": ["复杂度", "时间复杂度", "空间复杂度", "对数", "多项式", "O("],
    },
    {
        "slug": "concept-complexity-time",
        "title": "concept-complexity-time",
        "name": "时间复杂度",
        "module": "算法复杂度估算方法",
        "summary": "覆盖循环、递归与常见算法结构的时间复杂度分析。",
        "prerequisites": [],
        "parent_concept": "concept-complexity",
        "keywords": ["时间复杂度", "O(", "复杂度分析", "运行时间", "log n", "n log n"],
    },
    {
        "slug": "concept-complexity-space",
        "title": "concept-complexity-space",
        "name": "空间复杂度",
        "module": "算法复杂度估算方法",
        "summary": "覆盖额外存储开销、递归栈与辅助数组的空间复杂度分析。",
        "prerequisites": [],
        "parent_concept": "concept-complexity",
        "keywords": ["空间复杂度", "额外空间", "辅助数组", "递归栈"],
    },
    {
        "slug": "concept-complexity-orders",
        "title": "concept-complexity-orders",
        "name": "复杂度量级判断",
        "module": "算法复杂度估算方法",
        "summary": "覆盖常见量级比较、上界估算与是否可通过的判断。",
        "prerequisites": [],
        "parent_concept": "concept-complexity",
        "keywords": ["复杂度量级", "多项式", "对数", "线性", "平方", "指数"],
    },
    {
        "slug": "concept-cpp-high-precision",
        "title": "concept-cpp-high-precision",
        "name": "C++高精度运算",
        "module": "C++高精度运算",
        "summary": "覆盖高精度加减乘除与以数组或序列模拟大整数。",
        "prerequisites": [],
        "parent_concept": "",
        "keywords": ["高精度", "大整数", "进位", "借位", "vector<int>", "carry", "rem"],
    },
    {
        "slug": "concept-cpp-high-precision-add-sub",
        "title": "concept-cpp-high-precision-add-sub",
        "name": "高精度加减法",
        "module": "C++高精度运算",
        "summary": "覆盖大整数加法、减法、进位与借位处理。",
        "prerequisites": [],
        "parent_concept": "concept-cpp-high-precision",
        "keywords": ["高精度加法", "高精度减法", "进位", "借位", "carry"],
    },
    {
        "slug": "concept-cpp-high-precision-mul",
        "title": "concept-cpp-high-precision-mul",
        "name": "高精度乘法",
        "module": "C++高精度运算",
        "summary": "覆盖高精度乘低精度与高精度乘高精度的模拟实现。",
        "prerequisites": ["concept-cpp-high-precision-add-sub"],
        "parent_concept": "concept-cpp-high-precision",
        "keywords": ["高精度乘法", "大整数乘法", "乘低精度", "乘高精度"],
    },
    {
        "slug": "concept-cpp-high-precision-div",
        "title": "concept-cpp-high-precision-div",
        "name": "高精度除法",
        "module": "C++高精度运算",
        "summary": "覆盖高精度除低精度、商与余数处理。",
        "prerequisites": ["concept-cpp-high-precision-add-sub"],
        "parent_concept": "concept-cpp-high-precision",
        "keywords": ["高精度除法", "余数", "商", "rem"],
    },
    {
        "slug": "concept-linked-list",
        "title": "concept-linked-list",
        "name": "链表",
        "module": "链表",
        "summary": "覆盖单链表、双链表、循环链表的创建、插入、删除、遍历与查找。",
        "prerequisites": [],
        "parent_concept": "",
        "keywords": ["链表", "单链表", "双链表", "循环链表", "结点", "Node", "prev", "next", "哑结点"],
    },
    {
        "slug": "concept-linked-list-singly",
        "title": "concept-linked-list-singly",
        "name": "单链表",
        "module": "链表",
        "summary": "覆盖单链表的定义、遍历、插入、删除与头结点处理。",
        "prerequisites": [],
        "parent_concept": "concept-linked-list",
        "keywords": ["单链表", "next", "头插", "尾插", "删除结点"],
    },
    {
        "slug": "concept-linked-list-doubly",
        "title": "concept-linked-list-doubly",
        "name": "双链表",
        "module": "链表",
        "summary": "覆盖双链表的前驱后继维护与双向遍历。",
        "prerequisites": ["concept-linked-list-singly"],
        "parent_concept": "concept-linked-list",
        "keywords": ["双链表", "prev", "next", "双向遍历"],
    },
    {
        "slug": "concept-linked-list-circular",
        "title": "concept-linked-list-circular",
        "name": "循环链表",
        "module": "链表",
        "summary": "覆盖循环链表结构、终止条件与特殊边界处理。",
        "prerequisites": ["concept-linked-list-singly"],
        "parent_concept": "concept-linked-list",
        "keywords": ["循环链表", "环形链表", "尾指向头"],
    },
    {
        "slug": "concept-binary-search",
        "title": "concept-binary-search",
        "name": "二分算法",
        "module": "二分算法",
        "summary": "覆盖二分查找、二分答案以及边界收缩。",
        "prerequisites": ["concept-complexity"],
        "parent_concept": "",
        "keywords": ["二分", "二分查找", "二分答案", "mid", "有序", "lower_bound", "upper_bound"],
    },
    {
        "slug": "concept-binary-search-index",
        "title": "concept-binary-search-index",
        "name": "二分查找",
        "module": "二分算法",
        "summary": "覆盖有序序列上的查找、上下界与边界收缩。",
        "prerequisites": ["concept-complexity-time"],
        "parent_concept": "concept-binary-search",
        "keywords": ["二分查找", "lower_bound", "upper_bound", "mid", "有序"],
    },
    {
        "slug": "concept-binary-search-answer",
        "title": "concept-binary-search-answer",
        "name": "二分答案",
        "module": "二分算法",
        "summary": "覆盖单调性判定下的答案空间二分。",
        "prerequisites": ["concept-binary-search-index"],
        "parent_concept": "concept-binary-search",
        "keywords": ["二分答案", "单调性", "check 函数", "答案空间"],
    },
    {
        "slug": "concept-recursion",
        "title": "concept-recursion",
        "name": "递归算法",
        "module": "递归算法",
        "summary": "覆盖递归定义、递归终止条件、复杂度分析与常见优化。",
        "prerequisites": ["concept-complexity"],
        "parent_concept": "",
        "keywords": ["递归", "递归函数", "dfs", "回溯", "fib"],
    },
    {
        "slug": "concept-recursion-basics",
        "title": "concept-recursion-basics",
        "name": "递归基础",
        "module": "递归算法",
        "summary": "覆盖递归定义、递归出口与参数设计。",
        "prerequisites": ["concept-complexity-time"],
        "parent_concept": "concept-recursion",
        "keywords": ["递归", "递归出口", "递归函数", "fib"],
    },
    {
        "slug": "concept-recursion-backtracking",
        "title": "concept-recursion-backtracking",
        "name": "递归搜索与回溯",
        "module": "递归算法",
        "summary": "覆盖 DFS、状态恢复与搜索树剪枝。",
        "prerequisites": ["concept-recursion-basics"],
        "parent_concept": "concept-recursion",
        "keywords": ["dfs", "回溯", "搜索树", "剪枝"],
    },
    {
        "slug": "concept-divide-and-conquer",
        "title": "concept-divide-and-conquer",
        "name": "分治算法",
        "module": "分治算法",
        "summary": "覆盖归并排序、快速排序等典型分治结构与递归拆分。",
        "prerequisites": ["concept-recursion", "concept-complexity"],
        "parent_concept": "",
        "keywords": ["分治", "归并排序", "快速排序", "merge sort", "quick sort", "pivot", "枢轴"],
    },
    {
        "slug": "concept-divide-and-conquer-merge",
        "title": "concept-divide-and-conquer-merge",
        "name": "归并排序",
        "module": "分治算法",
        "summary": "覆盖分治划分、归并过程与稳定排序。",
        "prerequisites": ["concept-recursion-basics", "concept-complexity-time"],
        "parent_concept": "concept-divide-and-conquer",
        "keywords": ["归并排序", "merge sort", "归并", "稳定排序"],
    },
    {
        "slug": "concept-divide-and-conquer-quick",
        "title": "concept-divide-and-conquer-quick",
        "name": "快速排序",
        "module": "分治算法",
        "summary": "覆盖枢轴划分、递归分治与最坏情况分析。",
        "prerequisites": ["concept-recursion-basics", "concept-complexity-time"],
        "parent_concept": "concept-divide-and-conquer",
        "keywords": ["快速排序", "quick sort", "pivot", "枢轴", "划分"],
    },
    {
        "slug": "concept-greedy",
        "title": "concept-greedy",
        "name": "贪心算法",
        "module": "贪心算法",
        "summary": "覆盖贪心选择、局部最优、最优子结构与常见证明思路。",
        "prerequisites": ["concept-complexity"],
        "parent_concept": "",
        "keywords": ["贪心", "最优子结构", "局部最优"],
    },
    {
        "slug": "concept-greedy-strategy",
        "title": "concept-greedy-strategy",
        "name": "贪心策略设计",
        "module": "贪心算法",
        "summary": "覆盖局部最优选择、排序后贪心与策略构造。",
        "prerequisites": ["concept-complexity-orders"],
        "parent_concept": "concept-greedy",
        "keywords": ["贪心策略", "局部最优", "排序后贪心"],
    },
    {
        "slug": "concept-greedy-proof",
        "title": "concept-greedy-proof",
        "name": "贪心正确性证明",
        "module": "贪心算法",
        "summary": "覆盖交换论证、最优子结构与贪心正确性分析。",
        "prerequisites": ["concept-greedy-strategy"],
        "parent_concept": "concept-greedy",
        "keywords": ["交换论证", "最优子结构", "正确性证明", "贪心证明"],
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
    lines = [raw.rstrip() for raw in text.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def markdown_text(path: Path) -> str:
    return normalize_markdown(read_text(path))


def concept_definitions(level: int) -> List[Dict[str, object]]:
    if level != 5:
        raise ValueError(f"unsupported level {level}")
    return [dict(item) for item in LEVEL5_CONCEPTS]


def finalize_concepts(items: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    mapping: Dict[str, Dict[str, object]] = {}
    for raw in items:
        slug = str(raw["slug"]).strip()
        if not re.fullmatch(r"concept-[a-z0-9-]+", slug):
            raise ValueError(f"invalid concept slug: {slug}")
        if slug in mapping:
            raise ValueError(f"duplicate concept slug: {slug}")
        mapping[slug] = {
            "slug": slug,
            "title": str(raw.get("title") or slug),
            "name": str(raw["name"]).strip(),
            "module": str(raw.get("module") or raw["name"]).strip(),
            "summary": str(raw.get("summary", "")).strip(),
            "prerequisites": [str(item).strip() for item in raw.get("prerequisites", []) if str(item).strip()],
            "parent_concept": str(raw.get("parent_concept", "")).strip(),
            "keywords": [str(item).strip() for item in raw.get("keywords", []) if str(item).strip()],
        }
    for item in mapping.values():
        parent = item["parent_concept"]
        if parent and parent not in mapping:
            raise ValueError(f"unknown parent concept '{parent}' for {item['slug']}")
        for prereq in item["prerequisites"]:
            if prereq not in mapping:
                raise ValueError(f"unknown prerequisite '{prereq}' for {item['slug']}")
    for item in mapping.values():
        item["children"] = sorted([child["slug"] for child in mapping.values() if child["parent_concept"] == item["slug"]])
        item["is_leaf"] = len(item["children"]) == 0
    return mapping


def concept_map(level: int, blueprint: Dict[str, object] | None = None) -> Dict[str, Dict[str, object]]:
    current = ensure_blueprint_schema(blueprint or load_jsonish(CATALOG / "blueprint.yaml", {}))
    concept_items = []
    for slug, meta in current.get("concepts", {}).items():
        if int(meta.get("level", 0) or 0) != level:
            continue
        concept_items.append(
            {
                "slug": slug,
                "title": meta.get("title", slug),
                "name": meta.get("name", slug),
                "module": meta.get("module", meta.get("name", slug)),
                "summary": meta.get("summary", ""),
                "prerequisites": meta.get("prerequisites", []),
                "parent_concept": meta.get("parent_concept", ""),
                "keywords": meta.get("keywords", []),
            }
        )
    if concept_items:
        return finalize_concepts(concept_items)
    return finalize_concepts(concept_definitions(level))


def root_concepts(level: int) -> List[Dict[str, object]]:
    return [item for item in concept_map(level).values() if not item["parent_concept"]]


def descendants(slug: str, cmap: Dict[str, Dict[str, object]]) -> List[str]:
    found: List[str] = []
    stack = list(cmap.get(slug, {}).get("children", []))
    while stack:
        current = stack.pop()
        found.append(current)
        stack.extend(cmap.get(current, {}).get("children", []))
    return found


def is_parent_child_pair(a: str, b: str, cmap: Dict[str, Dict[str, object]]) -> bool:
    if not a or not b or a == b:
        return False
    return b in descendants(a, cmap) or a in descendants(b, cmap)


def ensure_index() -> None:
    index_path = WIKI / "index.md"
    text = read_text(index_path) or "# Wiki Index\n\n## Concepts\n\n## Syntheses\n"
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


def ensure_blueprint_schema(blueprint: Dict[str, object]) -> Dict[str, object]:
    blueprint.setdefault("exam", "gesp")
    blueprint.setdefault("subject", "cpp")
    blueprint.setdefault("levels", {})
    blueprint.setdefault("papers", {})
    blueprint.setdefault("concepts", {})
    blueprint.setdefault("question_types", ["single_choice", "true_false", "programming"])
    blueprint.setdefault(
        "naming",
        {
            "exam_page": "wiki/exams/exam-<year>-<month>.md",
            "question_page": "wiki/questions/question-<year>-<month>-<no>.md",
        },
    )
    blueprint.setdefault(
        "classification",
        {
            "mode": "llm_manual_import",
            "prefer_child_concepts": True,
            "fallback_to_parent": True,
            "invalid_policy": "needs_review",
            "provider": "deepseek",
            "outline_model": DEFAULT_OUTLINE_MODEL,
            "paper_model": DEFAULT_PAPER_MODEL,
        },
    )
    return blueprint


def deepseek_api_key() -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("missing DEEPSEEK_API_KEY environment variable")
    return api_key


def deepseek_chat_json(messages: List[Dict[str, str]], model: str) -> Dict[str, object]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        DEEPSEEK_ENDPOINT,
        data=data,
        headers={
            "Authorization": f"Bearer {deepseek_api_key()}",
            "Content-Type": "application/json",
            "Idempotency-Key": str(uuid4()),
        },
        method="POST",
    )
    last_exc: Exception | None = None
    body: Dict[str, Any] | None = None
    for attempt in range(5):
        try:
            with request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            break
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429 and attempt < 4:
                last_exc = exc
                time.sleep(8 * (attempt + 1))
                continue
            raise RuntimeError(f"deepseek api http error {exc.code}: {detail}") from exc
        except (error.URLError, TimeoutError) as exc:
            last_exc = exc
            if attempt == 4:
                raise RuntimeError(f"deepseek api network error: {exc}") from exc
            time.sleep(2 * (attempt + 1))
    if body is None:
        raise RuntimeError(f"deepseek api network error: {last_exc}")
    try:
        content = body["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            sanitized = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", content)
            return json.loads(sanitized)
    except Exception as exc:
        raise RuntimeError(f"invalid deepseek response payload: {body}") from exc


def generate_outline_concepts(level: int, outline_text: str, outline_name: str, model: str) -> Dict[str, Dict[str, object]]:
    system_prompt = """
你是 GESP C++ 大纲拆解助手。你的任务是把考试大纲拆成可复用、可挂题、可诊断掌握度的 concept 树。

必须遵守：
1. 返回 JSON 对象，顶层字段固定为 concepts。
2. 每个 concept 必须包含：slug, name, module, parent_concept, prerequisites, summary, keywords。
3. slug 必须使用英文 kebab-case，并以 concept- 开头。
4. parent_concept 为空字符串表示顶层 concept。
5. 大知识点必须拆成若干子 concept，不要只拆数论，其他同等规模主题也要拆。
6. prerequisites 只能引用同一份输出中的 slug。
7. keywords 使用中文词语数组，便于后续题目标注。
8. 不要发明大纲中完全不存在的主题，但可以把大纲中明显混在一起的大点按教学可复用粒度拆成子点。
9. 父 concept 本身保留为一个可挂题节点，因此即使有子 concept 也保留父节点。
10. summary 用中文，简短说明该 concept 的考查范围。
"""
    user_prompt = f"""
考试：GESP C++ {level} 级
来源文件：{outline_name}

请基于以下 Markdown 大纲直接拆分 concept 树，并覆盖所有主要知识模块：

```markdown
{outline_text}
```
"""
    result = deepseek_chat_json(
        [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        model,
    )
    concepts = result.get("concepts", [])
    if not isinstance(concepts, list) or not concepts:
        raise ValueError(f"deepseek outline result missing concepts: {result}")
    return finalize_concepts(concepts)


def init_state() -> None:
    blueprint_path = CATALOG / "blueprint.yaml"
    if not blueprint_path.exists():
        dump_jsonish(blueprint_path, ensure_blueprint_schema({}))
    else:
        dump_jsonish(blueprint_path, ensure_blueprint_schema(load_jsonish(blueprint_path, {})))
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


def rewrite_index_section(section: str, entries: List[tuple[str, str]]) -> None:
    text = read_text(WIKI / "index.md")
    lines = text.splitlines()
    heading = f"## {section}"
    if heading not in lines:
        lines.extend(["", heading, ""])
    start = lines.index(heading) + 1
    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    replacement = [f"- [[{page}]] — {summary}" for page, summary in entries]
    lines[start:end] = replacement if replacement else [""]
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
    directory = RAW_SYL if kind == "outline" else RAW_PP
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
    src_dir = RAW_SYL.resolve() if kind == "outline" else RAW_PP.resolve()
    archive_dir = RAW_ARCHIVE / ("syl" if kind == "outline" else "pp")
    try:
        parent = path.resolve().parent
    except FileNotFoundError:
        return
    if parent != src_dir:
        return
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / path.name
    if target.exists():
        target = archive_dir / f"{path.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}{path.suffix}"
    shutil.move(str(path), str(target))


def json_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


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


def parse_jsonish_scalar(raw: str, default):
    if raw is None or raw == "":
        return default
    try:
        return json.loads(raw)
    except Exception:
        return raw.strip('"')


def extract_markdown_section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.M | re.S)
    return match.group(1).strip() if match else ""


def concept_page_content(item: Dict[str, object], level: int, source_name: str, question_refs: List[str]) -> str:
    children = item.get("children", [])
    lines = [
        "---",
        f'title: {json_string(str(item["title"]))}',
        "type: concept",
        "exam: gesp",
        "subject: cpp",
        f"level: {level}",
        f'module: {json_string(str(item["module"]))}',
        f"parent_concept: {json_string(str(item['parent_concept']))}",
        f"prerequisites: {json.dumps(item['prerequisites'], ensure_ascii=False)}",
        f"children: {json.dumps(children, ensure_ascii=False)}",
        f"is_leaf: {'true' if item['is_leaf'] else 'false'}",
        f"question_refs: {json.dumps(question_refs, ensure_ascii=False)}",
        "---",
        "",
        "## Definition",
        "",
        str(item["summary"]),
        "",
        "## Notes",
        "",
        f"- 来源：{source_name}",
    ]
    if children:
        lines.extend(["- 子概念：" + "、".join(f"[[{slug}]]" for slug in children)])
    if item["parent_concept"]:
        lines.extend([f"- 父概念：[[{item['parent_concept']}]]"])
    if question_refs:
        lines.extend(["", "## Links", ""])
        lines.extend(f"- [[{qid}]]" for qid in question_refs)
    return "\n".join(lines)


def concept_slugs_for_level(level: int, blueprint: Dict[str, object]) -> List[str]:
    slugs = []
    for slug, meta in blueprint.get("concepts", {}).items():
        if int(meta.get("level", 0) or 0) == level:
            slugs.append(str(slug))
    return slugs


def update_concept_pages(
    level: int,
    source_name: str,
    concepts: Dict[str, Dict[str, object]] | None = None,
    question_refs_map: Dict[str, List[str]] | None = None,
) -> None:
    refs_map = question_refs_map or {}
    cmap = concepts or concept_map(level)
    for item in cmap.values():
        refs = sorted(refs_map.get(item["slug"], []))
        write_text(WIKI / "concepts" / f"{item['slug']}.md", concept_page_content(item, level, source_name, refs))
    rewrite_index_section("Concepts", [(str(item["slug"]), f"GESP C++ 五级考点：{item['name']}") for item in cmap.values()])


def sync_candidate_concepts(
    level: int,
    concepts: Dict[str, Dict[str, object]] | None = None,
    previous_slugs: List[str] | None = None,
    alias_map: Dict[str, str] | None = None,
) -> None:
    candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
    candidate.setdefault("exam", "gesp")
    candidate.setdefault("subject", "cpp")
    candidate.setdefault("candidate_id", "default")
    stale = set(previous_slugs or [])
    existing: Dict[str, Dict[str, object]] = {}
    for entry in candidate.get("concepts", []):
        concept_id = entry["concept_id"]
        if concept_id in stale:
            if not alias_map or concept_id not in alias_map:
                continue
            concept_id = alias_map[concept_id]
        merged = existing.setdefault(
            concept_id,
            {
                "concept_id": concept_id,
                "mastery_level": "unknown",
                "attempt_count": 0,
                "correct_count": 0,
                "last_attempt_at": "",
                "last_question_ids": [],
            },
        )
        merged["attempt_count"] += int(entry.get("attempt_count", 0))
        merged["correct_count"] += int(entry.get("correct_count", 0))
        if str(entry.get("last_attempt_at", "")) > str(merged.get("last_attempt_at", "")):
            merged["last_attempt_at"] = entry.get("last_attempt_at", "")
        for qid in entry.get("last_question_ids", []):
            if qid not in merged["last_question_ids"]:
                merged["last_question_ids"].append(qid)
        ratio = merged["correct_count"] / max(merged["attempt_count"], 1) if merged["attempt_count"] else 0
        if merged["attempt_count"] == 0:
            merged["mastery_level"] = "unknown"
        else:
            merged["mastery_level"] = "weak" if ratio == 0 else "developing" if ratio < 0.6 else "solid"
    cmap = concepts or concept_map(level)
    for item in cmap.values():
        existing.setdefault(
            str(item["slug"]),
            {
                "concept_id": item["slug"],
                "mastery_level": "unknown",
                "attempt_count": 0,
                "correct_count": 0,
                "last_attempt_at": "",
                "last_question_ids": [],
            },
        )
    candidate["concepts"] = sorted(existing.values(), key=lambda x: x["concept_id"])
    dump_jsonish(STATE / "candidates" / "default.yaml", candidate)


def current_question_ref_map() -> Dict[str, List[str]]:
    refs_map: Dict[str, List[str]] = defaultdict(list)
    for item in all_questions():
        for ref in item.get("concept_refs_list", []):
            refs_map[ref].append(item["question_id_raw"])
    return refs_map


def build_alias_map(previous_meta: Dict[str, Dict[str, object]], concepts: Dict[str, Dict[str, object]]) -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    root_by_module = {}
    root_by_name = {}
    for item in concepts.values():
        if item["parent_concept"]:
            continue
        root_by_module[str(item["module"])] = item["slug"]
        root_by_name[str(item["name"])] = item["slug"]
    for slug, meta in previous_meta.items():
        if slug in concepts:
            alias_map[slug] = slug
            continue
        name = str(meta.get("name", "")).strip()
        module = str(meta.get("module", "")).strip()
        if name in root_by_name:
            alias_map[slug] = root_by_name[name]
        elif module in root_by_module:
            alias_map[slug] = root_by_module[module]
    for legacy_slug, target_slug in LEGACY_CONCEPT_ALIASES.items():
        if target_slug in concepts:
            alias_map.setdefault(legacy_slug, target_slug)
    return alias_map


def migrate_question_concept_refs(alias_map: Dict[str, str], valid_slugs: set[str]) -> None:
    for record in all_questions():
        new_refs = []
        changed = False
        for ref in record.get("concept_refs_list", []):
            mapped = ref
            if ref not in valid_slugs and ref in alias_map:
                mapped = alias_map[ref]
                changed = True
            if mapped in valid_slugs and mapped not in new_refs:
                new_refs.append(mapped)
        if changed:
            record["concept_refs"] = new_refs
            write_question_record(record)


def clear_level_concepts(level: int, blueprint: Dict[str, object]) -> List[str]:
    previous = concept_slugs_for_level(level, blueprint)
    for slug in previous:
        blueprint.get("concepts", {}).pop(slug, None)
        path = WIKI / "concepts" / f"{slug}.md"
        if path.exists():
            path.unlink()
    return previous


def ingest_outline(path_str: str | None, model: str) -> None:
    init_repo()
    paths = resolve_input_paths(path_str, "outline")
    if not paths:
        print(json.dumps({"status": "no_input", "kind": "outline", "directory": str(RAW_SYL), "expected_extension": ".md"}, ensure_ascii=False))
        return
    for path in paths:
        text = markdown_text(path)
        level = slug_level(path, text)
        overview = markdown_section(text, "考核目标") or "未可靠提取考核目标。"
        cmap = generate_outline_concepts(level, text, path.name, model)
        blueprint = ensure_blueprint_schema(load_jsonish(CATALOG / "blueprint.yaml", {}))
        previous_meta = {
            slug: dict(meta)
            for slug, meta in blueprint.get("concepts", {}).items()
            if int(meta.get("level", 0) or 0) == level
        }
        previous_slugs = clear_level_concepts(level, blueprint)
        alias_map = build_alias_map(previous_meta, cmap)
        modules = []
        for root in [item for item in cmap.values() if not item["parent_concept"]]:
            modules.append(
                {
                    "slug": root["slug"],
                    "name": root["name"],
                    "prerequisites": root["prerequisites"],
                    "children": root["children"],
                }
            )
        blueprint.setdefault("levels", {})[str(level)] = {
            "outline_source": path.name,
            "overview": overview,
            "modules": modules,
        }
        for item in cmap.values():
            blueprint.setdefault("concepts", {})[item["slug"]] = {
                "exam": "gesp",
                "level": level,
                "title": item["title"],
                "name": item["name"],
                "module": item["module"],
                "summary": item["summary"],
                "prerequisites": item["prerequisites"],
                "parent_concept": item["parent_concept"],
                "children": item["children"],
                "is_leaf": item["is_leaf"],
                "keywords": item["keywords"],
        }
        blueprint["classification"]["outline_model"] = model
        dump_jsonish(CATALOG / "blueprint.yaml", blueprint)
        migrate_question_concept_refs(alias_map, set(cmap.keys()))
        update_concept_pages(level, path.name, cmap, current_question_ref_map())
        sync_candidate_concepts(level, cmap, previous_slugs, alias_map)
        append_log("gesp-ingest-outline", f"摄入大纲 {path.name}", "[[concept-number-theory]] 等层级 concept 页面")
        archive_source(path, "outline")


def exam_meta(path: Path, text: str) -> Dict[str, int | str]:
    match = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月", text) or re.search(r"(\d{4})[_ -](\d{1,2})", path.stem)
    if not match:
        raise ValueError(f"missing exam year/month in markdown content: {path}")
    year = int(match.group(1))
    month = int(match.group(2))
    level = slug_level(path, text)
    return {
        "year": year,
        "month": month,
        "level": level,
        "exam_page": f"exam-{year:04d}-{month:02d}",
        "paper_id": f"{year:04d}-{month:02d}",
    }


def answer_key(text: str) -> List[str]:
    match = re.search(r"答案\s+([A-D](?:\s+[A-D]){14})", text)
    if match:
        return re.findall(r"[A-D]", match.group(1))
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
        chunks = [part.strip() for part in re.split(r"\s+1(?:\s+2(?:\s+3)?)?\s+", body) if part.strip()]
        if len(chunks) != 4:
            return match.group(0)
        parts = []
        for label, chunk in zip(["A", "B", "C", "D"], chunks):
            parts.append(f"{label}.\n\n```cpp\n{chunk}\n```")
        return "\n\n".join(parts)

    return pattern.sub(repl, block)


def cleanup_question_markdown(block: str) -> str:
    block = rewrite_compact_option_fence(block).strip()
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
    return re.sub(r"\n{3,}", "\n\n", text)


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


def single_choice_content_status(stem: str, answer: str) -> str:
    if not answer:
        return "needs_review"
    if "A. B. C. D." in stem or "## " in stem:
        return "needs_review"
    if top_level_option_labels(stem) != ["A", "B", "C", "D"]:
        return "needs_review"
    if stem.count("```") % 2 != 0:
        return "needs_review"
    return "ok"


def overall_extraction_status(content_status: str, classification_status: str) -> str:
    return "ok" if content_status == "ok" and classification_status == "ok" else "needs_review"


def question_page_content(
    meta: Dict[str, int | str],
    qno: int,
    qtype: str,
    stem: str,
    answer: str,
    concept_refs: List[str],
    content_status: str,
    classification_status: str,
    classification_source: str,
    classification_reason: str,
    classification_confidence: float,
    fallback_parent_used: bool,
    review_notes: str = "",
) -> str:
    qid = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
    links = [f"- [[exam-{meta['year']:04d}-{meta['month']:02d}]]"] + [f"- [[{ref}]]" for ref in concept_refs]
    extraction_status = overall_extraction_status(content_status, classification_status)
    return f"""---
title: {json_string(qid)}
type: question
question_id: {json_string(qid)}
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
content_status: {content_status}
classification_status: {classification_status}
classification_source: {json_string(classification_source)}
classification_reason: {json_string(classification_reason)}
classification_confidence: {classification_confidence:.2f}
fallback_parent_used: {'true' if fallback_parent_used else 'false'}
classification_review_notes: {json_string(review_notes)}
extraction_status: {extraction_status}
---

## Stem

{stem}

## Answer

{answer or "未可靠提取。"}

## Analysis

首版未生成解析。

## Links

{chr(10).join(links) if links else ""}
"""


def question_file_path(question_id: str) -> Path:
    return WIKI / "questions" / f"{question_id}.md"


def load_question_record(path: Path) -> Dict[str, object]:
    fm = parse_frontmatter(path)
    body = read_text(path)
    question_id = parse_jsonish_scalar(fm.get("question_id", path.stem), path.stem)
    answer_raw = fm.get("answer", '""')
    analysis_raw = fm.get("analysis", '""')
    content_status = fm.get("content_status", fm.get("extraction_status", "needs_review"))
    classification_status = fm.get("classification_status", "ok" if fm.get("concept_refs", "[]") != "[]" else "needs_review")
    return {
        "question_id": question_id,
        "year": int(fm.get("year", 0)),
        "month": int(fm.get("month", 0)),
        "no": int(fm.get("no", 0)),
        "level": int(fm.get("level", 0)),
        "subject": fm.get("subject", "cpp"),
        "question_type": fm.get("question_type", ""),
        "answer": parse_jsonish_scalar(answer_raw, ""),
        "analysis": parse_jsonish_scalar(analysis_raw, ""),
        "concept_refs": parse_jsonish_scalar(fm.get("concept_refs", "[]"), []),
        "difficulty": fm.get("difficulty", '"unknown"').strip('"'),
        "content_status": content_status,
        "classification_status": classification_status,
        "classification_source": parse_jsonish_scalar(fm.get("classification_source", '"legacy"'), "legacy"),
        "classification_reason": parse_jsonish_scalar(fm.get("classification_reason", '""'), ""),
        "classification_confidence": float(fm.get("classification_confidence", "0")),
        "fallback_parent_used": fm.get("fallback_parent_used", "false").lower() == "true",
        "classification_review_notes": parse_jsonish_scalar(fm.get("classification_review_notes", '""'), ""),
        "stem_text": extract_markdown_section(body, "Stem"),
    }


def write_question_record(record: Dict[str, object]) -> None:
    meta = {
        "year": int(record["year"]),
        "month": int(record["month"]),
        "level": int(record["level"]),
    }
    content = question_page_content(
        meta,
        int(record["no"]),
        str(record["question_type"]),
        str(record["stem_text"]),
        str(record["answer"]),
        list(record["concept_refs"]),
        str(record["content_status"]),
        str(record["classification_status"]),
        str(record["classification_source"]),
        str(record["classification_reason"]),
        float(record["classification_confidence"]),
        bool(record["fallback_parent_used"]),
        str(record["classification_review_notes"]),
    )
    write_text(question_file_path(str(record["question_id"])), content)


def all_questions() -> List[Dict[str, object]]:
    items = []
    for path in sorted((WIKI / "questions").glob("question-*.md")):
        record = load_question_record(path)
        record["path"] = str(path)
        record["question_id_raw"] = str(record["question_id"])
        record["concept_refs_list"] = list(record["concept_refs"])
        items.append(record)
    return items


def exam_page_content(meta: Dict[str, int | str], source_name: str, question_pages: List[str]) -> str:
    return f"""---
title: {json_string(str(meta["exam_page"]))}
type: exam
exam: gesp
subject: cpp
level: {meta['level']}
year: {meta['year']}
month: {meta['month']}
question_refs: {json.dumps(question_pages, ensure_ascii=False)}
source: {json_string(source_name)}
---

## Summary

GESP C++ 五级 {meta['year']} 年 {meta['month']:02d} 月真题，共 {len(question_pages)} 题，题型包含单选、判断和编程。

## Questions

{chr(10).join(f"- [[{page}]]" for page in question_pages)}
"""


def concept_prompt_payload(level: int) -> List[Dict[str, object]]:
    payload = []
    for item in concept_map(level).values():
        payload.append(
            {
                "slug": item["slug"],
                "name": item["name"],
                "summary": item["summary"],
                "parent_concept": item["parent_concept"],
                "children": item["children"],
                "is_leaf": item["is_leaf"],
            }
        )
    return payload


def classification_request_content(meta: Dict[str, int | str], question_records: List[Dict[str, object]]) -> Dict[str, object]:
    return {
        "paper_id": meta["paper_id"],
        "exam_page": meta["exam_page"],
        "source": "gesp-ingest-paper",
        "classification_mode": "llm_manual_import",
        "rules": {
            "prefer_child_concepts": True,
            "fallback_to_parent_only_when_unsure": True,
            "max_concept_refs": "unlimited",
            "allow_parent_refs_only_with_fallback_parent_used": True,
            "reject_parent_and_child_together": True,
            "allowed_output_fields": [
                "question_id",
                "concept_refs",
                "primary_concept",
                "fallback_parent_used",
                "confidence",
                "reason",
            ],
        },
        "output_example": {
            "paper_id": meta["paper_id"],
            "classifications": [
                {
                    "question_id": "question-2025-03-01",
                    "concept_refs": ["concept-linked-list"],
                    "primary_concept": "concept-linked-list",
                    "fallback_parent_used": False,
                    "confidence": 0.94,
                    "reason": "题目核心考查链表操作。",
                }
            ],
        },
        "concepts": concept_prompt_payload(int(meta["level"])),
        "questions": [
            {
                "question_id": record["question_id"],
                "question_type": record["question_type"],
                "stem": record["stem_text"],
            }
            for record in question_records
        ],
    }


def write_classification_artifacts(meta: Dict[str, int | str], question_records: List[Dict[str, object]]) -> Dict[str, str]:
    request_path = PAPER_REQUESTS / f"{meta['paper_id']}.json"
    template_path = PAPER_RESULTS / f"{meta['paper_id']}.template.json"
    dump_jsonish(request_path, classification_request_content(meta, question_records))
    dump_jsonish(template_path, {"paper_id": meta["paper_id"], "classifications": []})
    return {"request": str(request_path), "template": str(template_path)}


def paper_classification_prompt(
    meta: Dict[str, int | str],
    question_records: List[Dict[str, object]],
    level: int,
) -> List[Dict[str, str]]:
    concepts = concept_prompt_payload(level)
    system_prompt = """
你是 GESP C++ 试题知识点标注助手。

任务：
1. 只从给定 concept 列表中选择 `concept_refs`。
2. 尽量细到子级 concept；只有无法可靠细分时才回退到父级。
3. 可以返回多个 concept_refs，不设数量上限。
4. 不允许同时返回父 concept 和它的子 concept。
5. 如果用了父 concept，`fallback_parent_used` 必须为 true；否则为 false。
6. `primary_concept` 必须是 `concept_refs` 中最核心的那个。
7. `confidence` 取 0 到 1 之间的小数。
8. 只返回 JSON 对象，顶层字段必须是 `paper_id` 和 `classifications`。
9. `classifications` 中每项字段固定为：question_id, concept_refs, primary_concept, fallback_parent_used, confidence, reason。
"""
    user_payload = {
        "paper_id": meta["paper_id"],
        "level": level,
        "concepts": concepts,
        "questions": [
            {
                "question_id": record["question_id"],
                "question_type": record["question_type"],
                "stem": record["stem_text"],
            }
            for record in question_records
        ],
    }
    return [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
    ]


def chunked(items: List[Dict[str, object]], size: int) -> List[List[Dict[str, object]]]:
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


def classify_question_records_with_deepseek(
    meta: Dict[str, int | str],
    question_records: List[Dict[str, object]],
    level: int,
    model: str,
) -> Dict[str, object]:
    results = {"paper_id": meta["paper_id"], "classifications": []}
    for batch in chunked(question_records, PAPER_CLASSIFICATION_BATCH_SIZE):
        payload = deepseek_chat_json(paper_classification_prompt(meta, batch, level), model)
        normalized = normalize_classification_results(payload)
        classifications = normalized.get("classifications", [])
        if not isinstance(classifications, list):
            raise ValueError(f"invalid deepseek paper classification payload: {payload}")
        results["classifications"].extend(classifications)
        time.sleep(2)
    return results


def ingest_paper(path_str: str | None, model: str) -> None:
    init_repo()
    paths = resolve_input_paths(path_str, "paper")
    if not paths:
        print(json.dumps({"status": "no_input", "kind": "paper", "directory": str(RAW_PP), "expected_extension": ".md"}, ensure_ascii=False))
        return
    blueprint = ensure_blueprint_schema(load_jsonish(CATALOG / "blueprint.yaml", {}))
    for path in paths:
        text = markdown_text(path)
        meta = exam_meta(path, text)
        single = require_section(text, "单选题", path)
        judge = require_section(text, "判断题", path)
        programming = require_section(text, "编程题", path)
        key = answer_key(single)
        judge_key = tf_answer_key(judge)
        question_records: List[Dict[str, object]] = []
        question_pages: List[str] = []

        single_blocks = parse_question_blocks(single)
        for idx, match in enumerate(single_blocks):
            local_no = int(match.group(1))
            start = match.start()
            end = single_blocks[idx + 1].start() if idx + 1 < len(single_blocks) else len(single)
            stem = cleanup_question_markdown(single[start:end])
            qid = f"question-{meta['year']:04d}-{meta['month']:02d}-{local_no:02d}"
            record = {
                "question_id": qid,
                "year": meta["year"],
                "month": meta["month"],
                "no": local_no,
                "level": meta["level"],
                "subject": "cpp",
                "question_type": "single_choice",
                "answer": key[local_no - 1] if local_no - 1 < len(key) else "",
                "analysis": "",
                "concept_refs": [],
                "difficulty": "unknown",
                "content_status": single_choice_content_status(stem, key[local_no - 1] if local_no - 1 < len(key) else ""),
                "classification_status": "pending",
                "classification_source": "pending_llm",
                "classification_reason": "",
                "classification_confidence": 0.0,
                "fallback_parent_used": False,
                "classification_review_notes": "等待 LLM 分类结果导入。",
                "stem_text": stem,
            }
            write_question_record(record)
            question_records.append(record)
            question_pages.append(qid)

        judge_blocks = parse_question_blocks(judge)
        for idx, match in enumerate(judge_blocks):
            local_no = int(match.group(1))
            start = match.start()
            end = judge_blocks[idx + 1].start() if idx + 1 < len(judge_blocks) else len(judge)
            stem = cleanup_question_markdown(judge[start:end])
            qno = 15 + local_no
            qid = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
            answer = judge_key[local_no - 1] if local_no - 1 < len(judge_key) else ""
            record = {
                "question_id": qid,
                "year": meta["year"],
                "month": meta["month"],
                "no": qno,
                "level": meta["level"],
                "subject": "cpp",
                "question_type": "true_false",
                "answer": answer,
                "analysis": "",
                "concept_refs": [],
                "difficulty": "unknown",
                "content_status": "ok" if answer else "needs_review",
                "classification_status": "pending",
                "classification_source": "pending_llm",
                "classification_reason": "",
                "classification_confidence": 0.0,
                "fallback_parent_used": False,
                "classification_review_notes": "等待 LLM 分类结果导入。",
                "stem_text": stem,
            }
            write_question_record(record)
            question_records.append(record)
            question_pages.append(qid)

        prog_matches = list(re.finditer(r"3\.(\d+)\s*编程题\s*(\d+)", programming))
        for idx, match in enumerate(prog_matches):
            local_no = int(match.group(2))
            start = match.start()
            end = prog_matches[idx + 1].start() if idx + 1 < len(prog_matches) else len(programming)
            stem = cleanup_question_markdown(programming[start:end])
            qno = 25 + local_no
            qid = f"question-{meta['year']:04d}-{meta['month']:02d}-{qno:02d}"
            record = {
                "question_id": qid,
                "year": meta["year"],
                "month": meta["month"],
                "no": qno,
                "level": meta["level"],
                "subject": "cpp",
                "question_type": "programming",
                "answer": "",
                "analysis": "",
                "concept_refs": [],
                "difficulty": "unknown",
                "content_status": "needs_review",
                "classification_status": "pending",
                "classification_source": "pending_llm",
                "classification_reason": "",
                "classification_confidence": 0.0,
                "fallback_parent_used": False,
                "classification_review_notes": "等待 LLM 分类结果导入。",
                "stem_text": stem,
            }
            write_question_record(record)
            question_records.append(record)
            question_pages.append(qid)

        write_text(WIKI / "exams" / f"{meta['exam_page']}.md", exam_page_content(meta, path.name, question_pages))
        blueprint.setdefault("papers", {})[meta["paper_id"]] = {
            "level": meta["level"],
            "source_file": path.name,
            "exam_page": meta["exam_page"],
            "question_count": len(question_pages),
            "classification_mode": "deepseek_direct",
            "classification_model": model,
            "classification_request": f"state/catalog/paper_ingest/requests/{meta['paper_id']}.json",
            "classification_template": f"state/catalog/paper_ingest/results/{meta['paper_id']}.template.json",
        }
        dump_jsonish(CATALOG / "blueprint.yaml", blueprint)
        for page in question_pages:
            update_index("Questions", page, f"{page} | {meta['year']}-{meta['month']:02d}")
        update_index("Exams", str(meta["exam_page"]), f"GESP C++ 五级 {meta['year']} 年 {meta['month']:02d} 月真题")
        artifacts = write_classification_artifacts(meta, question_records)
        payload = classify_question_records_with_deepseek(meta, question_records, int(meta["level"]), model)
        classification_result_path = PAPER_RESULTS / f"{meta['paper_id']}.json"
        dump_jsonish(classification_result_path, payload)
        summary = apply_classification_payload(payload)
        update_concept_pages(
            int(meta["level"]),
            blueprint["levels"].get(str(meta["level"]), {}).get("outline_source", "manual"),
            concept_map(int(meta["level"]), ensure_blueprint_schema(load_jsonish(CATALOG / "blueprint.yaml", {}))),
            current_question_ref_map(),
        )
        append_log("gesp-ingest-paper", f"摄入试卷 {path.name}", f"[[{meta['exam_page']}]]，已直连智谱完成分类")
        archive_source(path, "paper")
        print(
            json.dumps(
                {
                    "status": "ok",
                    "source_file": path.name,
                    "exam_page": meta["exam_page"],
                    "classification_model": model,
                    "classification_request": artifacts["request"],
                    "classification_template": artifacts["template"],
                    "classification_result": str(classification_result_path),
                    "updated": summary["updated"],
                    "needs_review": summary["needs_review"],
                    "review_file": summary["review_file"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )


def reingest_archived_papers(model: str) -> None:
    init_repo()
    archive_paths = sorted((RAW_ARCHIVE / "pp").glob("*.md"))
    if not archive_paths:
        print(json.dumps({"status": "no_input", "kind": "paper_archive", "directory": str(RAW_ARCHIVE / "pp")}, ensure_ascii=False))
        return
    processed = []
    failed = []
    for path in archive_paths:
        try:
            ingest_paper(str(path), model)
            processed.append(path.name)
        except Exception as exc:
            failed.append({"source_file": path.name, "error": str(exc)})
    print(
        json.dumps(
            {
                "status": "ok" if not failed else "partial",
                "processed": processed,
                "failed": failed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def normalize_classification_results(payload: object) -> Dict[str, object]:
    if isinstance(payload, list):
        return {"paper_id": "", "classifications": payload}
    if isinstance(payload, dict):
        if "classifications" in payload:
            return payload
        return {"paper_id": payload.get("paper_id", ""), "classifications": payload.get("questions", [])}
    raise ValueError("unsupported classification result payload")


def apply_classification_payload(payload: Dict[str, object]) -> Dict[str, object]:
    paper_id = str(payload.get("paper_id", ""))
    items = payload.get("classifications", [])
    if not isinstance(items, list):
        raise ValueError("classification results must contain a list in 'classifications'")
    question_map = {item["question_id_raw"]: item for item in all_questions()}
    if not items:
        raise ValueError("classification results are empty")
    if not paper_id:
        first_qid = str(items[0].get("question_id", ""))
        match = re.search(r"question-(\d{4})-(\d{2})-", first_qid)
        if not match:
            raise ValueError("cannot infer paper_id from classification results")
        paper_id = f"{match.group(1)}-{match.group(2)}"

    review_items = []
    updated = 0
    seen_question_ids = set()
    for raw in items:
        if not isinstance(raw, dict):
            continue
        question_id = str(raw.get("question_id", ""))
        if not question_id:
            continue
        seen_question_ids.add(question_id)
        record = question_map.get(question_id)
        if not record:
            review_items.append({"question_id": question_id, "issues": ["题目不存在于题库中。"], "raw": raw})
            continue
        ok, issues, reason, normalized = validate_classification_item(raw, paper_id, int(record["level"]), question_id)
        record["classification_source"] = "deepseek_direct"
        record["classification_reason"] = reason
        record["classification_confidence"] = float(normalized["confidence"])
        record["fallback_parent_used"] = bool(normalized["fallback_parent_used"])
        if ok:
            record["concept_refs"] = normalized["concept_refs"]
            record["classification_status"] = "ok"
            record["classification_review_notes"] = ""
            updated += 1
        else:
            record["concept_refs"] = []
            record["classification_status"] = "needs_review"
            record["classification_review_notes"] = " | ".join(issues)
            review_items.append({"question_id": question_id, "issues": issues, "raw": normalized})
        write_question_record(record)

    for qid, record in question_map.items():
        if f"{record['year']:04d}-{record['month']:02d}" != paper_id:
            continue
        if qid in seen_question_ids:
            continue
        record["concept_refs"] = []
        record["classification_status"] = "needs_review"
        record["classification_source"] = "deepseek_direct"
        record["classification_reason"] = ""
        record["classification_confidence"] = 0.0
        record["fallback_parent_used"] = False
        record["classification_review_notes"] = "LLM 结果未返回该题。"
        write_question_record(record)
        review_items.append({"question_id": qid, "issues": ["LLM 结果未返回该题。"], "raw": {}})

    if review_items:
        dump_jsonish(PAPER_REVIEWS / f"{paper_id}.json", {"paper_id": paper_id, "items": review_items})

    blueprint = ensure_blueprint_schema(load_jsonish(CATALOG / "blueprint.yaml", {}))
    paper_meta = blueprint.get("papers", {}).get(paper_id, {})
    level = int(paper_meta.get("level", 5))
    source_name = blueprint.get("levels", {}).get(str(level), {}).get("outline_source", "manual")
    update_concept_pages(level, source_name, concept_map(level, blueprint), current_question_ref_map())
    append_log("gesp-apply-paper-classification", f"导入 {paper_id} 的 LLM 分类结果", f"成功 {updated} 题，待审 {len(review_items)} 题")
    return {
        "paper_id": paper_id,
        "updated": updated,
        "needs_review": len(review_items),
        "review_file": str(PAPER_REVIEWS / f"{paper_id}.json") if review_items else "",
    }


def validate_classification_item(
    item: Dict[str, object],
    paper_id: str,
    level: int,
    question_id: str,
) -> tuple[bool, List[str], str, Dict[str, object]]:
    cmap = concept_map(level)
    issues: List[str] = []
    refs = item.get("concept_refs", [])
    if not isinstance(refs, list):
        issues.append("concept_refs 必须是数组。")
        refs = []
    refs = [str(ref) for ref in refs]
    primary = str(item.get("primary_concept", ""))
    fallback_parent_used = bool(item.get("fallback_parent_used", False))
    confidence = float(item.get("confidence", 0))
    reason = str(item.get("reason", ""))

    if len(refs) == 0:
        issues.append("concept_refs 不能为空。")
    if primary and primary not in refs:
        issues.append("primary_concept 必须包含在 concept_refs 内。")
    for ref in refs:
        if ref not in cmap:
            issues.append(f"未知 concept: {ref}")
    for idx, ref in enumerate(refs):
        if ref in cmap and not cmap[ref]["is_leaf"]:
            if not fallback_parent_used:
                issues.append(f"父级 concept {ref} 需要 fallback_parent_used=true。")
        for other in refs[idx + 1 :]:
            if is_parent_child_pair(ref, other, cmap):
                issues.append(f"不允许同时标注父子 concept: {ref}, {other}")
    if confidence < 0.6:
        issues.append("confidence 低于阈值 0.60。")

    normalized = {
        "question_id": question_id,
        "paper_id": paper_id,
        "concept_refs": refs,
        "primary_concept": primary,
        "fallback_parent_used": fallback_parent_used,
        "confidence": confidence,
        "reason": reason,
    }
    return (len(issues) == 0, issues, reason, normalized)


def apply_paper_classification(result_path: str) -> None:
    init_repo()
    path = (ROOT / result_path).resolve() if not Path(result_path).is_absolute() else Path(result_path)
    payload = normalize_classification_results(load_jsonish(path, {}))
    summary = apply_classification_payload(payload)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def create_attempt(filters: Dict[str, object], selected: List[Dict[str, object]]) -> str:
    attempt_id = datetime.now().strftime("attempt-%Y%m%d-%H%M%S")
    payload = {
        "attempt_id": attempt_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filters": filters,
        "questions": [
            {
                "question_id": item["question_id_raw"],
                "concept_refs": list(item.get("concept_refs_list", [])),
                "question_type": item.get("question_type", ""),
                "correct_answer": item.get("answer", ""),
                "stem_text": item.get("stem_text", ""),
            }
            for item in selected
        ],
        "answers": {},
        "grading": [],
    }
    dump_jsonish(STATE / "attempts" / f"{attempt_id}.yaml", payload)
    return attempt_id


def expand_requested_concepts(raw: str, level: int) -> set[str]:
    cmap = concept_map(level)
    wanted = {item.strip() for item in raw.split(",") if item.strip()}
    expanded = set()
    for slug in wanted:
        expanded.add(slug)
        expanded.update(descendants(slug, cmap))
    return expanded


def filter_questions_by_concepts(questions: List[Dict[str, object]], wanted: set[str]) -> List[Dict[str, object]]:
    return [q for q in questions if wanted.intersection(set(q.get("concept_refs_list", [])))]


def practice(args) -> None:
    questions = all_questions()
    if args.paper:
        year, month = args.paper.split("-")
        questions = [q for q in questions if str(q.get("year")) == year and int(q.get("month", 0)) == int(month)]
    if args.concepts:
        level = int(questions[0]["level"]) if questions else 5
        wanted = expand_requested_concepts(args.concepts, level)
        questions = filter_questions_by_concepts(questions, wanted)
    if args.wrong_only:
        candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
        weak = {c["concept_id"] for c in candidate.get("concepts", []) if c["mastery_level"] == "weak"}
        if weak and questions:
            level = int(questions[0]["level"])
            expanded = set()
            for slug in weak:
                expanded.add(slug)
                expanded.update(descendants(slug, concept_map(level)))
            questions = filter_questions_by_concepts(questions, expanded)
    count = min(args.count, len(questions))
    selected = questions[:count]
    attempt_id = create_attempt({"concepts": args.concepts, "paper": args.paper, "wrong_only": args.wrong_only, "count": count}, selected)
    lines = [f"# GESP Practice", "", f"attempt_id: {attempt_id}", ""]
    for idx, q in enumerate(selected, start=1):
        refs = ", ".join(q.get("concept_refs_list", [])) or "N/A"
        lines.extend(
            [
                f"## {idx}. {q['question_id_raw']}",
                f"- question_type: {q.get('question_type', '')}",
                f"- concept_refs: {refs}",
                "",
                str(q.get("stem_text", "未找到题面。")),
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
            key, value = pair.split("=", 1)
            answers[key] = value
    attempt["answers"].update(answers)
    grading = []
    candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
    concept_stats = {entry["concept_id"]: entry for entry in candidate.get("concepts", [])}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in attempt.get("questions", []):
        qid = item["question_id"]
        qtype = item["question_type"]
        expected = item.get("correct_answer", "")
        given = answers.get(qid, "")
        if qtype == "single_choice" and expected:
            correct, score, review_status, reason, confidence = given == expected, 1 if given == expected else 0, "auto", "客观题自动判分。", 1.0
        elif qtype == "true_false" and expected:
            correct, score, review_status, reason, confidence = given.lower() == expected.lower(), 1 if given.lower() == expected.lower() else 0, "auto", "判断题按标准答案自动判分。", 1.0
        else:
            correct, score, review_status, reason, confidence = False, 0, "needs_manual_review", "缺少可靠标准答案或属于编程题，仅提供待复核记录。", 0.2
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
            entry = concept_stats.setdefault(
                ref,
                {"concept_id": ref, "mastery_level": "unknown", "attempt_count": 0, "correct_count": 0, "last_attempt_at": "", "last_question_ids": []},
            )
            entry["attempt_count"] += 1
            entry["correct_count"] += score
            entry["last_attempt_at"] = now
            entry["last_question_ids"] = [qid] + entry.get("last_question_ids", [])[:4]
            ratio = entry["correct_count"] / max(entry["attempt_count"], 1)
            entry["mastery_level"] = "weak" if ratio == 0 else "developing" if ratio < 0.6 else "solid"
    attempt["grading"] = grading
    dump_jsonish(path, attempt)
    candidate["concepts"] = sorted(concept_stats.values(), key=lambda x: x["concept_id"])
    dump_jsonish(STATE / "candidates" / "default.yaml", candidate)
    print(json.dumps({"attempt_id": args.attempt_id, "graded": len(grading)}, ensure_ascii=False, indent=2))


def aggregate_concept_stats(concept_id: str, concept_entries: Dict[str, Dict[str, object]], cmap: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    related = [concept_id] + descendants(concept_id, cmap)
    total_attempt = 0
    total_correct = 0
    last_attempt_at = ""
    last_question_ids: List[str] = []
    for slug in related:
        entry = concept_entries.get(slug)
        if not entry:
            continue
        total_attempt += int(entry.get("attempt_count", 0))
        total_correct += int(entry.get("correct_count", 0))
        stamp = str(entry.get("last_attempt_at", ""))
        if stamp and stamp > last_attempt_at:
            last_attempt_at = stamp
        for qid in entry.get("last_question_ids", []):
            if qid not in last_question_ids:
                last_question_ids.append(qid)
    ratio = total_correct / total_attempt if total_attempt else 0
    mastery = "unknown"
    if total_attempt:
        mastery = "weak" if ratio == 0 else "developing" if ratio < 0.6 else "solid"
    return {
        "concept_id": concept_id,
        "mastery_level": mastery,
        "attempt_count": total_attempt,
        "correct_count": total_correct,
        "last_attempt_at": last_attempt_at,
        "last_question_ids": last_question_ids[:5],
    }


def report(args) -> None:
    candidate = load_jsonish(STATE / "candidates" / "default.yaml", {})
    concept_entries = {entry["concept_id"]: entry for entry in candidate.get("concepts", [])}
    blueprint = ensure_blueprint_schema(load_jsonish(CATALOG / "blueprint.yaml", {}))
    level = 5
    if blueprint.get("levels"):
        level = int(sorted(blueprint["levels"].keys())[0])
    cmap = concept_map(level)
    if args.concept:
        if args.concept in cmap and not cmap[args.concept]["is_leaf"]:
            concepts = [aggregate_concept_stats(args.concept, concept_entries, cmap)]
        else:
            base = concept_entries.get(
                args.concept,
                {"concept_id": args.concept, "mastery_level": "unknown", "attempt_count": 0, "correct_count": 0, "last_attempt_at": "", "last_question_ids": []},
            )
            concepts = [base]
    elif args.aggregate_parents:
        concepts = [aggregate_concept_stats(item["slug"], concept_entries, cmap) for item in cmap.values() if not item["parent_concept"]]
    else:
        concepts = []
        for item in cmap.values():
            if item["is_leaf"]:
                concepts.append(
                    concept_entries.get(
                        item["slug"],
                        {"concept_id": item["slug"], "mastery_level": "unknown", "attempt_count": 0, "correct_count": 0, "last_attempt_at": "", "last_question_ids": []},
                    )
                )
    if args.weak_only:
        concepts = [c for c in concepts if c["mastery_level"] in {"unknown", "weak", "developing"}]
    concepts.sort(key=lambda x: (x["mastery_level"], x["attempt_count"], x["concept_id"]))
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
    outline = sub.add_parser("ingest-outline")
    outline.add_argument("path", nargs="?")
    outline.add_argument("--model", default=DEFAULT_OUTLINE_MODEL)
    paper = sub.add_parser("ingest-paper")
    paper.add_argument("path", nargs="?")
    paper.add_argument("--model", default=DEFAULT_PAPER_MODEL)
    reingest = sub.add_parser("reingest-archived-papers")
    reingest.add_argument("--model", default=DEFAULT_PAPER_MODEL)
    apply_results = sub.add_parser("apply-paper-classification")
    apply_results.add_argument("result_path")
    practice_parser = sub.add_parser("practice")
    practice_parser.add_argument("--concepts", default="")
    practice_parser.add_argument("--count", type=int, default=5)
    practice_parser.add_argument("--paper", default="")
    practice_parser.add_argument("--wrong-only", action="store_true")
    grade_parser = sub.add_parser("grade")
    grade_parser.add_argument("attempt_id")
    grade_parser.add_argument("--answers", nargs="*", default=[])
    report_parser = sub.add_parser("report")
    report_parser.add_argument("--concept", default="")
    report_parser.add_argument("--weak-only", action="store_true")
    report_parser.add_argument("--aggregate-parents", action="store_true")
    args = parser.parse_args()
    if args.cmd == "init":
        init_repo()
    elif args.cmd == "ingest-outline":
        ingest_outline(args.path, args.model)
    elif args.cmd == "ingest-paper":
        ingest_paper(args.path, args.model)
    elif args.cmd == "reingest-archived-papers":
        reingest_archived_papers(args.model)
    elif args.cmd == "apply-paper-classification":
        apply_paper_classification(args.result_path)
    elif args.cmd == "practice":
        practice(args)
    elif args.cmd == "grade":
        grade(args)
    elif args.cmd == "report":
        report(args)


if __name__ == "__main__":
    main()
