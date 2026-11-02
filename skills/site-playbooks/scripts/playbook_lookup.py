#!/usr/bin/env python3
"""Look up, add, list, and lint per-site playbooks for browser-operating agents.

Store location: skills/site-playbooks/playbooks/ relative to this script
(i.e. <plugin>/skills/site-playbooks/playbooks/).

Subcommands:
  lookup <url|domain>  print the best-matching playbook (most specific glob wins)
  list                 one line per stored playbook
  add --file F --matches a,b [--force]
                       validate F's frontmatter and install it into the store
  lint                 parse every stored playbook, report failures

Python 3 stdlib only. Exit codes: 0 ok, 1 not found / validation failure /
lint failure, 2 usage or IO error.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

STORE = Path(__file__).resolve().parent.parent / "playbooks"
REQUIRED_SECTIONS = [
    "Quirks",
    "Login flow",
    "Anti-bot behavior",
    "Reliable selectors/strategy",
    "What to hand to the human",
]


def parse_frontmatter(text):
    """Parse the leading '---' fenced frontmatter block as key/value pairs.

    Values may be scalars ('site'), inline lists ([a, b]), or block lists
    ('-' lines). Returns (dict, body_after). Returns (None, None) when no
    well-formed frontmatter block is present.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    data = {}
    i = 1
    list_key = None
    while i < len(lines):
        raw = lines[i]
        if raw.strip() == "---":
            body = "\n".join(lines[i + 1:])
            return data, body
        if list_key is not None and raw.lstrip().startswith("-"):
            item = raw.lstrip()[1:].strip()
            if item:
                data[list_key].append(item)
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw.strip())
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                data[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
                list_key = None
            elif val == "":
                data[key] = []
                list_key = key
            else:
                data[key] = val.strip("'\"")
                list_key = None
        i += 1
    return None, None  # frontmatter never closed


def glob_to_regex(pattern):
    """Convert a domain glob to a regex where '*' matches within a single
    label (never across a dot). '*.github.com' therefore does NOT match the
    apex 'github.com'; 'github.com' matches only the apex host.
    """
    out = []
    for ch in pattern:
        if ch == "*":
            out.append("[^.]+")
        else:
            out.append(re.escape(ch))
    return "^" + "".join(out) + "$"


def pattern_matches(pattern, host):
    return re.match(glob_to_regex(pattern.lower()), host) is not None


def specificity(pattern):
    """Most specific pattern wins: plain domains beat 'domain-*' wildcards
    beat '*.suffix' wildcards; longer beats shorter within the same class."""
    p = pattern.lower()
    if p.endswith(".*"):
        cls, score = 0, len(p) - 2
    elif "*" in p:
        cls, score = 1, len(p)
    else:
        cls, score = 2, len(p)
    return (cls, score)


def host_of(target):
    """Extract the lowercased hostname from a URL or bare domain."""
    t = target.strip().lower()
    if "://" in t:
        t = urlsplit(t).hostname or ""
    elif t.startswith("www."):
        t = t[4:]
    t = t.split("/")[0].split("?")[0].split("#")[0]
    if ":" in t:
        t = t.rsplit(":", 1)[0]
    return t


def specificity(pattern):
    """Most specific pattern wins: exact domains beat wildcards, longer beats
    shorter. Wildcards score lower than plain strings of the same length."""
    p = pattern.lower()
    base = len(p)
    if "*" in p:
        base = int(base * 0.5)
    return base


def lookup(target):
    host = host_of(target)
    if not host:
        print("cannot read a host from %r" % target, file=sys.stderr)
        return 2
    best = None
    for pb in sorted(STORE.glob("*.md")):
        fm, _ = parse_frontmatter(pb.read_text(encoding="utf-8"))
        if fm is None:
            continue
        matches = fm.get("matches") or []
        if not isinstance(matches, list):
            matches = [matches]
        candidates = [host]
        if host.startswith("www."):
            candidates.append(host[4:])
        for pat in matches:
            pat_l = str(pat).lower().strip()
            for cand in candidates:
                if pattern_matches(pat_l, cand):
                    key = specificity(pat_l)
                    if best is None or key > best[0]:
                        best = (key, pat_l, pb.name)
                    break
    if best is None:
        print("no playbook matches %s (host %s)" % (target, host))
        return 1
    print("== playbook: %s (matched %s, host %s) ==" % (best[2], best[1], host))
    print((STORE / best[2]).read_text(encoding="utf-8"))
    return 0


def list_playbooks():
    if not STORE.exists() or not list(STORE.glob("*.md")):
        print("no playbooks in %s" % STORE)
        return 0
    for pb in sorted(STORE.glob("*.md")):
        fm, _ = parse_frontmatter(pb.read_text(encoding="utf-8"))
        kind = (fm or {}).get("kind", "?")
        matches = (fm or {}).get("matches") or []
        if isinstance(matches, list):
            matches = ",".join(matches)
        print("%s  kind=%s  matches=%s" % (pb.name, kind, matches))
    return 0


def lint_all():
    bad = 0
    files = sorted(STORE.glob("*.md")) if STORE.exists() else []
    if not files:
        print("nothing to lint: %s is empty" % STORE)
        return 0
    for pb in files:
        text = pb.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        errs = []
        if fm is None:
            errs.append("no frontmatter block")
        else:
            kind = fm.get("kind")
            if kind not in ("site", "pattern"):
                errs.append("kind missing or not site|pattern (got %r)" % kind)
            matches = fm.get("matches")
            if not isinstance(matches, list) or not matches:
                errs.append("matches must be a non-empty list")
        for section in REQUIRED_SECTIONS:
            if not re.search(r"^##\s+%s\b" % re.escape(section), body or "", re.M):
                errs.append("missing section: ## %s" % section)
        if errs:
            bad += 1
            print("%s: FAIL (%s)" % (pb.name, "; ".join(errs)))
        else:
            print("%s: ok" % pb.name)
    if bad:
        print("lint: %d of %d failed" % (bad, len(files)))
        return 1
    print("lint: all %d playbooks parse" % len(files))
    return 0


def add_playbook(args):
    src = Path(args.file)
    if not src.is_file():
        print("file not found: %s" % src, file=sys.stderr)
        return 2
    text = src.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        print("no frontmatter block: a playbook starts with '---' fenced frontmatter", file=sys.stderr)
        return 1
    kind = fm.get("kind")
    if kind not in ("site", "pattern"):
        print("frontmatter must have kind: site or kind: pattern (got %r)" % kind, file=sys.stderr)
        return 1
    cli_matches = [m.strip() for m in args.matches.split(",") if m.strip()]
    fm_matches = fm.get("matches")
    if isinstance(fm_matches, list):
        fm_matches = [str(x).strip() for x in fm_matches]
    elif fm_matches:
        fm_matches = [fm_matches]
    if cli_matches and not fm_matches:
        fm["matches"] = cli_matches
        fm_matches = cli_matches
        text = rebuild_with_matches(text, cli_matches)
    if not fm_matches:
        print("no matches: pass --matches a,b or list matches in frontmatter", file=sys.stderr)
        return 1
    for section in REQUIRED_SECTIONS:
        if not re.search(r"^##\s+%s\b" % re.escape(section), body or "", re.M):
            print("missing section: ## %s" % section, file=sys.stderr)
            return 1
    target = STORE / (src.stem + ".md")
    if target.exists() and not args.force:
        print("duplicate: %s already in store (use --force to replace)" % target.name, file=sys.stderr)
        return 1
    if args.force and target.exists():
        backup = target.with_suffix(".bak.md")
        shutil.copy2(target, backup)
        print("replaced %s (backup: %s)" % (target.name, backup.name))
    if not text.endswith("\n"):
        text += "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print("added %s (matches: %s)" % (target.name, ",".join(fm_matches)))
    return 0


def rebuild_with_matches(text, matches):
    """Insert a 'matches: [...]' line into the frontmatter block."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if i > 0 and ln.strip() == "---":
            lines.insert(i, "matches: [%s]" % ", ".join(matches))
            break
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="site-playbooks store CLI")
    sub = ap.add_subparsers(dest="cmd")
    p_look = sub.add_parser("lookup", help="print the best-matching playbook for a URL or domain")
    p_look.add_argument("target")
    sub.add_parser("list", help="list every stored playbook")
    p_add = sub.add_parser("add", help="validate and install a new playbook")
    p_add.add_argument("--file", required=True)
    p_add.add_argument("--matches", required=True, help="comma-separated globs, e.g. github.com,*.github.com")
    p_add.add_argument("--force", action="store_true", help="replace an existing playbook of the same name")
    sub.add_parser("lint", help="parse every stored playbook")
    a = ap.parse_args(argv)
    if a.cmd == "lookup":
        return lookup(a.target)
    if a.cmd == "list":
        return list_playbooks()
    if a.cmd == "add":
        return add_playbook(a)
    if a.cmd == "lint":
        return lint_all()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
