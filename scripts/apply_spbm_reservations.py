#!/usr/bin/env python3
"""Apply SPBM loopback port reservations to FabricEngine device types."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "device-types" / "Extreme Networks"
MT = ROOT / "module-types" / "Extreme Networks"

SPBM_LOW = "Reserved for internal loopback in SPBM low bandwidth mode"
SPBM_UE_LOW = (
    "Reserved for internal loopback in SPBM low bandwidth mode (Universal Ethernet port). "
    "See 5420 Series documentation for restrictions on using reserved loopback ports "
    "as front-panel ports."
)
SPBM_UE_LOW_5520 = (
    "Reserved for internal loopback in SPBM low bandwidth mode (Universal Ethernet port)"
)
SPBM_VIM = "VIM slot reserved for internal loopback in SPBM vim bandwidth mode"
SPBM_VIM_HIGH = (
    "VIM slot reserved for internal loopback in SPBM high/vim bandwidth mode. "
    "Vim mode uses less internal bandwidth speed than high mode."
)
SPBM_UE_HIGH = (
    "Reserved for internal loopback in SPBM high/vim bandwidth mode (Universal Ethernet port)"
)
SPBM_4220_LAST_SFP = (
    "In SPBM high bandwidth mode (default), UNI-NNI and NNI-UNI bandwidth "
    "is limited to 1 Gbps (last SFP+ port)"
)
SPBM_HIGH = "Reserved for internal loopback in SPBM high bandwidth mode"
SPBM_HIGH_VXLAN_ON = (
    "Reserved for internal loopback in SPBM high bandwidth mode "
    "(VXLAN Full Interworking Mode enabled)"
)
SPBM_LOW_AND_HIGH = (
    "Reserved for internal loopback in SPBM low bandwidth mode and SPBM high bandwidth mode"
)
SPBM_7830_16CE_VIM2 = (
    "Reserved for internal loopback in SPBM low bandwidth mode when installed in VIM2 (slot 3)"
)
SPBM_7830_8DE_VIM2 = SPBM_7830_16CE_VIM2

SPBM_7830_COMMENT = (
    "In SPBM low bandwidth mode, installing 7830-VIM-16CE in VIM2 (slot 3) reserves "
    "ports 3/13-3/16; installing 7830-VIM-8DE in VIM2 reserves ports 3/7-3/8. "
    "Otherwise no VIM ports are reserved."
)

# model suffix -> {port_name: (label, description)}
MODULE_BAY_RULES: dict[str, dict[str, tuple[str | None, str | None]]] = {
    "4220-8X": {
        "1/7": ("U1", SPBM_4220_LAST_SFP),
        "1/8": ("U2", SPBM_4220_LAST_SFP),
    },
    "4220-4MW-8P-4X": {
        "1/15": ("U1", SPBM_4220_LAST_SFP),
        "1/16": ("U2", SPBM_4220_LAST_SFP),
    },
    "4220-4MW-20P-4X": {
        "1/27": ("U1", SPBM_4220_LAST_SFP),
        "1/28": ("U2", SPBM_4220_LAST_SFP),
    },
    "5320-24P-8XE": {
        "1/25": (None, SPBM_LOW),
        "1/26": (None, SPBM_LOW),
        "1/27": (None, SPBM_LOW),
        "1/31": ("U1", None),
        "1/32": ("U2", None),
    },
    "5320-24T-8XE": {
        "1/25": (None, SPBM_LOW),
        "1/26": (None, SPBM_LOW),
        "1/27": (None, SPBM_LOW),
        "1/31": ("U1", None),
        "1/32": ("U2", None),
    },
    "5320-48P-8XE": {
        "1/49": (None, SPBM_LOW),
        "1/50": (None, SPBM_LOW),
        "1/51": (None, SPBM_LOW),
        "1/55": ("U1", None),
        "1/56": ("U2", None),
    },
    "5320-48T-8XE": {
        "1/49": (None, SPBM_LOW),
        "1/50": (None, SPBM_LOW),
        "1/51": (None, SPBM_LOW),
        "1/55": ("U1", None),
        "1/56": ("U2", None),
    },
    "5720-24MW": {
        "1/25": ("U1", None),
        "1/26": ("U2", None),
        "VIM": (None, SPBM_VIM_HIGH),
    },
    "5720-24MXW": {
        "1/25": ("U1", None),
        "1/26": ("U2", None),
        "VIM": (None, SPBM_VIM_HIGH),
    },
    "5720-48MW": {
        "1/49": ("U1", SPBM_UE_HIGH),
        "1/50": ("U2", SPBM_UE_HIGH),
        "VIM": (None, SPBM_VIM_HIGH),
    },
    "5720-48MXW": {
        "1/49": ("U1", SPBM_UE_HIGH),
        "1/50": ("U2", SPBM_UE_HIGH),
        "VIM": (None, SPBM_VIM_HIGH),
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
    MODULE_BAY_RULES[m] = {
        "1/29": ("U1", SPBM_UE_LOW),
        "1/30": ("U2", SPBM_UE_LOW),
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
    MODULE_BAY_RULES[m] = {
        "1/53": ("U1", SPBM_UE_LOW),
        "1/54": ("U2", SPBM_UE_LOW),
    }

PORT24_5520 = ["5520-24T", "5520-24W", "5520-24X"]
for m in PORT24_5520:
    MODULE_BAY_RULES[m] = {
        "1/25": ("U1", SPBM_UE_LOW_5520),
        "1/26": ("U2", SPBM_UE_LOW_5520),
        "VIM": (None, SPBM_VIM),
    }

PORT48_5520 = ["5520-12MW-36W", "5520-48SE", "5520-48T", "5520-48W"]
for m in PORT48_5520:
    MODULE_BAY_RULES[m] = {
        "1/49": ("U1", SPBM_UE_LOW_5520),
        "1/50": ("U2", SPBM_UE_LOW_5520),
        "VIM": (None, SPBM_VIM),
    }

# Universal Ethernet labels only (no SPBM reservations per FE 8.6 matrix)
LABEL_ONLY: dict[str, dict[str, str]] = {
    "4220-12T-4X": {"1/15": "U1", "1/16": "U2"},
    "4220-12P-4X": {"1/15": "U1", "1/16": "U2"},
    "4220-24T-4X": {"1/27": "U1", "1/28": "U2"},
    "4220-24P-4X": {"1/27": "U1", "1/28": "U2"},
    "4220-48T-4X": {"1/51": "U1", "1/52": "U2"},
    "4220-48P-4X": {"1/51": "U1", "1/52": "U2"},
    "4220-8MW-40P-4X": {"1/51": "U1", "1/52": "U2"},
    "4120-24MW-4Y": {"1/29": "U1", "1/30": "U2"},
    "4120-48MW-4Y": {"1/53": "U1", "1/54": "U2"},
    "5320-16P-4XE": {"1/19": "U1", "1/20": "U2"},
    "5320-16P-4XE-DC": {"1/19": "U1", "1/20": "U2"},
}

IFACE_SPBM_RULES: dict[str, dict[str, str]] = {
    "7520-48XT-6C": {
        "1/54": SPBM_HIGH,
        "1/53": SPBM_HIGH_VXLAN_ON,
    },
    "7520-48Y-8C": {
        "1/55": SPBM_LOW_AND_HIGH,
        "1/56": SPBM_LOW_AND_HIGH,
        "1/54": SPBM_HIGH,
        "1/53": SPBM_HIGH_VXLAN_ON,
    },
    "7520-48YE-8CE": {
        "1/55": SPBM_LOW_AND_HIGH,
        "1/56": SPBM_LOW_AND_HIGH,
        "1/54": SPBM_HIGH,
        "1/53": SPBM_HIGH_VXLAN_ON,
    },
    "7720-32C": {
        "1/31": SPBM_LOW_AND_HIGH,
        "1/32": SPBM_LOW_AND_HIGH,
        "1/30": SPBM_HIGH,
        "1/29": SPBM_HIGH_VXLAN_ON,
    },
}

VIM_MODULE_SPBM: dict[str, dict[str, str]] = {
    "7830-VIM-16CE-FabricEngine": {
        "{module}/13": SPBM_7830_16CE_VIM2,
        "{module}/14": SPBM_7830_16CE_VIM2,
        "{module}/15": SPBM_7830_16CE_VIM2,
        "{module}/16": SPBM_7830_16CE_VIM2,
    },
    "7830-VIM-8DE-FabricEngine": {
        "{module}/7": SPBM_7830_8DE_VIM2,
        "{module}/8": SPBM_7830_8DE_VIM2,
    },
}


def apply_module_bay_rules(
    data: dict, rules: dict[str, tuple[str | None, str | None]]
) -> None:
    for item in data.get("module-bays", []) or []:
        name = item.get("name")
        if name not in rules:
            continue
        label, desc = rules[name]
        if label is not None:
            item["label"] = label
        if desc is not None:
            item["description"] = desc
        else:
            item.pop("description", None)


def apply_label_only(data: dict, rules: dict[str, str]) -> None:
    for item in data.get("module-bays", []) or []:
        name = item.get("name")
        if name in rules:
            item["label"] = rules[name]


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

    for model, rules in MODULE_BAY_RULES.items():
        path = DT / f"FabricEngine-{model}.yaml"
        if not path.exists():
            print(f"SKIP missing {path.name}")
            continue
        data = yaml.safe_load(path.read_text())
        apply_module_bay_rules(data, rules)
        path.write_text(dump_yaml(data))
        updated.append(path.name)

    for model, rules in LABEL_ONLY.items():
        path = DT / f"FabricEngine-{model}.yaml"
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text())
        apply_label_only(data, rules)
        path.write_text(dump_yaml(data))
        updated.append(path.name)

    for model, rules in IFACE_SPBM_RULES.items():
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

    for model, rules in VIM_MODULE_SPBM.items():
        path = MT / f"{model}.yaml"
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text())
        apply_iface_rules(data, rules)
        path.write_text(dump_yaml(data))
        updated.append(path.name)

    print(f"Updated {len(set(updated))} files")


if __name__ == "__main__":
    main()
