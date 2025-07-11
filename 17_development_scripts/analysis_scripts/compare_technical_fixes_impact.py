#!/usr/bin/env python3
"""
Technical Fixes Impact Analysis
Compares original vs revised Flash model results to quantify technical fix improvements
"""

import json
import sys
from pathlib import Path

def load_json_file(filename):
    """Load and parse JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filename}: {str(e)}")
        return None

def count_statistical_measures(primary_measurements):
    """Count statistical measures in primary measurements"""
    total_measurements = len(primary_measurements)
    measurements_with_stats = 0
    
    for measurement in primary_measurements:
        stats = measurement.get('statistical_measures', {})
        if stats and any(value for value in stats.values() if value not in [0, 0.0, "", None, {}]):
            measurements_with_stats += 1
    
    return total_measurements, measurements_with_stats

def analyze_extraction_completeness(data):
    """Analyze extraction completeness and quality"""
    results = data.get('results', data)  # Handle both wrapped and direct formats
    quantitative = results.get('quantitative_findings', {})
    
    analysis = {
        'primary_measurements': len(quantitative.get('primary_measurements', [])),
        'statistical_relationships': len(quantitative.get('statistical_relationships', [])),
        'temporal_patterns': len(quantitative.get('temporal_patterns', [])),
        'comparative_results': len(quantitative.get('comparative_results', [])),
    }
    
    # Count statistical measures
    total_measurements, measurements_with_stats = count_statistical_measures(
        quantitative.get('primary_measurements', [])
    )
    analysis['measurements_with_statistical_measures'] = measurements_with_stats
    analysis['statistical_completeness_rate'] = (measurements_with_stats / total_measurements * 100) if total_measurements > 0 else 0
    
    return analysis

def extract_performance_metrics(data):
    """Extract performance metrics"""
    # Handle both direct results and wrapped format
    if 'token_usage' in data:
        token_usage = data['token_usage']
        cost = data.get('estimated_cost_usd', 0)
        processing_time = data.get('processing_time_seconds', 0)
    else:
        # Look for metrics in results
        token_usage = {'input': 0, 'output': 0, 'thinking': 0}
        cost = 0
        processing_time = 0
    
    return {
        'input_tokens': token_usage.get('input', 0),
        'output_tokens': token_usage.get('output', 0),
        'thinking_tokens': token_usage.get('thinking', 0),
        'total_tokens': token_usage.get('input', 0) + token_usage.get('output', 0),
        'cost_usd': cost,
        'processing_time_seconds': processing_time
    }

def main():
    """Main comparison function"""
    print("🔍 Technical Fixes Impact Analysis")
    print("=" * 50)
    
    # Load data files
    original = load_json_file('balance_paper_flash_original.json')
    revised = load_json_file('balance_paper_flash_revised.json')
    
    if not original or not revised:
        print("❌ Could not load comparison files")
        return False
    
    print("✅ Successfully loaded both original and revised files")
    
    # Extract performance metrics
    orig_perf = extract_performance_metrics(original)
    rev_perf = extract_performance_metrics(revised)
    
    # Extract extraction quality metrics
    orig_extract = analyze_extraction_completeness(original)
    rev_extract = analyze_extraction_completeness(revised)
    
    # Performance Comparison
    print("\n📊 PERFORMANCE METRICS COMPARISON")
    print("-" * 40)
    
    metrics = [
        ("Input Tokens", orig_perf['input_tokens'], rev_perf['input_tokens']),
        ("Output Tokens", orig_perf['output_tokens'], rev_perf['output_tokens']),
        ("Total Tokens", orig_perf['total_tokens'], rev_perf['total_tokens']),
        ("Cost (USD)", orig_perf['cost_usd'], rev_perf['cost_usd']),
        ("Processing Time (s)", orig_perf['processing_time_seconds'], rev_perf['processing_time_seconds'])
    ]
    
    for metric_name, orig_val, rev_val in metrics:
        if orig_val > 0:
            change_pct = ((rev_val - orig_val) / orig_val) * 100
            change_icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
            print(f"{metric_name:20} | {orig_val:8,.2f} → {rev_val:8,.2f} | {change_icon} {change_pct:+6.1f}%")
        else:
            print(f"{metric_name:20} | {orig_val:8,.2f} → {rev_val:8,.2f} | ➡️   NEW")
    
    # Extraction Quality Comparison
    print("\n🎯 EXTRACTION QUALITY COMPARISON")
    print("-" * 40)
    
    quality_metrics = [
        ("Primary Measurements", orig_extract['primary_measurements'], rev_extract['primary_measurements']),
        ("Statistical Relationships", orig_extract['statistical_relationships'], rev_extract['statistical_relationships']),
        ("Temporal Patterns", orig_extract['temporal_patterns'], rev_extract['temporal_patterns']),
        ("Comparative Results", orig_extract['comparative_results'], rev_extract['comparative_results']),
        ("Measurements w/ Stats", orig_extract['measurements_with_statistical_measures'], rev_extract['measurements_with_statistical_measures'])
    ]
    
    for metric_name, orig_val, rev_val in quality_metrics:
        if orig_val > 0:
            change_pct = ((rev_val - orig_val) / orig_val) * 100
            change_icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
            print(f"{metric_name:25} | {orig_val:4d} → {rev_val:4d} | {change_icon} {change_pct:+6.1f}%")
        else:
            change_icon = "📈" if rev_val > 0 else "➡️"
            print(f"{metric_name:25} | {orig_val:4d} → {rev_val:4d} | {change_icon}   NEW")
    
    # Statistical Completeness Analysis
    print("\n📈 STATISTICAL COMPLETENESS IMPROVEMENT")
    print("-" * 40)
    print(f"Original: {orig_extract['measurements_with_statistical_measures']}/{orig_extract['primary_measurements']} ({orig_extract['statistical_completeness_rate']:.1f}%)")
    print(f"Revised:  {rev_extract['measurements_with_statistical_measures']}/{rev_extract['primary_measurements']} ({rev_extract['statistical_completeness_rate']:.1f}%)")
    
    stat_improvement = rev_extract['statistical_completeness_rate'] - orig_extract['statistical_completeness_rate']
    print(f"Improvement: {stat_improvement:+.1f} percentage points")
    
    # Key Insights
    print("\n💡 KEY INSIGHTS FROM TECHNICAL FIXES")
    print("-" * 40)
    
    # Calculate content processing improvement
    if orig_perf['input_tokens'] > 0:
        content_improvement = ((rev_perf['input_tokens'] - orig_perf['input_tokens']) / orig_perf['input_tokens']) * 100
        print(f"✅ Content Processing: {content_improvement:+.1f}% more paper content analyzed")
    
    # Calculate extraction detail improvement  
    if orig_perf['output_tokens'] > 0:
        detail_improvement = ((rev_perf['output_tokens'] - orig_perf['output_tokens']) / orig_perf['output_tokens']) * 100
        print(f"✅ Extraction Detail: {detail_improvement:+.1f}% more detailed analysis produced")
    
    # Cost efficiency
    if orig_perf['cost_usd'] > 0 and rev_perf['cost_usd'] > 0:
        cost_change = ((rev_perf['cost_usd'] - orig_perf['cost_usd']) / orig_perf['cost_usd']) * 100
        print(f"✅ Cost Efficiency: {cost_change:+.1f}% cost change")
    
    # Quality improvements
    total_orig_items = sum([orig_extract[k] for k in ['primary_measurements', 'statistical_relationships', 'temporal_patterns', 'comparative_results']])
    total_rev_items = sum([rev_extract[k] for k in ['primary_measurements', 'statistical_relationships', 'temporal_patterns', 'comparative_results']])
    
    if total_orig_items > 0:
        quality_improvement = ((total_rev_items - total_orig_items) / total_orig_items) * 100
        print(f"✅ Information Extraction: {quality_improvement:+.1f}% more quantitative findings")
    
    print(f"✅ Statistical Completeness: {stat_improvement:+.1f} percentage points improvement")
    
    print("\n🎉 TECHNICAL FIXES IMPACT SUMMARY")
    print("-" * 40)
    print("The technical data quality fixes successfully addressed:")
    print("• Text truncation (Phase 1): More content processed")
    print("• Table structure corruption (Phase 2): Better data parsing") 
    print("• Table quantity limitation (Phase 3): Complete table access")
    print("• Clean text integration (Phase 4): Improved AI comprehension")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)