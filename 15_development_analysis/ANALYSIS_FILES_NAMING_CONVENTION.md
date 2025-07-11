# Analysis Files Naming Convention

## Overview
This document explains the systematic renaming of analysis files to enable clear before/after comparisons when testing technical data quality fixes.

## New Naming Pattern
```
{paper_name}_{model_type}_{version}.json
```

Where:
- **paper_name**: `balance_paper` or `rice_paper`
- **model_type**: `flash`, `pro`, or `human`
- **version**: `original` (before fixes) or `revised` (after fixes)

## Current Analysis Files

### Balance Paper (Balance of potassium in two long-term field experiments)
- ✅ `balance_paper_flash_original.json` - Gemini 2.5 Flash results (before technical fixes)
- ✅ `balance_paper_pro_original.json` - Gemini 2.5 Pro results (before technical fixes)  
- ✅ `balance_paper_human_original.json` - Human manual analysis (gold standard)

### Rice Paper (Impact of potassium management on soil dynamics and crop uptake in rice systems)
- ✅ `rice_paper_flash_original.json` - Gemini 2.5 Flash results (before technical fixes)
- ⚠️ `rice_paper_pro_original_ANALYSIS_DATA.json` - Pro model results documented in analysis file (original JSON file missing from filesystem)
- ✅ `rice_paper_human_original.json` - Human manual analysis (gold standard)

## Planned Future Files (After Technical Fixes Testing)

### Balance Paper - Revised Versions
- 🔄 `balance_paper_flash_revised.json` - Flash results with technical data quality fixes
- 🔄 `balance_paper_pro_revised.json` - Pro results with technical data quality fixes

### Rice Paper - Revised Versions  
- 🔄 `rice_paper_flash_revised.json` - Flash results with technical data quality fixes
- 🔄 `rice_paper_pro_revised.json` - Pro results with technical data quality fixes (first time testing)

## Comparison Matrix Enabled

This naming convention enables systematic comparisons:

### Performance Improvements (Technical Fixes Impact)
- **Flash improvement**: `flash_original` vs `flash_revised`
- **Pro improvement**: `pro_original` vs `pro_revised`

### Model Comparisons (At each version)
- **Original models**: `flash_original` vs `pro_original` vs `human_original`
- **Revised models**: `flash_revised` vs `pro_revised` vs `human_original`

### Gap Analysis (Distance to Human Performance)
- **Original gaps**: How far are `flash_original` and `pro_original` from `human_original`?
- **Revised gaps**: How far are `flash_revised` and `pro_revised` from `human_original`?
- **Gap reduction**: How much do technical fixes close the gap to human performance?

## Strategic Questions to Answer

1. **Technical Fix Impact**: Do technical fixes dramatically improve AI extraction quality?
2. **Model Selection**: Does Flash + Fixes ≥ Pro + Broken Data (cost optimization)?
3. **Remaining Gaps**: What percentage of quality gaps are technical vs intelligence limitations?
4. **ROI Analysis**: Cost-benefit of Pro model vs technical optimization?

## File Sources

### Original Sources (Preserved for Reference)
- Balance Flash: `8_stage_outputs/stage_1a/Balance of potassium...20250708_083033.json`
- Balance Pro: `8_stage_outputs/stage_1a_pro/Balance of potassium...20250708_060921.json`
- Balance Human: `human_extraction_stage_1a.json`
- Rice Flash: `8_stage_outputs/stage_1a/Impact of potassium...20250708_083533.json`
- Rice Human: `human_extraction_rice_systems_stage_1a.json`

### Technical Fixes Implemented
- **Phase 1**: Text truncation removed (15K → 30K+ characters)
- **Phase 2**: Table structure corruption fixed (string → structured format)
- **Phase 3**: Complete table processing (3 → 8 tables)
- **Expected Impact**: 47%→100% text coverage, 37.5%→100% table coverage, 16-37%→85%+ statistical measures

This systematic approach ensures clear tracking of improvement from technical infrastructure enhancements while maintaining rigorous comparison standards.