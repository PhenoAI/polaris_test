# Gut Microbiome Diversity — Medical Manifest

**Author:** Polaris AI (create-curated-phenotype v0.2.0)
**Last updated:** 2026-02-22
**Phenotype ID:** TBD

## Background

Gut microbiome diversity refers to the variety and distribution of microbial species within the gastrointestinal tract. Alpha diversity measures the species richness and evenness within a single sample, while beta diversity measures the dissimilarity between samples[^1]. The Shannon index is the most widely used alpha diversity metric (used in 78.7% of studies), as it accounts for both species richness and the uniformity of species distribution[^2][^3].

Higher gut microbiome diversity is generally associated with better health outcomes, while reduced diversity (dysbiosis) has been linked to various diseases including inflammatory bowel disease, metabolic disorders, and infectious complications[^4][^5]. However, the relationship between diversity and health is complex and disease-specific — some conditions show consistent diversity reductions while others do not[^6]. A Shannon index threshold of <3.0 has been used to define low bacterial diversity in clinical settings, particularly in septic shock patients where it correlates with increased mortality risk[^7].

The gut microbiome can be profiled using shotgun metagenomic sequencing followed by taxonomic classification. Two primary methods are used: MetaPhlAn 4, which uses marker genes for species-level profiling, and URS (Unique Relative Abundance), which provides strain-level resolution using unique genome segments[^8]. MetaPhlAn 4 relative abundances are expressed as percentages (0-100) and sum to approximately 100 per sample within each taxonomic level.

Diversity metrics in microbiome research face challenges due to cohort heterogeneity, disease staging differences, and methodological variations across studies, making universal cutoff thresholds difficult to establish[^9]. Despite these limitations, diversity indices remain valuable biomarkers for characterizing gut microbiome health status and are increasingly used in biobank research and clinical microbiome studies[^10].

## Data Plan

### Datasets Used

| Dataset | Table | Key Columns | Role |
|---------|-------|-------------|------|
| Gut microbiome | `ds.omics.gut_mb_metaphlan_species` | `participant_uuid`, `species`, `relative_abundance`, `mock` | Species-level taxonomic abundances for diversity calculation |
| Population | `ds.silverdb.participant` | `uuid`, `gender`, `year_of_birth` | Participant demographics for stratification |

### Features

#### Feature 1: Shannon Diversity Index
- **Type:** Continuous
- **Source:** Derived from `ds.omics.gut_mb_metaphlan_species`
- **Logic:** Calculated using the Shannon-Wiener formula: H' = -Σ(p_i × ln(p_i)), where p_i is the proportional abundance of species i. Computed across all detected species (relative_abundance > 0) per participant, excluding mock samples. Higher values indicate greater diversity.
- **Missingness:** Participants without microbiome data are excluded. Samples with <20 detected species are flagged as potentially low-quality or dysbiotic.
- **Output column:** `gut_microbiome_diversity__shannon_index`

#### Feature 2: Observed Species Richness
- **Type:** Continuous (integer)
- **Source:** Derived from `ds.omics.gut_mb_metaphlan_species`
- **Logic:** Count of distinct species with relative_abundance > 0 per participant, excluding mock samples. Represents species richness without considering evenness.
- **Missingness:** Participants without microbiome data are excluded.
- **Output column:** `gut_microbiome_diversity__observed_species`

#### Feature 3: Shannon Diversity Category
- **Type:** Categorical
- **Source:** Derived from Shannon index (Feature 1)
- **Logic:**
  - "Low diversity": Shannon index <3.0
  - "Normal diversity": Shannon index ≥3.0
  Threshold based on clinical studies associating Shannon <3.0 with adverse health outcomes[^7].
- **Missingness:** Missing if Shannon index cannot be calculated.
- **Output column:** `gut_microbiome_diversity__diversity_category`

#### Feature 4: Sample Quality Flag
- **Type:** Categorical
- **Source:** Derived from observed species richness (Feature 2)
- **Logic:**
  - "Low quality/dysbiotic": <20 detected species (may indicate technical issues or true dysbiosis)
  - "Adequate": ≥20 detected species
  Based on pipeline documentation noting samples with <20 prominent strains may indicate technical or biological dysbiosis.
- **Missingness:** Missing if species richness cannot be calculated.
- **Output column:** `gut_microbiome_diversity__quality_flag`

### Inclusion / Exclusion Rules

- Include all participants with valid gut microbiome samples (mock = false)
- Exclude mock community samples used for quality control
- No age, sex, or cohort restrictions applied
- For participants with multiple samples, use the most recent sample (highest sample_id)

### Labeling Logic

This is a descriptive phenotype rather than a diagnostic label. The curated phenotype provides multiple diversity metrics:

1. **Continuous metrics**: Shannon index and observed species richness provide quantitative measures of gut microbiome diversity
2. **Categorical classification**: Shannon diversity category classifies participants as having "Low diversity" or "Normal diversity" based on the clinically-relevant threshold of 3.0
3. **Quality assessment**: Quality flag identifies samples that may have technical issues or represent biological dysbiosis

These features enable:
- Stratification of participants by microbiome diversity levels
- Association studies linking diversity to health outcomes
- Quality control for downstream microbiome analyses

### Caveats and Limitations

- **Single timepoint**: Uses one sample per participant; microbiome diversity can vary over time with diet, medications, and health status
- **Threshold limitations**: The Shannon <3.0 threshold is derived from septic shock studies and may not generalize to all health conditions[^7]
- **Confounding factors**: Diversity is influenced by antibiotic use, diet, disease state, and sample collection methods — these factors are not accounted for in this phenotype
- **Missing data**: Participants without microbiome samples are excluded entirely
- **Low-quality samples**: Samples with low read counts may yield unreliable diversity estimates; read count thresholds are not applied in this version
- **Disease heterogeneity**: Association between diversity and health outcomes varies by disease[^6]; blanket interpretation of "low diversity = unhealthy" may be misleading
- **Methodology dependence**: Diversity estimates depend on the profiling method (MetaPhlAn 4 used here); URS or other methods may yield different values

## References

- [^1]: [Key features and guidelines for the application of microbial alpha diversity metrics](https://www.nature.com/articles/s41598-024-77864-y), Scientific Reports, 2024
- [^2]: [Gut microbiome diversity measures for metabolic conditions: a systematic scoping review](https://www.medrxiv.org/content/10.1101/2021.06.25.21259549v1.full), medRxiv, 2021
- [^3]: [Frontiers | The Power of Microbiome Studies: Some Considerations on Which Alpha and Beta Metrics to Use and How to Report Results](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2021.796025/full)
- [^4]: [The Shannon Index: Decoding The Diversity of the Microbiome's Role in Health and Disease](https://www.theevergreeninstitute.org/post/the-shannon-index-decoding-the-diversity-of-the-microbiome-s-role-in-health-and-disease)
- [^5]: [Microbiome epidemiology and association studies in human health](https://www.nature.com/articles/s41576-022-00529-x), Nature Reviews Genetics
- [^6]: [Drivers of Microbiome Biodiversity: A Review of General Rules, Feces, and Ignorance](https://journals.asm.org/doi/10.1128/mbio.01294-18), mBio
- [^7]: [Association Between Gut Bacterial Diversity and Mortality in Septic Shock Patients: A Cohort Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6788322/)
- [^8]: Leviatan S, Shoer S, Rothschild D, Gorodetski M, Segal E. "An expanded reference map of the human gut microbiome reveals hundreds of previously unknown species." Nature Communications, 2022
- [^9]: [Frontiers | Gut microbiota heterogeneity in non-alcoholic fatty liver disease: a narrative review of drivers, mechanisms, and clinical relevance](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2025.1645298/full)
- [^10]: [A predictive index for health status using species-level gut microbiome profiling](https://www.nature.com/articles/s41467-020-18476-8), Nature Communications
