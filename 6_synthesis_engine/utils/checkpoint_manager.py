"""
Checkpoint management for synthesis state persistence and recovery
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

class CheckpointManager:
    """Manages checkpoints for synthesis state and paper processing"""
    
    def __init__(self):
        self.checkpoint_dir = Path("14_backup_recovery/state_backups")
        self.tracking_dir = Path("13_iteration_tracking/paper_sequence")
        self.ensure_directories()
        self.checkpoint_registry = {}
        
    def ensure_directories(self):
        """Ensure checkpoint directories exist"""
        dirs = [
            self.checkpoint_dir,
            self.tracking_dir,
            Path("14_backup_recovery"),
            Path("13_iteration_tracking"),
            Path("13_iteration_tracking/integration_logs"),
            Path("13_iteration_tracking/state_evolution")
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            
        logging.info("Checkpoint directories initialized")
    
    async def create_checkpoint(self, stage: str, paper_index: int, paper_id: str) -> str:
        """Create checkpoint before processing each paper"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_id = f"{stage}_{paper_index:03d}_{timestamp}"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "stage": stage,
            "paper_index": paper_index,
            "paper_id": paper_id,
            "timestamp": datetime.now().isoformat(),
            "checkpoint_type": "paper_processing"
        }
        
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.checkpoint_registry[checkpoint_id] = checkpoint_data
            logging.info(f"Created checkpoint: {checkpoint_id}")
            
            return checkpoint_id
            
        except Exception as e:
            logging.error(f"Failed to create checkpoint {checkpoint_id}: {str(e)}")
            raise
    
    async def create_synthesis_checkpoint(self, synthesis_state: Dict[str, Any], 
                                        integration_index: int, paper_id: str) -> str:
        """Create checkpoint before synthesis integration"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_id = f"synthesis_{integration_index:03d}_{timestamp}"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "integration_index": integration_index,
            "paper_id": paper_id,
            "synthesis_state": synthesis_state,
            "timestamp": datetime.now().isoformat(),
            "checkpoint_type": "synthesis_integration"
        }
        
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.checkpoint_registry[checkpoint_id] = {
                "checkpoint_id": checkpoint_id,
                "integration_index": integration_index,
                "paper_id": paper_id,
                "timestamp": checkpoint_data["timestamp"],
                "checkpoint_type": "synthesis_integration",
                "file_path": str(checkpoint_file)
            }
            
            logging.info(f"Created synthesis checkpoint: {checkpoint_id}")
            return checkpoint_id
            
        except Exception as e:
            logging.error(f"Failed to create synthesis checkpoint {checkpoint_id}: {str(e)}")
            raise
    
    async def save_progress(self, checkpoint_id: str, stage_name: str, result_data: Dict[str, Any]):
        """Save progress data associated with checkpoint"""
        
        progress_file = self.tracking_dir / f"{checkpoint_id}_progress.json"
        
        progress_data = {
            "checkpoint_id": checkpoint_id,
            "stage_name": stage_name,
            "result_data": result_data,
            "save_timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
            
            logging.debug(f"Saved progress for checkpoint: {checkpoint_id}")
            
        except Exception as e:
            logging.error(f"Failed to save progress for {checkpoint_id}: {str(e)}")
            raise
    
    def validate_checkpoint_system(self) -> bool:
        """Validate checkpoint system is functional"""
        
        try:
            # Test checkpoint creation
            test_checkpoint = {
                "test": "validation",
                "timestamp": datetime.now().isoformat()
            }
            
            test_file = self.checkpoint_dir / "test_checkpoint.json"
            
            with open(test_file, 'w') as f:
                json.dump(test_checkpoint, f)
            
            with open(test_file, 'r') as f:
                loaded = json.load(f)
            
            os.remove(test_file)
            
            is_valid = loaded["test"] == "validation"
            logging.info(f"Checkpoint system validation: {'passed' if is_valid else 'failed'}")
            
            return is_valid
            
        except Exception as e:
            logging.error(f"Checkpoint system validation failed: {str(e)}")
            return False
    
    def list_checkpoints(self, checkpoint_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available checkpoints"""
        
        checkpoints = []
        
        for checkpoint_id, data in self.checkpoint_registry.items():
            if checkpoint_type is None or data.get("checkpoint_type") == checkpoint_type:
                checkpoints.append(data)
        
        # Sort by timestamp
        checkpoints.sort(key=lambda x: x.get("timestamp", ""))
        
        return checkpoints
    
    def get_latest_checkpoint(self, checkpoint_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent checkpoint"""
        
        checkpoints = self.list_checkpoints(checkpoint_type)
        
        if checkpoints:
            return checkpoints[-1]
        
        return None
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint data"""
        
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            logging.error(f"Checkpoint file not found: {checkpoint_id}")
            return None
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logging.error(f"Failed to load checkpoint {checkpoint_id}: {str(e)}")
            return None
 
