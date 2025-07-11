#!/usr/bin/env python3
"""
Comprehensive comparison of Stage 1A outputs
Legacy Individual Processing vs Batch Processing
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_results(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract results from wrapped or unwrapped format"""
    if 'results' in data:
        return data['results']
    return data

def compare_metadata(legacy: Dict[str, Any], batch: Dict[str, Any]) -> Dict[str, Any]:
    """Compare paper metadata sections"""
    comparison = {
        'section': 'paper_metadata',
        'matches': [],
        'differences': [],
        'legacy_only': [],
        'batch_only': []
    }
    
    legacy_meta = legacy.get('paper_metadata', {})
    batch_meta = batch.get('paper_metadata', {})
    
    # Compare each field
    all_keys = set(legacy_meta.keys()) | set(batch_meta.keys())
    
    for key in all_keys:
        if key in legacy_meta and key in batch_meta:
            if legacy_meta[key] == batch_meta[key]:
                comparison['matches'].append(f"{key}: {legacy_meta[key]}")
            else:
                comparison['differences'].append({
                    'field': key,
                    'legacy': legacy_meta[key],
                    'batch': batch_meta[key]
                })
        elif key in legacy_meta:
            comparison['legacy_only'].append(f"{key}: {legacy_meta[key]}")
        else:
            comparison['batch_only'].append(f"{key}: {batch_meta[key]}")
    
    return comparison

def compare_quantitative_findings(legacy: Dict[str, Any], batch: Dict[str, Any]) -> Dict[str, Any]:
    """Compare quantitative findings sections"""
    comparison = {
        'section': 'quantitative_findings',
        'primary_measurements_count': {
            'legacy': 0,
            'batch': 0
        },
        'parameter_comparison': [],
        'value_differences': []
    }
    
    legacy_findings = legacy.get('quantitative_findings', {})
    batch_findings = batch.get('quantitative_findings', {})
    
    # Count primary measurements
    legacy_measurements = legacy_findings.get('primary_measurements', [])
    batch_measurements = batch_findings.get('primary_measurements', [])
    
    comparison['primary_measurements_count']['legacy'] = len(legacy_measurements)
    comparison['primary_measurements_count']['batch'] = len(batch_measurements)
    
    # Create parameter maps for easier comparison
    legacy_params = {m.get('parameter'): m for m in legacy_measurements}
    batch_params = {m.get('parameter'): m for m in batch_measurements}
    
    # Compare parameters
    all_params = set(legacy_params.keys()) | set(batch_params.keys())
    
    for param in all_params:
        if param in legacy_params and param in batch_params:
            legacy_m = legacy_params[param]
            batch_m = batch_params[param]
            
            # Compare values
            if legacy_m.get('values') != batch_m.get('values'):
                comparison['value_differences'].append({
                    'parameter': param,
                    'legacy_values': legacy_m.get('values'),
                    'batch_values': batch_m.get('values'),
                    'units': legacy_m.get('units', 'N/A')
                })
            
            comparison['parameter_comparison'].append({
                'parameter': param,
                'in_legacy': True,
                'in_batch': True,
                'values_match': legacy_m.get('values') == batch_m.get('values')
            })
        elif param in legacy_params:
            comparison['parameter_comparison'].append({
                'parameter': param,
                'in_legacy': True,
                'in_batch': False,
                'values_match': False
            })
        else:
            comparison['parameter_comparison'].append({
                'parameter': param,
                'in_legacy': False,
                'in_batch': True,
                'values_match': False
            })
    
    return comparison

def compare_methodology(legacy: Dict[str, Any], batch: Dict[str, Any]) -> Dict[str, Any]:
    """Compare research methodology sections"""
    comparison = {
        'section': 'research_methodology',
        'structure_comparison': {},
        'detail_level': {}
    }
    
    legacy_method = legacy.get('research_methodology', {})
    batch_method = batch.get('research_methodology', {})
    
    # Compare top-level structure
    legacy_keys = set(legacy_method.keys())
    batch_keys = set(batch_method.keys())
    
    comparison['structure_comparison'] = {
        'common_sections': list(legacy_keys & batch_keys),
        'legacy_only': list(legacy_keys - batch_keys),
        'batch_only': list(batch_keys - legacy_keys)
    }
    
    # Compare detail level for common sections
    for section in comparison['structure_comparison']['common_sections']:
        legacy_content = str(legacy_method[section])
        batch_content = str(batch_method[section])
        
        comparison['detail_level'][section] = {
            'legacy_length': len(legacy_content),
            'batch_length': len(batch_content),
            'detail_ratio': len(batch_content) / len(legacy_content) if len(legacy_content) > 0 else 0
        }
    
    return comparison

