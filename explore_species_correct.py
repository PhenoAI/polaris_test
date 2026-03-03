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

# Sample species-level data
query = """
SELECT 
    participant_uuid,
    sample_id,
    clade_name,
    relative_abundance
FROM ds.omics.gut_mb_metaphlan
WHERE mock = false
    AND level = 'species'
LIMIT 10
"""

cursor.execute(query)
df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
print("Sample species-level data:")
print(df)

# Check species counts per participant
query2 = """
SELECT 
    participant_uuid,
    COUNT(*) as species_count,
    SUM(relative_abundance) as total_abundance
FROM ds.omics.gut_mb_metaphlan
WHERE mock = false
    AND level = 'species'
GROUP BY participant_uuid
ORDER BY species_count DESC
LIMIT 10
"""

cursor.execute(query2)
df2 = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
print("\nSpecies counts per participant (top 10):")
print(df2)

# Summary stats
query3 = """
SELECT 
    COUNT(DISTINCT participant_uuid) as n_participants,
    AVG(species_count) as avg_species,
    MIN(species_count) as min_species,
    MAX(species_count) as max_species
FROM (
    SELECT 
        participant_uuid,
        COUNT(*) as species_count
    FROM ds.omics.gut_mb_metaphlan
    WHERE mock = false
        AND level = 'species'
    GROUP BY participant_uuid
)
"""

cursor.execute(query3)
df3 = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
print("\nOverall summary:")
print(df3)

cursor.close()
connection.close()
