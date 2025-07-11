#!/usr/bin/env python3
"""
Compare Gemini 2.5 Flash vs Pro Results
Analyzes the differences between Flash and Pro model outputs for the same paper
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

def load_results(paper_id: str, results_dir: str = "8_stage_outputs") -> dict:
    """Load both Flash and Pro results for a paper"""
    results_path = Path(results_dir)
    
    # Find Flash results (standard 1a)
    flash_file = None
    for file in results_path.glob(f"*/{paper_id}_1a_*.json"):
        if "_pro" not in file.stem:
            flash_file = file
            break
    
    # Find Pro results
    pro_file = None
    for file in results_path.glob(f"*/{paper_id}_1a_pro_*.json"):
        pro_file = file
        break
    
    results = {}
    
    if flash_file and flash_file.exists():
        with open(flash_file, 'r', encoding='utf-8') as f:
            results['flash'] = json.load(f)
            results['flash_file'] = str(flash_file)
    else:
        print(f"⚠️  Flash results not found for {paper_id}")
        results['flash'] = None
        
    if pro_file and pro_file.exists():
        with open(pro_file, 'r', encoding='utf-8') as f:
            results['pro'] = json.load(f)
            results['pro_file'] = str(pro_file)
    else:
        print(f"⚠️  Pro results not found for {paper_id}")
        results['pro'] = None
    
    return results

def analyze_metadata_differences(flash_data: dict, pro_data: dict) -> dict:
    """Compare paper metadata extraction between models"""
    flash_meta = flash_data.get('paper_metadata', {})
    pro_meta = pro_data.get('paper_metadata', {})
    
    analysis = {
        'fields_only_in_flash': [],
        'fields_only_in_pro': [],
        'fields_different': [],
        'fields_same': []
    }
    
    all_fields = set(flash_meta.keys()) | set(pro_meta.keys())
    
    for field in all_fields:
        if field in flash_meta and field in pro_meta:
            if flash_meta[field] != pro_meta[field]:
                analysis['fields_different'].append({
                    'field': field,
                    'flash_value': flash_meta[field],
                    'pro_value': pro_meta[field]
                })
            else:
                analysis['fields_same'].append(field)
        elif field in flash_meta:
            analysis['fields_only_in_flash'].append({
                'field': field,
                'value': flash_meta[field]
            })
        else:
            analysis['fields_only_in_pro'].append({
                'field': field,
                'value': pro_meta[field]
            })
    
    return analysis

def analyze_key_findings(flash_data: dict, pro_data: dict) -> dict:
    """Compare key findings extraction between models"""
    flash_findings = flash_data.get('key_findings', [])
    pro_findings = pro_data.get('key_findings', [])
    
    analysis = {
        'flash_count': len(flash_findings),
        'pro_count': len(pro_findings),
        'flash_findings': flash_findings,
        'pro_findings': pro_findings,
        'summary': {
            'pro_found_more': len(pro_findings) > len(flash_findings),
            'difference': len(pro_findings) - len(flash_findings)
        }
    }
    
    return analysis

def analyze_token_usage(flash_data: dict, pro_data: dict) -> dict:
    """Compare token usage and costs between models"""
    flash_usage = flash_data.get('_usage_metadata', {})
    pro_usage = pro_data.get('_usage_metadata', {})
    
    analysis = {
        'flash_tokens': {
            'input': flash_usage.get('input_tokens', 0),
            'output': flash_usage.get('output_tokens', 0),
            'thinking': flash_usage.get('thinking_tokens', 0),
            'total': flash_usage.get('input_tokens', 0) + flash_usage.get('output_tokens', 0) + flash_usage.get('thinking_tokens', 0)
        },
        'pro_tokens': {
            'input': pro_usage.get('input_tokens', 0),
            'output': pro_usage.get('output_tokens', 0),
            'thinking': pro_usage.get('thinking_tokens', 0),
            'total': pro_usage.get('input_tokens', 0) + pro_usage.get('output_tokens', 0) + pro_usage.get('thinking_tokens', 0)
        },
        'flash_cost': flash_usage.get('total_cost_usd', 0),
        'pro_cost': pro_usage.get('total_cost_usd', 0),
        'cost_difference': pro_usage.get('total_cost_usd', 0) - flash_usage.get('total_cost_usd', 0),
        'cost_ratio': pro_usage.get('total_cost_usd', 0) / max(flash_usage.get('total_cost_usd', 1), 0.0001)
    }
    
    return analysis

def analyze_processing_time(flash_data: dict, pro_data: dict) -> dict:
    """Compare processing times between models"""
    flash_time = flash_data.get('_usage_metadata', {}).get('processing_time_seconds', 0)
    pro_time = pro_data.get('_usage_metadata', {}).get('processing_time_seconds', 0)
    
    analysis = {
        'flash_time_seconds': flash_time,
        'pro_time_seconds': pro_time,
        'time_difference': pro_time - flash_time,
        'pro_slower_by_factor': pro_time / max(flash_time, 0.1)
    }
    
    return analysis

def generate_comparison_report(paper_id: str, flash_data: dict, pro_data: dict) -> dict:
    """Generate comprehensive comparison report"""
    
    report = {
        'paper_id': paper_id,
        'timestamp': datetime.now().isoformat(),
        'comparison_type': 'flash_vs_pro',
        'metadata_analysis': analyze_metadata_differences(flash_data, pro_data),
        'key_findings_analysis': analyze_key_findings(flash_data, pro_data),
        'token_usage_analysis': analyze_token_usage(flash_data, pro_data),
        'processing_time_analysis': analyze_processing_time(flash_data, pro_data),
        'summary': {}
    }
    
    # Generate summary insights
    meta_analysis = report['metadata_analysis']
    findings_analysis = report['key_findings_analysis']
    token_analysis = report['token_usage_analysis']
    time_analysis = report['processing_time_analysis']
    
    report['summary'] = {
        'pro_advantages': [],
        'flash_advantages': [],
        'key_differences': [],
        'cost_efficiency': {
            'flash_cost': token_analysis['flash_cost'],
            'pro_cost': token_analysis['pro_cost'],
            'pro_cost_multiple': token_analysis['cost_ratio']
        },
        'performance_tradeoffs': {
            'pro_slower_by': f"{time_analysis['pro_slower_by_factor']:.1f}x",
            'pro_more_expensive_by': f"{token_analysis['cost_ratio']:.1f}x"
        }
    }
    
    # Determine advantages
    if len(meta_analysis['fields_only_in_pro']) > len(meta_analysis['fields_only_in_flash']):
        report['summary']['pro_advantages'].append("More metadata fields extracted")
    
    if findings_analysis['pro_count'] > findings_analysis['flash_count']:
        report['summary']['pro_advantages'].append(f"More key findings identified ({findings_analysis['pro_count']} vs {findings_analysis['flash_count']})")
    
    if token_analysis['flash_cost'] < token_analysis['pro_cost']:
        report['summary']['flash_advantages'].append("Lower cost per processing")
    
    if time_analysis['flash_time_seconds'] < time_analysis['pro_time_seconds']:
        report['summary']['flash_advantages'].append("Faster processing time")
    
    return report

def print_comparison_summary(report: dict):
    """Print a human-readable summary of the comparison"""
    
    print(f"\n{'='*80}")
    print(f"FLASH VS PRO COMPARISON: {report['paper_id']}")
    print(f"{'='*80}")
    
    # Cost Analysis
    cost_analysis = report['summary']['cost_efficiency']
    print(f"\n💰 COST ANALYSIS:")
    print(f"   Flash: ${cost_analysis['flash_cost']:.4f}")
    print(f"   Pro:   ${cost_analysis['pro_cost']:.4f}")
    print(f"   Pro is {cost_analysis['pro_cost_multiple']:.1f}x more expensive")
    
    # Performance Analysis
    perf_analysis = report['summary']['performance_tradeoffs']
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    print(f"   Pro is {perf_analysis['pro_slower_by']} slower")
    print(f"   Pro is {perf_analysis['pro_more_expensive_by']} more expensive")
    
    # Quality Analysis
    findings = report['key_findings_analysis']
    print(f"\n🔍 EXTRACTION QUALITY:")
    print(f"   Flash found {findings['flash_count']} key findings")
    print(f"   Pro found {findings['pro_count']} key findings")
    if findings['pro_count'] > findings['flash_count']:
        print(f"   ✅ Pro found {findings['summary']['difference']} more findings")
    elif findings['flash_count'] > findings['pro_count']:
        print(f"   ⚠️  Flash found {-findings['summary']['difference']} more findings")
    else:
        print(f"   ➡️  Both found same number of findings")
    
    # Metadata Analysis
    meta = report['metadata_analysis']
    print(f"\n📋 METADATA EXTRACTION:")
    print(f"   Fields only in Flash: {len(meta['fields_only_in_flash'])}")
    print(f"   Fields only in Pro: {len(meta['fields_only_in_pro'])}")
    print(f"   Fields with different values: {len(meta['fields_different'])}")
    print(f"   Fields with same values: {len(meta['fields_same'])}")
    
    # Pro Advantages
    if report['summary']['pro_advantages']:
        print(f"\n✅ PRO ADVANTAGES:")
        for advantage in report['summary']['pro_advantages']:
            print(f"   • {advantage}")
    
    # Flash Advantages
    if report['summary']['flash_advantages']:
        print(f"\n⚡ FLASH ADVANTAGES:")
        for advantage in report['summary']['flash_advantages']:
            print(f"   • {advantage}")
    
    # Key Differences
    if meta['fields_different']:
        print(f"\n🔄 KEY DIFFERENCES IN EXTRACTION:")
        for diff in meta['fields_different'][:5]:  # Show first 5 differences
            print(f"   • {diff['field']}:")
            print(f"     Flash: {str(diff['flash_value'])[:60]}...")
            print(f"     Pro:   {str(diff['pro_value'])[:60]}...")

def main():
    parser = argparse.ArgumentParser(description="Compare Flash vs Pro model results")
    parser.add_argument("paper_id", help="Paper ID to compare (without file extension)")
    parser.add_argument("--results-dir", default="8_stage_outputs", help="Directory containing results")
    parser.add_argument("--save-report", action="store_true", help="Save detailed comparison report")
    parser.add_argument("--verbose", action="store_true", help="Show detailed analysis")
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading results for paper: {args.paper_id}")
    results = load_results(args.paper_id, args.results_dir)
    
    if not results['flash'] or not results['pro']:
        print("❌ Cannot compare - missing Flash or Pro results")
        print("   Run both test_stage_1a.py and test_stage_1a_pro.py first")
        sys.exit(1)
    
    print(f"✅ Loaded Flash results from: {results['flash_file']}")
    print(f"✅ Loaded Pro results from: {results['pro_file']}")
    
    # Generate comparison report
    print("\n🔄 Analyzing differences...")
    report = generate_comparison_report(args.paper_id, results['flash'], results['pro'])
    
    # Print summary
    print_comparison_summary(report)
    
    # Save detailed report if requested
    if args.save_report:
        report_path = f"comparison_report_{args.paper_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Show verbose details if requested
    if args.verbose:
        print(f"\n{'='*80}")
        print("DETAILED ANALYSIS")
        print(f"{'='*80}")
        
        print("\n📋 METADATA FIELDS ONLY IN PRO:")
        for field in report['metadata_analysis']['fields_only_in_pro']:
            print(f"   • {field['field']}: {field['value']}")
        
        print("\n📋 METADATA FIELDS ONLY IN FLASH:")
        for field in report['metadata_analysis']['fields_only_in_flash']:
            print(f"   • {field['field']}: {field['value']}")
        
        print("\n🔍 PRO KEY FINDINGS:")
        for i, finding in enumerate(report['key_findings_analysis']['pro_findings'], 1):
            print(f"   {i}. {finding}")
        
        print("\n🔍 FLASH KEY FINDINGS:")
        for i, finding in enumerate(report['key_findings_analysis']['flash_findings'], 1):
            print(f"   {i}. {finding}")

if __name__ == "__main__":
    main()