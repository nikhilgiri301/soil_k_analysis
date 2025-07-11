"""
Stage 3B: Synthesis Validator
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
from utils.json_config import STAGE_TEMPERATURES

class SynthesisValidator:
    """Stage 3B: Validates paper synthesis results"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_3b_synthesis_validation"
        self.temperature = STAGE_TEMPERATURES.get(self.stage_name, 0.1)
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded synthesis validation prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load synthesis validation prompt: {str(e)}")
            raise
    
    async def validate(self, stage_3a_result: Dict[str, Any], 
                      stage_1b_result: Dict[str, Any],
                      stage_2b_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 3A synthesis results"""
        
        try:
            # If it's in approved_results, it's good - no checking needed
            
            # Format validation prompt using string replacement to avoid JSON brace conflicts
            formatted_prompt = self.prompt_template.replace(
                '{stage_1b_results}', json.dumps(stage_1b_result, indent=2)
            ).replace(
                '{stage_2b_results}', json.dumps(stage_2b_result, indent=2)
            ).replace(
                '{stage_3a_results}', json.dumps(stage_3a_result, indent=2)
            )
            
            # Generate validation
            validation_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Ensure result is dict
            if not isinstance(validation_result, dict):
                validation_result = {"success": False, "error": "Invalid response format"}
            
            # Add metadata
            validation_result['success'] = validation_result.get('success', True)
            validation_result['stage'] = '3B'
            validation_result['validation_timestamp'] = datetime.now().isoformat()
            validation_result['temperature_used'] = self.temperature
            validation_result['validated_stage'] = '3A'
            
            logging.info("Successfully validated Stage 3A synthesis")
            return validation_result
            
        except Exception as e:
            logging.error(f"Stage 3B validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stage": "3B",
                "validation_confidence": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }