#!/usr/bin/env python3
"""Audited Bizex *synthetic* lead snapshot ETL. Local standard-library implementation.

Does not represent a Bizex production system or a Spark/HDFS execution.
Usage: python scripts/etl_audited.py --input data/synthetic_leads.csv --output outputs/sample
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ['lead_id','created_at','platform','campaign_id','service_type','jurisdiction',
          'status','consultant','followup_at']


def tidy(value):
    return ' '.join((value or '').strip().split())


def parse_iso(s):
    s = tidy(s)
    if not s:
        raise ValueError('empty timestamp')
    dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timezone missing')
    return dt.astimezone(timezone.utc)


def save_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def run(input_path, output_dir):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = input_path.read_bytes()
    with input_path.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or any(field not in reader.fieldnames for field in FIELDS):
            raise ValueError('Required columns absent: ' + ', '.join(sorted(set(FIELDS) - set(reader.fieldnames or []))))
        source_rows = list(reader)
    selected = {}
    quarantined = []
    valid_count = 0
    for row_index, r in enumerate(source_rows, start=2):
        record = {f:tidy(r.get(f)) for f in FIELDS}
        if not record['lead_id']:
            quarantined.append({'source_row':row_index,'lead_id':'', 'reason':'MISSING_LEAD_ID'})
            continue
        try:
            ts = parse_iso(record['created_at'])
        except (ValueError, TypeError):
            quarantined.append({'source_row':row_index,'lead_id':record['lead_id'],'reason':'INVALID_CREATED_AT'})
            continue
        valid_count += 1
        # A later source row wins if two snapshots have identical timestamps.
        order_key = (ts, row_index)
        if record['lead_id'] not in selected or order_key > selected[record['lead_id']][0]:
            selected[record['lead_id']] = (order_key, record)
    curated = [selected[k][1] for k in sorted(selected)]
    snapshot = [{'lead_id': r['lead_id'], 'snapshot_at': r['followup_at'] or r['created_at'],
                 'status':r['status'],'consultant':r['consultant']}
                for r in curated if r['status']]
    save_csv(output_dir/'curated_leads.csv', curated, FIELDS)
    save_csv(output_dir/'lead_status_snapshot.csv', snapshot,
             ['lead_id','snapshot_at','status','consultant'])
    save_csv(output_dir/'quarantine.csv', quarantined, ['source_row','lead_id','reason'])
    platform_counts = Counter(r['platform'] or 'Unknown' for r in curated)
    save_csv(output_dir/'channel_counts.csv',
             [{'platform': k,'unique_leads':v} for k,v in sorted(platform_counts.items())],
             ['platform','unique_leads'])
    metrics = {
        'data_classification':'synthetic demonstration, no Bizex customer records',
        'execution_engine':'local Python standard library, not Hadoop/Spark/Hive',
        'input_file':input_path.name,
        'input_sha256':hashlib.sha256(payload).hexdigest(),
        'rows_input':len(source_rows),
        'rows_valid':valid_count,
        'rows_quarantined':len(quarantined),
        'rows_deduplicated':valid_count-len(curated),
        'unique_leads':len(curated),
        'latest_status_snapshots':len(snapshot),
        'counts_by_platform':dict(sorted(platform_counts.items()))
    }
    (output_dir/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    return metrics


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',dest='input_path',required=True)
    parser.add_argument('--output',dest='output_path',required=True)
    args=parser.parse_args()
    result=run(args.input_path,args.output_path)
    print('BIZEX | AUDITED LOCAL REFERENCE RUN')
    print('Data: SYNTHETIC ONLY | Engine: Python standard library')
    print('Not a Hadoop, Spark, Hive, or company production execution')
    for key in ['rows_input','rows_valid','rows_quarantined','rows_deduplicated','unique_leads','latest_status_snapshots']:
        print(f'{key:25}: {result[key]}')
    print('Source -> unique lead counts:')
    for k,v in result['counts_by_platform'].items():print(f'  {k:<18}: {v}')
    print('Output manifest: curated_leads.csv; lead_status_snapshot.csv; quarantine.csv; channel_counts.csv; metrics.json')
    print('INPUT_SHA256:',result['input_sha256'])

if __name__ == '__main__':
    main()
