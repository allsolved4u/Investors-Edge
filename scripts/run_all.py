# ===== FILE: scripts/run_all.py =====

import os
import subprocess
import sys


def run(cmd: str):
    print(f"\n$ {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        sys.exit(res.returncode)


def main():
    os.makedirs("artifacts", exist_ok=True)

    # 1) Golden compare
    run("pytest -q")

    # 2) Scenarios + summaries
    run("python scripts/scenario_report.py --outdir artifacts")

    # 3) Charts
    run("python scripts/charts.py --outdir artifacts")

    print("\nAll tasks finished. See artifacts/ for outputs.")


if __name__ == "__main__":
    main()
