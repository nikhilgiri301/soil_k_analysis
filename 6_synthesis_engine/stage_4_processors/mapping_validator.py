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
    """Stage 4B: Validates client mapping results"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_4b_mapping_validation"
        self.temperature = STAGE_TEMPERATURES.get(self.stage_name, 0.1)
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded mapping validation prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load mapping validation prompt: {str(e)}")
            raise
    
    async def validate(self, stage_4a_result: Dict[str, Any], 
                      client_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 4A client mapping results"""
        
        try:
            # Check if stage_4a failed
            if not stage_4a_result.get('success', False):
                return {
                    "success": False,
                    "stage": "4B",
                    "validation_errors": ["Stage 4A client mapping failed - cannot validate"],
                    "confidence_score": 0.0,
                    "validation_timestamp": datetime.now().isoformat()
                }
            
            # Format validation prompt
            formatted_prompt = self.prompt_template.format(
                mapping_result=json.dumps(stage_4a_result, indent=2),
                client_questions=json.dumps(client_architecture, indent=2)
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
            validation_result['stage'] = '4B'
            validation_result['validation_timestamp'] = datetime.now().isoformat()
            validation_result['temperature_used'] = self.temperature
            validation_result['validated_stage'] = '4A'
            
            logging.info("Successfully validated Stage 4A client mapping")
            return validation_result
            
        except Exception as e:
            logging.error(f"Stage 4B validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stage": "4B",
                "validation_confidence": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }