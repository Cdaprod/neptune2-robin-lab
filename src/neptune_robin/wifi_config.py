from __future__ import annotations

from pathlib import Path
import os
import re


def read_env(path: str | Path) -> dict[str, str]:
    values: dict[str, str] = {}
    p = Path(path)
    if not p.exists():
        return values
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def desired_values(env: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    result = {
        "CFG_WIFI_MODE": merged.get("MKS_WIFI_MODE", "0"),
        "CFG_WIFI_AP_NAME": merged.get("WIFI_SSID", "cda_Lab"),
        "CFG_WIFI_KEY_CODE": merged.get("WIFI_PASSWORD", ""),
        "CFG_CLOUD_ENABLE": merged.get("MKS_CLOUD_ENABLE", "0"),
        "WISI_LIST_SCAN": merged.get("WIFI_LIST_SCAN", "1"),
        "DISABLE_WIFI": merged.get("DISABLE_WIFI", "0"),
    }
    if not result["CFG_WIFI_KEY_CODE"]:
        raise ValueError("WIFI_PASSWORD is empty; put it in .env")
    return result


def patch_config(text: str, values: dict[str, str]) -> str:
    lines = text.splitlines()
    seen: set[str] = set()

    for i, original in enumerate(lines):
        for key, value in values.items():
            m = re.match(
                rf"^(?P<indent>\s*)(?P<prefix>>?){re.escape(key)}\s+\S+(?P<comment>\s+#.*)?$",
                original,
                flags=re.IGNORECASE,
            )
            if m:
                prefix = m.group("prefix") or ">"
                comment = m.group("comment") or ""
                lines[i] = f"{m.group('indent')}{prefix}{key} {value}{comment}"
                seen.add(key)
                break

    missing = [k for k in values if k not in seen]
    if missing:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("# Wi-Fi directives added by neptune-robin")
        for key in missing:
            lines.append(f">{key} {values[key]}")

    return "\n".join(lines) + "\n"


def patch_file(source: str | Path, output: str | Path, env_path: str | Path = ".env") -> Path:
    source = Path(source)
    output = Path(output)
    values = desired_values(read_env(env_path))
    patched = patch_config(source.read_text(encoding="utf-8", errors="replace"), values)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(patched, encoding="utf-8")
    return output
