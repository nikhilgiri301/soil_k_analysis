# CLAUDE.md

**CRITICAL RULE: Never run an API command unless I expressly ask you to under any circumstance, ever.**

**CRITICAL RULE: TIMEOUT PROTOCOL - If your command times out, you IMMEDIATELY:**
1. STOP all further actions
2. Report to USER: "My command timed out. Please instruct what I should do next."
3. WAIT for USER instructions - never automatically resume or take new actions
4. Remember: Claude Code has a 2-minute timeout limit that cannot be changed

**CRITICAL RULE: All stage processing scripts must have exactly 5 minutes timeout - never more, never less.**

**CRITICAL RULE: We will never do dry runs.**

**CRITICAL RULE: We will never have fallback options unless CLAUDE asks the USER and the USER allows CLAUDE to build in fallback options. CLAUDE may suggest fallback options, but CLAUDE NEVER implements anything without the USER expressly asking CLAUDE to do so.**

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Soil K Literature Synthesis Engine** - a 5-stage, 10-pass AI synthesis system designed to analyze soil potassium research papers and generate business intelligence for mining companies. The system processes PDFs through a sophisticated pipeline that extracts, validates, synthesizes, and maps research findings to client questions.

## Claude Working Instructions

- **Always ultrathink** when working on this complex synthesis system
- Use comprehensive analysis and consider multiple approaches before acting
- Think through implications step-by-step for all decisions
- This 5-stage, 10-pass AI system requires careful reasoning at every stage
- **CRITICAL**: Do what has been asked; nothing more, nothing less
- **NEVER** make assumptions or jump to solutions without being explicitly asked
- **ALWAYS** diagnose and understand problems before attempting fixes
- **RESEARCH FIRST**: Always research limitations and constraints before implementing solutions
- **SITUATIONAL AWARENESS**: Understand the broader context and goals of what we're trying to achieve
- **PROACTIVE INVESTIGATION**: Figure out important details that might not be explicitly asked for - this is the whole point of having AI assistance
- **UNDERSTAND GUARDRAILS**: Don't just find ways to do things - understand the constraints and limitations first
- **COMPREHENSIVE RESEARCH**: When working with new technologies/APIs, thoroughly research capabilities and limitations before implementation

### **CRITICAL: ENGLISH LANGUAGE INTERPRETATION**
- **"HOW" QUESTIONS = EXPLAIN THE APPROACH** - Do NOT implement, just explain the method/strategy
- **"GO DO X" OR "IMPLEMENT Y" = ACTION REQUESTS** - Only then should you take action
- **QUESTIONS vs REQUESTS**: 
  - "How would you...?" = Answer with explanation
  - "Can you recognize...?" = Answer the question, don't act
  - "Go ahead and..." = Take action
  - "Please implement..." = Take action
- **WAIT FOR EXPLICIT ACTION REQUESTS** before implementing any solutions
- **ANSWER QUESTIONS WITH EXPLANATIONS** not implementations

## Key Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Phase 1: PDF Processing
```bash
python 4_scripts/process_all_papers.py
```

### Phase 2: Main Synthesis Engine
```bash
python run_synthesis.py --api-key YOUR_GEMINI_API_KEY
```

### Limited Paper Processing (Testing)
```bash
# Process single paper for testing
python run_synthesis.py --api-key YOUR_API_KEY --limit 1

# Process 3 papers to test Stage 5 synthesis
python run_synthesis.py --api-key YOUR_API_KEY --limit 3
```

### Checkpoint/Resume Commands (Phase 2B)
```bash
# Resume from last successful stage
python run_synthesis.py --api-key YOUR_API_KEY --resume

# Resume from specific stage
python run_synthesis.py --api-key YOUR_API_KEY --from-stage 3A

# Force recache (ignore existing cache)
python run_synthesis.py --api-key YOUR_API_KEY --force-recache

# Inspect cached stage results
python run_synthesis.py --inspect-stage 1A

# Show completion status across papers
python run_synthesis.py --stage-summary

# Test individual stage on specific paper
python run_synthesis.py --test-stage 1A --paper specific_paper.pdf

# Clear cache for stage/paper
python run_synthesis.py --clear-cache 2A paper_name
```

### Environment Validation Only
```bash
python run_synthesis.py --api-key YOUR_API_KEY --validate-only
```

### Custom Configuration
```bash
python run_synthesis.py --config custom_config.json --api-key YOUR_API_KEY
```

