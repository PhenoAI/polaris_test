# Gut Microbiome Diversity — Logic Diagram

```mermaid
flowchart TD
    Start([Participant with gut microbiome sample]) --> GetSpecies[Fetch species-level abundances<br/>from ds.omics.gut_mb_metaphlan<br/>WHERE level='species' AND mock=false]

    GetSpecies --> CheckNull{participant_uuid<br/>is NULL?}
    CheckNull -->|Yes| Exclude1[Exclude from output]
    CheckNull -->|No| CheckOutlier{observed_species<br/>> 2000?}

    CheckOutlier -->|Yes| Exclude2[Exclude<br/>likely processing artifact]
    CheckOutlier -->|No| ComputeRichness[Compute observed_species:<br/>COUNT species with relative_abundance > 0]

    ComputeRichness --> ComputeShannon[Compute Shannon index:<br/>H = -Σpi × ln pi<br/>where pi = relative_abundance/100]

    ComputeShannon --> QualityCheck{observed_species<br/>< 20?}
    QualityCheck -->|Yes| LowQuality[sample_quality = 'Low Quality']
    QualityCheck -->|No| Adequate[sample_quality = 'Adequate']

    LowQuality --> DiversityCategory
    Adequate --> DiversityCategory{Shannon index<br/>value?}

    DiversityCategory -->|< 3.0| Low[diversity_category = 'Low']
    DiversityCategory -->|3.0 - 4.0| Moderate[diversity_category = 'Moderate']
    DiversityCategory -->|> 4.0| High[diversity_category = 'High']

    Low --> Output
    Moderate --> Output
    High --> Output

    Output[Output row with:<br/>- shannon_index<br/>- observed_species<br/>- sample_quality<br/>- diversity_category]

    Exclude1 -.-> End([Not in output])
    Exclude2 -.-> End
```

## Key Decision Points

1. **Data Quality Filters:**
   - Exclude mock community samples (mock=true)
   - Exclude NULL participant UUIDs
   - Exclude extreme outliers (>2000 species)

2. **Sample Quality Classification:**
   - Low Quality: <20 observed species (likely low biomass or technical failure)
   - Adequate: ≥20 observed species

3. **Diversity Categories:**
   - Low: Shannon index <3.0
   - Moderate: Shannon index 3.0-4.0
   - High: Shannon index >4.0

## Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `participant_uuid` | string | Unique participant identifier |
| `gut_microbiome_diversity__shannon_index` | double | Shannon diversity index (continuous, typically 0-6) |
| `gut_microbiome_diversity__observed_species` | int | Count of species with relative abundance >0 |
| `gut_microbiome_diversity__sample_quality` | string | 'Adequate' or 'Low Quality' |
| `gut_microbiome_diversity__diversity_category` | string | 'High', 'Moderate', or 'Low' |
