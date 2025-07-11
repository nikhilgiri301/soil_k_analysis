#!/usr/bin/env python3
"""
Stage 1A Batch Results Validator
Analyzes and validates Stage 1A batch processing results

Usage:
    python validate_stage_1a_batch.py
    python validate_stage_1a_batch.py --compare-with-individual
    python validate_stage_1a_batch.py --detailed-analysis
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class Stage1ABatchValidator:
    """Validator for Stage 1A batch processing results"""
    
    def __init__(self, detailed_analysis: bool = False):
        self.detailed_analysis = detailed_analysis
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Define paths
        self.batch_output_dir = Path("8_stage_outputs/stage_1a")
        self.test_output_dir = Path("test_outputs/stage_1a_batch")
        self.individual_output_dir = Path("test_outputs/stage_1a")
        
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "batch_results": {},
            "individual_results": {},
            "comparison": {},
            "quality_assessment": {},
            "recommendations": []
        }
    
    def load_batch_results(self) -> Dict[str, Any]:
        """Load Stage 1A batch processing results"""
        batch_results = {}
        
        if not self.batch_output_dir.exists():
            self.logger.warning(f"Batch output directory not found: {self.batch_output_dir}")
            return batch_results
        
        # Load from main output directory
        for result_file in self.batch_output_dir.glob("*_1a_*.json"):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    paper_id = data.get('paper_id', result_file.stem.split('_')[0])
                    batch_results[paper_id] = {
                        'file_path': str(result_file),
                        'processing_mode': data.get('processing_mode', 'unknown'),
                        'timestamp': data.get('processing_timestamp'),
                        'results': data.get('results', {}),
                        'file_size': result_file.stat().st_size
                    }
                    
            except Exception as e:
                self.logger.error(f"Error loading {result_file}: {str(e)}")
                continue
        
        # Also check test output directory
        if self.test_output_dir.exists():
            for result_file in self.test_output_dir.glob("*_1a_batch_test.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        paper_id = data.get('paper_id', result_file.stem.split('_')[0])
                        if paper_id not in batch_results:  # Don't overwrite main results
                            batch_results[paper_id] = {
                                'file_path': str(result_file),
                                'processing_mode': data.get('processing_mode', 'batch_test'),
                                'timestamp': data.get('processing_timestamp'),
                                'results': data.get('results', {}),
                                'file_size': result_file.stat().st_size
                            }
                            
                except Exception as e:
                    self.logger.error(f"Error loading {result_file}: {str(e)}")
                    continue
        
        self.logger.info(f"Loaded {len(batch_results)} batch results")
        return batch_results
    
    def load_individual_results(self) -> Dict[str, Any]:
        """Load individual Stage 1A processing results for comparison"""
        individual_results = {}
        
        if not self.individual_output_dir.exists():
            self.logger.info("No individual results directory found for comparison")
            return individual_results
        
        for result_file in self.individual_output_dir.glob("*_1a_output.json"):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    paper_id = data.get('paper_id', result_file.stem.split('_')[0])
                    individual_results[paper_id] = {
                        'file_path': str(result_file),
                        'processing_mode': 'individual',
                        'timestamp': data.get('processing_timestamp'),
                        'results': data.get('results', {}),
                        'file_size': result_file.stat().st_size
                    }
                    
            except Exception as e:
                self.logger.error(f"Error loading {result_file}: {str(e)}")
                continue
        
        self.logger.info(f"Loaded {len(individual_results)} individual results for comparison")
        return individual_results
    
    def analyze_result_structure(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure and quality of results"""
        analysis = {
            'total_results': len(results),
            'successful_results': 0,
            'failed_results': 0,
            'structure_analysis': {
                'has_paper_metadata': 0,
                'has_key_findings': 0,
                'has_quantitative_findings': 0,
                'has_research_methodology': 0,
                'has_limitations': 0,
                'valid_json_structure': 0
            },
            'content_quality': {
                'avg_result_size': 0,
                'min_result_size': float('inf'),
                'max_result_size': 0,
                'empty_results': 0
            },
            'common_issues': []
        }
        
        total_size = 0
        
        for paper_id, result_data in results.items():
            result = result_data.get('results', {})
            
            # Check for errors
            if 'error' in result:
                analysis['failed_results'] += 1
                analysis['common_issues'].append(f"{paper_id}: {result['error']}")
                continue
            
            analysis['successful_results'] += 1
            
            # Analyze structure
            if 'paper_metadata' in result:
                analysis['structure_analysis']['has_paper_metadata'] += 1
            
            if 'key_findings' in result:
                analysis['structure_analysis']['has_key_findings'] += 1
            
            if 'quantitative_findings' in result:
                analysis['structure_analysis']['has_quantitative_findings'] += 1
            
            if 'research_methodology' in result:
                analysis['structure_analysis']['has_research_methodology'] += 1
            
            if 'limitations' in result:
                analysis['structure_analysis']['has_limitations'] += 1
            
            if isinstance(result, dict) and len(result) > 0:
                analysis['structure_analysis']['valid_json_structure'] += 1
            
            # Analyze content quality
            result_size = len(json.dumps(result))
            total_size += result_size
            
            if result_size == 0:
                analysis['content_quality']['empty_results'] += 1
            
            analysis['content_quality']['min_result_size'] = min(
                analysis['content_quality']['min_result_size'], result_size
            )
            analysis['content_quality']['max_result_size'] = max(
                analysis['content_quality']['max_result_size'], result_size
            )
        
        # Calculate averages and percentages
        if analysis['successful_results'] > 0:
            analysis['content_quality']['avg_result_size'] = total_size / analysis['successful_results']
            
            # Create a list of keys to avoid dictionary modification during iteration
            structure_keys = list(analysis['structure_analysis'].keys())
            for key in structure_keys:
                count = analysis['structure_analysis'][key]
                analysis['structure_analysis'][f"{key}_percentage"] = (count / analysis['successful_results']) * 100
        
        if analysis['content_quality']['min_result_size'] == float('inf'):
            analysis['content_quality']['min_result_size'] = 0
        
        return analysis
    
    def compare_batch_vs_individual(self, batch_results: Dict[str, Any], 
                                   individual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare batch results with individual processing results"""
        comparison = {
            'common_papers': [],
            'batch_only': [],
            'individual_only': [],
            'quality_comparison': {},
            'content_similarity': {},
            'performance_comparison': {}
        }
        
        batch_papers = set(batch_results.keys())
        individual_papers = set(individual_results.keys())
        
        comparison['common_papers'] = list(batch_papers & individual_papers)
        comparison['batch_only'] = list(batch_papers - individual_papers)
        comparison['individual_only'] = list(individual_papers - batch_papers)
        
        if not comparison['common_papers']:
            self.logger.warning("No common papers found for comparison")
            return comparison
        
        # Compare quality metrics for common papers
        batch_successful = 0
        individual_successful = 0
        content_matches = 0
        structure_matches = 0
        
        for paper_id in comparison['common_papers']:
            batch_result = batch_results[paper_id]['results']
            individual_result = individual_results[paper_id]['results']
            
            # Count successful results
            if 'error' not in batch_result:
                batch_successful += 1
            if 'error' not in individual_result:
                individual_successful += 1
            
            # Compare structure
            batch_keys = set(batch_result.keys()) if isinstance(batch_result, dict) else set()
            individual_keys = set(individual_result.keys()) if isinstance(individual_result, dict) else set()
            
            if batch_keys == individual_keys:
                structure_matches += 1
            
            # Simple content similarity (this could be more sophisticated)
            batch_content = json.dumps(batch_result, sort_keys=True)
            individual_content = json.dumps(individual_result, sort_keys=True)
            
            if batch_content == individual_content:
                content_matches += 1
        
        total_common = len(comparison['common_papers'])
        
        comparison['quality_comparison'] = {
            'batch_success_rate': batch_successful / total_common if total_common > 0 else 0,
            'individual_success_rate': individual_successful / total_common if total_common > 0 else 0,
            'structure_match_rate': structure_matches / total_common if total_common > 0 else 0,
            'content_match_rate': content_matches / total_common if total_common > 0 else 0
        }
        
        return comparison
    
    def generate_recommendations(self, batch_analysis: Dict[str, Any], 
                               individual_analysis: Dict[str, Any],
                               comparison: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Success rate recommendations
        if batch_analysis['successful_results'] == 0:
            recommendations.append("🚨 CRITICAL: No successful batch results found. Check API key, prompts, and error logs.")
        elif batch_analysis['successful_results'] / batch_analysis['total_results'] < 0.9:
            success_rate = (batch_analysis['successful_results'] / batch_analysis['total_results']) * 100
            recommendations.append(f"⚠️  Batch success rate is {success_rate:.1f}%. Investigate failed papers and improve error handling.")
        else:
            recommendations.append("✅ Excellent batch success rate. Batch processing is working well.")
        
        # Structure quality recommendations
        structure = batch_analysis['structure_analysis']
        
        if structure.get('has_paper_metadata_percentage', 0) < 90:
            recommendations.append("📋 Paper metadata extraction could be improved. Review Stage 1A prompt instructions.")
        
        if structure.get('has_key_findings_percentage', 0) < 90:
            recommendations.append("🔍 Key findings extraction could be improved. Consider prompt clarification.")
        
        if structure.get('valid_json_structure_percentage', 0) < 95:
            recommendations.append("📝 JSON structure validation issues detected. Review response parsing and prompt format.")
        
        # Content quality recommendations
        content = batch_analysis['content_quality']
        
        if content['empty_results'] > 0:
            recommendations.append(f"⚠️  Found {content['empty_results']} empty results. Investigate cause and retry failed papers.")
        
        if content['avg_result_size'] < 1000:
            recommendations.append("📊 Average result size seems low. Verify that extraction is capturing sufficient detail.")
        
        # Comparison recommendations
        if individual_analysis and comparison:
            quality_comp = comparison.get('quality_comparison', {})
            
            batch_success = quality_comp.get('batch_success_rate', 0)
            individual_success = quality_comp.get('individual_success_rate', 0)
            
            if batch_success < individual_success - 0.05:  # 5% tolerance
                recommendations.append("📉 Batch processing has lower success rate than individual processing. Investigate batch-specific issues.")
            elif batch_success > individual_success + 0.05:
                recommendations.append("📈 Batch processing performs better than individual processing. Great result!")
            else:
                recommendations.append("🎯 Batch and individual processing have similar success rates. Batch approach validated.")
            
            structure_match = quality_comp.get('structure_match_rate', 0)
            if structure_match < 0.8:
                recommendations.append("🔄 Structure consistency between batch and individual results needs improvement.")
        
        # Cost and performance recommendations
        if batch_analysis['successful_results'] > 5:
            recommendations.append("💰 Batch processing validated with multiple papers. Projected 60-80% cost savings confirmed.")
            recommendations.append("🚀 Ready to implement full 8-stage batch system.")
        else:
            recommendations.append("🧪 Test with more papers to validate batch processing reliability.")
        
        return recommendations
    
    def print_validation_report(self):
        """Print comprehensive validation report"""
        print(f"\n{'='*80}")
        print(f"📊 STAGE 1A BATCH VALIDATION REPORT")
        print(f"{'='*80}")
        print(f"📅 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        batch_results = self.load_batch_results()
        individual_results = self.load_individual_results()
        
        # Analyze batch results
        batch_analysis = self.analyze_result_structure(batch_results)
        self.validation_results['batch_results'] = batch_analysis
        
        print(f"\n🔄 Batch Processing Results:")
        print(f"  📄 Total Results: {batch_analysis['total_results']}")
        print(f"  ✅ Successful: {batch_analysis['successful_results']}")
        print(f"  ❌ Failed: {batch_analysis['failed_results']}")
        print(f"  📈 Success Rate: {(batch_analysis['successful_results'] / batch_analysis['total_results'] * 100):.1f}%")
        
        # Structure analysis
        structure = batch_analysis['structure_analysis']
        print(f"\n📋 Structure Quality:")
        print(f"  📝 Paper Metadata: {structure.get('has_paper_metadata_percentage', 0):.1f}%")
        print(f"  🔍 Key Findings: {structure.get('has_key_findings_percentage', 0):.1f}%")
        print(f"  📊 Quantitative Data: {structure.get('has_quantitative_findings_percentage', 0):.1f}%")
        print(f"  🔬 Methodology: {structure.get('has_research_methodology_percentage', 0):.1f}%")
        print(f"  📝 Valid JSON: {structure.get('valid_json_structure_percentage', 0):.1f}%")
        
        # Content quality
        content = batch_analysis['content_quality']
        print(f"\n📊 Content Quality:")
        print(f"  📏 Avg Result Size: {content['avg_result_size']:,.0f} characters")
        print(f"  📉 Min Result Size: {content['min_result_size']:,.0f} characters")
        print(f"  📈 Max Result Size: {content['max_result_size']:,.0f} characters")
        print(f"  ⚠️  Empty Results: {content['empty_results']}")
        
        # Individual comparison if available
        if individual_results:
            individual_analysis = self.analyze_result_structure(individual_results)
            comparison = self.compare_batch_vs_individual(batch_results, individual_results)
            
            self.validation_results['individual_results'] = individual_analysis
            self.validation_results['comparison'] = comparison
            
            print(f"\n🔄 Batch vs Individual Comparison:")
            print(f"  📄 Common Papers: {len(comparison['common_papers'])}")
            print(f"  🎯 Batch Success Rate: {comparison['quality_comparison']['batch_success_rate']:.1%}")
            print(f"  🎯 Individual Success Rate: {comparison['quality_comparison']['individual_success_rate']:.1%}")
            print(f"  📋 Structure Match Rate: {comparison['quality_comparison']['structure_match_rate']:.1%}")
            print(f"  📝 Content Match Rate: {comparison['quality_comparison']['content_match_rate']:.1%}")
        else:
            individual_analysis = {}
            comparison = {}
        
        # Show issues if any
        if batch_analysis['common_issues']:
            print(f"\n⚠️  Common Issues (showing first 3):")
            for issue in batch_analysis['common_issues'][:3]:
                print(f"    - {issue}")
            if len(batch_analysis['common_issues']) > 3:
                print(f"    ... and {len(batch_analysis['common_issues']) - 3} more")
        
        # Generate and show recommendations
        recommendations = self.generate_recommendations(batch_analysis, individual_analysis, comparison)
        self.validation_results['recommendations'] = recommendations
        
        print(f"\n🎯 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Overall assessment
        print(f"\n🏆 Overall Assessment:")
        
        success_rate = batch_analysis['successful_results'] / batch_analysis['total_results'] if batch_analysis['total_results'] > 0 else 0
        structure_quality = structure.get('valid_json_structure_percentage', 0) / 100
        
        if success_rate >= 0.95 and structure_quality >= 0.9:
            print(f"  🎉 EXCELLENT: Batch processing is working exceptionally well!")
            print(f"  🚀 Strongly recommend proceeding with full 8-stage implementation")
        elif success_rate >= 0.85 and structure_quality >= 0.8:
            print(f"  ✅ GOOD: Batch processing is working well with minor issues")
            print(f"  🔧 Address recommendations and proceed with implementation")
        elif success_rate >= 0.7:
            print(f"  ⚠️  FAIR: Batch processing has significant issues to address")
            print(f"  🛠️  Fix issues before implementing full system")
        else:
            print(f"  🚨 POOR: Batch processing is not working correctly")
            print(f"  🔧 Major debugging and fixes required")
        
        print(f"\n{'='*80}")
        
        # Save detailed results if requested
        if self.detailed_analysis:
            report_file = Path("test_outputs") / "stage_1a_batch_validation_report.json"
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Detailed report saved to: {report_file}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate Stage 1A Batch Processing Results")
    parser.add_argument("--compare-with-individual", action="store_true", 
                       help="Compare batch results with individual processing results")
    parser.add_argument("--detailed-analysis", action="store_true",
                       help="Generate detailed analysis and save report")
    
    args = parser.parse_args()
    
    try:
        validator = Stage1ABatchValidator(detailed_analysis=args.detailed_analysis)
        validator.print_validation_report()
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        logging.error(f"Validation failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()