### TRUE Batch Processing (Phase 2F - Cost Optimization)
```bash
# Run TRUE Gemini Batch API processing (50% cost savings)
python true_stage_1a_batch_processor.py --api-key YOUR_API_KEY

# Monitor batch job status (1-24 hour completion time)
# Job submission returns job ID for tracking
```

### 🚨 **ACTIVE BATCH JOB - DO NOT LOSE THIS INFORMATION**
**Current Job Status**: ⏳ PENDING/RUNNING  
**Job ID**: `pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr`  
**Job Name**: `batches/pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr`  
**Submitted**: July 10, 2025 at 04:54:44 UTC  
**Papers**: 22 papers (2.01 MB batch file)  
**Expected Completion**: 1-24 hours from submission  

### Monitor Active Batch Job
```bash
# Check current job status (run every few hours)
python3 -c "
import google.genai as genai
client = genai.Client(api_key='YOUR_API_KEY')
job = client.batches.get(name='batches/pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr')
print(f'Status: {job.state.name}')
print(f'Update Time: {job.update_time}')
if job.state.name == 'JOB_STATE_SUCCEEDED':
    print('✅ JOB COMPLETED - Ready to download results!')
"

# When job completes, download results with:
python true_stage_1a_batch_processor.py --api-key YOUR_API_KEY --download-results pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr
```

**📋 See [BATCH_PROCESSING_GUIDELINES.md](BATCH_PROCESSING_GUIDELINES.md) for complete batch processing documentation including:**
- True Gemini Batch API implementation 
- 50% cost savings vs individual processing
- Job submission, monitoring, and result retrieval
- Flexible validation framework fixes
- Production-ready error handling

### Individual Stage Testing (Phase 2E)
```bash
# Stage 1A: Generic Extraction
python test_stage_1a.py --paper "paper_name.json" --api-key YOUR_API_KEY

# Stage 1B: Generic Validation (requires 1A dependency)
python test_stage_1b.py --paper "paper_name.json" --api-key YOUR_API_KEY

# Stage 2A: Soil K Specific Extraction  
python test_stage_2a.py --paper "paper_name.json" --api-key YOUR_API_KEY

# Stage 2B: Soil K Validation (requires 2A dependency)
python test_stage_2b.py --paper "paper_name.json" --api-key YOUR_API_KEY

# Stage 3A: Paper Synthesis (requires 1B and 2B dependencies)
python test_stage_3a.py --paper "paper_name.json" --api-key YOUR_API_KEY

# Complete testing sequence (1A → 1B → 2A → 2B → 3A)
python test_stage_1a.py --paper "paper_name.json" --api-key YOUR_API_KEY
python test_stage_1b.py --paper "paper_name.json" --api-key YOUR_API_KEY  
python test_stage_2a.py --paper "paper_name.json" --api-key YOUR_API_KEY
python test_stage_2b.py --paper "paper_name.json" --api-key YOUR_API_KEY
python test_stage_3a.py --paper "paper_name.json" --api-key YOUR_API_KEY

# Common testing options
--disable-cache     # Force fresh processing, ignore cache
--verbose           # Show detailed processing information
--save-debug        # Save debug information and intermediate states
--use-main-cache    # Use main pipeline cache (may find existing results)
--output-dir DIR    # Override default test_outputs/ directory
```

### 🚀 Stage 1A Batch Processing Test (CURRENT PRIORITY)
```bash
# 🧪 RECOMMENDED: Test batch processing concept with Stage 1A only
# This validates 60-80% cost savings before implementing full 8-stage system

# Basic test (3 papers - RECOMMENDED FIRST RUN)
python test_stage_1a_batch.py --api-key YOUR_GEMINI_API_KEY --limit 3 --test-mode

# Full test (all 25 papers - after basic test success)
python test_stage_1a_batch.py --api-key YOUR_GEMINI_API_KEY --test-mode

# Dry run (no API calls - planning only)
python test_stage_1a_batch.py --api-key dummy_key --dry-run --limit 5

# Validate batch results
python validate_stage_1a_batch.py --detailed-analysis
```

### Batch Processing (Future - After Stage 1A Test Success)
```bash
# Full 8-stage batch processing (60-80% cost savings)
python process_all_papers_batch.py --api-key YOUR_GEMINI_API_KEY

# Test mode with limited papers
python process_all_papers_batch.py --api-key YOUR_KEY --limit 5 --test-mode

# Resume from specific stage
python process_all_papers_batch.py --api-key YOUR_KEY --resume-from-stage 3A
```

## Architecture Overview

