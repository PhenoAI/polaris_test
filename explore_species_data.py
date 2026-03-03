import os
import pandas as pd
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

connection = sql.connect(
    server_hostname=os.environ["DATABRICKS_HOST"],
    http_path=f"/sql/1.0/warehouses/{os.environ['DATABRICKS_SQL_WAREHOUSE_ID']}",
    access_token=os.environ["DATABRICKS_TOKEN"]
)
cursor = connection.cursor()

# Check species-level table structure
query = """
SELECT 
    participant_uuid,
    sample_id,
    species,
    relative_abundance
FROM ds.omics.gut_mb_metaphlan_species
WHERE mock = false
LIMIT 10
"""

cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
print("Sample data:")
print(df)

# Check how many species per participant
query2 = """
SELECT 
    participant_uuid,
    COUNT(*) as species_count,
    SUM(relative_abundance) as total_abundance
FROM ds.omics.gut_mb_metaphlan_species
WHERE mock = false
    AND species IS NOT NULL
GROUP BY participant_uuid
ORDER BY species_count DESC
LIMIT 10
"""

cursor.execute(query2)
df2 = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
print("\nSpecies counts per participant:")
print(df2)

cursor.close()
connection.close()
