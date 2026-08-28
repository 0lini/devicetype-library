#!/usr/bin/env python3
"""Generate FabricEngine device-type YAMLs from Switch Engine definitions."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "device-types" / "Extreme Networks"
MT = ROOT / "module-types" / "Extreme Networks"

OPTICAL_TYPES = {
    "10gbase-x-sfpp",
    "25gbase-x-sfp28",
    "1000base-x-sfp",
    "100gbase-x-sfpdd",
    "100gbase-x-qsfp28",
    "400gbase-x-qsfpdd",
    "400gbase-x-qsfp56",
    "100gbase-x-sfp56",
}

SERIES_COMMENTS = {
    "5420": (
        "Dual-persona Universal Hardware running Fabric Engine (VOSS). "
        "[5420 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5420-Series-Data-Sheet)"
    ),
    "5520": (
        "Dual-persona Universal Hardware running Fabric Engine (VOSS). Modular PSUs and VIM slot. "
        "[5520 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5520-Series-Data-Sheet)"
    ),
    "5120": (
        "Dual-persona Universal Hardware running Fabric Engine (VOSS). Modular PSUs. "
        "[5120 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/5120-Series-Data-Sheet)"
    ),
    "4120": (
        "Dual-persona Universal Hardware running Fabric Engine (VOSS). "
        "[4000 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/4000-Series-Data-Sheet?v=bb9ebc88)"
    ),
    "4220": (
        "Dual-persona Universal Hardware running Fabric Engine (VOSS). "
        "[4000 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/4000-Series-Data-Sheet?v=bb9ebc88)"
    ),
    "7520": (
        "Dual-persona Universal Hardware running Fabric Engine (VOSS). Modular PSUs. "
        "[7520 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/b5da59835f5d4d10b740208284c8bc09?v=9df9bc2b)"
    ),
}

# Leaf/aggregation platforms model fixed QSFP ports as interfaces (not module-bays).
DENSE_OPTICAL_PREFIXES = ("7520", "7720", "7830")

SOURCES = sorted(
    p.name
    for p in DT.glob("*.yaml")
    if re.match(r"^(5420[A-Z]?|5520|5120|4120|4220|7520)-", p.name)
    and "FabricEngine" not in p.name
)


def slugify(model: str) -> str:
    return f"extreme-networks-fabricengine-{model.lower()}"


def is_numeric_port(name: str) -> bool:
    return bool(re.fullmatch(r"\d+", name))


def convert_interface(
    iface: dict, port_num: int, dense_optical: bool = False
) -> tuple[dict | None, dict | None]:
    """Return (interface, module_bay) — one may be None."""
    name = iface["name"]
    itype = iface.get("type", "")

    if name in ("U1", "U2"):
        if dense_optical:
            new_iface = {k: v for k, v in iface.items()}
            new_iface["name"] = f"1/{port_num}"
            new_iface["label"] = name
            return new_iface, None
        bay = {
            "name": f"1/{port_num}",
            "label": name,
            "position": f"1/{port_num}",
        }
        if iface.get("description"):
            bay["description"] = iface["description"]
        return None, bay

    if is_numeric_port(name):
        n = int(name)
        if itype in OPTICAL_TYPES and not dense_optical:
            bay = {"name": f"1/{n}", "label": str(n), "position": f"1/{n}"}
            if iface.get("description"):
                bay["description"] = iface["description"]
            return None, bay
        new_iface = {k: v for k, v in iface.items()}
        new_iface["name"] = f"1/{n}"
        new_iface["label"] = str(n)
        return new_iface, None

    return iface, None


def normalize_power_ports(power_ports: list[dict] | None) -> list[dict] | None:
    if not power_ports:
        return None
    out = []
    for pp in power_ports:
        pp = dict(pp)
        n = pp.get("name", "")
        if n in ("Power", "C14", "PSU1"):
            pp["name"] = "PS#1"
        elif n == "RPS1":
            pp["name"] = "PS#2"
        out.append(pp)
    return out


def normalize_module_bays(bays: list[dict] | None) -> list[dict] | None:
    if not bays:
        return None
    out = []
    for bay in bays:
        bay = dict(bay)
        n = bay.get("name", "")
        if n in ("PSU-1", "PSU1"):
            bay["name"] = "PS#1"
        elif n in ("PSU-2", "PSU2"):
            bay["name"] = "PS#2"
        elif n == "5520-VIM-4":
            bay["name"] = "VIM"
        if "position" in bay and bay["position"] is not None:
            bay["position"] = str(bay["position"])
        out.append(bay)
    return out


def normalize_console(consoles: list[dict] | None) -> list[dict]:
    if not consoles:
        return [{"name": "Console", "type": "rj-45"}]
    out = []
    for c in consoles:
        c = dict(c)
        if c.get("name") in ("RJ45", "Console"):
            c["name"] = "Console"
            c["type"] = "rj-45"
        elif c.get("name") in ("USB", "usb", "USB console"):
            c["name"] = "USB console"
            c["type"] = "usb-micro-b"
        out.append(c)
    return out


def convert_device(src: Path) -> dict:
    data = yaml.safe_load(src.read_text())
    model = data["model"]

    out: dict = {}
    skip_keys = {
        "model", "slug", "interfaces", "module-bays", "power-ports", "console-ports",
        "comments", "front_image", "rear_image",
    }
    for k, v in data.items():
        if k not in skip_keys:
            out[k] = v

    fe_model = f"FabricEngine-{model}"
    out["manufacturer"] = "Extreme Networks"
    out["model"] = fe_model
    out["part_number"] = model
    out["slug"] = slugify(model)
    prefix = re.match(r"^(5420[A-Z]?|5520|5120|4120|4220|7520)", model).group(1)
    if prefix.startswith("5420"):
        prefix = "5420"
    out["comments"] = SERIES_COMMENTS.get(
        prefix, "Dual-persona Universal Hardware running Fabric Engine (VOSS)."
    )
    dense_optical = model.startswith(DENSE_OPTICAL_PREFIXES)

    out["console-ports"] = normalize_console(data.get("console-ports"))

    raw_ifaces = data.get("interfaces", [])
    max_port = max(
        (int(i["name"]) for i in raw_ifaces if is_numeric_port(i["name"])),
        default=0,
    )
    u_assign = {"U1": None, "U2": None}

    interfaces = []
    module_bays = list(normalize_module_bays(data.get("module-bays")) or [])

    for iface in raw_ifaces:
        if iface["name"] in ("Mgmt", "Management"):
            continue
        if iface["name"] in u_assign:
            max_port += 1
            u_assign[iface["name"]] = max_port

    for iface in raw_ifaces:
        if iface["name"] in ("Mgmt", "Management"):
            continue
        port_num = int(iface["name"]) if is_numeric_port(iface["name"]) else u_assign.get(iface["name"])
        new_iface, bay = convert_interface(iface, port_num, dense_optical=dense_optical)
        if new_iface:
            interfaces.append(new_iface)
        if bay:
            module_bays.append(bay)

    mgmt = [
        {"name": "Mgmt-oob", "type": "1000base-t", "mgmt_only": True},
        {"name": "Mgmt-clip", "type": "virtual", "mgmt_only": True},
        {"name": "Mgmt-vlan", "type": "virtual", "mgmt_only": True},
    ]
    out["interfaces"] = mgmt + interfaces

    pp = normalize_power_ports(data.get("power-ports"))
    if pp:
        out["power-ports"] = pp
    if module_bays:
        out["module-bays"] = module_bays

    return out


def dump_yaml(data: dict) -> str:
    body = yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{body}"


def write_7830_chassis() -> None:
    data = {
        "manufacturer": "Extreme Networks",
        "model": "FabricEngine-7830-32CE-8DE",
        "slug": "extreme-networks-fabricengine-7830-32ce-8de",
        "part_number": "7830-32CE-8DE",
        "u_height": 2,
        "is_full_depth": True,
        "weight": 17.2,
        "weight_unit": "kg",
        "airflow": "front-to-rear",
        "comments": (
            "Dual-persona Universal Hardware running Fabric Engine (VOSS). "
            "32x100G QSFP28 (1/1-1/32) and 8x400G QSFP-DD (1/33-1/40); VIM1/VIM2 slots use "
            "2/x and 3/x respectively. Odd QSFP28 ports support channelization. "
            "[7830 Series Datasheet](https://extr-p-001.sitecorecontenthub.cloud/api/public/content/7830-series-data-sheet?v=7ba08e6a) | "
            "[7830 Series Installation Guide](https://documentation.extremenetworks.com/7830%20Series%20Installation%20Guide/downloads/7830_Series_Installation_Guide.pdf)"
        ),
        "console-ports": [{"name": "Console", "type": "rj-45"}],
        "interfaces": [
            {"name": "Mgmt-oob", "type": "1000base-t", "mgmt_only": True, "description": "100M/1G/10G RJ-45 OOB"},
            {
                "name": "Mgmt-oob-sfp",
                "type": "10gbase-x-sfpp",
                "mgmt_only": True,
                "description": "1G/10G SFP+ OOB",
            },
            {"name": "Mgmt-clip", "type": "virtual", "mgmt_only": True},
            {"name": "Mgmt-vlan", "type": "virtual", "mgmt_only": True},
        ]
        + [
            {"name": f"1/{i}", "label": str(i), "type": "100gbase-x-qsfp28"}
            for i in range(1, 33)
        ]
        + [
            {"name": f"1/{i}", "label": str(i), "type": "400gbase-x-qsfpdd"}
            for i in range(33, 41)
        ],
        "module-bays": [
            {"name": "PS#1", "position": "1"},
            {"name": "PS#2", "position": "2"},
            {"name": "VIM1", "position": "2"},
            {"name": "VIM2", "position": "3"},
        ],
    }
    (DT / "FabricEngine-7830-32CE-8DE.yaml").write_text(dump_yaml(data))


def write_vim_modules() -> None:
    vim5520 = [
        ("5520-VIM-4X-FabricEngine", "5520-VIM-4X", "4 x 10Gbase-X SFP+ ports (unpopulated)", "10gbase-x-sfpp", 4, 170),
        ("5520-VIM-4XE-FabricEngine", "5520-VIM-4XE", "4 x 1/10Gb SFP+ LRM and MACsec ports (unpopulated)", "10gbase-x-sfpp", 4, 170),
    ]
    for model, pn, comment, itype, count, weight in vim5520:
        data = {
            "manufacturer": "Extreme Networks",
            "model": model,
            "part_number": pn,
            "comments": comment,
            "weight": weight,
            "weight_unit": "g",
            "interfaces": [{"name": f"2/{i}", "type": itype} for i in range(1, count + 1)],
        }
        (MT / f"{pn}-FabricEngine.yaml").write_text(dump_yaml(data))

    vim7830_specs = [
        ("7830-VIM-24YE", "24 x 10/25G SFP28 ports (unpopulated). Use VIM1 (2/x) or VIM2 (3/x) bay.", "25gbase-x-sfp28", 24, 1360),
        ("7830-VIM-16CE", "16 x 100G QSFP28 ports (unpopulated). Use VIM1 (2/x) or VIM2 (3/x) bay.", "100gbase-x-qsfp28", 16, 1910),
        ("7830-VIM-8DE", "8 x 400G QSFP-DD ports (unpopulated). Use VIM1 (2/x) or VIM2 (3/x) bay.", "400gbase-x-qsfpdd", 8, 1650),
        ("7830-VIM-24CE", "24 x 100G SFP56-DD ports (unpopulated). Use VIM1 (2/x) or VIM2 (3/x) bay.", "100gbase-x-sfpdd", 24, 1650),
    ]
    for pn, comment, itype, count, weight_g in vim7830_specs:
        data = {
            "manufacturer": "Extreme Networks",
            "model": f"{pn}-FabricEngine",
            "part_number": pn,
            "comments": comment,
            "weight": round(weight_g / 1000, 2),
            "weight_unit": "kg",
            "interfaces": [{"name": f"{{module}}/{i}", "type": itype} for i in range(1, count + 1)],
        }
        (MT / f"{pn}-FabricEngine.yaml").write_text(dump_yaml(data))

    psu7830 = [
        ("XN-ACPWR-2400W-FB", "2400W AC PSU, front-to-back (C20 inlet). 7830 Series.", "iec-60320-c20", 2400, 0.95, "front-to-rear"),
        ("XN-ACPWR-2400W-BF", "2400W AC PSU, back-to-front (C20 inlet). 7830 Series.", "iec-60320-c20", 2400, 0.93, "rear-to-front"),
        ("XN-DCPWR-2400W-FB", "2400W DC PSU, front-to-back. 7830 Series.", "dc-terminal", 2400, 0.95, "front-to-rear"),
        ("XN-DCPWR-2400W-BF", "2400W DC PSU, back-to-front. 7830 Series.", "dc-terminal", 2400, 0.93, "rear-to-front"),
    ]
    for model, comment, ptype, draw, weight, airflow in psu7830:
        if (MT / f"{model}.yaml").exists():
            continue
        data = {
            "manufacturer": "Extreme Networks",
            "model": model,
            "part_number": model,
            "comments": comment,
            "weight": weight,
            "weight_unit": "kg",
            "airflow": airflow,
            "power-ports": [{"name": "PS#{module}", "type": ptype, "maximum_draw": draw}],
        }
        (MT / f"{model}.yaml").write_text(dump_yaml(data))


def main() -> None:
    created = []
    for name in SOURCES:
        src = DT / name
        model = yaml.safe_load(src.read_text())["model"]
        dst = DT / f"FabricEngine-{model}.yaml"
        out = convert_device(src)
        dst.write_text(dump_yaml(out))
        created.append(dst.name)

    write_7830_chassis()
    created.append("FabricEngine-7830-32CE-8DE.yaml")
    write_vim_modules()

    print(f"Generated {len(created)} device types:")
    for n in sorted(created):
        print(f"  {n}")


if __name__ == "__main__":
    main()