def calculate_overall_quality_metrics(legacy: Dict[str, Any], batch: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall quality metrics"""
    metrics = {
        'total_content_size': {
            'legacy': len(json.dumps(legacy)),
            'batch': len(json.dumps(batch))
        },
        'completeness_score': {},
        'data_extraction_depth': {}
    }
    
    # Check key sections presence
    key_sections = [
        'paper_metadata', 'research_methodology', 'quantitative_findings',
        'environmental_context', 'agricultural_systems', 'temporal_dynamics',
        'data_quality_assessment', 'literature_integration'
    ]
    
    legacy_sections = sum(1 for s in key_sections if s in legacy and legacy[s])
    batch_sections = sum(1 for s in key_sections if s in batch and batch[s])
    
    metrics['completeness_score'] = {
        'legacy': f"{legacy_sections}/{len(key_sections)}",
        'batch': f"{batch_sections}/{len(key_sections)}",
        'sections_present': {
            'legacy': [s for s in key_sections if s in legacy and legacy[s]],
            'batch': [s for s in key_sections if s in batch and batch[s]]
        }
    }
    
    # Count total data points
    def count_data_points(obj, path=""):
        count = 0
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    count += count_data_points(v, f"{path}.{k}")
                elif v is not None and v != "" and v != []:
                    count += 1
        elif isinstance(obj, list):
            for item in obj:
                count += count_data_points(item, path)
        return count
    
    metrics['data_extraction_depth'] = {
        'legacy_data_points': count_data_points(legacy),
        'batch_data_points': count_data_points(batch)
    }
    
    return metrics

def print_comprehensive_comparison(legacy_file: str, batch_file: str):
    """Print comprehensive comparison report"""
    # Load files
    legacy_data = load_json_file(legacy_file)
    batch_data = load_json_file(batch_file)
    
    # Extract results
    legacy_results = extract_results(legacy_data)
    batch_results = extract_results(batch_data)
    
    print("="*80)
    print("COMPREHENSIVE STAGE 1A OUTPUT COMPARISON")
    print("Legacy Individual Processing vs Batch Processing")
    print("="*80)
    
    # 1. Metadata Comparison
    print("\n1. PAPER METADATA COMPARISON")
    print("-"*40)
    meta_comp = compare_metadata(legacy_results, batch_results)
    print(f"Matching fields: {len(meta_comp['matches'])}")
    print(f"Different fields: {len(meta_comp['differences'])}")
    print(f"Legacy only: {len(meta_comp['legacy_only'])}")
    print(f"Batch only: {len(meta_comp['batch_only'])}")
    
    if meta_comp['differences']:
        print("\nDifferences found:")
        for diff in meta_comp['differences']:
            print(f"  {diff['field']}:")
            print(f"    Legacy: {diff['legacy']}")
            print(f"    Batch: {diff['batch']}")
    
    # 2. Quantitative Findings Comparison
    print("\n2. QUANTITATIVE FINDINGS COMPARISON")
    print("-"*40)
    quant_comp = compare_quantitative_findings(legacy_results, batch_results)
    print(f"Legacy measurements: {quant_comp['primary_measurements_count']['legacy']}")
    print(f"Batch measurements: {quant_comp['primary_measurements_count']['batch']}")
    
    # Count matches
    param_matches = sum(1 for p in quant_comp['parameter_comparison'] if p['in_legacy'] and p['in_batch'] and p['values_match'])
    param_both = sum(1 for p in quant_comp['parameter_comparison'] if p['in_legacy'] and p['in_batch'])
    
    print(f"\nParameter overlap: {param_both} parameters in both")
    print(f"Value matches: {param_matches}/{param_both} parameters with identical values")
    
    if quant_comp['value_differences']:
        print(f"\nValue differences found: {len(quant_comp['value_differences'])}")
        for i, diff in enumerate(quant_comp['value_differences'][:5]):  # Show first 5
            print(f"\n  {i+1}. {diff['parameter']} ({diff['units']}):")
            print(f"     Legacy: {diff['legacy_values']}")
            print(f"     Batch: {diff['batch_values']}")
        if len(quant_comp['value_differences']) > 5:
            print(f"\n  ... and {len(quant_comp['value_differences']) - 5} more differences")
    
    # 3. Methodology Comparison
    print("\n3. RESEARCH METHODOLOGY COMPARISON")
    print("-"*40)
    method_comp = compare_methodology(legacy_results, batch_results)
    print(f"Common sections: {len(method_comp['structure_comparison']['common_sections'])}")
    print(f"Legacy only sections: {len(method_comp['structure_comparison']['legacy_only'])}")
    print(f"Batch only sections: {len(method_comp['structure_comparison']['batch_only'])}")
    
    print("\nDetail level comparison (batch/legacy ratio):")
    for section, details in method_comp['detail_level'].items():
        ratio = details['detail_ratio']
        status = "MORE" if ratio > 1.1 else "LESS" if ratio < 0.9 else "SIMILAR"
        print(f"  {section}: {ratio:.2f} ({status} detail)")
    
    # 4. Overall Quality Metrics
    print("\n4. OVERALL QUALITY METRICS")
    print("-"*40)
    metrics = calculate_overall_quality_metrics(legacy_results, batch_results)
    
    print(f"Total content size:")
    print(f"  Legacy: {metrics['total_content_size']['legacy']:,} characters")
    print(f"  Batch: {metrics['total_content_size']['batch']:,} characters")
    print(f"  Ratio: {metrics['total_content_size']['batch'] / metrics['total_content_size']['legacy']:.2f}")
    
    print(f"\nCompleteness score:")
    print(f"  Legacy: {metrics['completeness_score']['legacy']} sections")
    print(f"  Batch: {metrics['completeness_score']['batch']} sections")
    
    print(f"\nData extraction depth:")
    print(f"  Legacy: {metrics['data_extraction_depth']['legacy_data_points']:,} data points")
    print(f"  Batch: {metrics['data_extraction_depth']['batch_data_points']:,} data points")
    ratio = metrics['data_extraction_depth']['batch_data_points'] / metrics['data_extraction_depth']['legacy_data_points']
    print(f"  Ratio: {ratio:.2f}")
    
    # 5. Summary Assessment
    print("\n5. SUMMARY ASSESSMENT")
    print("-"*40)
    
    # Calculate overall similarity score
    total_params = len(quant_comp['parameter_comparison'])
    matching_params = sum(1 for p in quant_comp['parameter_comparison'] if p['in_legacy'] and p['in_batch'])
    param_similarity = matching_params / total_params if total_params > 0 else 0
    
    value_matches = sum(1 for p in quant_comp['parameter_comparison'] if p['values_match'])
    value_similarity = value_matches / matching_params if matching_params > 0 else 0
    
    size_ratio = metrics['total_content_size']['batch'] / metrics['total_content_size']['legacy']
    
    print(f"Parameter Coverage Similarity: {param_similarity:.1%}")
    print(f"Value Match Rate: {value_similarity:.1%}")
    print(f"Content Size Ratio: {size_ratio:.2f}")
    
    # Overall verdict
    if param_similarity > 0.9 and value_similarity > 0.8 and 0.8 < size_ratio < 1.2:
        print("\n✅ VERDICT: EXCELLENT QUALITY MATCH")
        print("The batch processing maintains high quality comparable to individual processing.")
    elif param_similarity > 0.8 and value_similarity > 0.7:
        print("\n✅ VERDICT: GOOD QUALITY MATCH")
        print("The batch processing provides good quality with minor differences.")
    elif param_similarity > 0.7:
        print("\n⚠️  VERDICT: MODERATE QUALITY MATCH")
        print("The batch processing has some quality differences that may need investigation.")
    else:
        print("\n❌ VERDICT: POOR QUALITY MATCH")
        print("Significant quality differences detected between batch and individual processing.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    # File paths - Using Agricultural Pollution paper that was actually freshly processed in batch
    legacy_file = "test_outputs/stage_1a/Agricultural Pollution Field Burning_1a_output.json"
    batch_file = "8_stage_outputs/stage_1a/Agricultural Pollution Field Burning_1a_20250710_025943.json"
    
    print("CORRECTED COMPARISON: Fresh Batch vs Individual Processing")
    print_comprehensive_comparison(legacy_file, batch_file)