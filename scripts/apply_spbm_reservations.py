#!/usr/bin/env python3
"""Apply SPBM loopback port reservation descriptions to FabricEngine device types."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "device-types" / "Extreme Networks"

SPBM_LOW = "Reserved for internal loopback in SPBM low bandwidth mode"
SPBM_UE_LOW = (
    "Universal Ethernet port; reserved for internal loopback in SPBM low bandwidth mode"
)
SPBM_VIM = "VIM slot reserved for internal loopback in SPBM vim bandwidth mode"
SPBM_VIM_HIGH = (
    "VIM slot reserved for internal loopback in SPBM high/vim bandwidth mode"
)
SPBM_UE_HIGH = (
    "Universal Ethernet port; reserved for internal loopback in SPBM high/vim bandwidth mode"
)
SPBM_4220_SFP = (
    "Last SFP+ port; in SPBM high bandwidth mode UNI-NNI and NNI-UNI bandwidth is limited to 1 Gbps"
)

# model suffix -> {bay_or_iface_name: (label, description)}
RULES: dict[str, dict[str, tuple[str | None, str | None]]] = {
    # 5320 8XE - already mostly correct; normalize descriptions
    "5320-24P-8XE": {
        "1/25": (None, SPBM_LOW),
        "1/26": (None, SPBM_LOW),
        "1/27": (None, SPBM_LOW),
    },
    "5320-24T-8XE": {
        "1/25": (None, SPBM_LOW),
        "1/26": (None, SPBM_LOW),
        "1/27": (None, SPBM_LOW),
    },
    "5320-48P-8XE": {
        "1/49": (None, SPBM_LOW),
        "1/50": (None, SPBM_LOW),
        "1/51": (None, SPBM_LOW),
    },
    "5320-48T-8XE": {
        "1/49": (None, SPBM_LOW),
        "1/50": (None, SPBM_LOW),
        "1/51": (None, SPBM_LOW),
    },
    # 4220 - last 2 SFP+ only
    "4220-8X": {
        "1/7": ("7", SPBM_4220_SFP),
        "1/8": ("8", SPBM_4220_SFP),
    },
    "4220-4MW-8P-4X": {
        "1/15": ("15", SPBM_4220_SFP),
        "1/16": ("16", SPBM_4220_SFP),
    },
    "4220-4MW-20P-4X": {
        "1/27": ("27", SPBM_4220_SFP),
        "1/28": ("28", SPBM_4220_SFP),
    },
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
    RULES[m] = {
        "1/29": ("29", SPBM_UE_LOW),
        "1/30": ("30", SPBM_UE_LOW),
    }

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
    RULES[m] = {
        "1/53": ("53", SPBM_UE_LOW),
        "1/54": ("54", SPBM_UE_LOW),
    }

PORT24_5520 = ["5520-24T", "5520-24W", "5520-24X"]
for m in PORT24_5520:
    RULES[m] = {
        "1/25": ("25", SPBM_UE_LOW),
        "1/26": ("26", SPBM_UE_LOW),
        "VIM": (None, SPBM_VIM),
    }

PORT48_5520 = ["5520-12MW-36W", "5520-48SE", "5520-48T", "5520-48W"]
for m in PORT48_5520:
    RULES[m] = {
        "1/49": ("49", SPBM_UE_LOW),
        "1/50": ("50", SPBM_UE_LOW),
        "VIM": (None, SPBM_VIM),
    }

RULES["5720-24MW"] = {
    "1/25": ("25", None),
    "1/26": ("26", None),
    "VIM": (None, SPBM_VIM_HIGH),
}
RULES["5720-24MXW"] = RULES["5720-24MW"].copy()

RULES["5720-48MW"] = {
    "1/49": ("49", SPBM_UE_HIGH),
    "1/50": ("50", SPBM_UE_HIGH),
    "VIM": (None, SPBM_VIM_HIGH),
}
RULES["5720-48MXW"] = RULES["5720-48MW"].copy()

IFACE_RULES: dict[str, dict[str, str]] = {
    "7520-48XT-6C": {
        "1/54": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode disabled)"
        ),
        "1/53": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode enabled)"
        ),
    },
    "7520-48Y-8C": {
        "1/55": "Reserved for internal loopback in SPBM high bandwidth mode",
        "1/56": "Reserved for internal loopback in SPBM high bandwidth mode",
        "1/54": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode disabled)"
        ),
        "1/53": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode enabled)"
        ),
    },
    "7520-48YE-8CE": {
        "1/55": "Reserved for internal loopback in SPBM high bandwidth mode",
        "1/56": "Reserved for internal loopback in SPBM high bandwidth mode",
        "1/54": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode disabled)"
        ),
        "1/53": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode enabled)"
        ),
    },
    "7720-32C": {
        "1/31": "Reserved for internal loopback in SPBM high bandwidth mode",
        "1/32": "Reserved for internal loopback in SPBM high bandwidth mode",
        "1/30": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode disabled)"
        ),
        "1/29": (
            "Reserved for internal loopback in SPBM high bandwidth mode "
            "(VXLAN Full Interworking Mode enabled)"
        ),
    },
}

SPBM_7830_COMMENT = (
    "In SPBM low bandwidth mode, installing 7830-VIM-16CE in VIM2 (slot 3) reserves "
    "ports 3/13-3/16; installing 7830-VIM-8DE in VIM2 reserves ports 3/7-3/8. "
    "Otherwise no VIM ports are reserved."
)


def apply_bay_rules(data: dict, rules: dict[str, tuple[str | None, str | None]]) -> None:
    for section in ("module-bays",):
        items = data.get(section)
        if not items:
            continue
        for item in items:
            name = item.get("name")
            if name not in rules:
                continue
            label, desc = rules[name]
            if label is not None:
                item["label"] = label
            if desc is not None:
                item["description"] = desc
            elif "description" in item and desc is None:
                # Clear stale stacking/loopback text when explicitly unset
                stale = (
                    "Can be used for stacking",
                    "Connects at 1x40Gb",
                    "Reserved for internal loopback when a VIM is installed",
                )
                if any(item["description"].startswith(s) for s in stale):
                    del item["description"]


def apply_iface_rules(data: dict, rules: dict[str, str]) -> None:
    for item in data.get("interfaces", []) or []:
        name = item.get("name")
        if name in rules:
            item["description"] = rules[name]


def dump_yaml(data: dict) -> str:
    body = yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{body}"


def main() -> None:
    updated = []
    for model, rules in RULES.items():
        path = DT / f"FabricEngine-{model}.yaml"
        if not path.exists():
            print(f"SKIP missing {path.name}")
            continue
        data = yaml.safe_load(path.read_text())
        apply_bay_rules(data, rules)
        path.write_text(dump_yaml(data))
        updated.append(path.name)

    for model, rules in IFACE_RULES.items():
        path = DT / f"FabricEngine-{model}.yaml"
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text())
        apply_iface_rules(data, rules)
        path.write_text(dump_yaml(data))
        updated.append(path.name)

    path = DT / "FabricEngine-7830-32CE-8DE.yaml"
    data = yaml.safe_load(path.read_text())
    base = data.get("comments", "")
    if SPBM_7830_COMMENT not in base:
        data["comments"] = f"{base.rstrip()} {SPBM_7830_COMMENT}"
    path.write_text(dump_yaml(data))
    updated.append(path.name)

    print(f"Updated {len(set(updated))} files")


if __name__ == "__main__":
    main()
