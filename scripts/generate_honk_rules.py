"""Generate action-free Honk remote lists from the shared Clash lists."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("Direct", "Proxy", "AI")
SUPPORTED = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}


def render(name):
    source = ROOT / "Clash" / f"{name}.list"
    entries = []
    for number, raw in enumerate(source.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2 or parts[0] not in SUPPORTED or not parts[1]:
            raise ValueError(f"{source.relative_to(ROOT)}:{number}: unsupported rule")
        if any(ord(char) < 32 for char in parts[1]):
            raise ValueError(f"{source.relative_to(ROOT)}:{number}: control character")
        entries.append(",".join(parts))
    if not entries:
        raise ValueError(f"{name}: empty source")
    return (f"# Generated from Clash/{name}.list; no outbound actions.\n" +
            "\n".join(entries) + "\n").encode("utf-8"), len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = {name: render(name) for name in NAMES}
    stale = []
    for name, (content, count) in rendered.items():
        output = ROOT / "Honk" / "remote" / f"{name}.list"
        if args.check:
            if not output.exists() or output.read_bytes() != content:
                stale.append(str(output.relative_to(ROOT)))
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        print(f"Honk/remote/{name}.list: {count} rules")
    if stale:
        parser.exit(1, "Generated files need updating: " + ", ".join(stale) + "\n")


if __name__ == "__main__":
    main()