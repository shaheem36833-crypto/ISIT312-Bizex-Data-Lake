#!/usr/bin/env python3
"""Synthetic *local* algorithm comparison (Python keyed reducer vs SQLite window SQL).

Not Hadoop MapReduce, not Spark; timings cannot establish cluster throughput.
"""
import csv
import json
import random
import sqlite3
import statistics
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SIZES=[10000,50000,100000]
SEED=312
REPEATS=3

def create_rows(n):
    rng=random.Random(SEED+n)
    base=datetime(2026,6,1,tzinfo=timezone.utc)
    channels=['Instagram','Facebook','Website','WhatsApp']
    # 10% repeat snapshots: realistic *simulation*, not evidence of company rate.
    keys=max(1,int(n*0.9))
    rows=[]
    for i in range(n):
        lead='SYN-'+str(rng.randrange(keys)).zfill(7)
        stamp=base+timedelta(seconds=rng.randrange(60*60*24*30))
        rows.append((lead,stamp.isoformat(),channels[rng.randrange(4)],i))
    return rows

def reducer(rows):
    chosen={}
    for lead,date,channel,idx in rows:
        key=(date,idx)
        if lead not in chosen or key > chosen[lead][0]:
            chosen[lead]=(key,channel)
    return dict(sorted(Counter(item[1] for item in chosen.values()).items()))

def sql_window(rows):
    connection=sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE t(lead_id TEXT, created_at TEXT, platform TEXT, row_idx INTEGER)')
    connection.executemany('INSERT INTO t VALUES(?,?,?,?)',rows)
    result=dict(connection.execute('''SELECT platform, COUNT(*) FROM (
        SELECT platform, ROW_NUMBER() OVER(PARTITION BY lead_id ORDER BY created_at DESC, row_idx DESC) AS rn
        FROM t) WHERE rn = 1 GROUP BY platform ORDER BY platform''').fetchall())
    connection.close()
    return result

def main():
    results=[]
    for n in SIZES:
        rows=create_rows(n)
        trials={}
        outputs={}
        for label,fn in [('Python keyed reducer',reducer),('SQLite window SQL',sql_window)]:
            times=[]
            for i in range(REPEATS):
                t0=time.perf_counter();res=fn(rows);times.append((time.perf_counter()-t0)*1000)
            outputs[label]=res
            trials[label]=statistics.median(times)
        if outputs['Python keyed reducer'] != outputs['SQLite window SQL']:
            raise AssertionError('Comparison outputs differ')
        unique=sum(outputs['Python keyed reducer'].values())
        for label in trials:
            results.append({'rows_input':n,'unique_leads':unique,'method':label,
                            'median_ms':round(trials[label],3),'repeats':REPEATS,
                            'outputs_match':True})
        print(f'{n:>7,} synthetic rows: {unique:>7,} unique | Python reducer {trials["Python keyed reducer"]:>9.2f} ms | SQLite SQL {trials["SQLite window SQL"]:>9.2f} ms | output match YES')
    out=ROOT/'evidence'
    out.mkdir(exist_ok=True)
    with (out/'benchmark_results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    (out/'benchmark_results.json').write_text(json.dumps({'limitations':[
        'Generated synthetic data; no company records used',
        'In-memory single-machine algorithm comparison; not Spark or Hadoop MapReduce',
        'Includes SQLite insertion in SQL timing; excludes file ingestion in Python timing',
        'Three timing repeats; hardware and load affect results',
        'Do not interpret as streaming latency or a production throughput benchmark'
    ],'results':results},indent=2)+'\n',encoding='utf-8')
    print('BENCHMARK METHOD: median of 3 runs, one machine, synthetic data')
    print('NOT evidence of Hadoop MapReduce vs Spark performance')

if __name__=='__main__':main()
