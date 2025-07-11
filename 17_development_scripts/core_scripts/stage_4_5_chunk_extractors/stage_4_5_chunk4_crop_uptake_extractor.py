#!/usr/bin/env python3
"""
Stage 4.5 Chunk 4: Crop Uptake Integration Evidence Extractor
Extracts all crop-soil K uptake relationship evidence from Stage 4B outputs

This script processes all 25 Stage 4B files and combines crop uptake integration evidence into a single file.
Focuses on: crop-soil K relationships, uptake efficiency, plant K factors, soil-solution dynamics.
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
        logging.FileHandler('stage_4_5_chunk4_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CropUptakeIntegrationExtractor:
    """
    Extracts crop uptake integration evidence from Stage 4B outputs
    
    Target: All evidence related to crop-soil K relationships, uptake mechanisms,
    plant efficiency factors, and soil solution dynamics affecting crop K availability
    """
    
    def __init__(self, 
                 stage_4b_dir: str = "8_stage_outputs/stage_4b/approved_results",
                 output_dir: str = "8_stage_outputs/stage_4_5_chunks"):
        """Initialize the crop uptake integration extractor"""
        self.stage_4b_dir = Path(stage_4b_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track extraction statistics
        self.stats = {
            'papers_processed': 0,
            'papers_with_uptake_evidence': 0,
            'total_evidence_pieces': 0,
            'evidence_by_category': {},
            'parameters_extracted': set(),
            'extraction_errors': []
        }
        
        # Combined output structure
        self.combined_output = {
            'chunk_metadata': {
                'chunk_id': 'crop_uptake_integration',
                'chunk_description': 'All crop-soil K uptake integration evidence from 25 papers',
                'extraction_timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'papers_processed': []
            },
            'evidence_by_paper': {}
        }
        
        # Define uptake-related patterns to identify
        self.uptake_patterns = {
            'plant_efficiency': ['plant_k_efficiency', 'uptake_efficiency', 'k_use_efficiency', 'k_utilization'],
            'soil_solution': ['soil_solution_k', 'solution_k', 'available_k', 'soluble_k'],
            'root_zone': ['root_zone', 'rhizosphere', 'root_uptake', 'root_k'],
            'depletion': ['k_depletion', 'depletion_zone', 'nutrient_depletion'],
            'concentration': ['k_concentration', 'concentration_gradient', 'k_content'],
            'kinetics': ['uptake_kinetic', 'absorption_kinetic', 'k_uptake_rate'],
            'efficiency': ['efficiency_factor', 'nutrient_efficiency', 'k_recovery'],
            'buffering': ['k_buffer', 'buffering_capacity', 'k_intensity'],
            'relationships': ['crop_uptake_relationship', 'plant_soil_relationship', 'uptake_correlation']
        }
    
    def process_all_papers(self) -> Dict[str, Any]:
        """Main processing method - extracts crop uptake integration evidence from all papers"""
        logger.info("="*80)
        logger.info("Starting Crop Uptake Integration Evidence Extraction")
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
                    evidence = self._extract_uptake_evidence(paper_data, paper_name)
                    
                    if evidence['evidence_pieces']:
                        self.combined_output['evidence_by_paper'][paper_name] = evidence
                        self.stats['papers_with_uptake_evidence'] += 1
                        logger.info(f"  ✓ Extracted {len(evidence['evidence_pieces'])} evidence pieces")
                    else:
                        logger.warning(f"  ⚠ No crop uptake integration evidence found")
                    
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
    
    def _extract_uptake_evidence(self, paper_data: Dict[str, Any], paper_name: str) -> Dict[str, Any]:
        """Extract all crop uptake integration evidence from a single paper"""
        evidence_collection = []
        results = paper_data.get('results', {})
        enhanced_mapping = results.get('enhanced_mapping', {})
        
        # 1. Extract from parameter_evidence_mapping (uptake-related parameters)
        param_mapping = enhanced_mapping.get('parameter_evidence_mapping', {})
        
        # Uptake-related parameters to prioritize
        uptake_params = [
            'plant_k_efficiency_factors', 'soil_solution_k_concentration',
            'root_zone_k_depletion', 'crop_uptake_relationships',
            'soil_solution_k_concentration', 'k_buffering_capacity',
            'plant_available_k', 'uptake_kinetics', 'k_use_efficiency',
            'nutrient_use_efficiency', 'k_recovery_efficiency'
        ]
        
        for param_name, param_data in param_mapping.items():
            # Check if this is an uptake-related parameter
            is_uptake_related = (param_name in uptake_params or 
                               any(uptake_term in param_name.lower() 
                                   for patterns in self.uptake_patterns.values() 
                                   for uptake_term in patterns))
            
            # Also check direct evidence and supporting evidence for uptake mentions
            direct_evidence = param_data.get('direct_evidence', [])
            supporting_evidence = param_data.get('supporting_evidence', [])
            
            has_uptake_context = False
            uptake_categories = []
            
            # Check evidence content for uptake mentions (safely handle different data types)
            if direct_evidence or supporting_evidence:
                try:
                    evidence_text = str(direct_evidence) + str(supporting_evidence)
                    evidence_lower = evidence_text.lower()
                    
                    for category, patterns in self.uptake_patterns.items():
                        if any(pattern in evidence_lower for pattern in patterns):
                            has_uptake_context = True
                            uptake_categories.append(category)
                except Exception as e:
                    logger.debug(f"Error processing evidence text for {param_name}: {str(e)}")
            
            if is_uptake_related or has_uptake_context:
                evidence_piece = {
                    'evidence_type': 'crop_uptake_parameter',
                    'parameter_name': param_name,
                    'uptake_categories': uptake_categories,
                    'confidence_level': param_data.get('confidence_level', 0.0),
                    'direct_evidence': direct_evidence,
                    'supporting_evidence': supporting_evidence,
                    'temporal_relevance': param_data.get('temporal_relevance', ''),
                    'geographic_applicability': param_data.get('geographic_applicability', []),
                    'integration_readiness': param_data.get('integration_readiness', ''),
                    'uncertainty_range': param_data.get('uncertainty_range', {})
                }
                evidence_collection.append(evidence_piece)
                
                # Track statistics
                self.stats['parameters_extracted'].add(param_name)
                for category in uptake_categories:
                    self.stats['evidence_by_category'][category] = \
                        self.stats['evidence_by_category'].get(category, 0) + 1
        
        # 2. Extract from integration_parameter_evidence (if exists)
        integration_evidence = enhanced_mapping.get('integration_parameter_evidence', {})
        for integration_aspect, integration_data in integration_evidence.items():
            if isinstance(integration_data, dict):
                evidence_piece = {
                    'evidence_type': 'integration_parameter_synthesis',
                    'integration_aspect': integration_aspect,
                    'evidence_base': integration_data.get('evidence_base', []),
                    'integration_mechanisms': integration_data.get('integration_mechanisms', ''),
                    'efficiency_factors': integration_data.get('efficiency_factors', {}),
                    'confidence_level': integration_data.get('confidence_level', 0.0),
                    'scaling_considerations': integration_data.get('scaling_considerations', []),
                    'validation_requirements': integration_data.get('validation_requirements', [])
                }
                evidence_collection.append(evidence_piece)
        
        # 3. Look for uptake-related evidence in other mapping sections
        # Check regional synthesis for uptake-related parameters
        regional_synthesis = enhanced_mapping.get('regional_evidence_synthesis', {})
        for region_data in regional_synthesis.values():
            if isinstance(region_data, dict):
                for subregion_data in region_data.values():
                    if isinstance(subregion_data, dict):
                        param_coverage = subregion_data.get('parameter_coverage', [])
                        regional_note = subregion_data.get('regional_context_note', '')
                        
                        # Check if uptake-related parameters are mentioned
                        uptake_params_mentioned = []
                        try:
                            for param in param_coverage:
                                if isinstance(param, str):  # Safety check
                                    if any(uptake_term in param.lower() 
                                           for patterns in self.uptake_patterns.values() 
                                           for uptake_term in patterns):
                                        uptake_params_mentioned.append(param)
                        except Exception as e:
                            logger.debug(f"Error processing param_coverage: {str(e)}")
                        
                        # Check regional notes for uptake mentions
                        uptake_context = []
                        try:
                            if isinstance(regional_note, str):  # Safety check
                                note_lower = regional_note.lower()
                                for category, patterns in self.uptake_patterns.items():
                                    if any(pattern in note_lower for pattern in patterns):
                                        uptake_context.append(category)
                        except Exception as e:
                            logger.debug(f"Error processing regional_note: {str(e)}")
                        
                        if uptake_params_mentioned or uptake_context:
                            evidence_piece = {
                                'evidence_type': 'regional_uptake_evidence',
                                'uptake_parameters': uptake_params_mentioned,
                                'uptake_context': uptake_context,
                                'evidence_strength': subregion_data.get('evidence_strength', ''),
                                'confidence_assessment': subregion_data.get('confidence_assessment', {}),
                                'regional_context_note': regional_note,
                                'integration_requirements': subregion_data.get('integration_requirements', [])
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
                'uptake_parameters': len([e for e in evidence_collection 
                                        if e['evidence_type'] == 'crop_uptake_parameter']),
                'integration_synthesis': len([e for e in evidence_collection 
                                            if e['evidence_type'] == 'integration_parameter_synthesis']),
                'regional_uptake_evidence': len([e for e in evidence_collection 
                                               if e['evidence_type'] == 'regional_uptake_evidence']),
                'uptake_categories_identified': list(set([cat for e in evidence_collection 
                                                        for cat in e.get('uptake_categories', []) + 
                                                        e.get('uptake_context', [])]))
            }
        }
    
    def _save_combined_output(self):
        """Save the combined crop uptake integration evidence output"""
        output_path = self.output_dir / "chunk4_crop_uptake_integration.json"
        
        # Add final statistics to metadata
        self.combined_output['chunk_metadata']['extraction_statistics'] = {
            'papers_processed': self.stats['papers_processed'],
            'papers_with_evidence': self.stats['papers_with_uptake_evidence'],
            'total_evidence_pieces': self.stats['total_evidence_pieces'],
            'unique_parameters': len(self.stats['parameters_extracted']),
            'uptake_categories_covered': len(self.stats['evidence_by_category'])
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
                'chunk_id': 'crop_uptake_integration',
                'timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'extraction_approach': 'Targeted crop uptake integration evidence extraction from Stage 4B enhanced mappings'
            },
            'processing_summary': {
                'papers_processed': self.stats['papers_processed'],
                'papers_with_uptake_evidence': self.stats['papers_with_uptake_evidence'],
                'success_rate': f"{(self.stats['papers_with_uptake_evidence'] / max(1, self.stats['papers_processed']) * 100):.1f}%",
                'total_evidence_pieces': self.stats['total_evidence_pieces'],
                'average_evidence_per_paper': self.stats['total_evidence_pieces'] / max(1, self.stats['papers_with_uptake_evidence'])
            },
            'evidence_distribution': {
                'by_uptake_category': dict(sorted(self.stats['evidence_by_category'].items(), 
                                                key=lambda x: x[1], reverse=True)),
                'unique_parameters': sorted(list(self.stats['parameters_extracted'])),
                'parameter_count': len(self.stats['parameters_extracted'])
            },
            'quality_metrics': {
                'extraction_errors': len(self.stats['extraction_errors']),
                'error_details': self.stats['extraction_errors'] if self.stats['extraction_errors'] else None,
                'data_completeness': 'high' if self.stats['papers_with_uptake_evidence'] > 15 else 'medium'
            },
            'next_steps': {
                'validation': 'Review extracted evidence for completeness and accuracy',
                'stage_5a': 'Process chunk4_crop_uptake_integration.json through Stage 5A synthesis',
                'optimization': 'Apply learnings to remaining chunk extractors'
            }
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save extraction report"""
        report_path = self.output_dir / "chunk4_extraction_report.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved extraction report to: {report_path}")
            
        except Exception as e:
            logger.error(f"✗ Error saving report: {str(e)}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("STAGE 4.5 - CHUNK 4: Crop Uptake Integration Evidence Extraction")
    print("="*80)
    print("Extracting crop-soil K uptake relationships: efficiency, kinetics, mechanisms")
    print()
    
    # Initialize extractor
    extractor = CropUptakeIntegrationExtractor()
    
    # Process all papers
    try:
        report = extractor.process_all_papers()
        
        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETED")
        print("="*80)
        print(f"Papers processed: {report['processing_summary']['papers_processed']}")
        print(f"Papers with evidence: {report['processing_summary']['papers_with_uptake_evidence']}")
        print(f"Success rate: {report['processing_summary']['success_rate']}")
        print(f"Total evidence pieces: {report['processing_summary']['total_evidence_pieces']}")
        print(f"\nTop uptake categories by evidence count:")
        for category, count in list(report['evidence_distribution']['by_uptake_category'].items())[:6]:
            print(f"  - {category}: {count} pieces")
        
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