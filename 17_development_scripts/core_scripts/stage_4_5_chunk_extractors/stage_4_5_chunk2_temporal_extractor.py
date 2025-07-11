#!/usr/bin/env python3
"""
Stage 4.5 Chunk 2: Temporal Soil K Supply Evidence Extractor
Extracts all temporal/time-based evidence from Stage 4B outputs

This script processes all 25 Stage 4B files and combines temporal evidence into a single file.
Focuses on: annual rates, seasonal patterns, long-term trends, sustainability timelines.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stage_4_5_chunk2_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TemporalEvidenceExtractor:
    """
    Extracts temporal/time-based soil K evidence from Stage 4B outputs
    
    Target: All evidence related to time horizons, seasonal patterns, 
    annual rates, depletion timelines, and sustainability periods
    """
    
    def __init__(self, 
                 stage_4b_dir: str = "8_stage_outputs/stage_4b/approved_results",
                 output_dir: str = "8_stage_outputs/stage_4_5_chunks"):
        """Initialize the temporal evidence extractor"""
        self.stage_4b_dir = Path(stage_4b_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track extraction statistics
        self.stats = {
            'papers_processed': 0,
            'papers_with_temporal_evidence': 0,
            'total_evidence_pieces': 0,
            'evidence_by_timeframe': {},
            'parameters_extracted': set(),
            'extraction_errors': []
        }
        
        # Combined output structure
        self.combined_output = {
            'chunk_metadata': {
                'chunk_id': 'temporal_soil_k_supply',
                'chunk_description': 'All temporal/time-based soil K evidence from 25 papers',
                'extraction_timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'papers_processed': []
            },
            'evidence_by_paper': {}
        }
    
    def process_all_papers(self) -> Dict[str, Any]:
        """Main processing method - extracts temporal evidence from all papers"""
        logger.info("="*80)
        logger.info("Starting Temporal Soil K Supply Evidence Extraction")
        logger.info("="*80)
        
        # Get all Stage 4B files
        stage_4b_files = list(self.stage_4b_dir.glob("*_4b_*.json"))
        logger.info(f"Found {len(stage_4b_files)} Stage 4B files to process")
        
        # Process each file
        for idx, file_path in enumerate(stage_4b_files, 1):
            logger.info(f"\nProcessing [{idx}/{len(stage_4b_files)}]: {file_path.name}")
            
            try:
                # Extract paper name from filename
                paper_name = file_path.name.split('_4b_')[0]
                
                # Load and process the file
                paper_data = self._load_stage_4b_file(file_path)
                if paper_data:
                    evidence = self._extract_temporal_evidence(paper_data, paper_name)
                    
                    if evidence['evidence_pieces']:
                        self.combined_output['evidence_by_paper'][paper_name] = evidence
                        self.stats['papers_with_temporal_evidence'] += 1
                        logger.info(f"  ✓ Extracted {len(evidence['evidence_pieces'])} evidence pieces")
                    else:
                        logger.warning(f"  ⚠ No temporal evidence found")
                    
                    self.stats['papers_processed'] += 1
                    self.combined_output['chunk_metadata']['papers_processed'].append(paper_name)
                    
            except Exception as e:
                error_msg = f"Failed to process {file_path.name}: {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                logger.error(traceback.format_exc())
                self.stats['extraction_errors'].append(error_msg)
        
        # Save combined output
        self._save_combined_output()
        
        # Generate and save report
        report = self._generate_extraction_report()
        self._save_report(report)
        
        return report
    
    def _load_stage_4b_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and validate Stage 4B JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if 'results' not in data:
                logger.warning(f"No 'results' section in {file_path.name}")
                return None
            
            if 'enhanced_mapping' not in data['results']:
                logger.warning(f"No 'enhanced_mapping' section in {file_path.name}")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {str(e)}")
            return None
    
    def _extract_temporal_evidence(self, paper_data: Dict[str, Any], paper_name: str) -> Dict[str, Any]:
        """Extract all temporal evidence from a single paper"""
        evidence_collection = []
        results = paper_data.get('results', {})
        enhanced_mapping = results.get('enhanced_mapping', {})
        
        # 1. Extract from parameter_evidence_mapping (temporal relevance)
        param_mapping = enhanced_mapping.get('parameter_evidence_mapping', {})
        
        # Temporal-related parameters to prioritize
        temporal_params = [
            'annual_kg_k2o_per_ha', 'sustainability_years', 'depletion_rate',
            'seasonal_release_patterns', 'annual_net_balance', 'annual_replenishment_rate',
            'growing_season_supply', 'off_season_accumulation', 'cumulative_k_depletion',
            'productivity_decline_rate', 'soil_reserve_drawdown', 'total_extractable_k_decline',
            'irreversible_k_fixation', 'restoration_requirements', 'temporal_dynamics',
            'pre_monsoon_k_levels', 'post_monsoon_k_depletion', 'long_term_sustainability',
            'long_rotation_k_balance', 'ratoon_k_depletion'
        ]
        
        for param_name, param_data in param_mapping.items():
            temporal_relevance = param_data.get('temporal_relevance', '')
            
            # Check if this is a temporal parameter or has temporal relevance
            is_temporal = (param_name in temporal_params or 
                          temporal_relevance or
                          'annual' in param_name.lower() or
                          'seasonal' in param_name.lower() or
                          'temporal' in param_name.lower() or
                          'year' in param_name.lower())
            
            if is_temporal:
                evidence_piece = {
                    'evidence_type': 'parameter_with_temporal_context',
                    'parameter_name': param_name,
                    'temporal_relevance': temporal_relevance,
                    'confidence_level': param_data.get('confidence_level', 0.0),
                    'direct_evidence': param_data.get('direct_evidence', []),
                    'supporting_evidence': param_data.get('supporting_evidence', []),
                    'geographic_applicability': param_data.get('geographic_applicability', []),
                    'integration_readiness': param_data.get('integration_readiness', ''),
                    'uncertainty_range': param_data.get('uncertainty_range', {})
                }
                evidence_collection.append(evidence_piece)
                
                # Track statistics
                self.stats['parameters_extracted'].add(param_name)
                if temporal_relevance:
                    timeframe = self._categorize_timeframe(temporal_relevance)
                    self.stats['evidence_by_timeframe'][timeframe] = \
                        self.stats['evidence_by_timeframe'].get(timeframe, 0) + 1
        
        # 2. Extract from temporal_dynamics_mapping (if exists)
        temporal_dynamics = enhanced_mapping.get('temporal_dynamics_mapping', {})
        for temporal_aspect, temporal_data in temporal_dynamics.items():
            if isinstance(temporal_data, dict):
                evidence_piece = {
                    'evidence_type': 'temporal_dynamics_synthesis',
                    'temporal_aspect': temporal_aspect,
                    'evidence_base': temporal_data.get('evidence_base', []),
                    'pattern_characterization': temporal_data.get('pattern_characterization', ''),
                    'confidence_level': temporal_data.get('confidence_level', 0.0),
                    'geographic_scope': temporal_data.get('geographic_scope', []),
                    'agricultural_relevance': temporal_data.get('agricultural_relevance', ''),
                    'timescale': temporal_data.get('timescale', ''),
                    'inflection_points': temporal_data.get('inflection_points', [])
                }
                evidence_collection.append(evidence_piece)
        
        # 3. Extract temporal constraints and limitations
        constraint_validation = results.get('constraint_validation', {})
        if constraint_validation:
            temporal_constraints = constraint_validation.get('temporal_constraint_completeness', {})
            if temporal_constraints:
                evidence_piece = {
                    'evidence_type': 'temporal_constraints',
                    'completeness': temporal_constraints.get('complete', False),
                    'constraint_omissions': temporal_constraints.get('constraint_omissions', []),
                    'limitation_understatements': temporal_constraints.get('limitation_understatements', []),
                    'constraint_enhancements': temporal_constraints.get('constraint_enhancements', [])
                }
                evidence_collection.append(evidence_piece)
        
        # 4. Extract evidence about temporal patterns from validation enhancements
        validation_enhancements = results.get('validation_enhancements', {})
        if validation_enhancements:
            temporal_mapping = validation_enhancements.get('temporal_dynamics_mapping', {})
            if temporal_mapping:
                evidence_piece = {
                    'evidence_type': 'temporal_pattern_validation',
                    'short_term_patterns': temporal_mapping.get('short_term_seasonal_to_annual', {}),
                    'medium_term_patterns': temporal_mapping.get('medium_term_2_to_15_years', {}),
                    'long_term_patterns': temporal_mapping.get('long_term_15_plus_years', {}),
                    'inflection_point_evidence': temporal_mapping.get('inflection_point_evidence', {}),
                    'pattern_reliability': temporal_mapping.get('pattern_reliability', '')
                }
                evidence_collection.append(evidence_piece)
        
        # Update total count
        self.stats['total_evidence_pieces'] += len(evidence_collection)
        
        return {
            'paper_metadata': {
                'paper_id': paper_name,
                'processing_timestamp': paper_data.get('processing_timestamp', ''),
                'stage_4b_validation_passed': paper_data.get('validation_passed', False)
            },
            'evidence_pieces': evidence_collection,
            'evidence_summary': {
                'total_pieces': len(evidence_collection),
                'parameters_with_temporal_context': len([e for e in evidence_collection 
                                                        if e['evidence_type'] == 'parameter_with_temporal_context']),
                'temporal_dynamics_pieces': len([e for e in evidence_collection 
                                               if e['evidence_type'] == 'temporal_dynamics_synthesis']),
                'has_temporal_pattern_validation': any(e['evidence_type'] == 'temporal_pattern_validation' 
                                                     for e in evidence_collection)
            }
        }
    
    def _categorize_timeframe(self, temporal_relevance: str) -> str:
        """Categorize temporal relevance into timeframe buckets"""
        relevance_lower = temporal_relevance.lower()
        
        if 'seasonal' in relevance_lower or 'monthly' in relevance_lower:
            return 'seasonal'
        elif 'annual' in relevance_lower or '1 year' in relevance_lower:
            return 'annual'
        elif any(term in relevance_lower for term in ['2-5 year', '2 to 5', 'medium-term', 'medium term']):
            return '2-5_years'
        elif any(term in relevance_lower for term in ['5-15 year', '5 to 15', '10 year', 'decade']):
            return '5-15_years'
        elif any(term in relevance_lower for term in ['15+ year', '15 year', 'long-term', 'long term', 'decadal']):
            return '15+_years'
        else:
            return 'unspecified'
    
    def _save_combined_output(self):
        """Save the combined temporal evidence output"""
        output_path = self.output_dir / "chunk2_temporal_soil_k_supply.json"
        
        # Add final statistics to metadata
        self.combined_output['chunk_metadata']['extraction_statistics'] = {
            'papers_processed': self.stats['papers_processed'],
            'papers_with_evidence': self.stats['papers_with_temporal_evidence'],
            'total_evidence_pieces': self.stats['total_evidence_pieces'],
            'unique_parameters': len(self.stats['parameters_extracted']),
            'timeframes_covered': len(self.stats['evidence_by_timeframe'])
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.combined_output, f, indent=2, ensure_ascii=False)
            logger.info(f"\n✓ Saved combined output to: {output_path}")
            
        except Exception as e:
            logger.error(f"✗ Error saving combined output: {str(e)}")
    
    def _generate_extraction_report(self) -> Dict[str, Any]:
        """Generate comprehensive extraction report"""
        report = {
            'extraction_metadata': {
                'chunk_id': 'temporal_soil_k_supply',
                'timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'extraction_approach': 'Targeted temporal evidence extraction from Stage 4B enhanced mappings'
            },
            'processing_summary': {
                'papers_processed': self.stats['papers_processed'],
                'papers_with_temporal_evidence': self.stats['papers_with_temporal_evidence'],
                'success_rate': f"{(self.stats['papers_with_temporal_evidence'] / max(1, self.stats['papers_processed']) * 100):.1f}%",
                'total_evidence_pieces': self.stats['total_evidence_pieces'],
                'average_evidence_per_paper': self.stats['total_evidence_pieces'] / max(1, self.stats['papers_with_temporal_evidence'])
            },
            'evidence_distribution': {
                'by_timeframe': dict(sorted(self.stats['evidence_by_timeframe'].items())),
                'unique_parameters': sorted(list(self.stats['parameters_extracted'])),
                'parameter_count': len(self.stats['parameters_extracted'])
            },
            'quality_metrics': {
                'extraction_errors': len(self.stats['extraction_errors']),
                'error_details': self.stats['extraction_errors'] if self.stats['extraction_errors'] else None,
                'data_completeness': 'high' if self.stats['papers_with_temporal_evidence'] > 20 else 'medium'
            },
            'next_steps': {
                'validation': 'Review extracted evidence for completeness and accuracy',
                'stage_5a': 'Process chunk2_temporal_soil_k_supply.json through Stage 5A synthesis',
                'optimization': 'Apply learnings to remaining chunk extractors'
            }
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save extraction report"""
        report_path = self.output_dir / "chunk2_extraction_report.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved extraction report to: {report_path}")
            
        except Exception as e:
            logger.error(f"✗ Error saving report: {str(e)}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("STAGE 4.5 - CHUNK 2: Temporal Soil K Supply Evidence Extraction")
    print("="*80)
    print("Extracting time-based evidence: annual rates, seasonal patterns, long-term trends")
    print()
    
    # Initialize extractor
    extractor = TemporalEvidenceExtractor()
    
    # Process all papers
    try:
        report = extractor.process_all_papers()
        
        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETED")
        print("="*80)
        print(f"Papers processed: {report['processing_summary']['papers_processed']}")
        print(f"Papers with evidence: {report['processing_summary']['papers_with_temporal_evidence']}")
        print(f"Success rate: {report['processing_summary']['success_rate']}")
        print(f"Total evidence pieces: {report['processing_summary']['total_evidence_pieces']}")
        print(f"\nEvidence by timeframe:")
        for timeframe, count in report['evidence_distribution']['by_timeframe'].items():
            print(f"  - {timeframe}: {count} pieces")
        
        if report['quality_metrics']['extraction_errors']:
            print(f"\n⚠ Extraction errors: {report['quality_metrics']['extraction_errors']}")
        
        print("\n✓ Ready for Stage 5A processing")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())