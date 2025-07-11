#!/usr/bin/env python3
"""
Comprehensive Stage 3A vs Stage 3B Enhancement Value Analysis
Analyzes the value proposition of Stage 3B's enhancements compared to Stage 3A output
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re

def load_stage_result(stage_id: str, paper_id: str) -> Dict[str, Any]:
    """Load stage result from 8_stage_outputs directory"""
    
    # Look for the most recent output file for this stage/paper
    stage_dir = Path("8_stage_outputs") / f"stage_{stage_id}"
    
    if not stage_dir.exists():
        raise FileNotFoundError(f"Stage {stage_id} output directory not found")
    
    # Find files matching the paper pattern
    matching_files = []
    for file_path in stage_dir.glob("*.json"):
        if paper_id in file_path.name and f"_{stage_id}_" in file_path.name:
            matching_files.append(file_path)
    
    if not matching_files:
        raise FileNotFoundError(f"No {stage_id} output found for paper: {paper_id}")
    
    # Get the most recent file
    latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_synthesis_content(stage_result: Dict[str, Any]) -> str:
    """Extract the main synthesis content from a stage result"""
    
    if 'results' in stage_result:
        results = stage_result['results']
        
        # For Stage 3A, extract the main synthesis content
        if 'integrated_soil_k_findings' in results:
            return json.dumps(results, indent=2)
        
        # For Stage 3B, extract the enhanced synthesis
        if 'enhanced_synthesis' in results:
            return json.dumps(results['enhanced_synthesis'], indent=2)
    
    return json.dumps(stage_result, indent=2)

def analyze_content_metrics(content: str) -> Dict[str, Any]:
    """Analyze basic content metrics"""
    
    return {
        'character_count': len(content),
        'word_count': len(content.split()),
        'line_count': content.count('\n'),
        'json_objects': content.count('{'),
        'json_arrays': content.count('['),
        'numeric_values': len(re.findall(r'\d+\.?\d*', content)),
        'scientific_terms': len(re.findall(r'\b(?:potassium|K|soil|fertilization|depletion|balance|exchangeable|bioavailable|sustainability|temporal|spatial|agricultural|methodological)\b', content, re.IGNORECASE)),
        'quantitative_references': len(re.findall(r'\d+(?:\.\d+)?\s*(?:mg|kg|ha|years?|%)', content))
    }

def identify_enhancement_categories(stage_3a_content: str, stage_3b_content: str) -> List[Dict[str, Any]]:
    """Identify specific enhancement categories added in Stage 3B"""
    
    enhancements = []
    
    # Check for cross-track integration enhancements
    if 'cross-track' in stage_3b_content.lower() and 'cross-track' not in stage_3a_content.lower():
        enhancements.append({
            'type': 'cross_track_integration',
            'description': 'Added cross-track integration between generic and soil K findings',
            'value': 'high'
        })
    
    # Check for enhanced quantitative characterization
    stage_3a_numbers = len(re.findall(r'\d+(?:\.\d+)?\s*(?:mg|kg|ha|years?|%)', stage_3a_content))
    stage_3b_numbers = len(re.findall(r'\d+(?:\.\d+)?\s*(?:mg|kg|ha|years?|%)', stage_3b_content))
    
    if stage_3b_numbers > stage_3a_numbers:
        enhancements.append({
            'type': 'quantitative_enhancement',
            'description': f'Added {stage_3b_numbers - stage_3a_numbers} additional quantitative references',
            'value': 'medium'
        })
    
    # Check for enhanced process understanding
    if 'mechanistic_insights' in stage_3b_content and len(re.findall(r'mechanistic_insights.*?(?=})', stage_3b_content)) > len(re.findall(r'mechanistic_insights.*?(?=})', stage_3a_content)):
        enhancements.append({
            'type': 'mechanistic_enhancement',
            'description': 'Enhanced mechanistic understanding and process insights',
            'value': 'high'
        })
    
    # Check for enhanced uncertainty characterization
    if stage_3b_content.lower().count('uncertainty') > stage_3a_content.lower().count('uncertainty'):
        enhancements.append({
            'type': 'uncertainty_enhancement',
            'description': 'Enhanced uncertainty characterization and propagation',
            'value': 'high'
        })
    
    # Check for enhanced temporal dynamics
    if stage_3b_content.lower().count('temporal') > stage_3a_content.lower().count('temporal'):
        enhancements.append({
            'type': 'temporal_enhancement',
            'description': 'Enhanced temporal dynamics analysis',
            'value': 'medium'
        })
    
    # Check for enhanced spatial patterns
    if stage_3b_content.lower().count('spatial') > stage_3a_content.lower().count('spatial'):
        enhancements.append({
            'type': 'spatial_enhancement',
            'description': 'Enhanced spatial pattern analysis',
            'value': 'medium'
        })
    
    return enhancements

def calculate_cost_effectiveness(stage_3a_cost: float, stage_3b_cost: float, content_increase: float, enhancement_count: int) -> Dict[str, Any]:
    """Calculate cost-effectiveness metrics"""
    
    validation_cost = stage_3b_cost - stage_3a_cost
    
    return {
        'validation_cost_usd': round(validation_cost, 4),
        'cost_per_percent_increase': round(validation_cost / content_increase if content_increase > 0 else 0, 4),
        'cost_per_enhancement': round(validation_cost / enhancement_count if enhancement_count > 0 else 0, 4),
        'content_increase_per_dollar': round(content_increase / validation_cost if validation_cost > 0 else 0, 2),
        'enhancement_value_ratio': round(enhancement_count / validation_cost if validation_cost > 0 else 0, 2)
    }

def generate_enhancement_quality_assessment(enhancements: List[Dict[str, Any]], content_metrics_3a: Dict[str, Any], content_metrics_3b: Dict[str, Any]) -> Dict[str, Any]:
    """Generate qualitative assessment of enhancement quality"""
    
    high_value_enhancements = len([e for e in enhancements if e['value'] == 'high'])
    medium_value_enhancements = len([e for e in enhancements if e['value'] == 'medium'])
    
    scientific_term_increase = content_metrics_3b['scientific_terms'] - content_metrics_3a['scientific_terms']
    quantitative_increase = content_metrics_3b['quantitative_references'] - content_metrics_3a['quantitative_references']
    
    quality_score = (high_value_enhancements * 3 + medium_value_enhancements * 2 + 
                    min(scientific_term_increase / 10, 2) + min(quantitative_increase / 5, 2)) / 10
    
    return {
        'quality_score': round(quality_score, 2),
        'high_value_enhancements': high_value_enhancements,
        'medium_value_enhancements': medium_value_enhancements,
        'scientific_term_increase': scientific_term_increase,
        'quantitative_reference_increase': quantitative_increase,
        'overall_assessment': 'excellent' if quality_score >= 0.8 else 'good' if quality_score >= 0.6 else 'adequate' if quality_score >= 0.4 else 'poor'
    }

def main():
    """Main analysis function"""
    
    paper_id = "Balance of potassium in two long-term field experiments with different fertilization treatments"
    
    try:
        # Load stage results
        print("Loading Stage 3A and 3B results...")
        stage_3a_result = load_stage_result('3a', paper_id)
        stage_3b_result = load_stage_result('3b', paper_id)
        
        # Extract synthesis content
        stage_3a_content = extract_synthesis_content(stage_3a_result)
        stage_3b_content = extract_synthesis_content(stage_3b_result)
        
        # Analyze content metrics
        print("Analyzing content metrics...")
        metrics_3a = analyze_content_metrics(stage_3a_content)
        metrics_3b = analyze_content_metrics(stage_3b_content)
        
        # Calculate content increase
        content_increase_percent = ((metrics_3b['character_count'] - metrics_3a['character_count']) / metrics_3a['character_count']) * 100
        
        # Identify enhancements
        print("Identifying enhancement categories...")
        enhancements = identify_enhancement_categories(stage_3a_content, stage_3b_content)
        
        # Calculate cost effectiveness
        stage_3a_cost = stage_3a_result.get('estimated_cost_usd', 0)
        stage_3b_cost = stage_3b_result.get('estimated_cost_usd', 0)
        
        cost_effectiveness = calculate_cost_effectiveness(
            stage_3a_cost, stage_3b_cost, content_increase_percent, len(enhancements)
        )
        
        # Generate quality assessment
        quality_assessment = generate_enhancement_quality_assessment(enhancements, metrics_3a, metrics_3b)
        
        # Compile comprehensive analysis
        analysis_result = {
            'paper_id': paper_id,
            'analysis_timestamp': '2025-07-09T05:30:00Z',
            'content_comparison': {
                'stage_3a_metrics': metrics_3a,
                'stage_3b_metrics': metrics_3b,
                'content_increase_percent': round(content_increase_percent, 2),
                'word_count_increase': metrics_3b['word_count'] - metrics_3a['word_count'],
                'line_count_increase': metrics_3b['line_count'] - metrics_3a['line_count']
            },
            'enhancement_analysis': {
                'total_enhancements': len(enhancements),
                'enhancement_categories': enhancements,
                'quality_assessment': quality_assessment
            },
            'cost_analysis': {
                'stage_3a_cost_usd': stage_3a_cost,
                'stage_3b_cost_usd': stage_3b_cost,
                'cost_effectiveness': cost_effectiveness
            },
            'token_usage_comparison': {
                'stage_3a_tokens': stage_3a_result.get('token_usage', {}),
                'stage_3b_tokens': stage_3b_result.get('token_usage', {}),
                'input_token_increase': stage_3b_result.get('token_usage', {}).get('input', 0) - stage_3a_result.get('token_usage', {}).get('input', 0),
                'output_token_increase': stage_3b_result.get('token_usage', {}).get('output', 0) - stage_3a_result.get('token_usage', {}).get('output', 0)
            },
            'value_proposition': {
                'enhancement_justification': f"Stage 3B produces {content_increase_percent:.1f}% more content with {len(enhancements)} specific enhancements, including {quality_assessment['high_value_enhancements']} high-value improvements for ${cost_effectiveness['validation_cost_usd']:.4f} additional cost.",
                'cost_per_enhancement': f"${cost_effectiveness['cost_per_enhancement']:.4f} per enhancement",
                'recommendation': 'justified' if quality_assessment['quality_score'] >= 0.6 and cost_effectiveness['cost_per_enhancement'] <= 0.02 else 'conditional' if quality_assessment['quality_score'] >= 0.4 else 'not_recommended'
            }
        }
        
        # Display results
        print("\n" + "="*80)
        print("COMPREHENSIVE STAGE 3A vs STAGE 3B ENHANCEMENT VALUE ANALYSIS")
        print("="*80)
        
        print(f"\n📊 CONTENT COMPARISON:")
        print(f"   Stage 3A: {metrics_3a['character_count']:,} characters, {metrics_3a['word_count']:,} words")
        print(f"   Stage 3B: {metrics_3b['character_count']:,} characters, {metrics_3b['word_count']:,} words")
        print(f"   Increase: {content_increase_percent:.1f}% content increase")
        
        print(f"\n🔧 ENHANCEMENT ANALYSIS:")
        print(f"   Total enhancements: {len(enhancements)}")
        print(f"   High-value enhancements: {quality_assessment['high_value_enhancements']}")
        print(f"   Medium-value enhancements: {quality_assessment['medium_value_enhancements']}")
        print(f"   Quality score: {quality_assessment['quality_score']}/1.0 ({quality_assessment['overall_assessment']})")
        
        print(f"\n💰 COST ANALYSIS:")
        print(f"   Stage 3A cost: ${stage_3a_cost:.4f}")
        print(f"   Stage 3B cost: ${stage_3b_cost:.4f}")
        print(f"   Validation cost: ${cost_effectiveness['validation_cost_usd']:.4f}")
        print(f"   Cost per enhancement: ${cost_effectiveness['cost_per_enhancement']:.4f}")
        
        print(f"\n📈 TOKEN USAGE:")
        print(f"   Input token increase: {analysis_result['token_usage_comparison']['input_token_increase']:,}")
        print(f"   Output token increase: {analysis_result['token_usage_comparison']['output_token_increase']:,}")
        
        print(f"\n✅ VALUE PROPOSITION:")
        print(f"   {analysis_result['value_proposition']['enhancement_justification']}")
        print(f"   Recommendation: {analysis_result['value_proposition']['recommendation'].upper()}")
        
        print(f"\n📋 SPECIFIC ENHANCEMENTS:")
        for i, enhancement in enumerate(enhancements, 1):
            print(f"   {i}. {enhancement['description']} (Value: {enhancement['value']})")
        
        # Save detailed analysis
        output_file = "stage_3_enhancement_value_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Detailed analysis saved to: {output_file}")
        print("="*80)
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None

if __name__ == "__main__":
    result = main()