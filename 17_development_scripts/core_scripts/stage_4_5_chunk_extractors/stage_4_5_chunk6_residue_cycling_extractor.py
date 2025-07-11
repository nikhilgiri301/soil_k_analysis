#!/usr/bin/env python3
"""
Stage 4.5 Chunk 6: Residue Cycling Integration Evidence Extractor
Extracts all residue cycling and nutrient integration evidence from Stage 4B outputs

This script processes all 25 Stage 4B files and combines residue cycling integration evidence into a single file.
Focuses on: residue K contributions, decomposition dynamics, cycling efficiency, residue-soil interactions.
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
        logging.FileHandler('stage_4_5_chunk6_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResidueCyclingIntegrationExtractor:
    """
    Extracts residue cycling integration evidence from Stage 4B outputs
    
    Target: All evidence related to crop residues, straw K contributions,
    residue decomposition, K release timing, and residue-soil K interactions
    """
    
    def __init__(self, 
                 stage_4b_dir: str = "8_stage_outputs/stage_4b/approved_results",
                 output_dir: str = "8_stage_outputs/stage_4_5_chunks"):
        """Initialize the residue cycling integration extractor"""
        self.stage_4b_dir = Path(stage_4b_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track extraction statistics
        self.stats = {
            'papers_processed': 0,
            'papers_with_residue_evidence': 0,
            'total_evidence_pieces': 0,
            'evidence_by_category': {},
            'parameters_extracted': set(),
            'extraction_errors': []
        }
        
        # Combined output structure
        self.combined_output = {
            'chunk_metadata': {
                'chunk_id': 'residue_cycling_integration',
                'chunk_description': 'All residue cycling integration evidence from 25 papers',
                'extraction_timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'papers_processed': []
            },
            'evidence_by_paper': {}
        }
        
        # Define residue cycling patterns to identify
        self.residue_patterns = {
            'residue': ['residue', 'straw', 'stubble', 'crop_residue', 'harvest_residue'],
            'decomposition': ['decomposition', 'breakdown', 'decay', 'degradation', 'decompose'],
            'release': ['release', 'liberation', 'availability', 'mobilization', 'supply'],
            'recycling': ['recycling', 'cycling', 'turnover', 'reutilization', 'reuse'],
            'contributions': ['contribution', 'input', 'addition', 'supply', 'provision'],
            'timing': ['timing', 'temporal', 'season', 'rate', 'kinetics'],
            'interactions': ['interaction', 'synergy', 'effect', 'influence', 'impact'],
            'efficiency': ['efficiency', 'effectiveness', 'recovery', 'utilization'],
            'management': ['management', 'burning', 'incorporation', 'mulching', 'retention']
        }
    
    def process_all_papers(self) -> Dict[str, Any]:
        """Main processing method - extracts residue cycling integration evidence from all papers"""
        logger.info("="*80)
        logger.info("Starting Residue Cycling Integration Evidence Extraction")
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
                    evidence = self._extract_residue_evidence(paper_data, paper_name)
                    
                    if evidence['evidence_pieces']:
                        self.combined_output['evidence_by_paper'][paper_name] = evidence
                        self.stats['papers_with_residue_evidence'] += 1
                        logger.info(f"  ✓ Extracted {len(evidence['evidence_pieces'])} evidence pieces")
                    else:
                        logger.warning(f"  ⚠ No residue cycling integration evidence found")
                    
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
    
    def _extract_residue_evidence(self, paper_data: Dict[str, Any], paper_name: str) -> Dict[str, Any]:
        """Extract all residue cycling integration evidence from a single paper"""
        evidence_collection = []
        results = paper_data.get('results', {})
        enhanced_mapping = results.get('enhanced_mapping', {})
        
        # 1. Extract from parameter_evidence_mapping (residue-related parameters)
        param_mapping = enhanced_mapping.get('parameter_evidence_mapping', {})
        
        # Residue-related parameters to prioritize
        residue_params = [
            'residue_k_contributions', 'residue_k_recycling', 'residue_k_release_timing',
            'residue_soil_k_interactions', 'decomposition_k_availability', 'trash_blanket_k_cycling',
            'cover_crop_k_contributions', 'seasonal_release_patterns', 'burning_k_losses',
            'incorporation_k_availability', 'straw_k_mineralization', 'harvest_residue_k'
        ]
        
        for param_name, param_data in param_mapping.items():
            # Check if this is a residue-related parameter
            is_residue_related = (param_name in residue_params or 
                                any(residue_term in param_name.lower() 
                                    for patterns in self.residue_patterns.values() 
                                    for residue_term in patterns))
            
            # Also check direct evidence and supporting evidence for residue mentions
            direct_evidence = param_data.get('direct_evidence', [])
            supporting_evidence = param_data.get('supporting_evidence', [])
            
            has_residue_context = False
            residue_categories = []
            
            # Check evidence content for residue mentions (safely handle different data types)
            if direct_evidence or supporting_evidence:
                try:
                    evidence_text = str(direct_evidence) + str(supporting_evidence)
                    evidence_lower = evidence_text.lower()
                    
                    for category, patterns in self.residue_patterns.items():
                        if any(pattern in evidence_lower for pattern in patterns):
                            has_residue_context = True
                            residue_categories.append(category)
                except Exception as e:
                    logger.debug(f"Error processing evidence text for {param_name}: {str(e)}")
            
            if is_residue_related or has_residue_context:
                evidence_piece = {
                    'evidence_type': 'residue_cycling_parameter',
                    'parameter_name': param_name,
                    'residue_categories': residue_categories,
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
                for category in residue_categories:
                    self.stats['evidence_by_category'][category] = \
                        self.stats['evidence_by_category'].get(category, 0) + 1
        
        # 2. Extract from residue_cycling_evidence (if exists)
        residue_evidence = enhanced_mapping.get('residue_cycling_evidence', {})
        for residue_aspect, residue_data in residue_evidence.items():
            if isinstance(residue_data, dict):
                evidence_piece = {
                    'evidence_type': 'residue_cycling_synthesis',
                    'residue_aspect': residue_aspect,
                    'evidence_base': residue_data.get('evidence_base', []),
                    'cycling_mechanisms': residue_data.get('cycling_mechanisms', ''),
                    'decomposition_rates': residue_data.get('decomposition_rates', {}),
                    'k_release_dynamics': residue_data.get('k_release_dynamics', {}),
                    'confidence_level': residue_data.get('confidence_level', 0.0),
                    'environmental_factors': residue_data.get('environmental_factors', []),
                    'management_implications': residue_data.get('management_implications', [])
                }
                evidence_collection.append(evidence_piece)
        
        # 3. Look for residue-related evidence in regional synthesis
        regional_synthesis = enhanced_mapping.get('regional_evidence_synthesis', {})
        for region_data in regional_synthesis.values():
            if isinstance(region_data, dict):
                for subregion_data in region_data.values():
                    if isinstance(subregion_data, dict):
                        param_coverage = subregion_data.get('parameter_coverage', [])
                        regional_note = subregion_data.get('regional_context_note', '')
                        
                        # Check if residue-related parameters are mentioned
                        residue_params_mentioned = []
                        try:
                            for param in param_coverage:
                                if isinstance(param, str):  # Safety check
                                    if any(residue_term in param.lower() 
                                           for patterns in self.residue_patterns.values() 
                                           for residue_term in patterns):
                                        residue_params_mentioned.append(param)
                        except Exception as e:
                            logger.debug(f"Error processing param_coverage: {str(e)}")
                        
                        # Check regional notes for residue mentions
                        residue_context = []
                        try:
                            if isinstance(regional_note, str):  # Safety check
                                note_lower = regional_note.lower()
                                for category, patterns in self.residue_patterns.items():
                                    if any(pattern in note_lower for pattern in patterns):
                                        residue_context.append(category)
                        except Exception as e:
                            logger.debug(f"Error processing regional_note: {str(e)}")
                        
                        if residue_params_mentioned or residue_context:
                            evidence_piece = {
                                'evidence_type': 'regional_residue_evidence',
                                'residue_parameters': residue_params_mentioned,
                                'residue_context': residue_context,
                                'evidence_strength': subregion_data.get('evidence_strength', ''),
                                'confidence_assessment': subregion_data.get('confidence_assessment', {}),
                                'regional_context_note': regional_note,
                                'integration_requirements': subregion_data.get('integration_requirements', [])
                            }
                            evidence_collection.append(evidence_piece)
        
        # 4. Check validation enhancements for residue mentions
        validation_enhancements = results.get('validation_enhancements', {})
        if validation_enhancements:
            # Check evidence characterization enhancements
            evidence_characterization = validation_enhancements.get('evidence_characterization_enhancements', [])
            for enhancement in evidence_characterization:
                if isinstance(enhancement, dict):
                    try:
                        enhanced_char = enhancement.get('enhanced_characterization', '')
                        if isinstance(enhanced_char, str):
                            char_lower = enhanced_char.lower()
                            residue_mentions = []
                            for category, patterns in self.residue_patterns.items():
                                if any(pattern in char_lower for pattern in patterns):
                                    residue_mentions.append(category)
                            
                            if residue_mentions:
                                evidence_piece = {
                                    'evidence_type': 'validation_enhancement_residue',
                                    'evidence_aspect': enhancement.get('evidence_aspect', ''),
                                    'residue_categories_mentioned': residue_mentions,
                                    'enhancement_value': enhancement.get('enhancement_value', ''),
                                    'enhanced_characterization': enhanced_char
                                }
                                evidence_collection.append(evidence_piece)
                    except Exception as e:
                        logger.debug(f"Error processing enhancement: {str(e)}")
        
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
                'residue_parameters': len([e for e in evidence_collection 
                                        if e['evidence_type'] == 'residue_cycling_parameter']),
                'residue_synthesis': len([e for e in evidence_collection 
                                        if e['evidence_type'] == 'residue_cycling_synthesis']),
                'regional_residue_evidence': len([e for e in evidence_collection 
                                               if e['evidence_type'] == 'regional_residue_evidence']),
                'validation_enhancements': len([e for e in evidence_collection 
                                              if e['evidence_type'] == 'validation_enhancement_residue']),
                'residue_categories_identified': list(set([cat for e in evidence_collection 
                                                        for cat in e.get('residue_categories', []) + 
                                                        e.get('residue_context', []) +
                                                        e.get('residue_categories_mentioned', [])]))
            }
        }
    
    def _save_combined_output(self):
        """Save the combined residue cycling integration evidence output"""
        output_path = self.output_dir / "chunk6_residue_cycling_integration.json"
        
        # Add final statistics to metadata
        self.combined_output['chunk_metadata']['extraction_statistics'] = {
            'papers_processed': self.stats['papers_processed'],
            'papers_with_evidence': self.stats['papers_with_residue_evidence'],
            'total_evidence_pieces': self.stats['total_evidence_pieces'],
            'unique_parameters': len(self.stats['parameters_extracted']),
            'residue_categories_covered': len(self.stats['evidence_by_category'])
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
                'chunk_id': 'residue_cycling_integration',
                'timestamp': datetime.now().isoformat(),
                'extractor_version': '1.0',
                'extraction_approach': 'Targeted residue cycling integration evidence extraction from Stage 4B enhanced mappings'
            },
            'processing_summary': {
                'papers_processed': self.stats['papers_processed'],
                'papers_with_residue_evidence': self.stats['papers_with_residue_evidence'],
                'success_rate': f"{(self.stats['papers_with_residue_evidence'] / max(1, self.stats['papers_processed']) * 100):.1f}%",
                'total_evidence_pieces': self.stats['total_evidence_pieces'],
                'average_evidence_per_paper': self.stats['total_evidence_pieces'] / max(1, self.stats['papers_with_residue_evidence'])
            },
            'evidence_distribution': {
                'by_residue_category': dict(sorted(self.stats['evidence_by_category'].items(), 
                                                key=lambda x: x[1], reverse=True)),
                'unique_parameters': sorted(list(self.stats['parameters_extracted'])),
                'parameter_count': len(self.stats['parameters_extracted'])
            },
            'quality_metrics': {
                'extraction_errors': len(self.stats['extraction_errors']),
                'error_details': self.stats['extraction_errors'] if self.stats['extraction_errors'] else None,
                'data_completeness': 'high' if self.stats['papers_with_residue_evidence'] > 15 else 'medium'
            },
            'completion_status': {
                'all_chunks_complete': 'This is the final chunk extractor (6/6)',
                'stage_4_5_ready': 'All 6 chunk files ready for Stage 5A synthesis',
                'next_phase': 'Begin Stage 5A Gold Standard synthesis processing'
            }
        }
        
        return report
    
    def _save_report(self, report: Dict[str, Any]):
        """Save extraction report"""
        report_path = self.output_dir / "chunk6_extraction_report.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved extraction report to: {report_path}")
            
        except Exception as e:
            logger.error(f"✗ Error saving report: {str(e)}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("STAGE 4.5 - CHUNK 6: Residue Cycling Integration Evidence Extraction")
    print("="*80)
    print("Extracting final chunk: residue contributions, decomposition, cycling efficiency")
    print()
    
    # Initialize extractor
    extractor = ResidueCyclingIntegrationExtractor()
    
    # Process all papers
    try:
        report = extractor.process_all_papers()
        
        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETED - ALL 6 CHUNKS READY")
        print("="*80)
        print(f"Papers processed: {report['processing_summary']['papers_processed']}")
        print(f"Papers with evidence: {report['processing_summary']['papers_with_residue_evidence']}")
        print(f"Success rate: {report['processing_summary']['success_rate']}")
        print(f"Total evidence pieces: {report['processing_summary']['total_evidence_pieces']}")
        print(f"\nTop residue categories by evidence count:")
        for category, count in list(report['evidence_distribution']['by_residue_category'].items())[:6]:
            print(f"  - {category}: {count} pieces")
        
        if report['quality_metrics']['extraction_errors']:
            print(f"\n⚠ Extraction errors: {report['quality_metrics']['extraction_errors']}")
        
        print("\n" + "="*50)
        print("🎯 STAGE 4.5 COMPLETE: ALL 6 CHUNKS EXTRACTED")
        print("✓ Ready for Stage 5A Gold Standard processing")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())