#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/make_validation_fixture.py
python3 scripts/etl_audited.py --input data/synthetic_leads.csv --output outputs/baseline | tee evidence/baseline_run.txt
python3 scripts/etl_audited.py --input data/synthetic_validation_fixture.csv --output outputs/fixture | tee evidence/fixture_run.txt
python3 scripts/test_etl.py | tee evidence/test_results.txt
python3 scripts/benchmark_methods.py | tee evidence/benchmark_log.txt
printf '\nEvidence saved under evidence/. All data synthetic; all runs local.\n'
