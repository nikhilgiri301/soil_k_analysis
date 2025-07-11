# Flash vs Pro Model Comparison

This directory contains scripts for comparing Gemini 2.5 Flash vs Gemini 2.5 Pro performance on identical Stage 1A tasks.

## Overview

The comparison isolates **model capability** as the only variable to understand:
- Statistical pattern recognition differences
- Scientific interpretation depth variations  
- Quantitative data extraction completeness
- Processing time and cost trade-offs

## Files Created

### Core Test Scripts
- `test_stage_1a.py` - Original Flash model test (unchanged)
- `test_stage_1a_pro.py` - **NEW** Pro model test (identical logic, different model)
- `test_flash_vs_pro.py` - **NEW** Automated batch comparison runner
- `compare_flash_pro_results.py` - **NEW** Results analysis and reporting

### Key Differences in Pro Version

1. **Model Selection**: Uses `gemini-2.5-pro` instead of `gemini-2.5-flash`
2. **Output Naming**: Saves to `*_1a_pro_*` files for clear distinction
3. **Cache Namespace**: Uses separate cache (`test_pro_*`) to avoid conflicts
4. **Metadata Tagging**: Adds model identification to all results
5. **Cost Calculation**: Uses Pro pricing ($1.25 input, $5.00 output per 1M tokens)

## Usage

### Option 1: Run Individual Tests

```bash
# Run Flash model
python3 test_stage_1a.py --paper "your_paper.pdf" --api-key "your_key"

# Run Pro model  
python3 test_stage_1a_pro.py --paper "your_paper.pdf" --api-key "your_key"

# Compare results
python3 compare_flash_pro_results.py your_paper --verbose --save-report
```

### Option 2: Automated Batch Comparison

```bash
# Run both models and generate comparison automatically
python3 test_flash_vs_pro.py --paper "your_paper.pdf" --api-key "your_key" --verbose

# Run only Flash model
python3 test_flash_vs_pro.py --paper "your_paper.pdf" --api-key "your_key" --flash-only

# Run only Pro model
python3 test_flash_vs_pro.py --paper "your_paper.pdf" --api-key "your_key" --pro-only
```

## Output Structure

### Flash Results
```
8_stage_outputs/stage_1a/
├── paper_name_1a_20250708_123456.json      # Flash results
└── paper_name_1a_debug.json                # Flash debug info
```

### Pro Results  
```
8_stage_outputs/stage_1a_pro/
├── paper_name_1a_pro_20250708_123456.json  # Pro results
└── paper_name_1a_pro_debug.json            # Pro debug info
```

### Comparison Reports
```
comparison_report_paper_name_20250708_123456.json  # Detailed analysis
```

## What Gets Compared

### 1. Extraction Quality
- **Metadata Fields**: Which fields each model extracts
- **Key Findings**: Number and content of findings identified
- **Methodology Description**: Depth and accuracy of method extraction
- **Limitation Recognition**: Ability to identify study limitations

### 2. Scientific Depth
- **Pattern Recognition**: Statistical correlation identification
- **Quantitative Data**: Numerical value extraction accuracy
- **Interpretation Quality**: Scientific reasoning and conclusions
- **Citation Context**: Understanding of research context

### 3. Performance Metrics
- **Token Usage**: Input, output, and thinking token consumption
- **Processing Time**: End-to-end completion time
- **Cost Analysis**: Dollar cost per paper processed
- **Error Rates**: Success/failure rates and error types

### 4. Business Value
- **Decision Relevance**: Extraction of business-critical parameters
- **Uncertainty Quantification**: Explicit uncertainty statements
- **Actionability**: Practical applicability of extracted information

## Expected Differences

### Pro Model Advantages
- **Deeper Analysis**: More sophisticated pattern recognition
- **Better Context**: Improved understanding of scientific context
- **More Findings**: Identification of additional key findings
- **Higher Accuracy**: Better quantitative data extraction

### Flash Model Advantages  
- **Speed**: Faster processing times
- **Cost**: Lower per-paper processing cost
- **Efficiency**: Better cost/value ratio for routine tasks

## Analysis Workflow

1. **Run Both Models** on same paper with identical prompts
2. **Generate Comparison Report** with detailed analysis
3. **Analyze Trade-offs** between cost, speed, and quality
4. **Identify Use Cases** where each model excels
5. **Optimize Pipeline** based on findings

## Key Questions Answered

1. **Quality Gap**: How much better is Pro vs Flash for scientific extraction?
2. **Cost Justification**: Is the Pro premium worth the improved results?
3. **Speed vs Accuracy**: What's the optimal model for different use cases?
4. **Pipeline Optimization**: Which stages benefit most from Pro model?

## Example Comparison Output

```
FLASH VS PRO COMPARISON: paper_example
================================================================================

💰 COST ANALYSIS:
   Flash: $0.0123
   Pro:   $0.0567
   Pro is 4.6x more expensive

⚡ PERFORMANCE ANALYSIS:
   Pro is 2.3x slower
   Pro is 4.6x more expensive

🔍 EXTRACTION QUALITY:
   Flash found 8 key findings
   Pro found 12 key findings  
   ✅ Pro found 4 more findings

📋 METADATA EXTRACTION:
   Fields only in Flash: 2
   Fields only in Pro: 7
   Fields with different values: 3
   Fields with same values: 15

✅ PRO ADVANTAGES:
   • More metadata fields extracted
   • More key findings identified (12 vs 8)
   • Better quantitative data extraction

⚡ FLASH ADVANTAGES:
   • Lower cost per processing
   • Faster processing time
```

## Implementation Notes

### Model Selection Override
The Pro version creates a `GeminiClientPro` class that overrides the model selection:

```python
class GeminiClientPro(GeminiClient):
    def __init__(self, api_key: str, enable_thinking: bool = True):
        # ... initialization code ...
        # Force use of Gemini 2.5 Pro model
        self.model = genai.GenerativeModel("gemini-2.5-pro")
```

### Result Isolation
- Pro results use separate cache namespace (`test_pro_*`)
- Pro outputs saved to `*_1a_pro_*` files
- Comparison script automatically finds matching pairs

### Metadata Enrichment
All Pro results include model identification:
```json
{
  "_model_metadata": {
    "model_name": "gemini-2.5-pro",
    "model_variant": "pro", 
    "test_type": "stage_1a_pro_comparison",
    "timestamp": "2025-07-08T12:34:56"
  }
}
```

## Next Steps

1. **Run Comparison** on representative papers
2. **Analyze Results** to identify patterns
3. **Optimize Pipeline** based on findings
4. **Document Best Practices** for model selection
5. **Implement Hybrid Approach** using both models strategically

This comparison framework provides the foundation for data-driven model selection and pipeline optimization.