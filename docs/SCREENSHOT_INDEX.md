# Course-VM screenshot evidence index

These screenshots were supplied by the team in `Bizex_screenshots.zip`; they are included unaltered. They document a course VM session, **not** a company production deployment. Screenshot filenames are kept as supplied.

| File | Visible evidence |
|---|---|
| `S01_files_in_vm.png` | Project files shared/mounted in VM |
| `S02_hadoop_jps.png` | Hadoop daemons running and Java processes listed |
| `S03_raw_zone_hdfs.png` | HDFS raw directory, `synthetic_leads.csv`, and preview |
| `S04_spark_python_versions.png` | Spark 3.0.3 and Python 3.4.3 in VM |
| `S05_etl_script_in_vm.png` | Scala job file available in VM |
| `S06_spark_etl_run.png` | Actual Scala Spark `:load`; 12 raw, 12 curated, 12 derived status; platform counts |
| `S07_curated_before_tuning.png` | First HDFS curated Parquet listing |
| `S08_hive_services_jps.png` | Hive metastore-related services / `jps` |
| `S09_hive_tables_created.png` | Beeline created `bizex_lake` and external Hive tables |
| `S10_hive_queries_2m16s.png` | Beeline analytics grouped by platform, service/jurisdiction and status |
| `S11_spark_sql_18s.png` | Same kinds of grouped analytics shown in Spark SQL (run time in filename) |
| `S12_curated_after_tuning.png` | Later Spark results alongside curated Parquet files |

**Use in report:** raw input = S03; Spark job execution = S06; Parquet output = S07 or S12; Hive tables = S09; Hive query results = S10. These are direct evidence of VM execution. The screenshots alone cannot establish an apples-to-apples Spark-vs-Hive performance benchmark.
