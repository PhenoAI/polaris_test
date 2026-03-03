import os
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

connection = sql.connect(
    server_hostname=os.environ["DATABRICKS_HOST"],
    http_path=f"/sql/1.0/warehouses/{os.environ['DATABRICKS_SQL_WAREHOUSE_ID']}",
    access_token=os.environ["DATABRICKS_TOKEN"]
)
cursor = connection.cursor()

# Describe table schema
cursor.execute("DESCRIBE TABLE ds.omics.gut_mb_metaphlan_species")
schema = cursor.fetchall()

print("Schema for gut_mb_metaphlan_species:")
for row in schema[:20]:  # First 20 columns
    print(f"  {row[0]}: {row[1]}")

cursor.close()
connection.close()
