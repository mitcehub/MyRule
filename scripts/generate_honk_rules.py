"""Generate Honk remote rule sources and references from the shared Clash lists."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"Direct": "direct", "Proxy": "🚀 节点选择", "AI": "🤖 ChatGPT"}
MATCHERS = {"DOMAIN": "full", "DOMAIN-SUFFIX": "suffix", "DOMAIN-KEYWORD": "keyword"}


def render(name, outbound):
    source = ROOT / "Clash" / f"{name}.list"
    lines = [f"# Generated from Clash/{name}.list; edit that list and run scripts/generate_honk_rules.py.",
             "# Routing fragment only: no nodes, subscriptions, groups or fallback.", "routing {"]
    count = 0
    for number, raw in enumerate(source.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2 or parts[0] not in MATCHERS or not parts[1]:
            raise ValueError(f"{source.relative_to(ROOT)}:{number}: unsupported rule: {line}")
        value = parts[1]
        if any(ord(char) < 32 for char in value) or '"' in value or "\\" in value:
            raise ValueError(f"{source.relative_to(ROOT)}:{number}: unsupported character in domain")
        value = json.dumps(value, ensure_ascii=False)
        lines.append(f"    domain({MATCHERS[parts[0]]}: {value}) -> {outbound}")
        count += 1
    lines.append("}")
    source_name = "my-" + name.lower()
    return (f"# Requires Honk with remote rule_set support; not a static matcher list.\n"
            f"rule_set {{\n    {source_name} {{\n"
            f"        url: 'https://raw.githubusercontent.com/mitcehub/MyRule/main/Honk/remote/{name}.list'\n"
            "        format: text\n        behavior: classical\n"
            "        route: '🇭🇰 港台自动'\n        interval: 86400\n    }\n}\n"
            f"routing {{\n    rule_set('{source_name}') -> {outbound}\n}}\n"), count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated files without changing them")
    args = parser.parse_args()
    # Render every input first, so an unsupported rule cannot cause a partial update.
    rendered = {name: render(name, outbound) for name, outbound in TARGETS.items()}
    stale = []
    for name, (content, count) in rendered.items():
        output = ROOT / "Honk" / f"{name}.dae"
        expected = content.encode("utf-8")
        if args.check:
            if not output.exists() or output.read_bytes() != expected:
                stale.append(str(output.relative_to(ROOT)))
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(expected)
        print(f"Honk/{name}.dae: {count} rules")
        # The remote rule_set reader expects action-free classical lists.
        # Reuse the validated source instead of maintaining another domain list.
        remote = ROOT / "Honk" / "remote" / f"{name}.list"
        entries = [line.strip() for line in (ROOT / "Clash" / f"{name}.list")
                   .read_text(encoding="utf-8-sig").splitlines()
                   if line.strip() and not line.lstrip().startswith("#")]
        remote_bytes = (f"# Generated from Clash/{name}.list; no outbound actions.\n"
                        + "\n".join(entries) + "\n").encode("utf-8")
        if args.check:
            if not remote.exists() or remote.read_bytes() != remote_bytes:
                stale.append(str(remote.relative_to(ROOT)))
        else:
            remote.parent.mkdir(parents=True, exist_ok=True)
            remote.write_bytes(remote_bytes)
        print(f"Honk/remote/{name}.list: {len(entries)} rules")
    if stale:
        parser.exit(1, "Generated files need updating: " + ", ".join(stale) + "\n")


if __name__ == "__main__":
    main()
