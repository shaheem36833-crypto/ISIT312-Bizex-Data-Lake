#!/usr/bin/env python3
"""Create synthetic edge-case records to verify validation and deduplication."""
import csv
from pathlib import Path
from etl_audited import FIELDS
base=Path(__file__).resolve().parents[1]
with (base/'data/synthetic_leads.csv').open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
index={r['lead_id']:r for r in rows}
newer=dict(index['SYN-002'],created_at='2026-06-09T11:00:00Z',status='Won')
tied=dict(index['SYN-007'],status='Warm Prospect')
missing=dict(index['SYN-004'],lead_id='',status='New')
invalid=dict(index['SYN-005'],lead_id='SYN-999',created_at='INVALID-DATE')
rows.extend([newer,tied,missing,invalid])
with (base/'data/synthetic_validation_fixture.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
print('Generated 16 synthetic fixture rows: 12 baseline + 2 duplicates + 2 invalid records')
