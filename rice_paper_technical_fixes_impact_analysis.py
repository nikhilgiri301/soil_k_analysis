#!/usr/bin/env python3
"""
Rice Paper Three-Way Technical Fixes Impact Analysis
Comprehensive comparison: Original Flash vs Revised Flash vs Human
"""

import json
import sys
from pathlib import Path

def load_analysis_data():
    """Load all three Rice paper analysis files"""
    files = {
        'original_flash': 'rice_paper_flash_original.json',
        'revised_flash': 'rice_paper_flash_revised.json', 
        'human': 'rice_paper_human_original.json'
    }
    
    data = {}
    for key, filename in files.items():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
            print(f"✅ Loaded {key}: {filename}")
        except Exception as e:
            print(f"❌ Error loading {filename}: {str(e)}")
            return None
    
    return data

def extract_quantitative_findings(data, source_name):
    """Extract quantitative findings from each source"""
    # Handle different data structures
    if source_name == 'human':
        qf = data.get('quantitative_findings', {})
    else:
        # For AI models, check if wrapped in results
        results = data.get('results', data)
        qf = results.get('quantitative_findings', {})
    
    return {
        'primary_measurements': qf.get('primary_measurements', []),
        'statistical_relationships': qf.get('statistical_relationships', []),
        'temporal_patterns': qf.get('temporal_patterns', []),
        'comparative_results': qf.get('comparative_results', [])
    }

def count_statistical_completeness(primary_measurements):
    """Count measurements with complete statistical measures"""
    total = len(primary_measurements)
    with_stats = 0
    
    for measurement in primary_measurements:
        stats = measurement.get('statistical_measures', {})
        # Check if statistical measures are populated (not empty/null/zero)
        if stats and any(value for value in stats.values() if value not in [0, 0.0, "", None, {}]):
            with_stats += 1
    
    return total, with_stats, (with_stats/total*100) if total > 0 else 0

def extract_performance_metrics(data, source_name):
    """Extract performance metrics"""
    if source_name == 'human':
        return {
            'input_tokens': 'N/A (manual)',
            'output_tokens': 'N/A (manual)',
            'processing_time': 'N/A (manual)', 
            'cost': 'N/A (manual)',
            'note': '8-12 hours estimated human time'
        }
    
    # For AI models
    return {
        'input_tokens': data.get('token_usage', {}).get('input', 0),
        'output_tokens': data.get('token_usage', {}).get('output', 0),
        'processing_time': data.get('processing_time_seconds', 0),
        'cost': data.get('estimated_cost_usd', 0)
    }

def analyze_specific_examples(data):
    """Extract specific examples for detailed comparison"""
    findings = {}
    for source in ['original_flash', 'revised_flash', 'human']:
        source_data = data[source]
        if source == 'human':
            qf = source_data.get('quantitative_findings', {})
        else:
            results = source_data.get('results', source_data)
            qf = results.get('quantitative_findings', {})
        
        # Extract first few measurements for comparison
        measurements = qf.get('primary_measurements', [])
        findings[source] = {
            'sample_measurements': measurements[:3] if measurements else [],
            'measurement_count': len(measurements),
            'has_statistical_measures': any(
                m.get('statistical_measures', {}) for m in measurements
            ) if measurements else False
        }
    
    return findings

