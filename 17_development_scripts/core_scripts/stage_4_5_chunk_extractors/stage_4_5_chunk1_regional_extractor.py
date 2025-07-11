#!/usr/bin/env python3
"""
Stage 4.5 Chunk 1: Regional Soil K Supply Evidence Extractor
Extracts all regional/geographic evidence from Stage 4B outputs

This script implements a rigorous, targeted extraction approach for the first chunk.
It processes all 25 Stage 4B files and combines regional evidence into a single file.
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
        logging.FileHandler('stage_4_5_chunk1_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RegionalEvidenceExtractor:
    """
    Extracts regional/geographic soil K evidence from Stage 4B outputs
    
    Target: All evidence related to geographic regions, spatial variations, 
    and location-specific soil K parameters
    """
    
    def __init__(self, 
                 stage_4b_dir: str = "8_stage_outputs/stage_4b/approved_results",
                 output_dir: str = "8_stage_outputs/stage_4_5_chunks"):
        """Initialize the regional evidence extractor"""
        self.stage_4b_dir = Path(stage_4b_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track extraction statistics
        self.stats = {
            'papers_processed': 0,
            'papers_with_regional_evidence': 0,
            'total_evidence_pieces': 0,
            'evidence_by_region': {},
            'parameters_extracted': set(),
            'extraction_errors': []
        }
        
        # Combined output structure
        self.combined_output = {
            'chunk_metadata': {
                'chunk_id': 'regional_soil_k_supply',
                'chunk_description': 'All geographic/regional soil K evidence from 25 papers',
                'extraction_timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'papers_processed': []
            },
            'evidence_by_paper': {}
        }
    
    def process_all_papers(self) -> Dict[str, Any]:
        """Main processing method - extracts regional evidence from all papers"""
        logger.info("="*80)
        logger.info("Starting Regional Soil K Supply Evidence Extraction")
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
                    evidence = self._extract_regional_evidence(paper_data, paper_name)
                    
                    if evidence['evidence_pieces']:
                        self.combined_output['evidence_by_paper'][paper_name] = evidence
                        self.stats['papers_with_regional_evidence'] += 1
                        logger.info(f"  ✓ Extracted {len(evidence['evidence_pieces'])} evidence pieces")
                    else:
                        logger.warning(f"  ⚠ No regional evidence found")
                    
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
    
    def _extract_regional_evidence(self, paper_data: Dict[str, Any], paper_name: str) -> Dict[str, Any]:
        """Extract all regional evidence from a single paper"""
        evidence_collection = []
        results = paper_data.get('results', {})
        enhanced_mapping = results.get('enhanced_mapping', {})
        
        # 1. Extract from parameter_evidence_mapping
        param_mapping = enhanced_mapping.get('parameter_evidence_mapping', {})
        for param_name, param_data in param_mapping.items():
            geographic_applicability = param_data.get('geographic_applicability', [])
            
            if geographic_applicability:
                # This parameter has geographic relevance
                evidence_piece = {
                    'evidence_type': 'parameter_with_regional_context',
                    'parameter_name': param_name,
                    'geographic_applicability': geographic_applicability,
                    'confidence_level': param_data.get('confidence_level', 0.0),
                    'direct_evidence': param_data.get('direct_evidence', []),
                    'supporting_evidence': param_data.get('supporting_evidence', []),
                    'temporal_relevance': param_data.get('temporal_relevance', ''),
                    'integration_readiness': param_data.get('integration_readiness', ''),
                    'uncertainty_range': param_data.get('uncertainty_range', {})
                }
                evidence_collection.append(evidence_piece)
                
                # Track statistics
                self.stats['parameters_extracted'].add(param_name)
                for region in geographic_applicability:
                    self.stats['evidence_by_region'][region] = \
                        self.stats['evidence_by_region'].get(region, 0) + 1
        
        # 2. Extract from regional_evidence_synthesis (if exists)
        regional_synthesis = enhanced_mapping.get('regional_evidence_synthesis', {})
        for region, region_data in regional_synthesis.items():
            if region == 'geographic_extrapolation':
                # Handle extrapolation evidence separately
                if isinstance(region_data, dict):
                    evidence_piece = {
                        'evidence_type': 'geographic_extrapolation_assessment',
                        'extrapolation_confidence': region_data.get('extrapolation_confidence', {}),
                        'adjustment_factors': region_data.get('adjustment_factors', []),
                        'validation_requirements': region_data.get('validation_requirements', [])
                    }
                    evidence_collection.append(evidence_piece)
            else:
                # Regular regional evidence
                if isinstance(region_data, dict):
                    for subregion, subregion_data in region_data.items():
                        if isinstance(subregion_data, dict):
                            evidence_piece = {
                                'evidence_type': 'regional_synthesis',
                                'region': region,
                                'subregion': subregion,
                                'evidence_strength': subregion_data.get('evidence_strength', ''),
                                'parameter_coverage': subregion_data.get('parameter_coverage', []),
                                'confidence_assessment': subregion_data.get('confidence_assessment', {}),
                                'regional_context_note': subregion_data.get('regional_context_note', ''),
                                'integration_requirements': subregion_data.get('integration_requirements', [])
                            }
                            evidence_collection.append(evidence_piece)
        
        # 3. Extract geographic constraints and limitations
        constraint_validation = results.get('constraint_validation', {})
        if constraint_validation:
            geographic_constraints = constraint_validation.get('geographic_constraint_completeness', {})
            if geographic_constraints:
                evidence_piece = {
                    'evidence_type': 'geographic_constraints',
                    'completeness': geographic_constraints.get('complete', False),
                    'constraint_omissions': geographic_constraints.get('constraint_omissions', []),
                    'boundary_mischaracterizations': geographic_constraints.get('boundary_mischaracterizations', []),
                    'constraint_enhancements': geographic_constraints.get('constraint_enhancements', [])
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
                'parameters_with_geographic_context': len([e for e in evidence_collection 
                                                          if e['evidence_type'] == 'parameter_with_regional_context']),
                'regional_synthesis_pieces': len([e for e in evidence_collection 
                                                if e['evidence_type'] == 'regional_synthesis']),
                'has_extrapolation_assessment': any(e['evidence_type'] == 'geographic_extrapolation_assessment' 
                                                  for e in evidence_collection)
            }
        }
    
    def _save_combined_output(self):
        """Save the combined regional evidence output"""
        output_path = self.output_dir / "chunk1_regional_soil_k_supply.json"
        
        # Add final statistics to metadata
        self.combined_output['chunk_metadata']['extraction_statistics'] = {
            'papers_processed': self.stats['papers_processed'],
            'papers_with_evidence': self.stats['papers_with_regional_evidence'],
            'total_evidence_pieces': self.stats['total_evidence_pieces'],
            'unique_parameters': len(self.stats['parameters_extracted']),
            'regions_covered': len(self.stats['evidence_by_region'])
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
                'chunk_id': 'regional_soil_k_supply',
                'timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'extraction_approach': 'Targeted regional evidence extraction from Stage 4B enhanced mappings'
            },
            'processing_summary': {
                'papers_processed': self.stats['papers_processed'],
                'papers_with_regional_evidence': self.stats['papers_with_regional_evidence'],
                'success_rate': f"{(self.stats['papers_with_regional_evidence'] / max(1, self.stats['papers_processed']) * 100):.1f}%",
                'total_evidence_pieces': self.stats['total_evidence_pieces'],
                'average_evidence_per_paper': self.stats['total_evidence_pieces'] / max(1, self.stats['papers_with_regional_evidence'])
            },
            'evidence_distribution': {
                'by_region': dict(sorted(self.stats['evidence_by_region'].items(), 
                                       key=lambda x: x[1], reverse=True)),
                'unique_parameters': sorted(list(self.stats['parameters_extracted'])),
                'parameter_count': len(self.stats['parameters_extracted'])
            },
            'quality_metrics': {
                'extraction_errors': len(self.stats['extraction_errors']),
                'error_details': self.stats['extraction_errors'] if self.stats['extraction_errors'] else None,
                'data_completeness': 'high' if self.stats['papers_with_regional_evidence'] > 20 else 'medium'
            },
            'next_steps': {
                'validation': 'Review extracted evidence for completeness and accuracy',
                'stage_5a': 'Process chunk1_regional_soil_k_supply.json through Stage 5A synthesis',
                'optimization': 'Apply learnings to other chunk extractors'
            }
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save extraction report"""
        report_path = self.output_dir / "chunk1_extraction_report.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved extraction report to: {report_path}")
            
        except Exception as e:
            logger.error(f"✗ Error saving report: {str(e)}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("STAGE 4.5 - CHUNK 1: Regional Soil K Supply Evidence Extraction")
    print("="*80)
    print("Rigorous extraction approach with comprehensive logging and validation")
    print()
    
    # Initialize extractor
    extractor = RegionalEvidenceExtractor()
    
    # Process all papers
    try:
        report = extractor.process_all_papers()
        
        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETED")
        print("="*80)
        print(f"Papers processed: {report['processing_summary']['papers_processed']}")
        print(f"Papers with evidence: {report['processing_summary']['papers_with_regional_evidence']}")
        print(f"Success rate: {report['processing_summary']['success_rate']}")
        print(f"Total evidence pieces: {report['processing_summary']['total_evidence_pieces']}")
        print(f"\nTop 5 regions by evidence count:")
        for region, count in list(report['evidence_distribution']['by_region'].items())[:5]:
            print(f"  - {region}: {count} pieces")
        
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