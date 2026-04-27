#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SKILLS_DIR = ROOT / ".agents" / "skills"
DISABLED_GROUPS_DIR = ROOT / ".agents" / "skill-groups" / "disabled"
CONFIG_PATH = ROOT / ".agents" / "skill-groups" / "active.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "always_on_groups": ["core"],
    "active_groups": ["core"],
    "group_rules": {
        "wiki": {"prefixes": ["wiki-"]},
        "gesp": {"prefixes": ["gesp-"]},
        "memory": {"exact": ["req-mem"]},
        "core": {"exact": ["skill-group-switcher"]},
    },
}


@dataclass
class SkillInventory:
    grouped: dict[str, list[str]]
    active_grouped: dict[str, list[str]]
    disabled_grouped: dict[str, list[str]]
    ungrouped: list[str]


class SkillGroupError(Exception):
    pass


def ensure_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return json.loads(json.dumps(DEFAULT_CONFIG))

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config = json.load(f)

    changed = False
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = json.loads(json.dumps(value))
            changed = True

    config["always_on_groups"] = dedupe_preserve(config.get("always_on_groups", []))
    active_groups = dedupe_preserve(config.get("active_groups", []))
    config["active_groups"] = merge_groups(active_groups, config["always_on_groups"])

    if changed:
        save_config(config)

    return config


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def merge_groups(groups: list[str], always_on_groups: list[str]) -> list[str]:
    return dedupe_preserve(always_on_groups + groups)


def list_skill_names() -> list[str]:
    if not SKILLS_DIR.exists():
        return []
    names: list[str] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / "SKILL.md").exists():
            names.append(entry.name)
    return names


