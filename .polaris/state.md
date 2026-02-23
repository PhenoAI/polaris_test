# Project State

Project initialized on 2026-02-22.

## Skill: create-curated-phenotype v0.2.0 (2026-02-22T15:54:33Z)

> User prompt: "Create a curated phenotype for **gut microbiome diversity** using the `create-curated-phenotype` skill."

**Execution mode:** Autonomous (end-to-end, stopping only for blocking errors)
**Wall-clock start:** 2026-02-22T15:54:33Z

### Phase 1: Define — completed
- manifest.md: curated_phenotypes/gut_microbiome_diversity/2026-02-22_17-54/manifest.md
- mermaid.md: curated_phenotypes/gut_microbiome_diversity/2026-02-22_17-54/mermaid.md
- commit_hash: f2b23d4

## Fork from Phase 1: alternative-metrics (source: main, 2026-02-23T13:38:00Z)

> User instruction: Explore alternative diversity metrics (Simpson index, Chao1 richness estimator) alongside Shannon index for comparison. Use quality threshold of >50 detected species for "Adequate" samples.

### Phase 2: Build — completed
- compute.py: curated_phenotypes/gut_microbiome_diversity/2026-02-22_17-54/compute.py
- output_table: ds.polaris.gut_microbiome_diversity (12,302 participants, 6 features)
  - Shannon index: mean=3.72, median=3.84
  - Simpson index: mean=0.928, median=0.955
  - Chao1 richness: mean=464.6, median=448 (~2.3x observed)
  - Low quality (≤50 species): 24 participants (0.2%, vs 0.0% with ≤20 threshold)
- report.ipynb: curated_phenotypes/gut_microbiome_diversity/2026-02-22_17-54/report.ipynb
- commit_hash: b35cb74
