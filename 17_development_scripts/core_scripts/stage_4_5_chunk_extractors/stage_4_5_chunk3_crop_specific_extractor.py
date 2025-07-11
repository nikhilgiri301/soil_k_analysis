#!/usr/bin/env python3
"""
Stage 4.5 Chunk 3: Crop-Specific Soil K Supply Evidence Extractor
Extracts all crop system specific evidence from Stage 4B outputs

This script processes all 25 Stage 4B files and combines crop-specific evidence into a single file.
Focuses on: rice systems, cotton systems, sugarcane, mixed cropping, crop-specific K dynamics.
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
        logging.FileHandler('stage_4_5_chunk3_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CropSpecificEvidenceExtractor:
    """
    Extracts crop-specific soil K evidence from Stage 4B outputs
    
    Target: All evidence related to specific crop systems, crop K requirements,
    crop-soil K interactions, and crop management effects on soil K
    """
    
    def __init__(self, 
                 stage_4b_dir: str = "8_stage_outputs/stage_4b/approved_results",
                 output_dir: str = "8_stage_outputs/stage_4_5_chunks"):
        """Initialize the crop-specific evidence extractor"""
        self.stage_4b_dir = Path(stage_4b_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track extraction statistics
        self.stats = {
            'papers_processed': 0,
            'papers_with_crop_evidence': 0,
            'total_evidence_pieces': 0,
            'evidence_by_crop': {},
            'parameters_extracted': set(),
            'extraction_errors': []
        }
        
        # Combined output structure
        self.combined_output = {
            'chunk_metadata': {
                'chunk_id': 'crop_specific_soil_k_supply',
                'chunk_description': 'All crop system specific soil K evidence from 25 papers',
                'extraction_timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'papers_processed': []
            },
            'evidence_by_paper': {}
        }
        
        # Define crop-related patterns to identify
        self.crop_patterns = {
            'rice': ['rice', 'paddy', 'flooded', 'anaerobic_k_release', 'puddling', 'upland_rice'],
            'cotton': ['cotton', 'boll_development', 'high_k_demand', 'cotton_systems'],
            'sugarcane': ['sugarcane', 'ratoon', 'trash_blanket', 'long_rotation'],
            'mixed_cropping': ['intercrop', 'rotation', 'mixed_cropping', 'cover_crop'],
            'cereals': ['cereal', 'grain', 'wheat', 'maize', 'corn'],
            'oil_palm': ['oil_palm', 'palm'],
            'soybean': ['soybean', 'legume'],
            'vegetables': ['vegetable', 'horticultural']
        }
    
    def process_all_papers(self) -> Dict[str, Any]:
        """Main processing method - extracts crop-specific evidence from all papers"""
        logger.info("="*80)
        logger.info("Starting Crop-Specific Soil K Supply Evidence Extraction")
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
                    evidence = self._extract_crop_evidence(paper_data, paper_name)
                    
                    if evidence['evidence_pieces']:
                        self.combined_output['evidence_by_paper'][paper_name] = evidence
                        self.stats['papers_with_crop_evidence'] += 1
                        logger.info(f"  ✓ Extracted {len(evidence['evidence_pieces'])} evidence pieces")
                    else:
                        logger.warning(f"  ⚠ No crop-specific evidence found")
                    
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
    
    def _extract_crop_evidence(self, paper_data: Dict[str, Any], paper_name: str) -> Dict[str, Any]:
        """Extract all crop-specific evidence from a single paper"""
        evidence_collection = []
        results = paper_data.get('results', {})
        enhanced_mapping = results.get('enhanced_mapping', {})
        
        # 1. Extract from parameter_evidence_mapping (crop-related parameters)
        param_mapping = enhanced_mapping.get('parameter_evidence_mapping', {})
        
        # Crop-related parameters to prioritize
        crop_params = [
            'anaerobic_k_release', 'aerobic_k_availability', 'puddling_k_effects',
            'water_k_concentration', 'upland_rice', 'flooded_conditions',
            'high_k_demand_supply', 'boll_development_k_needs', 'irrigation_k_mobilization',
            'ratoon_k_depletion', 'trash_blanket_k_cycling', 'long_rotation_k_balance',
            'intercrop_k_competition', 'rotation_k_cycling_efficiency', 'cover_crop_k_contributions',
            'plant_k_efficiency_factors', 'crop_uptake_relationships', 'residue_k_recycling'
        ]
        
        for param_name, param_data in param_mapping.items():
            # Check if this is a crop-specific parameter
            is_crop_specific = (param_name in crop_params or 
                              any(crop_term in param_name.lower() 
                                  for crop_patterns in self.crop_patterns.values() 
                                  for crop_term in crop_patterns))
            
            # Also check direct evidence and supporting evidence for crop mentions
            direct_evidence = param_data.get('direct_evidence', [])
            supporting_evidence = param_data.get('supporting_evidence', [])
            
            has_crop_context = False
            crop_systems_mentioned = []
            
            # Check evidence content for crop mentions
            if direct_evidence or supporting_evidence:
                evidence_text = str(direct_evidence) + str(supporting_evidence)
                evidence_lower = evidence_text.lower()
                
                for crop_type, patterns in self.crop_patterns.items():
                    if any(pattern in evidence_lower for pattern in patterns):
                        has_crop_context = True
                        crop_systems_mentioned.append(crop_type)
            
            if is_crop_specific or has_crop_context:
                evidence_piece = {
                    'evidence_type': 'crop_specific_parameter',
                    'parameter_name': param_name,
                    'crop_systems_mentioned': crop_systems_mentioned,
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
                for crop_type in crop_systems_mentioned:
                    self.stats['evidence_by_crop'][crop_type] = \
                        self.stats['evidence_by_crop'].get(crop_type, 0) + 1
        
        # 2. Extract from crop_system_evidence_synthesis (if exists)
        crop_synthesis = enhanced_mapping.get('crop_system_evidence_synthesis', {})
        for crop_system, crop_data in crop_synthesis.items():
            if isinstance(crop_data, dict):
                evidence_piece = {
                    'evidence_type': 'crop_system_synthesis',
                    'crop_system': crop_system,
                    'evidence_base': crop_data.get('evidence_base', []),
                    'system_characteristics': crop_data.get('system_characteristics', ''),
                    'k_dynamics': crop_data.get('k_dynamics', {}),
                    'management_effects': crop_data.get('management_effects', []),
                    'confidence_level': crop_data.get('confidence_level', 0.0),
                    'geographic_applicability': crop_data.get('geographic_applicability', []),
                    'sustainability_implications': crop_data.get('sustainability_implications', '')
                }
                evidence_collection.append(evidence_piece)
        
        # 3. Look for crop mentions in regional synthesis with crop context
        regional_synthesis = enhanced_mapping.get('regional_evidence_synthesis', {})
        for region_data in regional_synthesis.values():
            if isinstance(region_data, dict):
                for subregion_data in region_data.values():
                    if isinstance(subregion_data, dict):
                        param_coverage = subregion_data.get('parameter_coverage', [])
                        regional_note = subregion_data.get('regional_context_note', '')
                        
                        # Check if crop-specific parameters are mentioned
                        crop_params_mentioned = []
                        for param in param_coverage:
                            if any(crop_term in param.lower() 
                                   for crop_patterns in self.crop_patterns.values() 
                                   for crop_term in crop_patterns):
                                crop_params_mentioned.append(param)
                        
                        # Check regional notes for crop mentions
                        crop_context = []
                        note_lower = regional_note.lower()
                        for crop_type, patterns in self.crop_patterns.items():
                            if any(pattern in note_lower for pattern in patterns):
                                crop_context.append(crop_type)
                        
                        if crop_params_mentioned or crop_context:
                            evidence_piece = {
                                'evidence_type': 'regional_crop_evidence',
                                'crop_parameters': crop_params_mentioned,
                                'crop_context': crop_context,
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
                'crop_specific_parameters': len([e for e in evidence_collection 
                                               if e['evidence_type'] == 'crop_specific_parameter']),
                'crop_system_synthesis': len([e for e in evidence_collection 
                                            if e['evidence_type'] == 'crop_system_synthesis']),
                'regional_crop_evidence': len([e for e in evidence_collection 
                                             if e['evidence_type'] == 'regional_crop_evidence']),
                'crop_systems_identified': list(set([crop for e in evidence_collection 
                                                   for crop in e.get('crop_systems_mentioned', []) + 
                                                   e.get('crop_context', [])]))
            }
        }
    
    def _save_combined_output(self):
        """Save the combined crop-specific evidence output"""
        output_path = self.output_dir / "chunk3_crop_specific_soil_k_supply.json"
        
        # Add final statistics to metadata
        self.combined_output['chunk_metadata']['extraction_statistics'] = {
            'papers_processed': self.stats['papers_processed'],
            'papers_with_evidence': self.stats['papers_with_crop_evidence'],
            'total_evidence_pieces': self.stats['total_evidence_pieces'],
            'unique_parameters': len(self.stats['parameters_extracted']),
            'crop_systems_covered': len(self.stats['evidence_by_crop'])
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
                'chunk_id': 'crop_specific_soil_k_supply',
                'timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'extraction_approach': 'Targeted crop-specific evidence extraction from Stage 4B enhanced mappings'
            },
            'processing_summary': {
                'papers_processed': self.stats['papers_processed'],
                'papers_with_crop_evidence': self.stats['papers_with_crop_evidence'],
                'success_rate': f"{(self.stats['papers_with_crop_evidence'] / max(1, self.stats['papers_processed']) * 100):.1f}%",
                'total_evidence_pieces': self.stats['total_evidence_pieces'],
                'average_evidence_per_paper': self.stats['total_evidence_pieces'] / max(1, self.stats['papers_with_crop_evidence'])
            },
            'evidence_distribution': {
                'by_crop_system': dict(sorted(self.stats['evidence_by_crop'].items(), 
                                            key=lambda x: x[1], reverse=True)),
                'unique_parameters': sorted(list(self.stats['parameters_extracted'])),
                'parameter_count': len(self.stats['parameters_extracted'])
            },
            'quality_metrics': {
                'extraction_errors': len(self.stats['extraction_errors']),
                'error_details': self.stats['extraction_errors'] if self.stats['extraction_errors'] else None,
                'data_completeness': 'high' if self.stats['papers_with_crop_evidence'] > 20 else 'medium'
            },
            'next_steps': {
                'validation': 'Review extracted evidence for completeness and accuracy',
                'stage_5a': 'Process chunk3_crop_specific_soil_k_supply.json through Stage 5A synthesis',
                'optimization': 'Apply learnings to remaining chunk extractors'
            }
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save extraction report"""
        report_path = self.output_dir / "chunk3_extraction_report.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved extraction report to: {report_path}")
            
        except Exception as e:
            logger.error(f"✗ Error saving report: {str(e)}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("STAGE 4.5 - CHUNK 3: Crop-Specific Soil K Supply Evidence Extraction")
    print("="*80)
    print("Extracting crop system evidence: rice, cotton, sugarcane, mixed cropping")
    print()
    
    # Initialize extractor
    extractor = CropSpecificEvidenceExtractor()
    
    # Process all papers
    try:
        report = extractor.process_all_papers()
        
        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETED")
        print("="*80)
        print(f"Papers processed: {report['processing_summary']['papers_processed']}")
        print(f"Papers with evidence: {report['processing_summary']['papers_with_crop_evidence']}")
        print(f"Success rate: {report['processing_summary']['success_rate']}")
        print(f"Total evidence pieces: {report['processing_summary']['total_evidence_pieces']}")
        print(f"\nTop crop systems by evidence count:")
        for crop, count in list(report['evidence_distribution']['by_crop_system'].items())[:8]:
            print(f"  - {crop}: {count} pieces")
        
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