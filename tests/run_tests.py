"""Vérifie le solveur sur les cas de test fournis avec le sujet.

Pour chaque graphe tests/data/test_afN.apx, compare aux fichiers attendus
test_afN_co.txt (sémantique complète) et test_afN_st.txt (sémantique stable) :
  - l'ensemble des extensions ;
  - les arguments acceptés de façon sceptique et crédule.

Usage : python tests/run_tests.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from my_solver import ArgumentationFramework  # noqa: E402

DATA = os.path.join(ROOT, "tests", "data")


def parse_expected(path):
    """Lit un fichier attendu : extensions, arguments sceptiques et crédules."""
    with open(path, encoding="utf-8") as fh:
        lines = [line.strip() for line in fh]

    extensions, skeptical, credulous = set(), set(), set()
    section = None
    for line in lines:
        if not line:
            continue
        if line.endswith("extensions:"):
            section = "ext"
        elif line.startswith("Skeptically"):
            section = "skep"
        elif line.startswith("Credulously"):
            section = "cred"
        elif section == "ext" and line.startswith("["):
            inside = line.strip("[]")
            extensions.add(frozenset(a for a in inside.split(",") if a))
        elif section in ("skep", "cred") and line != "None of them":
            args = {a.strip() for a in re.split(r"[,\s]+", line) if a.strip()}
            (skeptical if section == "skep" else credulous).update(args)
    return extensions, skeptical, credulous


def check(apx, semantics):
    af = ArgumentationFramework(apx)
    found = (af.find_complete_extensions() if semantics == "co"
             else af.find_stable_extensions())
    found = {frozenset(ext) for ext in found}

    expected_path = apx.replace(".apx", f"_{semantics}.txt")
    expected, skeptical, credulous = parse_expected(expected_path)

    arguments = set(af.arguments)
    got_skeptical = {a for a in arguments
                     if found and af.is_skeptically_accepted(a, found) == "YES"}
    got_credulous = {a for a in arguments
                     if af.is_credulously_accepted(a, found) == "YES"}

    errors = []
    if found != expected:
        errors.append(f"extensions {sorted(map(sorted, found))} != {sorted(map(sorted, expected))}")
    if got_skeptical != skeptical:
        errors.append(f"sceptiques {sorted(got_skeptical)} != {sorted(skeptical)}")
    if got_credulous != credulous:
        errors.append(f"crédules {sorted(got_credulous)} != {sorted(credulous)}")
    return errors


def main():
    failures = 0
    cases = sorted(f for f in os.listdir(DATA) if f.endswith(".apx"))
    for name in cases:
        for semantics in ("co", "st"):
            errors = check(os.path.join(DATA, name), semantics)
            status = "OK " if not errors else "ERR"
            print(f"[{status}] {name} ({semantics})")
            for err in errors:
                print("      ", err)
            failures += bool(errors)
    print(f"\n{2 * len(cases) - failures}/{2 * len(cases)} cas réussis")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
