#!/usr/bin/env python3
"""Small, dependency-free governance checks. All comparisons fail closed."""
import argparse
import os
from pathlib import Path
import re
import subprocess


ROOT = "backend/crm/src/main/resources/migration/"


def git(*args):
    return subprocess.check_output(["git", *args], text=True).rstrip("\n")


def diff(base, mode, path=None):
    git("rev-parse", "--verify", base + "^{commit}")
    args = ["diff", "--no-renames", "--name-status", "-z"]
    if mode == "committed":
        args += [base, "HEAD"]
    elif mode == "staged":
        args += ["--cached", base]
    elif mode == "worktree":
        args += [base]
    else:
        raise ValueError("scope must be committed, staged or worktree")
    args += ["--"] + ([path] if path else [])
    parts = git(*args).split("\0")
    changes = list(zip(parts[0:-1:2], parts[1::2]))
    if mode == "worktree":
        changes += [("A", p) for p in git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
                    if p and (path is None or p.startswith(path))]
    return changes


def version(path):
    m = re.fullmatch(ROOT + r"(\d+(?:\.\d+)*)/(?:ddl|dml)/V(\d+(?:[._]\d+)*)__.+\.sql", path)
    if not m:
        raise ValueError("Invalid migration name: " + path)
    parts = tuple(int(x) for x in re.split(r"[._]", m[2]))
    prefix = tuple(int(x) for x in m[1].split("."))
    if parts[:len(prefix)] != prefix or len(parts) <= len(prefix):
        raise ValueError("Directory/version mismatch: " + path)
    while len(parts) > 1 and parts[-1] == 0:
        parts = parts[:-1]
    return parts


def migrations(base, mode):
    historical = [p for p in git("ls-tree", "-r", "--name-only", base, "--", ROOT).splitlines() if p.endswith(".sql")]
    used = {version(p): p for p in historical}
    highest = max(used, default=())
    for status, path in diff(base, mode, ROOT):
        if status != "A":
            raise ValueError("Applied migration is immutable: " + status + " " + path)
        v = version(path)
        if v in used or v <= highest:
            raise ValueError("Duplicate or out-of-order migration: " + path)
        used[v] = path
    print("Migration check passed: base=" + base + " scope=" + mode)


def classify(paths, full=False):
    flags = dict(backend=full, web=full, mobile=full)
    for path in paths:
        if path.startswith(("docs/", "openspec/")) or (path.endswith(".md") and "/" not in path):
            continue
        if path.startswith("backend/"):
            flags["backend"] = True
        elif path.startswith("frontend/packages/web/"):
            flags["web"] = True
        elif path.startswith("frontend/packages/mobile/"):
            flags["mobile"] = True
        elif path.startswith("frontend/") and path not in ("frontend/AGENTS.md",):
            flags["web"] = flags["mobile"] = True
        else:
            flags = dict.fromkeys(flags, True)
    return flags


def aggregate(flags, results):
    for name in ("policy", "classify"):
        if results.get(name) != "success":
            raise ValueError("Required job failed: " + name)
    for name, needed in flags.items():
        expected = "success" if needed else "skipped"
        if results.get(name) != expected:
            raise ValueError(name + ": expected " + expected + ", got " + str(results.get(name)))


def baseline(base, head_branch, base_branch):
    path = "governance/upstream-baseline.env"
    def parse(text):
        values = dict(re.findall(r"^(UPSTREAM_\w+)=(\S+)$", text, re.M))
        if values.get("UPSTREAM_URL") != "https://github.com/1Panel-dev/CordysCRM.git":
            raise ValueError("Unexpected upstream URL")
        if not re.fullmatch("[0-9a-f]{40}", values.get("UPSTREAM_COMMIT", "")):
            raise ValueError("Upstream commit must be a full SHA")
        return values["UPSTREAM_COMMIT"]
    old = parse(git("show", base + ":" + path))
    new = parse(Path(path).read_text())
    if old != new:
        if not (head_branch == "upstream-sync" and base_branch == "develop"
                or head_branch == "develop" and base_branch == "main"):
            raise ValueError("Baseline may change only in sync or develop promotion PR")
        git("fetch", "--no-tags", "https://github.com/1Panel-dev/CordysCRM.git",
            "+refs/heads/main:refs/remotes/governance-official/main")
        git("merge-base", "--is-ancestor", new, "refs/remotes/governance-official/main")
        git("merge-base", "--is-ancestor", old, new)
        print("Official migration impact (NOT upgrade approval):")
        print(git("diff", "--name-status", old, new, "--", ROOT))
    git("cat-file", "-e", new + "^{commit}")
    git("merge-base", "--is-ancestor", new, "HEAD")
    # Always check local patches, plus immutability relative to previously merged
    # local migrations. Official migration changes are handled by the report above.
    migrations(new, "committed")
    if old == new:
        migrations(base, "committed")
    else:
        official_paths = set(git("diff", "--name-only", old, new, "--", ROOT).splitlines())
        for status, p in diff(base, "committed", ROOT):
            if status != "A" and p not in official_paths:
                raise ValueError("Local migration changed during sync: " + p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["migrations", "classify", "aggregate", "baseline"])
    parser.add_argument("base", nargs="?", default="HEAD^")
    parser.add_argument("mode", nargs="?", default="committed")
    a = parser.parse_args()
    os.chdir(git("rev-parse", "--show-toplevel"))
    if a.command == "migrations":
        migrations(a.base, a.mode)
    elif a.command == "baseline":
        baseline(a.base, os.environ.get("HEAD_BRANCH", ""), os.environ.get("BASE_BRANCH", ""))
    elif a.command == "classify":
        full = (os.environ.get("BASE_BRANCH") == "main"
                or os.environ.get("HEAD_BRANCH") == "upstream-sync"
                or os.environ.get("EVENT") == "workflow_dispatch")
        paths = [p for _, p in diff(a.base, "committed")]
        for name, value in classify(paths, full).items():
            print(name + "=" + str(value).lower())
    else:
        flags = {}
        for name in ("backend", "web", "mobile"):
            flag = os.environ.get("PLAN_" + name.upper())
            if flag not in ("true", "false"):
                raise ValueError("Missing or invalid classification: " + name)
            flags[name] = flag == "true"
        aggregate(flags, {n: os.environ.get("RESULT_" + n.upper())
                          for n in ("policy", "classify", "backend", "web", "mobile")})


if __name__ == "__main__":
    main()
