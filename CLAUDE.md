# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Soil K Literature Synthesis Engine** - a 5-stage, 10-pass AI synthesis system designed to analyze soil potassium research papers and generate business intelligence for mining companies. The system processes PDFs through a sophisticated pipeline that extracts, validates, synthesizes, and maps research findings to client questions.

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

### Resume from Checkpoint
```bash
python run_synthesis.py --api-key YOUR_API_KEY --resume-from checkpoint_id
```

### Environment Validation Only
```bash
python run_synthesis.py --api-key YOUR_API_KEY --validate-only
```

### Custom Configuration
```bash
python run_synthesis.py --config custom_config.json --api-key YOUR_API_KEY
```

## Architecture Overview

### Data Flow Pipeline
1. **1_source_pdfs/** - Raw PDF research papers
2. **2_processed_data/** - Extracted text and tables from PDFs
3. **3_synthesis_ready/** - Standardized JSON data ready for synthesis
4. **6_synthesis_engine/** - Core 5-stage processing engine
5. **8_stage_outputs/** - Intermediate results from each stage
6. **9_final_synthesis/** - Client-ready deliverables

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