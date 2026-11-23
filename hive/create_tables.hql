CREATE DATABASE IF NOT EXISTS bizex_lake; USE bizex_lake;
CREATE EXTERNAL TABLE IF NOT EXISTS curated_leads (lead_id STRING, created_at STRING, platform STRING, campaign_id STRING, service_type STRING, jurisdiction STRING, status STRING, consultant STRING, followup_at STRING, created_at_ts TIMESTAMP, followup_at_ts TIMESTAMP) STORED AS PARQUET LOCATION '/data/curated/bizex_demo/leads';
CREATE EXTERNAL TABLE IF NOT EXISTS status_events (lead_id STRING, event_at TIMESTAMP, status STRING, consultant STRING) STORED AS PARQUET LOCATION '/data/curated/bizex_demo/status_events';
