SELECT platform, COUNT(DISTINCT lead_id) AS leads FROM bizex_lake.curated_leads GROUP BY platform;
SELECT service_type, jurisdiction, COUNT(DISTINCT lead_id) AS leads FROM bizex_lake.curated_leads GROUP BY service_type,jurisdiction;
SELECT status, COUNT(DISTINCT lead_id) AS leads FROM bizex_lake.curated_leads GROUP BY status;
