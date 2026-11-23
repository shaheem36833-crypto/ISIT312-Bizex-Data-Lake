# Data dictionary and privacy
|Field|Meaning|Handling|
|---|---|---|
|lead_id|Source lead key|Required; pseudonymous in analytics|
|created_at|Creation timestamp|Parse and normalize timezone|
|platform|Lead channel|Map to controlled values|
|campaign_id|Campaign/form key|Join only after key verification|
|service_type|Enquiry category|Governed mapping|
|jurisdiction|Preferred location|Normalize; preserve Unsure|
|status|Lifecycle state|Governed values; retain source value|
|consultant|Assigned owner|Restrict access; aggregate reporting|
|followup_at|Follow-up timestamp|Use after definition is confirmed|
Names, phones, emails and free text are excluded. Restrict and segregate identity data if required operationally.
