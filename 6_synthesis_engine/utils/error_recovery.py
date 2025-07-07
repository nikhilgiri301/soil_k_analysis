# 6_synthesis_engine/utils/error_recovery.py

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import traceback

class ErrorRecovery:
    """Comprehensive error recovery and resilience management"""
    
    def __init__(self):
        self.recovery_log = []
        self.error_patterns = {}
        self.recovery_strategies = self.initialize_recovery_strategies()
    
    def initialize_recovery_strategies(self) -> Dict[str, Any]:
        """Define recovery strategies for different error types"""
        return {
            "api_error": {
                "strategy": "retry_with_backoff",
                "max_retries": 3,
                "backoff_factor": 2,
                "recoverable": True
            },
            "json_parsing_error": {
                "strategy": "prompt_adjustment",
                "max_retries": 2,
                "recoverable": True
            },
            "validation_error": {
                "strategy": "fallback_processing",
                "max_retries": 1,
                "recoverable": True
            },
            "synthesis_state_error": {
                "strategy": "checkpoint_rollback",
                "max_retries": 1,
                "recoverable": True
            },
            "critical_system_error": {
                "strategy": "graceful_shutdown",
                "max_retries": 0,
                "recoverable": False
            }
        }
    
    async def attempt_recovery(self, error: Exception) -> Dict[str, Any]:
        """Main recovery coordination"""
        
        error_type = self.classify_error(error)
        recovery_strategy = self.recovery_strategies.get(error_type, 
                                                       self.recovery_strategies["critical_system_error"])
        
        recovery_result = {
            "error_type": error_type,
            "error_message": str(error),
            "recovery_strategy": recovery_strategy["strategy"],
            "recoverable": recovery_strategy["recoverable"],
            "recovery_timestamp": datetime.now().isoformat(),
            "checkpoint": None
        }
        
        if recovery_strategy["recoverable"]:
            try:
                if recovery_strategy["strategy"] == "checkpoint_rollback":
                    checkpoint = await self.find_latest_valid_checkpoint()
                    recovery_result["checkpoint"] = checkpoint
                
                self.recovery_log.append(recovery_result)
                logging.info(f"Recovery attempted for {error_type}: {recovery_strategy['strategy']}")
                
            except Exception as recovery_error:
                logging.error(f"Recovery attempt failed: {str(recovery_error)}")
                recovery_result["recoverable"] = False
        
        return recovery_result
    
    async def handle_paper_error(self, paper: Dict[str, Any], paper_index: int, 
                                error: Exception, completed_papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle errors during individual paper processing"""
        
        error_record = {
            "paper_id": paper.get('filename', 'unknown'),
            "paper_index": paper_index,
            "error": str(error),
            "error_type": self.classify_error(error),
            "completed_papers_count": len(completed_papers),
            "error_timestamp": datetime.now().isoformat()
        }
        
        # Determine if processing can continue
        continue_processing = self.should_continue_processing(error, paper_index, len(completed_papers))
        
        if continue_processing:
            logging.warning(f"Skipping paper {paper.get('filename')} due to error, continuing with remaining papers")
        else:
            logging.error(f"Critical error processing paper {paper.get('filename')}, stopping processing")
        
        return {
            "continue": continue_processing,
            "error_record": error_record,
            "recovery_action": "skip_paper" if continue_processing else "stop_processing"
        }
    
    async def handle_integration_error(self, paper_mapping: Dict[str, Any], integration_index: int,
                                     error: Exception, current_synthesis_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors during iterative synthesis integration"""
        
        error_record = {
            "paper_id": paper_mapping.get('paper_id', 'unknown'),
            "integration_index": integration_index,
            "error": str(error),
            "error_type": self.classify_error(error),
            "synthesis_state_version": current_synthesis_state.get('synthesis_metadata', {}).get('current_version'),
            "error_timestamp": datetime.now().isoformat()
        }
        
        # Attempt to recover synthesis state
        recovery_result = await self.recover_synthesis_state(current_synthesis_state, integration_index)
        
        return {
            "continue": recovery_result["recoverable"],
            "recovered_state": recovery_result.get("recovered_state", current_synthesis_state),
            "error_record": error_record,
            "recovery_action": recovery_result["action"]
        }
    
    def classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate recovery strategy"""
        
        error_str = str(error).lower()
        
        if "api" in error_str or "rate limit" in error_str or "quota" in error_str:
            return "api_error"
        elif "json" in error_str or "parse" in error_str:
            return "json_parsing_error"
        elif "validation" in error_str:
            return "validation_error"
        elif "synthesis" in error_str or "state" in error_str:
            return "synthesis_state_error"
        else:
            return "critical_system_error"
    
    def should_continue_processing(self, error: Exception, paper_index: int, completed_count: int) -> bool:
        """Determine if processing should continue after paper error"""
        
        error_type = self.classify_error(error)
        
        # Don't continue for critical errors
        if error_type == "critical_system_error":
            return False
        
        # Continue if we have reasonable completion rate
        if completed_count > 0 and (completed_count / (paper_index + 1)) > 0.5:
            return True
        
        # Continue for non-critical errors early in processing
        if paper_index < 5 and error_type != "critical_system_error":
            return True
        
        return False
    
    async def recover_synthesis_state(self, current_state: Dict[str, Any], 
                                    integration_index: int) -> Dict[str, Any]:
        """Attempt to recover synthesis state after integration error"""
        
        try:
            # Look for previous valid state
            if integration_index > 0:
                # Try to load previous incremental state
                previous_state_file = f"12_synthesis_state/incremental_states/incremental_{integration_index-1:03d}_*.json"
                # Implementation would load the previous state
                
                return {
                    "recoverable": True,
                    "recovered_state": current_state,  # Would be loaded state
                    "action": "rollback_to_previous",
                    "rollback_index": integration_index - 1
                }
            else:
                # Initialize fresh state
                return {
                    "recoverable": True,
                    "recovered_state": self.create_minimal_state(),
                    "action": "initialize_minimal_state"
                }
                
        except Exception as recovery_error:
            logging.error(f"State recovery failed: {str(recovery_error)}")
            return {
                "recoverable": False,
                "action": "unrecoverable_state_error"
            }
    
    def create_minimal_state(self) -> Dict[str, Any]:
        """Create minimal synthesis state for recovery"""
        return {
            "synthesis_metadata": {
                "initialization_timestamp": datetime.now().isoformat(),
                "papers_integrated": 0,
                "current_version": "1.0.0-recovery",
                "state_type": "recovery_synthesis"
            },
            "question_responses": {},
            "evidence_registry": {},
            "conflict_registry": {"identified_conflicts": [], "resolved_conflicts": [], "unresolved_conflicts": []},
            "pattern_recognition": {"emerging_patterns": [], "validated_patterns": [], "contradicted_patterns": []},
            "confidence_tracking": {"overall_confidence": 0.0},
            "evidence_gaps": {"critical_gaps": [], "moderate_gaps": [], "minor_gaps": []}
        } 