### Data Flow Pipeline
1. **1_source_pdfs/** - Raw PDF research papers
2. **2_processed_data/** - Extracted text and tables from PDFs
3. **3_synthesis_ready/** - Standardized JSON data ready for synthesis
4. **6_synthesis_engine/** - Core 5-stage processing engine
5. **8_stage_outputs/** - Intermediate results from each stage
6. **9_final_synthesis/** - Client-ready deliverables
7. **10_stage_cache/** - Cached stage results for checkpoint/resume (Phase 2B)

### Core Components

**Master Controller** (`6_synthesis_engine/master_controller.py`):
- Orchestrates the entire 10-pass synthesis process
- Manages parallel processing across 5 stages
- Handles checkpoint/resume functionality

**Stage Processing Architecture**:
- **Stages 1-2**: Parallel extraction (generic + soil K specific)
- **Stage 3**: Paper-level synthesis
- **Stage 4**: Client question mapping
- **Stage 5**: Cross-paper integration and knowledge synthesis

**Validation Framework**:
- Quality controllers at each stage
- Confidence scoring throughout
- Conservative bias for business decision safety

### Key Configuration Files

- `6_synthesis_engine/config.json` - Main system configuration
- `7_client_architecture/question_tree.json` - Client questions structure
- `7_client_architecture/parameter_definitions.json` - Business parameters
- `6_synthesis_engine/prompts/` - AI prompts for each stage

## Working with the Synthesis Engine

### Environment Setup
The system requires a Gemini API key and validates the environment before processing:
- Checks for required directories
- Validates Phase 1 data availability
- Confirms client architecture files exist

### Key Classes and Methods

**SoilKAnalysisEngine** (`6_synthesis_engine/master_controller.py`):
- `process_all_papers()` - Main synthesis orchestration
- `process_stages_1_to_4()` - Per-paper processing
- `process_stage_5()` - Cross-paper integration

**Phase1DataAdapter** (`6_synthesis_engine/utils/data_adapter.py`):
- Loads and standardizes Phase 1 processing outputs
- Handles data format conversions for synthesis engine

### Error Handling and Recovery
- Automatic retry with exponential backoff
- Graceful degradation on single paper failures
- Comprehensive checkpoint/resume system
- Detailed logging to `11_validation_logs/synthesis_engine.log`

## Development Notes

### Adding New Stages
Each stage follows the pattern:
1. Create processor class in appropriate `stage_X_processors/` directory
2. Add corresponding prompt file in `6_synthesis_engine/prompts/`
3. Register in `master_controller.py` initialization
4. Update configuration in `config.json`

### Validation Framework
All stages include validation passes. The system uses:
- Conservative confidence calibration
- Citation traceability requirements
- Quality thresholds for business decision readiness

### Client Architecture
The system is designed for mining company clients with:
- Uncertainty-aware parameter delivery
- Geographic applicability assessment
- Business risk considerations
- Conservative recommendation confidence levels

## Output Structure

Final deliverables include:
- Executive summaries with confidence levels
- Parameter analysis with uncertainty quantification
- Regional applicability assessments
- Evidence traceability registry
- Business implications and recommendations

The system transforms research parameters from "unknown unknowns" to "known unknowns" with quantified confidence levels suitable for business modeling.

## Current Development Focus

**🚀 CURRENT PRIORITY: Stage 1A Batch Processing Test** - Smart validation approach testing batch processing concepts with Stage 1A only before implementing the full 8-stage system. This approach validates 60-80% cost savings without the complexity of dependencies.

### Why Stage 1A Batch Test First?
- **Isolated Testing**: No dependencies to complicate validation
- **Cost Validation**: Real measurement of Gemini Batch Mode + Implicit Caching savings  
- **Quick Iteration**: Fast feedback for prompt and process optimization
- **Risk Mitigation**: Validate approach before investing in full 8-stage implementation

### Key Stage 1A Batch Test Objectives
1. **Validate Gemini Batch Mode** (50% cost savings)
2. **Test Implicit Caching** (75% savings on repeated prompts) 
3. **Verify JSONL batch creation** and result processing
4. **Measure actual cost savings** vs projections
5. **Assess extraction quality** in batch mode
6. **Test error handling** and recovery patterns

### Expected Outcomes
- **60-80% total cost savings** confirmed
- **95%+ success rate** for Stage 1A extraction
- **Quality validation** compared to individual processing
- **Green light decision** for full 8-stage batch implementation

### Completed Implementation (Phase 1, 2A & 2B)
✅ Data adapter fixes (individual paper loading)
✅ `--limit N` argument implementation  
✅ Single paper testing and API integration
✅ Validation logic fixes and JSON template formatting
✅ **Complete checkpoint/resume system** (StageCacheManager, audit commands, cost tracking)
✅ **Cache integration testing** (successful cache operations, API cost analysis)
✅ **Issue discovery and analysis** (3 specific technical problems identified)

### Current Testing Commands (Available)
```bash
# Test with single paper (✅ Cache system working, issues identified)
python run_synthesis.py --api-key YOUR_KEY --limit 1

# Debug and audit commands (✅ Fully operational)
python run_synthesis.py --cache-stats
python run_synthesis.py --stage-summary
python run_synthesis.py --inspect-stage 1A

# Clear cache for testing fixes
python run_synthesis.py --clear-cache all "paper_name"
```

### Checkpoint/Resume Commands (✅ Fully Implemented)
```bash
# Resume from last successful stage
python run_synthesis.py --api-key YOUR_KEY --resume

# Resume from specific stage
python run_synthesis.py --api-key YOUR_KEY --from-stage 3A

# Force recache (ignore existing cache)
python run_synthesis.py --api-key YOUR_KEY --force-recache

# Disable caching for debugging
python run_synthesis.py --api-key YOUR_KEY --disable-cache
```

### Post-Fix Testing Commands (Phase 2C Goals)
```bash
# Test complete pipeline after fixes (Target: all 8 stages successful)
python run_synthesis.py --api-key YOUR_KEY --limit 1

# Test cache efficiency (Target: significant cost savings on second run)
python run_synthesis.py --api-key YOUR_KEY --limit 1  # Second run

# Multi-paper testing (Target: Stage 5 synthesis verification)
python run_synthesis.py --api-key YOUR_KEY --limit 3

# Full processing (Target: all 25 papers with checkpoint optimization)
python run_synthesis.py --api-key YOUR_KEY
```

## Current Development Status: Stages 1-4 Complete - Ready for Stage 5 Gold Standard ✅ 

**Major Milestone Achieved**: All individual paper processing (Stages 1-4) successfully completed for all 25 papers with 100% success rate.

### ✅ **Complete Stage Processing Achievement**:
- **Stages 1A/1B**: Generic extraction and validation ✅ (25/25 papers)
- **Stages 2A/2B**: Soil K specific extraction and validation ✅ (25/25 papers)  
- **Stages 3A/3B**: Paper synthesis and validation ✅ (25/25 papers)
- **Stages 4A/4B**: Client mapping and validation ✅ (25/25 papers)

**Total: 200 successful stage completions with zero failures**

### ✅ **Quality Validation Results**:
- **Stage 4A Quality Diagnostic**: AI mapping performs **better than manual analysis** with superior detail and organization
- **Stage 4B Enhancement Analysis**: Provides significant enhancements - granular parameter-specific intelligence with actionable confidence levels
- **Data Quality**: Enhanced pipeline delivering 90-95% extraction quality (up from 70-75%)
- **Business Intelligence**: All papers now mapped to client question architecture with calibrated confidence levels

### 🚀 **Ready for Gold Standard Implementation**:
- **All Prerequisites Complete**: Stage 4B outputs available for all 25 papers
- **Stage 4.5 Script Ready**: Programmatic chunk extraction to reduce 150+ AI calls to 14 AI calls
- **Architecture Validated**: Natural overlap analysis confirms cross-sectional integration preservation
- **Next Phase**: Execute Stage 4.5 → Stages 5A/5B → 6A/6B → 7A/7B (chunk-based synthesis)

### **Key Benefits Validated**:
- **Cost-Effective Development**: Individual stage testing framework proven successful
- **Flash Model Integration**: All stages optimized for Gemini 2.5 Flash model  
- **Natural Dependency Resolution**: Stages automatically find and use previous results
- **Error Isolation**: Successful debugging and quality improvement throughout pipeline
- **Standard Pipeline Integration**: All outputs properly stored for next-stage processing

### **Critical Documentation**:
- **[VALIDATION_STAGE_BUSINESS_VALUE_DOCUMENTATION.md](VALIDATION_STAGE_BUSINESS_VALUE_DOCUMENTATION.md)**: Definitive evidence that validation stages are mission-critical for business-grade output. Shows Stage 1B caught 3 critical errors (50% error rate) in Stage 1A, including data hallucination and 62% numerical overestimation. Validation stages transform unreliable AI extraction into trustworthy business intelligence suitable for mining company investment decisions.
- **[SYNTHESIS_IMPLEMENTATION_PLAN.md](SYNTHESIS_IMPLEMENTATION_PLAN.md)**: Complete roadmap with Priority 1 (Stages 1-4) now achieved, ready for Priority 2 (Stage 5 Gold Standard)