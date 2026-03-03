import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Databricks SQL warehouse
connection = sql.connect(
    server_hostname=os.environ["DATABRICKS_HOST"],
    http_path=f"/sql/1.0/warehouses/{os.environ['DATABRICKS_SQL_WAREHOUSE_ID']}",
    access_token=os.environ["DATABRICKS_TOKEN"]
)
cursor = connection.cursor()

# Execute query
query = """
SELECT 
    COUNT(*) as total_records, 
    COUNT(DISTINCT participant_uuid) as unique_participants 
FROM ds.omics.gut_mb_metaphlan 
WHERE mock = false
"""

cursor.execute(query)
result = cursor.fetchall()

# Print results
for row in result:
    print(f"Total records: {row[0]:,}")
    print(f"Unique participants: {row[1]:,}")

# Cleanup
cursor.close()
connection.close()
