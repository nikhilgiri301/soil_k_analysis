"""
Stage 4B: Mapping Validator
"""

import json
from datetime import datetime
from typing import Dict, Any
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_loader import PromptLoader
from utils.gemini_client import GeminiClient
from utils.config import STAGE_TEMPERATURES

class MappingValidator:
    """Stage 4B: Validates client question mapping accuracy"""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.prompt_loader = PromptLoader()
        self.stage_name = "stage_4b_mapping_validation"
        self.temperature = STAGE_TEMPERATURES[self.stage_name]
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded mapping validation prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load mapping validation prompt: {str(e)}")
            raise
    
    async def validate_mapping(self, stage_4a_result: Dict[str, Any], 
                              stage_3b_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 4A client mapping accuracy"""
        
        try:
            # Format validation prompt
            formatted_prompt = self.prompt_template.format(
                stage_4a_mapping=json.dumps(stage_4a_result, indent=2),
                stage_3b_synthesis=json.dumps(stage_3b_result, indent=2)
            )
            
            # Generate validation with strict temperature
            validation_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Add metadata
            validation_result['stage'] = '4B'
            validation_result['paper_id'] = stage_3b_result.get('paper_id', 'unknown')
            validation_result['validation_timestamp'] = datetime.now().isoformat()
            validation_result['temperature_used'] = self.temperature
            validation_result['validated_stage'] = '4A'
            
            logging.info(f"Successfully validated mapping: {stage_3b_result.get('paper_id')}")
            return validation_result
            
        except Exception as e:
            logging.error(f"Stage 4B mapping validation failed: {str(e)}")
            return {
                "error": str(e),
                "stage": "4B",
                "paper_id": stage_3b_result.get('paper_id', 'unknown'),
                "validation_confidence": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }
