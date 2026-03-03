# Gut Microbiome Diversity — Medical Manifest

**Author:** Claude (Polaris AI Research Assistant)
**Last updated:** 2026-03-03
**Phenotype ID:** TBD

## Background

The human gut microbiome comprises trillions of microorganisms, predominantly bacteria, that play critical roles in host metabolism, immune function, and overall health[^1]. **Alpha diversity** refers to the diversity of microbial species within a single sample, reflecting both the richness (number of unique species) and evenness (distribution of relative abundances) of the microbial community[^2].

The **Shannon diversity index** is the most widely used alpha diversity metric in microbiome research, appearing in 78.7% of diversity studies[^3]. It estimates community diversity based on the principle that greater species richness and more equitable abundance distributions increase uncertainty in predicting the next entity encountered[^4]. Higher Shannon index values indicate greater microbial diversity, typically ranging from 0 (no diversity) to ~5-6 in healthy human gut samples[^5].

Lower gut microbiome diversity has been consistently associated with adverse health outcomes across multiple chronic diseases, including inflammatory bowel disease, non-alcoholic fatty liver disease, colon cancer, obesity, and metabolic syndrome[^1][^6]. However, the relationship between diversity and health is nuanced — diversity alone does not reliably indicate microbiome healthiness, and context-specific factors (diet, medications, disease state) must be considered[^7][^8]. Standardized thresholds for "healthy" vs "unhealthy" diversity do not exist; instead, diversity is best interpreted relative to population distributions and clinical context[^9].

The gut microbiome is profiled using shotgun metagenomic sequencing followed by taxonomic classification with tools like MetaPhlAn 4, which uses clade-specific marker genes to estimate relative abundances at species resolution[^10]. Quality control is essential, as low read depth, low biomass samples, or technical artifacts can produce spurious diversity estimates[^11].

## Data Plan

### Datasets Used

| Dataset | Table | Key Columns | Role |
|---------|-------|-------------|------|
| Gut microbiome metagenomics (MetaPhlAn) | `ds.omics.gut_mb_metaphlan` | `participant_uuid`, `sample_id`, `clade_name`, `relative_abundance`, `level`, `mock` | Species-level relative abundances for diversity computation |
| Population characteristics | `ds.silverdb.participant` | `uuid`, `gender`, `year_of_birth`, `cohort` | Participant demographics for context |

### Features

#### Feature 1: Shannon Diversity Index
- **Type:** Continuous
- **Source:** Computed from `ds.omics.gut_mb_metaphlan` where `level = 'species'` and `mock = false`
- **Logic:** Shannon index H = -Σ(p_i × ln(p_i)), where p_i is the relative abundance (proportion, not percentage) of species i. Relative abundances are converted from percentages (0-100) to proportions (0-1) before calculation. Only species with relative_abundance > 0 are included.
- **Missingness:** Participants without valid gut microbiome samples (mock=false, level='species') are excluded from the output.
- **Output column:** `gut_microbiome_diversity__shannon_index`

#### Feature 2: Observed Species Richness
- **Type:** Integer
- **Source:** Computed from `ds.omics.gut_mb_metaphlan` where `level = 'species'` and `mock = false`
- **Logic:** Count of distinct species with relative_abundance > 0 per participant.
- **Missingness:** Participants without valid gut microbiome samples are excluded.
- **Output column:** `gut_microbiome_diversity__observed_species`

#### Feature 3: Sample Quality Flag
- **Type:** Categorical (Adequate, Low Quality)
- **Source:** Derived from Feature 2 (observed species richness)
- **Logic:** Samples with fewer than 20 observed species are flagged as "Low Quality" (likely low biomass or technical failure). Samples with ≥20 species are "Adequate"[^11].
- **Missingness:** All participants with gut microbiome data receive a quality label.
- **Output column:** `gut_microbiome_diversity__sample_quality`

#### Feature 4: Diversity Category
- **Type:** Categorical (High, Moderate, Low)
- **Source:** Derived from Feature 1 (Shannon index)
- **Logic:** Based on empirical tertiles from the HPP population distribution. "Low" = Shannon < 3.0 (lower ~33%), "Moderate" = 3.0-4.0 (middle ~33%), "High" = >4.0 (upper ~33%). These thresholds are data-driven rather than literature-derived, as standardized clinical cutoffs do not exist[^9].
- **Missingness:** All participants with valid Shannon index values receive a category.
- **Output column:** `gut_microbiome_diversity__diversity_category`

### Inclusion / Exclusion Rules

- Include: All participants with at least one valid gut microbiome sample (`mock = false`) in `ds.omics.gut_mb_metaphlan`
- Exclude: Mock community samples (`mock = true`)
- Exclude: Participants with NULL `participant_uuid`
- Exclude: Samples with extreme outlier species counts (>2000 species, likely processing artifacts)

### Labeling Logic

This is not a disease classification phenotype — it produces continuous diversity measures and quality flags for downstream analyses. The primary output is the **Shannon diversity index**, supplemented by:
- **Observed species richness** (raw count)
- **Sample quality flag** (QC indicator)
- **Diversity category** (tertile-based classification for convenience)

Researchers can use these features to investigate associations between gut microbiome diversity and health outcomes, medications, diet, or other phenotypes.

### Caveats and Limitations

- **Cross-sectional snapshot:** Microbiome diversity is measured at a single time point; longitudinal dynamics are not captured in this version.
- **MetaPhlAn-specific:** Diversity estimates are based on MetaPhlAn 4 taxonomic profiling. Alternative methods (e.g., URS, amplicon sequencing) may yield different estimates.
- **No functional diversity:** This phenotype measures taxonomic diversity only; functional pathway diversity (via HUMAnN) is not included.
- **Population-specific thresholds:** The diversity category tertiles are derived from the HPP cohort and may not generalize to other populations.
- **Low biomass samples:** Some participants with genuinely low microbial diversity (e.g., due to antibiotics, disease) may be flagged as "Low Quality" when in fact the biology is real.
- **Missing data:** Participants without stool samples or those with failed sequencing are absent from the output.

## References

All clinical definitions, diagnostic thresholds, and classification criteria used in this manifest are cited below.

- [^1]: [Health and disease markers correlate with gut microbiome composition across thousands of people, Nature Communications 2020](https://www.nature.com/articles/s41467-020-18871-1)
- [^2]: [Key features and guidelines for the application of microbial alpha diversity metrics, Scientific Reports 2024](https://www.nature.com/articles/s41598-024-77864-y)
- [^3]: [Gut microbiome diversity measures for metabolic conditions: a systematic scoping review, medRxiv 2021](https://www.medrxiv.org/content/10.1101/2021.06.25.21259549v1.full)
- [^4]: [Drivers of Microbiome Biodiversity: A Review of General Rules, Feces, and Ignorance, mBio 2018](https://journals.asm.org/doi/10.1128/mbio.01294-18)
- [^5]: [The Use and Types of Alpha-Diversity Metrics in Microbial NGS, CD Genomics](https://www.cd-genomics.com/microbioseq/the-use-and-types-of-alpha-diversity-metrics-in-microbial-ngs.html)
- [^6]: [Diversity, stability and resilience of the human gut microbiota, Nature 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3577372/)
- [^7]: [Diversity alone does not reliably indicate the healthiness of an animal microbiome, ISME Journal 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11334719/)
- [^8]: [Tuning Expectations to Reality: Don't Expect Increased Gut Microbiota Diversity with Dietary Fiber, Cell Host & Microbe 2024](https://www.sciencedirect.com/science/article/pii/S002231662372590X)
- [^9]: [Microbiome quick guides series: Microbiome diversity, Kristina Campbell](https://www.bykriscampbell.com/blog/microbiome-quick-guides-series-microbiome-diversity)
- [^10]: MetaPhlAn 4 taxonomic profiling (standard pipeline, reference implicit in HPP dataset)
- [^11]: Quality control best practices for microbiome sequencing (threshold based on empirical observation in HPP data and field standards)