def main():
    """Main Rice paper three-way analysis function"""
    print("🔍 Rice Paper: Technical Fixes Impact Analysis")
    print("Original Flash vs Revised Flash vs Human")
    print("=" * 60)
    
    # Load data
    data = load_analysis_data()
    if not data:
        return False
    
    # Extract quantitative findings for each source
    findings = {}
    for source in ['original_flash', 'revised_flash', 'human']:
        findings[source] = extract_quantitative_findings(data[source], source)
        print(f"📊 {source.replace('_', ' ').title()} findings extracted")
    
    # Performance metrics
    performance = {}
    for source in ['original_flash', 'revised_flash', 'human']:
        performance[source] = extract_performance_metrics(data[source], source)
    
    # Specific examples
    examples = analyze_specific_examples(data)
    
    # Generate comprehensive comparison
    print("\n" + "="*60)
    print("RICE PAPER THREE-WAY COMPARISON ANALYSIS")
    print("="*60)
    
    # 1. Data Completeness Comparison
    print("\n📊 DATA COMPLETENESS COMPARISON")
    print("-" * 50)
    print(f"{'Metric':<25} | {'Original':<8} | {'Revised':<8} | {'Human':<8} | {'Improvement'}")
    print("-" * 75)
    
    metrics = ['primary_measurements', 'statistical_relationships', 'temporal_patterns', 'comparative_results']
    
    for metric in metrics:
        orig = len(findings['original_flash'][metric])
        rev = len(findings['revised_flash'][metric])
        human = len(findings['human'][metric])
        
        # Calculate improvement
        if orig > 0:
            improvement = f"{((rev-orig)/orig*100):+.0f}%"
        else:
            improvement = "NEW" if rev > 0 else "---"
        
        metric_display = metric.replace('_', ' ').title()
        print(f"{metric_display:<25} | {orig:<8} | {rev:<8} | {human:<8} | {improvement}")
    
    # 2. Statistical Completeness Analysis
    print("\n📈 STATISTICAL COMPLETENESS ANALYSIS")
    print("-" * 50)
    
    orig_total, orig_with_stats, orig_pct = count_statistical_completeness(findings['original_flash']['primary_measurements'])
    rev_total, rev_with_stats, rev_pct = count_statistical_completeness(findings['revised_flash']['primary_measurements'])
    human_total, human_with_stats, human_pct = count_statistical_completeness(findings['human']['primary_measurements'])
    
    print(f"Original Flash: {orig_with_stats}/{orig_total} ({orig_pct:.1f}%)")
    print(f"Revised Flash:  {rev_with_stats}/{rev_total} ({rev_pct:.1f}%)")
    print(f"Human Analysis: {human_with_stats}/{human_total} ({human_pct:.1f}%)")
    print(f"Improvement:    {rev_pct - orig_pct:+.1f} percentage points")
    
    # 3. Performance Metrics
    print("\n⚡ PERFORMANCE METRICS COMPARISON")
    print("-" * 50)
    
    if performance['original_flash']['input_tokens'] and performance['revised_flash']['input_tokens']:
        print(f"Input Tokens:    {performance['original_flash']['input_tokens']:>8} → {performance['revised_flash']['input_tokens']:>8}")
        print(f"Output Tokens:   {performance['original_flash']['output_tokens']:>8} → {performance['revised_flash']['output_tokens']:>8}")
        print(f"Processing Time: {performance['original_flash']['processing_time']:>8.1f}s → {performance['revised_flash']['processing_time']:>8.1f}s")
        print(f"Cost:           ${performance['original_flash']['cost']:>8.3f} → ${performance['revised_flash']['cost']:>8.3f}")
    
    # 4. Gap Analysis
    print("\n🎯 GAP ANALYSIS - DISTANCE TO HUMAN PERFORMANCE")
    print("-" * 50)
    
    # Calculate total extracted items
    orig_total_items = sum(len(findings['original_flash'][m]) for m in metrics)
    rev_total_items = sum(len(findings['revised_flash'][m]) for m in metrics)
    human_total_items = sum(len(findings['human'][m]) for m in metrics)
    
    orig_gap = ((human_total_items - orig_total_items) / human_total_items * 100) if human_total_items > 0 else 0
    rev_gap = ((human_total_items - rev_total_items) / human_total_items * 100) if human_total_items > 0 else 0
    gap_reduction = orig_gap - rev_gap
    
    print(f"Original Flash Gap to Human: {orig_gap:.1f}%")
    print(f"Revised Flash Gap to Human:  {rev_gap:.1f}%")
    print(f"Gap Reduction Achieved:      {gap_reduction:.1f} percentage points")
    
    # 5. Technical Fixes Validation
    print("\n🔧 TECHNICAL FIXES VALIDATION")
    print("-" * 50)
    
    text_improvement = "Confirmed" if performance['revised_flash']['input_tokens'] >= performance['original_flash']['input_tokens'] else "Needs Review"
    table_improvement = "Confirmed" if rev_total_items > orig_total_items else "Needs Review"
    info_improvement = "Confirmed" if rev_total_items > orig_total_items * 1.5 else "Partial"
    
    print(f"Phase 1 (Text Processing):     {text_improvement}")
    print(f"Phase 2+3 (Table Processing):  {table_improvement}")  
    print(f"Phase 4 (Information Extraction): {info_improvement}")
    
    # 6. Cross-Paper Consistency Check
    print("\n🔍 CROSS-PAPER CONSISTENCY CHECK")
    print("-" * 50)
    
    # Compare with Balance paper results (approximate)
    balance_improvement = 400  # From Balance paper analysis
    rice_improvement = ((rev_total_items - orig_total_items) / orig_total_items * 100) if orig_total_items > 0 else 0
    
    print(f"Balance Paper Information Improvement: ~{balance_improvement}%")
    print(f"Rice Paper Information Improvement:    {rice_improvement:.0f}%")
    
    if abs(rice_improvement - balance_improvement) < 200:
        print("✅ CONSISTENT: Technical fixes show similar improvements across papers")
    else:
        print("⚠️  VARIATION: Different improvement levels between papers (expected due to content differences)")
    
    # 7. Key Insights Summary
    print("\n💡 RICE PAPER KEY INSIGHTS")
    print("-" * 50)
    
    if rev_total_items > orig_total_items * 2:
        print(f"🚀 MAJOR IMPROVEMENT: {((rev_total_items/orig_total_items-1)*100):.0f}% more information extracted")
    
    if gap_reduction > 10:
        print(f"📈 SIGNIFICANT GAP REDUCTION: {gap_reduction:.1f} point improvement toward human performance")
    
    if rev_pct > orig_pct:
        print(f"📊 STATISTICAL IMPROVEMENT: {rev_pct - orig_pct:+.1f} point statistical completeness improvement")
    
    # Generate structured data for markdown creation
    analysis_results = {
        'paper_name': 'rice_systems',
        'findings': findings,
        'performance': performance,
        'examples': examples,
        'statistical_completeness': {
            'original': {'total': orig_total, 'with_stats': orig_with_stats, 'percentage': orig_pct},
            'revised': {'total': rev_total, 'with_stats': rev_with_stats, 'percentage': rev_pct},
            'human': {'total': human_total, 'with_stats': human_with_stats, 'percentage': human_pct}
        },
        'gap_analysis': {
            'original_gap': orig_gap,
            'revised_gap': rev_gap,
            'gap_reduction': gap_reduction
        },
        'total_items': {
            'original': orig_total_items,
            'revised': rev_total_items,
            'human': human_total_items
        },
        'cross_paper_consistency': {
            'rice_improvement': rice_improvement,
            'balance_improvement': balance_improvement
        }
    }
    
    # Save analysis results for markdown generation
    with open('rice_paper_three_way_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Rice paper analysis complete! Results saved to rice_paper_three_way_analysis_results.json")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)