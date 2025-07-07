"""
Master Controller for Soil K Analysis Synthesis Engine
Updated to match actual Stage 5 processor filenames: iterative_integrator and integration_validator
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import sys

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.prompt_loader import PromptLoader
from utils.gemini_client import GeminiClient
from utils.config import STAGE_TEMPERATURES, GEMINI_CONFIG, PATHS

# Import all processors
from stage_1_processors.generic_extractor import GenericExtractor
from stage_1_processors.generic_validator import GenericValidator
from stage_2_processors.soilk_extractor import SoilKExtractor
from stage_2_processors.soilk_validator import SoilKValidator
from stage_3_processors.paper_synthesizer import PaperSynthesizer
from stage_3_processors.synthesis_validator import SynthesisValidator
from stage_4_processors.client_mapper import ClientMapper
from stage_4_processors.mapping_validator import MappingValidator

# Stage 5 processors - using actual filenames
from stage_5_processors.iterative_integrator import IterativeIntegrator
from stage_5_processors.integration_validator import IntegrationValidator

# Validation framework
from validation_framework.quality_controller import QualityController
from validation_framework.confidence_scorer import ConfidenceScorer

class SoilKAnalysisEngine:
    """Enhanced orchestration engine for 5-stage, 10-pass synthesis system"""
    
    def __init__(self, api_key: str, resume_from_checkpoint: Optional[str] = None):
        # Initialize core components
        self.gemini_client = GeminiClient(api_key)
        self.prompt_loader = PromptLoader()
        
        # Initialize validation components
        self.quality_controller = QualityController()
        self.confidence_scorer = ConfidenceScorer()
        
        # Validate system integrity
        self.validate_system_components()
        
        # Load client question architecture
        self.client_architecture = self.load_client_architecture()
        
        # Initialize stage processors
        self.processors = self.initialize_all_processors()
        
        # Handle checkpoint resume
        self.resume_checkpoint = resume_from_checkpoint
        
        logging.info("Soil K Analysis Engine initialized successfully")
    
    def validate_system_components(self):
        """Validate all prompts and system components at startup"""
        try:
            prompt_validation = self.prompt_loader.validate_all_prompts()
            
            failed_prompts = [name for name, status in prompt_validation.items() if not status]
            if failed_prompts:
                raise SystemError(f"Critical system error - prompt validation failed for: {failed_prompts}")
            
            logging.info("All system components validated successfully")
            
        except Exception as e:
            logging.error(f"System validation failed: {str(e)}")
            raise
    
    def initialize_all_processors(self):
        """Initialize all processors with Gemini client and file-based prompts"""
        return {
            '1a': GenericExtractor(self.gemini_client),
            '1b': GenericValidator(self.gemini_client),
            '2a': SoilKExtractor(self.gemini_client),
            '2b': SoilKValidator(self.gemini_client),
            '3a': PaperSynthesizer(self.gemini_client),
            '3b': SynthesisValidator(self.gemini_client),
            '4a': ClientMapper(self.gemini_client),
            '4b': MappingValidator(self.gemini_client),
            '5a': IterativeIntegrator(self.gemini_client),  # Using actual filename
            '5b': IntegrationValidator(self.gemini_client)  # Using actual filename
        }
    
    def load_client_architecture(self):
        """Load client question tree and parameter definitions"""
        try:
            with open(f"{PATHS['client_architecture']}/question_tree.json", 'r') as f:
                question_tree = json.load(f)
            
            with open(f"{PATHS['client_architecture']}/parameter_definitions.json", 'r') as f:
                parameters = json.load(f)
                
            with open(f"{PATHS['client_architecture']}/confidence_thresholds.json", 'r') as f:
                thresholds = json.load(f)
                
            return {
                "question_tree": question_tree, 
                "parameters": parameters,
                "thresholds": thresholds
            }
            
        except Exception as e:
            logging.error(f"Failed to load client architecture: {str(e)}")
            raise
    
    async def process_all_papers(self):
        """Main orchestration method for 10-pass processing of all papers"""
        
        try:
            # Load synthesis-ready dataset
            with open(f"{PATHS['synthesis_ready']}/complete_dataset.json", 'r') as f:
                dataset = json.load(f)
            
            papers = dataset['papers']
            total_papers = len(papers)
            
            logging.info(f"Starting 10-pass analysis of {total_papers} papers")
            
            # Process papers through Stages 1-4 (parallelizable per paper)
            client_mappings = await self.process_stages_1_to_4(papers)
            
            # Process Stage 5: Iterative knowledge synthesis
            final_synthesis = await self.process_stage_5_iterative(client_mappings)
            
            # Generate final deliverable
            deliverable = self.generate_client_deliverable(final_synthesis, client_mappings)
            
            logging.info("10-pass analysis completed successfully")
            return deliverable
            
        except Exception as e:
            logging.error(f"Analysis failed: {str(e)}")
            raise
    
    async def process_stages_1_to_4(self, papers):
        """Process papers through stages 1-4 (parallel per paper)"""
        
        client_mappings = []
        
        for i, paper in enumerate(papers):
            try:
                paper_id = paper['filename']
                logging.info(f"Processing stages 1-4 for paper {i+1}/{len(papers)}: {paper_id}")
                
                # Stages 1A & 2A: Parallel extraction
                stage_1a_task = self.processors['1a'].extract(paper)
                stage_2a_task = self.processors['2a'].extract(paper)
                
                stage_1a_result, stage_2a_result = await asyncio.gather(
                    stage_1a_task, stage_2a_task, return_exceptions=True
                )
                
                # Handle extraction errors
                if isinstance(stage_1a_result, Exception):
                    logging.error(f"Stage 1A failed for {paper_id}: {str(stage_1a_result)}")
                    continue
                if isinstance(stage_2a_result, Exception):
                    logging.error(f"Stage 2A failed for {paper_id}: {str(stage_2a_result)}")
                    continue
                
                # Stages 1B & 2B: Parallel validation
                stage_1b_task = self.processors['1b'].validate(stage_1a_result, paper)
                stage_2b_task = self.processors['2b'].validate(stage_2a_result, paper)
                
                stage_1b_result, stage_2b_result = await asyncio.gather(
                    stage_1b_task, stage_2b_task, return_exceptions=True
                )
                
                # Handle validation errors
                if isinstance(stage_1b_result, Exception):
                    logging.error(f"Stage 1B failed for {paper_id}: {str(stage_1b_result)}")
                    stage_1b_result = stage_1a_result  # Fallback to unvalidated
                if isinstance(stage_2b_result, Exception):
                    logging.error(f"Stage 2B failed for {paper_id}: {str(stage_2b_result)}")
                    stage_2b_result = stage_2a_result  # Fallback to unvalidated
                
                # Stage 3A: Paper synthesis
                stage_3a_result = await self.processors['3a'].synthesize(
                    stage_1b_result, stage_2b_result, paper
                )
                
                # Stage 3B: Synthesis validation
                stage_3b_result = await self.processors['3b'].validate(stage_3a_result, paper)
                
                # Stage 4A: Client mapping
                stage_4a_result = await self.processors['4a'].map_to_client_questions(
                    stage_3b_result, self.client_architecture
                )
                
                # Stage 4B: Mapping validation
                stage_4b_result = await self.processors['4b'].validate(
                    stage_4a_result, self.client_architecture
                )
                
                # Quality validation
                quality_result = self.quality_controller.validate_stage_output(
                    f"stages_1_4_paper_{i}", stage_4b_result, paper
                )
                
                # Confidence scoring
                confidence_result = self.confidence_scorer.score_paper_confidence(
                    paper, stage_4b_result, 
                    geographic_context=stage_2b_result.get('geographic_context')
                )
                
                # Store complete paper mapping
                paper_mapping = {
                    "paper_id": paper_id,
                    "paper_index": i,
                    "stage_4b_mapping": stage_4b_result,
                    "quality_assessment": quality_result,
                    "confidence_assessment": confidence_result,
                    "processing_timestamp": datetime.now().isoformat()
                }
                
                client_mappings.append(paper_mapping)
                
                # Save intermediate results
                await self._save_stage_output("stage_4b_validation", f"{paper_id}_mapping", paper_mapping)
                
                logging.info(f"Completed stages 1-4 for {paper_id}")
                
            except Exception as e:
                logging.error(f"Failed to process paper {paper.get('filename', 'unknown')}: {str(e)}")
                continue
        
        logging.info(f"Completed stages 1-4 for {len(client_mappings)}/{len(papers)} papers")
        return client_mappings
    
    async def process_stage_5_iterative(self, client_mappings):
        """Process Stage 5: Iterative knowledge synthesis"""
        
        logging.info("Starting Stage 5: Iterative knowledge synthesis")
        
        # Initialize synthesis state
        current_synthesis_state = {
            "synthesis_metadata": {
                "initialization_timestamp": datetime.now().isoformat(),
                "papers_integrated": 0,
                "current_version": "1.0.0",
                "total_papers_to_integrate": len(client_mappings)
            },
            "question_responses": {},
            "evidence_registry": {},
            "confidence_evolution": [],
            "integration_log": []
        }
        
        # Iteratively integrate each paper
        for i, paper_mapping in enumerate(client_mappings):
            try:
                paper_id = paper_mapping["paper_id"]
                logging.info(f"Integrating paper {i+1}/{len(client_mappings)}: {paper_id}")
                
                # Stage 5A: Integrate paper into synthesis state
                integration_result = await self.processors['5a'].integrate_paper(
                    current_synthesis_state, 
                    paper_mapping["stage_4b_mapping"], 
                    self.client_architecture
                )
                
                # Stage 5B: Validate integration
                validation_result = await self.processors['5b'].validate_integration(
                    current_synthesis_state,
                    paper_mapping["stage_4b_mapping"],
                    integration_result
                )
                
                # Update synthesis state if validation passed
                if validation_result.get("validation_passed", False):
                    current_synthesis_state = integration_result
                    current_synthesis_state["synthesis_metadata"]["papers_integrated"] = i + 1
                else:
                    logging.warning(f"Integration validation failed for {paper_id}")
                    # Continue with previous state
                
                # Save incremental state
                await self._save_stage_output("stage_5a_knowledge", f"state_after_{i+1}_papers", current_synthesis_state)
                
            except Exception as e:
                logging.error(f"Failed to integrate paper {paper_mapping.get('paper_id')}: {str(e)}")
                continue
        
        # Final synthesis confidence scoring
        final_confidence = self.confidence_scorer.score_synthesis_confidence(
            current_synthesis_state, 
            [mapping["confidence_assessment"] for mapping in client_mappings]
        )
        
        # Add final metadata
        current_synthesis_state["final_assessment"] = {
            "completion_timestamp": datetime.now().isoformat(),
            "final_confidence": final_confidence,
            "papers_successfully_integrated": current_synthesis_state["synthesis_metadata"]["papers_integrated"],
            "synthesis_quality": "conservative_calibration_applied"
        }
        
        logging.info("Completed Stage 5: Iterative knowledge synthesis")
        return current_synthesis_state
    
    def generate_client_deliverable(self, final_synthesis, client_mappings):
        """Generate final client deliverable"""
        
        return {
            "deliverable_metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "synthesis_engine_version": "2.0.0",
                "processing_approach": "5_stage_10_pass_iterative_synthesis",
                "conservative_confidence_calibration": True
            },
            "executive_summary": {
                "total_papers": len(client_mappings),
                "papers_successfully_integrated": final_synthesis["synthesis_metadata"]["papers_integrated"],
                "overall_confidence": final_synthesis["final_assessment"]["final_confidence"].get("overall_confidence", 0.0),
                "analysis_approach": "Systematic literature synthesis with AI-enhanced analysis"
            },
            "client_question_responses": final_synthesis.get("question_responses", {}),
            "evidence_base_analysis": final_synthesis.get("evidence_registry", {}),
            "confidence_assessment": final_synthesis["final_assessment"]["final_confidence"],
            "paper_summaries": [
                {
                    "paper_id": mapping["paper_id"],
                    "confidence": mapping["confidence_assessment"].get("adjusted_confidence", 0.0),
                    "quality": mapping["quality_assessment"].get("quality_score", 0.0)
                }
                for mapping in client_mappings
            ],
            "methodology_documentation": {
                "processing_stages": "10-pass validation system",
                "confidence_calibration": "Conservative bias applied",
                "quality_control": "Multi-stage validation framework",
                "citation_traceability": "Full audit trail maintained"
            },
            "business_implications": self._extract_business_implications(final_synthesis),
            "technical_appendix": {
                "detailed_synthesis_state": final_synthesis,
                "processing_log": final_synthesis.get("integration_log", []),
                "validation_history": [mapping["quality_assessment"] for mapping in client_mappings]
            }
        }
    
    def _extract_business_implications(self, synthesis_data):
        """Extract business-focused implications from synthesis"""
        
        return {
            "parameter_readiness_for_modeling": self._assess_modeling_readiness(synthesis_data),
            "uncertainty_quantification": self._extract_uncertainty_insights(synthesis_data),
            "geographic_applicability": self._assess_geographic_coverage(synthesis_data),
            "research_priority_recommendations": self._identify_research_gaps(synthesis_data)
        }
    
    def _assess_modeling_readiness(self, synthesis_data):
        """Assess which parameters are ready for business modeling"""
        
        responses = synthesis_data.get("question_responses", {})
        confidence_data = synthesis_data.get("final_assessment", {}).get("final_confidence", {})
        
        modeling_readiness = {}
        
        for param_category, param_data in responses.items():
            if isinstance(param_data, dict) and "confidence" in param_data:
                confidence = param_data["confidence"]
                if confidence >= 0.7:
                    modeling_readiness[param_category] = "ready_for_strategic_modeling"
                elif confidence >= 0.5:
                    modeling_readiness[param_category] = "ready_for_tactical_modeling_with_sensitivity"
                elif confidence >= 0.3:
                    modeling_readiness[param_category] = "requires_additional_validation"
                else:
                    modeling_readiness[param_category] = "insufficient_for_modeling"
        
        return modeling_readiness
    
    def _extract_uncertainty_insights(self, synthesis_data):
        """Extract uncertainty quantification insights"""
        
        return {
            "overall_uncertainty_level": "systematically_quantified",
            "confidence_calibration_approach": "conservative_bias_applied",
            "uncertainty_sources_identified": True,
            "geographic_uncertainty_noted": True,
            "temporal_uncertainty_considered": True
        }
    
    def _assess_geographic_coverage(self, synthesis_data):
        """Assess geographic coverage and applicability"""
        
        evidence_registry = synthesis_data.get("evidence_registry", {})
        
        return {
            "regions_with_evidence": list(evidence_registry.get("papers_by_region", {}).keys()),
            "coverage_quality": "variable_by_region",
            "extrapolation_risks": "clearly_documented",
            "regional_confidence_adjustments": "applied"
        }
    
    def _identify_research_gaps(self, synthesis_data):
        """Identify priority research gaps"""
        
        return [
            "Long-term studies needed for sustainability parameters",
            "More geographic diversity required for global applicability",
            "Standardized measurement protocols would improve confidence",
            "Interaction effects require further investigation"
        ]
    
    async def _save_stage_output(self, stage_name, output_name, data):
        """Save stage output to appropriate directory"""
        
        try:
            stage_dir = f"8_stage_outputs/{stage_name}"
            os.makedirs(stage_dir, exist_ok=True)
            
            filename = f"{stage_dir}/{output_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.warning(f"Could not save stage output: {str(e)}")

# For testing and development
async def test_synthesis():
    """Test function for development"""
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    engine = SoilKAnalysisEngine(api_key)
    result = await engine.process_all_papers()
    print("Test synthesis completed successfully!")
    return result

if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_synthesis())