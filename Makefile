# ===== FILE: Makefile =====

.PHONY: install golden-write golden-test scenarios charts all

install:
\tpip install -r requirements.txt

golden-write:
\tpython -m validation.golden --baseline baselines/golden_2024.json --write

golden-test:
\tpytest -q

scenarios:
\tpython scripts/scenario_report.py --outdir artifacts

charts:
\tpython scripts/charts.py --outdir artifacts

all: golden-test scenarios charts
