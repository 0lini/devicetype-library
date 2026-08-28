#!/usr/bin/env python3
"""Apply Universal Ethernet faceplate labels to FabricEngine device types."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "device-types" / "Extreme Networks"

SPBM_7830_COMMENT = (
    "In SPBM low bandwidth mode, installing 7830-VIM-16CE in VIM2 (slot 3) reserves "
    "ports 3/13-3/16; installing 7830-VIM-8DE in VIM2 reserves ports 3/7-3/8. "
    "Otherwise no VIM ports are reserved."
)

# model suffix -> {bay_or_iface_name: faceplate label}
LABEL_RULES: dict[str, dict[str, str]] = {
    "4220-8X": {"1/7": "U1", "1/8": "U2"},
    "4220-4MW-8P-4X": {"1/15": "U1", "1/16": "U2"},
    "4220-4MW-20P-4X": {"1/27": "U1", "1/28": "U2"},
    "4220-12T-4X": {"1/15": "U1", "1/16": "U2"},
    "4220-12P-4X": {"1/15": "U1", "1/16": "U2"},
    "4220-24T-4X": {"1/27": "U1", "1/28": "U2"},
    "4220-24P-4X": {"1/27": "U1", "1/28": "U2"},
    "4220-48T-4X": {"1/51": "U1", "1/52": "U2"},
    "4220-48P-4X": {"1/51": "U1", "1/52": "U2"},
    "4220-8MW-40P-4X": {"1/51": "U1", "1/52": "U2"},
    "4120-24MW-4Y": {"1/29": "U1", "1/30": "U2"},
    "4120-48MW-4Y": {"1/53": "U1", "1/54": "U2"},
}

PORT24_5420 = [
    "5420F-24T-4XE",
    "5420F-8W-16P-4XE",
    "5420F-24P-4XE",
    "5420F-24S-4XE",
    "5420M-24T-4YE",
    "5420M-24W-4YE",
]
for m in PORT24_5420:
    LABEL_RULES[m] = {"1/29": "U1", "1/30": "U2"}

PORT48_5420 = [
    "5420F-48T-4XE",
    "5420F-16MW-32P-4XE",
    "5420F-16W-32P-4XE",
    "5420F-48P-4XE",
    "5420F-48P-4XL",
    "5420M-48T-4YE",
    "5420M-48W-4YE",
    "5420M-16MW-32P-4YE",
    "5420M-24W-24S-4YE",
]
for m in PORT48_5420:
    LABEL_RULES[m] = {"1/53": "U1", "1/54": "U2"}

PORT24_5520 = ["5520-24T", "5520-24W", "5520-24X"]
for m in PORT24_5520:
    LABEL_RULES[m] = {"1/25": "U1", "1/26": "U2"}

PORT48_5520 = ["5520-12MW-36W", "5520-48SE", "5520-48T", "5520-48W"]
for m in PORT48_5520:
    LABEL_RULES[m] = {"1/49": "U1", "1/50": "U2"}

LABEL_RULES["5720-24MW"] = {"1/25": "U1", "1/26": "U2"}
LABEL_RULES["5720-24MXW"] = LABEL_RULES["5720-24MW"].copy()
LABEL_RULES["5720-48MW"] = {"1/49": "U1", "1/50": "U2"}
LABEL_RULES["5720-48MXW"] = LABEL_RULES["5720-48MW"].copy()

for m in ("5320-24P-8XE", "5320-24T-8XE"):
    LABEL_RULES.setdefault(m, {}).update({"1/31": "U1", "1/32": "U2"})
for m in ("5320-48P-8XE", "5320-48T-8XE"):
    LABEL_RULES.setdefault(m, {}).update({"1/55": "U1", "1/56": "U2"})
for m in ("5320-16P-4XE", "5320-16P-4XE-DC"):
    LABEL_RULES.setdefault(m, {}).update({"1/19": "U1", "1/20": "U2"})

KEEP_DESCRIPTION_PREFIXES = (
    "Removable storage",
    "Redundant",
    "Fixed power",
    "LRM capable",
    "Direct to CPU",
    "CPU and BMC",
    "40/100G only",
    "100M/1G/10G RJ-45 OOB",
    "1G/10G SFP+ OOB",
)


def should_drop_description(desc: str) -> bool:
    if any(desc.startswith(prefix) for prefix in KEEP_DESCRIPTION_PREFIXES):
        return False
    lowered = desc.lower()
    drop_markers = (
        "spbm",
        "stacking",
        "internal loopback",
        "100gb ethernet",
        "last sfp+",
        "supports ",
        "universal ethernet port",
        "vim slot reserved",
        "for normal use or for",
        "connects at 1x40gb",
    )
    return any(marker in lowered for marker in drop_markers)


def strip_redundant_descriptions(data: dict) -> bool:
    changed = False
    for section in ("interfaces", "module-bays"):
        for item in data.get(section, []) or []:
            desc = item.get("description")
            if desc and should_drop_description(desc):
                del item["description"]
                changed = True
    return changed


def apply_label_rules(data: dict, rules: dict[str, str]) -> None:
    for item in data.get("module-bays", []) or []:
        name = item.get("name")
        if name in rules:
            item["label"] = rules[name]
            item.pop("description", None)


def dump_yaml(data: dict) -> str:
    body = yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{body}"


def main() -> None:
    updated = []
    for model, rules in LABEL_RULES.items():
        path = DT / f"FabricEngine-{model}.yaml"
        if not path.exists():
            print(f"SKIP missing {path.name}")
            continue
        data = yaml.safe_load(path.read_text())
        apply_label_rules(data, rules)
        path.write_text(dump_yaml(data))
        updated.append(path.name)

    path = DT / "FabricEngine-7830-32CE-8DE.yaml"
    data = yaml.safe_load(path.read_text())
    base = data.get("comments", "")
    if SPBM_7830_COMMENT not in base:
        data["comments"] = f"{base.rstrip()} {SPBM_7830_COMMENT}"
    path.write_text(dump_yaml(data))
    updated.append(path.name)

    for path in sorted(DT.glob("FabricEngine-*.yaml")):
        data = yaml.safe_load(path.read_text())
        if strip_redundant_descriptions(data):
            path.write_text(dump_yaml(data))
            updated.append(path.name)

    print(f"Updated {len(set(updated))} files")


if __name__ == "__main__":
    main()
