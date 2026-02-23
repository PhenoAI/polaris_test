"""
Gut Microbiome Diversity — Compute Script (Alternative Metrics Fork)

Computes multiple alpha diversity metrics:
- Shannon index (primary)
- Simpson index (evenness-focused)
- Chao1 richness estimator (accounts for rare species)
- Observed species richness

Uses SQL-based computation for performance on large dataset (~4.3M rows).

Output table: ds.polaris.gut_microbiome_diversity
Index: participant_uuid (cross-sectional)
"""

import os
from databricks import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Databricks connection parameters
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_WAREHOUSE_ID = os.getenv("DATABRICKS_SQL_WAREHOUSE_ID")

# Output table
OUTPUT_CATALOG = "ds"
OUTPUT_SCHEMA = "polaris"
OUTPUT_TABLE = "gut_microbiome_diversity"

# Shannon diversity threshold for categorization
SHANNON_THRESHOLD = 3.0
# Quality threshold: >50 detected species for adequate quality
MIN_SPECIES_THRESHOLD = 50


def compute_diversity_in_sql(connection) -> None:
    """Compute diversity metrics entirely in SQL and write to output table.

    This approach is much faster than fetching all rows and computing in Python.
    """
    full_table = f"{OUTPUT_CATALOG}.{OUTPUT_SCHEMA}.{OUTPUT_TABLE}"

    print("Computing diversity metrics in Databricks SQL...")

    # Create schema if needed
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {OUTPUT_CATALOG}.{OUTPUT_SCHEMA}")
        print(f"✓ Schema {OUTPUT_CATALOG}.{OUTPUT_SCHEMA} verified")

    # Drop existing table
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {full_table}")
        print(f"✓ Dropped existing table (if any)")

    # Compute diversity metrics in SQL and create output table
    # Shannon index: H' = -Σ(p_i × ln(p_i))
    # Simpson index: D = 1 - Σ(p_i²)
    # Chao1: S_chao1 = S_obs + (F1² / 2*F2) where F1=singletons, F2=doubletons
    sql_query = f"""
    CREATE TABLE {full_table} AS
    WITH most_recent_samples AS (
        -- Select most recent sample per participant (highest sample_id)
        SELECT
            participant_uuid,
            MAX(sample_id) as max_sample_id
        FROM ds.omics.gut_mb_metaphlan
        WHERE level = 'species'
            AND mock = false
            AND species IS NOT NULL
            AND relative_abundance > 0
        GROUP BY participant_uuid
    ),
    species_data AS (
        -- Get species abundances for most recent samples
        SELECT
            m.participant_uuid,
            m.species,
            m.relative_abundance
        FROM ds.omics.gut_mb_metaphlan m
        INNER JOIN most_recent_samples mrs
            ON m.participant_uuid = mrs.participant_uuid
            AND m.sample_id = mrs.max_sample_id
        WHERE m.level = 'species'
            AND m.mock = false
            AND m.species IS NOT NULL
            AND m.relative_abundance > 0
    ),
    normalized_abundances AS (
        -- Normalize abundances to proportions
        SELECT
            participant_uuid,
            species,
            relative_abundance,
            relative_abundance / SUM(relative_abundance) OVER (PARTITION BY participant_uuid) as proportion
        FROM species_data
    ),
    rare_species_counts AS (
        -- Count singletons and doubletons for Chao1
        -- Using relative abundance thresholds as proxies
        -- Singleton: very low abundance (bottom 5th percentile)
        -- Doubleton: low abundance (5th-10th percentile)
        SELECT
            participant_uuid,
            COUNT(CASE WHEN proportion <= 0.001 THEN 1 END) as singletons,
            COUNT(CASE WHEN proportion > 0.001 AND proportion <= 0.002 THEN 1 END) as doubletons
        FROM normalized_abundances
        GROUP BY participant_uuid
    ),
    diversity_metrics AS (
        -- Compute all diversity indices per participant
        SELECT
            n.participant_uuid,
            -- Shannon index: -Σ(p_i × ln(p_i))
            -SUM(n.proportion * LN(n.proportion)) as shannon_index,
            -- Simpson index: 1 - Σ(p_i²)
            1 - SUM(n.proportion * n.proportion) as simpson_index,
            -- Observed species richness
            COUNT(DISTINCT n.species) as observed_species,
            -- Chao1 estimator: S_obs + (F1² / (2*F2))
            -- If F2=0, use bias-corrected: S_obs + (F1*(F1-1))/(2*(F2+1))
            COUNT(DISTINCT n.species) +
                CASE
                    WHEN r.doubletons > 0 THEN (r.singletons * r.singletons) / (2.0 * r.doubletons)
                    WHEN r.singletons > 1 THEN (r.singletons * (r.singletons - 1)) / 2.0
                    ELSE 0
                END as chao1_richness
        FROM normalized_abundances n
        LEFT JOIN rare_species_counts r ON n.participant_uuid = r.participant_uuid
        GROUP BY n.participant_uuid, r.singletons, r.doubletons
    )
    SELECT
        participant_uuid,
        shannon_index as gut_microbiome_diversity__shannon_index,
        simpson_index as gut_microbiome_diversity__simpson_index,
        observed_species as gut_microbiome_diversity__observed_species,
        chao1_richness as gut_microbiome_diversity__chao1_richness,
        -- Shannon diversity category (primary classification)
        CASE
            WHEN shannon_index < {SHANNON_THRESHOLD} THEN 'Low diversity'
            ELSE 'Normal diversity'
        END as gut_microbiome_diversity__diversity_category,
        -- Sample quality flag (updated threshold: >50 species)
        CASE
            WHEN observed_species <= {MIN_SPECIES_THRESHOLD} THEN 'Low quality/dysbiotic'
            ELSE 'Adequate'
        END as gut_microbiome_diversity__quality_flag
    FROM diversity_metrics
    """

    with connection.cursor() as cursor:
        print("Executing diversity computation query...")
        cursor.execute(sql_query)
        print(f"✓ Created table {full_table}")

    # Get summary statistics
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT
                COUNT(*) as total_participants,
                AVG(gut_microbiome_diversity__shannon_index) as mean_shannon,
                PERCENTILE(gut_microbiome_diversity__shannon_index, 0.5) as median_shannon,
                AVG(gut_microbiome_diversity__simpson_index) as mean_simpson,
                PERCENTILE(gut_microbiome_diversity__simpson_index, 0.5) as median_simpson,
                AVG(gut_microbiome_diversity__observed_species) as mean_species,
                PERCENTILE(gut_microbiome_diversity__observed_species, 0.5) as median_species,
                AVG(gut_microbiome_diversity__chao1_richness) as mean_chao1,
                PERCENTILE(gut_microbiome_diversity__chao1_richness, 0.5) as median_chao1,
                SUM(CASE WHEN gut_microbiome_diversity__diversity_category = 'Low diversity' THEN 1 ELSE 0 END) as low_diversity_count,
                SUM(CASE WHEN gut_microbiome_diversity__quality_flag = 'Low quality/dysbiotic' THEN 1 ELSE 0 END) as low_quality_count
            FROM {full_table}
        """)
        row = cursor.fetchone()

        if row:
            total, mean_sh, med_sh, mean_si, med_si, mean_sp, med_sp, mean_ch, med_ch, low_div, low_qual = row
            print(f"\n✓ Computed diversity for {total:,} participants")
            print(f"  Shannon index: mean={mean_sh:.2f}, median={med_sh:.2f}")
            print(f"  Simpson index: mean={mean_si:.3f}, median={med_si:.3f}")
            print(f"  Observed species: mean={mean_sp:.1f}, median={med_sp:.0f}")
            print(f"  Chao1 richness: mean={mean_ch:.1f}, median={med_ch:.0f}")
            print(f"  Low diversity: {low_div:,} ({low_div/total*100:.1f}%)")
            print(f"  Low quality/dysbiotic: {low_qual:,} ({low_qual/total*100:.1f}%)")


def main():
    """Main execution flow."""
    print("=" * 80)
    print("Gut Microbiome Diversity — Compute Pipeline (Alternative Metrics)")
    print("=" * 80)

    # Validate environment
    if not all([DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE_ID]):
        raise ValueError("Missing Databricks credentials in .env file")

    # Connect to Databricks
    print("\nConnecting to Databricks...")
    connection = sql.connect(
        server_hostname=DATABRICKS_HOST.replace("https://", "").rstrip("/"),
        http_path=f"/sql/1.0/warehouses/{DATABRICKS_WAREHOUSE_ID}",
        access_token=DATABRICKS_TOKEN,
    )
    print("✓ Connected to Databricks")

    try:
        # Compute diversity metrics in SQL and create output table
        compute_diversity_in_sql(connection)

        print("\n" + "=" * 80)
        print("✓ Pipeline completed successfully")
        print("=" * 80)

    finally:
        connection.close()
        print("\nClosed Databricks connection")


if __name__ == "__main__":
    main()
