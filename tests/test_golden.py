# ===== FILE: tests/test_golden.py =====

from validation.golden import run_golden_suite

def test_golden_baseline():
    ok, msgs = run_golden_suite("baselines/golden_2024.json", write=False)
    assert ok, "Golden drift:\n" + "\n".join(msgs)
