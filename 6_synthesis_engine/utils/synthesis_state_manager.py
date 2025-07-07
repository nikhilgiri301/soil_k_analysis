# 6_synthesis_engine/utils/synthesis_state_manager.py

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

class SynthesisStateManager:
    """Manages iterative synthesis state persistence and evolution"""
    
    def __init__(self):
        self.state_dir = "12_synthesis_state"
        self.checkpoints_dir = f"{self.state_dir}/checkpoints"
        self.incremental_dir = f"{self.state_dir}/incremental_states"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all state directories exist"""
        dirs = [self.state_dir, self.checkpoints_dir, self.incremental_dir]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def initialize_synthesis_state(self) -> Dict[str, Any]:
        """Initialize empty synthesis state matching prompt expectations"""
        
        initial_state = {
            "synthesis_metadata": {
                "initialization_timestamp": datetime.now().isoformat(),
                "papers_integrated": 0,
                "current_version": "1.0.0",
                "state_type": "iterative_synthesis"
            },
            "question_responses": {
                "quantitative_parameters": {},
                "temporal_dynamics": {},
                "probability_assessment": {},
                "regional_variations": {},
                "agricultural_integration": {},
                "scaling_extrapolation": {}
            },
            "evidence_registry": {
                "papers_by_region": {},
                "papers_by_timeframe": {},
                "methodological_approaches": {},
                "confidence_levels": {}
            },
            "conflict_registry": {
                "identified_conflicts": [],
                "resolved_conflicts": [],
                "unresolved_conflicts": []
            },
            "pattern_recognition": {
                "emerging_patterns": [],
                "validated_patterns": [],
                "contradicted_patterns": []
            },
            "confidence_tracking": {
                "overall_confidence": 0.0,
                "question_confidence": {},
                "regional_confidence": {},
                "temporal_confidence": {}
            },
            "evidence_gaps": {
                "critical_gaps": [],
                "moderate_gaps": [],
                "minor_gaps": []
            }
        }
        
        # Save initial state
        self.save_state(initial_state, "initial")
        return initial_state
    
    def save_state(self, state: Dict[str, Any], stage_marker: str):
        """Save synthesis state with timestamp and stage marker"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"synthesis_state_{stage_marker}_{timestamp}.json"
        filepath = f"{self.state_dir}/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            logging.info(f"Synthesis state saved: {filename}")
        except Exception as e:
            logging.error(f"Failed to save synthesis state: {str(e)}")
            raise
    
    async def save_incremental_state(self, state: Dict[str, Any], paper_index: int, paper_id: str):
        """Save incremental state after each paper integration"""
        filename = f"incremental_{paper_index:03d}_{paper_id.replace('.pdf', '')}.json"
        filepath = f"{self.incremental_dir}/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            logging.info(f"Incremental state saved: {filename}")
        except Exception as e:
            logging.error(f"Failed to save incremental state: {str(e)}")
            raise
    
    async def save_final_synthesis(self, final_synthesis: Dict[str, Any]):
        """Save final synthesis with comprehensive metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_synthesis_{timestamp}.json"
        filepath = f"9_final_synthesis/{filename}"
        
        try:
            os.makedirs("9_final_synthesis", exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(final_synthesis, f, indent=2)
            logging.info(f"Final synthesis saved: {filename}")
        except Exception as e:
            logging.error(f"Failed to save final synthesis: {str(e)}")
            raise
    
    def validate_storage(self) -> bool:
        """Validate storage system is functional"""
        try:
            test_state = {"test": "validation"}
            test_file = f"{self.state_dir}/validation_test.json"
            
            with open(test_file, 'w') as f:
                json.dump(test_state, f)
            
            with open(test_file, 'r') as f:
                loaded = json.load(f)
            
            os.remove(test_file)
            return loaded == test_state
            
        except Exception as e:
            logging.error(f"Storage validation failed: {str(e)}")
            return False 
