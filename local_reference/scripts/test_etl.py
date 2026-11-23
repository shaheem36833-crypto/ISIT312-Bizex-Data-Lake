#!/usr/bin/env python3
"""Reproducible assertions; test data are synthetic."""
import csv
import tempfile
from pathlib import Path
from etl_audited import run
base=Path(__file__).resolve().parents[1]

def load_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def check(label,cond):
    assert cond,label
    print('PASS  '+label)

with tempfile.TemporaryDirectory() as td:
    t=Path(td)
    m=run(base/'data/synthetic_leads.csv',t/'baseline')
    check('baseline source rows = 12',m['rows_input']==12)
    check('baseline curated unique leads = 12',m['unique_leads']==12)
    check('baseline has zero quarantine',m['rows_quarantined']==0)
    check('baseline has 12 latest status snapshots',m['latest_status_snapshots']==12)
    m2=run(base/'data/synthetic_validation_fixture.csv',t/'fixture')
    check('edge-case input rows = 16',m2['rows_input']==16)
    check('edge-case bad rows = 2',m2['rows_quarantined']==2)
    check('edge-case duplicate rows = 2',m2['rows_deduplicated']==2)
    check('edge-case unique leads = 12',m2['unique_leads']==12)
    leads={r['lead_id']:r for r in load_csv(t/'fixture/curated_leads.csv')}
    check('newer timestamp wins for duplicate SYN-002',leads['SYN-002']['status']=='Won')
    check('later source row wins ties for SYN-007',leads['SYN-007']['status']=='Warm Prospect')
    rejected={r['reason'] for r in load_csv(t/'fixture/quarantine.csv')}
    check('both missing-ID and invalid-date checks execute',rejected=={'MISSING_LEAD_ID','INVALID_CREATED_AT'})
    check('source-specific totals reconcile',sum(m2['counts_by_platform'].values())==m2['unique_leads'])
    rerun=run(base/'data/synthetic_validation_fixture.csv',t/'second')
    check('repeat run produces deterministic metrics',m2==rerun)
    check('repeat run produces identical curated output',(t/'fixture/curated_leads.csv').read_bytes()==(t/'second/curated_leads.csv').read_bytes())
print('RESULT  13 / 13 assertions passed; local Python execution only.')
