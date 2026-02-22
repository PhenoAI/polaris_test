# Gut Microbiome Diversity — Logic Diagram

```mermaid
flowchart TD
    Start([Participant with gut microbiome sample]) --> GetData[Query species-level abundances<br/>from ds.omics.gut_mb_metaphlan_species]
    GetData --> FilterMock{Filter mock = false}
    FilterMock -->|No valid data| Exclude[Exclude participant]
    FilterMock -->|Valid data| CountSpecies[Count observed species<br/>with relative_abundance > 0]

    CountSpecies --> CalcShannon[Calculate Shannon Index<br/>H' = -Σ p_i × ln p_i]

    CalcShannon --> CheckQuality{Observed species >= 20?}
    CheckQuality -->|No| LowQuality[quality_flag = Low quality/dysbiotic]
    CheckQuality -->|Yes| AdequateQuality[quality_flag = Adequate]

    LowQuality --> CheckShannon{Shannon Index >= 3.0?}
    AdequateQuality --> CheckShannon

    CheckShannon -->|No| LowDiv[diversity_category = Low diversity]
    CheckShannon -->|Yes| NormalDiv[diversity_category = Normal diversity]

    LowDiv --> Output[Output:<br/>shannon_index continuous<br/>observed_species count<br/>diversity_category<br/>quality_flag]
    NormalDiv --> Output

    Exclude --> End([Not included in output])
    Output --> End2([Include in curated phenotype])

    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style End2 fill:#e1f5e1
    style LowDiv fill:#ffcccc
    style NormalDiv fill:#ccffcc
    style LowQuality fill:#fff3cd
    style AdequateQuality fill:#d4edda
```

## Decision Logic Summary

1. **Data Acquisition**: Extract species-level MetaPhlAn abundances for each participant
2. **Quality Control**: Exclude mock community samples (mock = true)
3. **Feature Computation**:
   - **Observed species richness**: Count distinct species with relative_abundance > 0
   - **Shannon index**: Apply Shannon-Wiener formula across all detected species
4. **Quality Assessment**: Flag samples with <20 species as potentially low-quality or dysbiotic
5. **Diversity Classification**: Apply threshold of 3.0 to categorize as "Low diversity" or "Normal diversity"
6. **Output**: Generate participant-level record with all four features
