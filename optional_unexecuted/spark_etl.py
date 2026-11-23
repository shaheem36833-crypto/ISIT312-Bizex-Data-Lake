# Zeppelin paragraph: %spark.pyspark
from pyspark.sql import functions as F, Window
input_uri="hdfs:///data/raw/bizex_demo/synthetic_leads.csv"; output_uri="hdfs:///data/curated/bizex_demo"
raw=spark.read.option("header",True).option("inferSchema",False).csv(input_uri)
clean=(raw.select("lead_id","created_at","platform","campaign_id","service_type","jurisdiction","status","consultant","followup_at").withColumn("lead_id",F.trim("lead_id")).withColumn("platform",F.initcap(F.trim("platform"))).withColumn("service_type",F.trim("service_type")).withColumn("jurisdiction",F.initcap(F.trim("jurisdiction"))).withColumn("status",F.trim("status")).withColumn("created_at_ts",F.to_timestamp("created_at")).withColumn("followup_at_ts",F.to_timestamp("followup_at")).filter(F.col("lead_id").isNotNull() & (F.col("lead_id")!="")))
win=Window.partitionBy("lead_id").orderBy(F.col("created_at_ts").desc_nulls_last())
leads=clean.withColumn("rn",F.row_number().over(win)).filter("rn=1").drop("rn")
events=leads.filter(F.col("status").isNotNull() & (F.col("status")!="")).select("lead_id",F.coalesce("followup_at_ts","created_at_ts").alias("event_at"),"status","consultant")
leads.write.mode("overwrite").parquet(output_uri+"/leads");events.write.mode("overwrite").parquet(output_uri+"/status_events")
leads.groupBy("platform").count().orderBy("platform").show()
