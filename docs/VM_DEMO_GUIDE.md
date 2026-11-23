# Replay the actual Scala → HDFS → Hive demo on the course VM

The supplied screenshots show **Hadoop 2.7.3, Spark 3.0.3 with Scala 2.12.10, Hive 2.1.1, and Python 3.4.3**. Commands below assume those services are already configured. They are a practical replay guide, **not** a claim that the replay was executed here.

## 1. Move the project files to your VM

Copy `data/synthetic_leads.csv`, `spark/spark_etl.scala`, `hive/create_tables.hql`, and `hive/analysis_queries.sql` to the VM. On the team's machine they were available via a VirtualBox shared folder under `/media/sf_vmshare/Bizex_demo/`. Adapt the paths if yours differ.

## 2. Verify Hadoop daemons and upload the CSV

```bash
jps
hdfs dfs -mkdir -p /data/raw/bizex_demo
hdfs dfs -put -f /path/on/vm/synthetic_leads.csv /data/raw/bizex_demo/synthetic_leads.csv
hdfs dfs -ls -R /data/raw/bizex_demo
hdfs dfs -cat /data/raw/bizex_demo/synthetic_leads.csv | head
```

Expected HDFS file is `hdfs:///data/raw/bizex_demo/synthetic_leads.csv`. `spark_etl.scala` contains that path and writes to `hdfs:///data/curated/bizex_demo`. Running it again overwrites the demo curated folders.

## 3. Run **Scala** Spark ETL (working VM route)

```bash
spark-shell
```

Inside `spark-shell`, use the *actual path* on your VM:

```scala
:load /path/on/vm/spark_etl.scala
```

Expected from the packaged 12-row CSV: 12 raw rows, 12 curated unique lead snapshots, 12 derived status rows; Instagram=5, Website=3, Facebook=2, WhatsApp=2. See `S06_spark_etl_run.png`.

Why Scala instead of PySpark? The VM's Python 3.4.3 is not compatible with the packaged Python Spark workflow. Do not change system Python just for this deadline unless the VM owner approves.

## 4. Inspect curated HDFS files

```bash
hdfs dfs -ls -R /data/curated/bizex_demo
```

Expect Parquet directories `/leads` and `/status_events`, each containing output part files.

## 5. Create Hive tables, then run analytics

If configured on your course VM, for example:

```bash
$HIVE_HOME/bin/beeline -u 'jdbc:hive2://localhost:10000' -n bigdata -f /path/on/vm/create_tables.hql
$HIVE_HOME/bin/beeline -u 'jdbc:hive2://localhost:10000' -n bigdata -f /path/on/vm/analysis_queries.sql
```

The demo screenshots show these scripts executed through Beeline against Hive 2.1.1. If your class VM uses a different account or JDBC URL, substitute those details. If access prompts for a password, **do not** save the password in the repo.

## 6. Show during the presentation (3–4 minutes)

- **00:00–00:30** Proposed architecture: CSV → HDFS → Spark/Scala → Parquet → Hive.
- **00:30–01:00** Show HDFS raw listing (`S03`).
- **01:00–02:00** Run (or show actual run screenshot) Scala script and explain 12/12 processed (`S06`).
- **02:00–02:30** Show curated Parquet HDFS folders (`S12`).
- **02:30–03:30** Query with Beeline and explain channel counts (`S10`).

If the VM is unavailable live, use the **genuine screenshots** and explain it is a replay of a completed run, not a live demo. Do not substitute local Python tests and call them Spark jobs.

## Distinguish current implementation from planned enhancements

The Scala code standardizes fields, filters missing IDs, deduplicates, writes Parquet and derives a single status record per lead. The architecture proposes further protections (explicit quarantine, governance, scheduling and broader source integration) that were **not implemented** in this VM demo.
