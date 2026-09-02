#!/usr/bin/env python3
"""Redirect self-loop gate, adversarially tested.

The gate this exercises exists because loisirs73.fr shipped 816 self-looping
rules with every gate green. A guard written after such an incident is worth
nothing until it has been shown to fire on the exact shape that caused it, so
that is what these cases are:

  * the two forced shapes that took the 73 down (`/x/ -> /x` and `/x -> /x/`)
    trip the gate;
  * the unforced variant trips too — no forcing marker only DEFERS the loop to
    the first request with no matching file, it does not prevent it;
  * an absolute self-host URL on either side is normalised and caught;
  * a genuine redirect, a 200 rewrite, a 404 rule and an off-host target all
    pass — a gate that fails on those would be turned off within a week;
  * a lookalike host (`loisirs74.fr.evil.com`) is NOT treated as ours, which is
    the difference between a prefix match and a host match;
  * the live `_redirects` in this repo is clean.

Runs offline, reads only files it writes itself plus the repo's `_redirects`.
pytest or standalone.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "scripts", "gate_redirect_selfloop.py")


def _run(body):
    """Run the gate over a throwaway _redirects; return (exit_code, output)."""
    with tempfile.NamedTemporaryFile("w", suffix="_redirects", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(body)
        path = fh.name
    try:
        p = subprocess.run([sys.executable, GATE, "--redirects", path],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr
    finally:
        os.unlink(path)


LOOPS = [
    ("forced, slash on the source — the 73's own shape",
     "/lac-d-annecy/    /lac-d-annecy    301!"),
    ("forced, slash on the target — same loop, mirrored",
     "/telepherique     /telepherique/   301!"),
    ("unforced: defers the loop, does not prevent it",
     "/plage/           /plage           301"),
    ("absolute self-host source",
     "https://loisirs74.fr/thermes/   /thermes   301"),
    ("absolute self-host target, www form",
     "/annecy/    https://www.loisirs74.fr/annecy    301"),
    ("status omitted — Netlify defaults to 301, so still a loop",
     "/defaulted/    /defaulted"),
]

CLEAN = [
    ("a real redirect between two different paths",
     "/vieux    /nouveau    301"),
    ("a 200 rewrite is not a redirect",
     "/rewrite/    /rewrite    200"),
    ("a 404 rule is not a redirect",
     "/gone/    /gone    404"),
    ("an off-host target is somebody else's loop",
     "/off    https://example.com/off    301"),
    ("a lookalike host is NOT us — prefix match would be a false positive",
     "/lookalike    https://loisirs74.fr.evil.com/lookalike    301"),
    ("comments and blank lines are ignored",
     "# /commented/  /commented  301!\n\n"),
]


def test_selfloops_trip():
    for label, rule in LOOPS:
        code, out = _run(rule + "\n")
        assert code == 1, f"MISSED a self-loop ({label}):\n{rule}\n{out}"
        assert "self-redirect" in out, f"no diagnosis for ({label}):\n{out}"


def test_clean_rules_pass():
    for label, rule in CLEAN:
        code, out = _run(rule + "\n")
        assert code == 0, f"FALSE POSITIVE ({label}):\n{rule}\n{out}"


def test_mixed_file_reports_every_loop():
    body = "\n".join(r for _, r in LOOPS + CLEAN) + "\n"
    code, out = _run(body)
    assert code == 1, out
    assert f"{len(LOOPS)} self-redirect(s)" in out, \
        f"expected exactly {len(LOOPS)} loops flagged:\n{out}"
    assert "2 forced" in out, f"forced count wrong:\n{out}"


def test_live_redirects_are_clean():
    p = subprocess.run([sys.executable, GATE], capture_output=True, text=True)
    assert p.returncode == 0, f"the repo's own _redirects self-loops:\n{p.stdout}"


if __name__ == "__main__":
    for fn in (test_selfloops_trip, test_clean_rules_pass,
               test_mixed_file_reports_every_loop, test_live_redirects_are_clean):
        fn()
        print(f"  ✓ {fn.__name__}")
    print("test_gate_redirect_selfloop: all passed")