def iter_skill_dirs(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    return sorted(
        entry for entry in base_dir.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").exists()
    )


def iter_disabled_skill_dirs() -> list[Path]:
    if not DISABLED_GROUPS_DIR.exists():
        return []

    skill_dirs: list[Path] = []
    for group_dir in sorted(DISABLED_GROUPS_DIR.iterdir()):
        if not group_dir.is_dir():
            continue
        skill_dirs.extend(iter_skill_dirs(group_dir))
    return skill_dirs


def discover_skill_locations() -> dict[str, Path]:
    locations: dict[str, Path] = {}
    for skill_dir in iter_skill_dirs(SKILLS_DIR):
        locations[skill_dir.name] = skill_dir
    for skill_dir in iter_disabled_skill_dirs():
        locations.setdefault(skill_dir.name, skill_dir)
    return locations


def classify_skill(skill_name: str, group_rules: dict[str, Any]) -> str | None:
    for group_name, rule in group_rules.items():
        exact = rule.get("exact", [])
        if skill_name in exact:
            return group_name

    for group_name, rule in group_rules.items():
        prefixes = rule.get("prefixes", [])
        if any(skill_name.startswith(prefix) for prefix in prefixes):
            return group_name

    return None


def build_inventory(config: dict[str, Any]) -> SkillInventory:
    grouped = {group_name: [] for group_name in config["group_rules"]}
    active_grouped = {group_name: [] for group_name in config["group_rules"]}
    disabled_grouped = {group_name: [] for group_name in config["group_rules"]}
    ungrouped: list[str] = []
    active_names = {path.name for path in iter_skill_dirs(SKILLS_DIR)}

    for skill_name in sorted(discover_skill_locations()):
        group_name = classify_skill(skill_name, config["group_rules"])
        if group_name is None:
            ungrouped.append(skill_name)
            continue
        grouped.setdefault(group_name, []).append(skill_name)
        if skill_name in active_names:
            active_grouped.setdefault(group_name, []).append(skill_name)
        else:
            disabled_grouped.setdefault(group_name, []).append(skill_name)

    for names in grouped.values():
        names.sort()
    for names in active_grouped.values():
        names.sort()
    for names in disabled_grouped.values():
        names.sort()

    return SkillInventory(
        grouped=grouped,
        active_grouped=active_grouped,
        disabled_grouped=disabled_grouped,
        ungrouped=sorted(ungrouped),
    )


def normalize_group_tokens(tokens: list[str]) -> list[str]:
    groups: list[str] = []
    for token in tokens:
        for piece in token.split(","):
            normalized = piece.strip()
            if normalized:
                groups.append(normalized)
    return dedupe_preserve(groups)


def validate_groups(requested: list[str], config: dict[str, Any]) -> None:
    known_groups = set(config["group_rules"])
    unknown = [group for group in requested if group not in known_groups]
    if unknown:
        valid = ", ".join(sorted(known_groups))
        raise SkillGroupError(
            f"未知 group: {', '.join(unknown)}。可用 group: {valid}"
        )


def target_skill_path(skill_name: str, group_name: str, active_groups: list[str]) -> Path:
    if group_name in active_groups:
        return SKILLS_DIR / skill_name
    return DISABLED_GROUPS_DIR / group_name / skill_name


def sync_skill_layout(config: dict[str, Any]) -> list[str]:
    moved_skills: list[str] = []
    skill_locations = discover_skill_locations()

    for skill_name, current_path in skill_locations.items():
        group_name = classify_skill(skill_name, config["group_rules"])
        if group_name is None:
            continue

        destination = target_skill_path(skill_name, group_name, config["active_groups"])
        if current_path == destination:
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise SkillGroupError(
                f"目标路径已存在，无法移动 skill: {destination}"
            )
        shutil.move(str(current_path), str(destination))
        moved_skills.append(skill_name)

        parent = current_path.parent
        while parent != ROOT and parent != DISABLED_GROUPS_DIR:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent

    return sorted(moved_skills)


def apply_command(config: dict[str, Any], command: str, groups: list[str]) -> tuple[dict[str, Any], list[str], list[str]]:
    validate_groups(groups, config)
    active_before = config["active_groups"][:]
    always_on = config["always_on_groups"]

    if command == "status":
        moved_skills = sync_skill_layout(config)
        return config, [], moved_skills

    if command == "on":
        config["active_groups"] = merge_groups(active_before + groups, always_on)
    elif command == "off":
        denied = [group for group in groups if group in always_on]
        if denied:
            raise SkillGroupError(
                f"不能关闭始终启用组: {', '.join(denied)}"
            )
        deny_set = set(groups)
        config["active_groups"] = [
            group for group in active_before if group not in deny_set
        ]
        config["active_groups"] = merge_groups(config["active_groups"], always_on)
    elif command == "set":
        denied = [group for group in groups if group in always_on]
        if denied:
            raise SkillGroupError(
                "set 命令不需要显式包含始终启用组；它们会自动保留: "
                + ", ".join(denied)
            )
        config["active_groups"] = merge_groups(groups, always_on)
    else:
        raise SkillGroupError(f"不支持的命令: {command}")

    changed = sorted(set(config["active_groups"]) ^ set(active_before))
    save_config(config)
    moved_skills = sync_skill_layout(config)
    return config, changed, moved_skills


def build_response(
    config: dict[str, Any],
    inventory: SkillInventory,
    command: str,
    changed_groups: list[str],
    moved_skills: list[str],
) -> dict[str, Any]:
    active_groups = config["active_groups"]
    available_groups = sorted(config["group_rules"])
    optional_groups = [
        group_name for group_name in available_groups
        if group_name not in config["always_on_groups"]
    ]
    active_skills = sorted(
        skill_name
        for group_name in active_groups
        for skill_name in inventory.active_grouped.get(group_name, [])
    )
    return {
        "command": command,
        "config_path": str(CONFIG_PATH),
        "disabled_groups_dir": str(DISABLED_GROUPS_DIR),
        "always_on_groups": config["always_on_groups"],
        "available_groups": available_groups,
        "optional_groups": optional_groups,
        "active_groups": active_groups,
        "changed_groups": changed_groups,
        "changed_skills": moved_skills,
        "grouped_skills": inventory.grouped,
        "active_grouped_skills": inventory.active_grouped,
        "disabled_grouped_skills": inventory.disabled_grouped,
        "active_skills": active_skills,
        "ungrouped_skills": inventory.ungrouped,
        "suggested_commands": {
            "status": "/skills status",
            "enable_examples": [
                f"/skills on {group_name}" for group_name in optional_groups
            ],
            "set_examples": [
                f"/skills set {group_name}" for group_name in optional_groups
            ],
        },
    }


def print_human(result: dict[str, Any]) -> None:
    print(f"命令: {result['command']}")
    print(f"配置文件: {result['config_path']}")
    print(f"停用目录: {result['disabled_groups_dir']}")
    print("始终启用组: " + ", ".join(result["always_on_groups"]))
    print("可选 groups: " + ", ".join(result["available_groups"]))
    if result["optional_groups"]:
        print("可开关 groups: " + ", ".join(result["optional_groups"]))
    print("当前激活组: " + ", ".join(result["active_groups"]))
    if result["changed_groups"]:
        print("本次变更组: " + ", ".join(result["changed_groups"]))
    else:
        print("本次变更组: 无")
    if result["changed_skills"]:
        print("受影响 skills: " + ", ".join(result["changed_skills"]))
    else:
        print("受影响 skills: 无")
    print("组内 skills:")
    for group_name in sorted(result["grouped_skills"]):
        all_members = result["grouped_skills"][group_name]
        active_members = result["active_grouped_skills"][group_name]
        disabled_members = result["disabled_grouped_skills"][group_name]
        summary = ", ".join(all_members) if all_members else "(空)"
        print(f"- {group_name}: {summary}")
        print(
            "  可见: "
            + (", ".join(active_members) if active_members else "(空)")
            + " | 已隐藏: "
            + (", ".join(disabled_members) if disabled_members else "(空)")
        )
    if result["ungrouped_skills"]:
        print(
            "未分组 skills: "
            + ", ".join(result["ungrouped_skills"])
            + "。请在 group_rules 中补充显式规则。"
        )
    print("常用命令:")
    print(f"- {result['suggested_commands']['status']}")
    for command in result["suggested_commands"]["enable_examples"]:
        print(f"- {command}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    json_requested = "--json" in argv
    normalized_argv = [arg for arg in argv if arg != "--json"]

    parser = argparse.ArgumentParser(
        description="按组管理当前项目的本地 skill 启用状态。"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出机器可读 JSON",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")

    parser_on = subparsers.add_parser("on")
    parser_on.add_argument("groups", nargs="+")

    parser_off = subparsers.add_parser("off")
    parser_off.add_argument("groups", nargs="+")

    parser_set = subparsers.add_parser("set")
    parser_set.add_argument("groups", nargs="+")

    args = parser.parse_args(normalized_argv)
    if json_requested:
        args.json = True
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = ensure_config()
    groups = normalize_group_tokens(getattr(args, "groups", []) or [])

    try:
        config, changed_groups, moved_skills = apply_command(config, args.command, groups)
        inventory = build_inventory(config)
        result = build_response(config, inventory, args.command, changed_groups, moved_skills)
    except SkillGroupError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2

    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
