"""
Stage 1B: Generic Extraction Validator
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

class GenericValidator:
    """Stage 1B: Validates generic paper extraction for accuracy and completeness"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_1b_generic_validation"
        self.temperature = STAGE_TEMPERATURES.get(self.stage_name, 0.1)
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded validation prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load validation prompt: {str(e)}")
            raise
    
    async def validate(self, stage_1a_result: Dict[str, Any], paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 1A extraction against original paper"""
        
        try:
            # Check if stage_1a failed
            if not stage_1a_result.get('success', False):
                return {
                    "success": False,
                    "stage": "1B",
                    "paper_id": paper_data.get('filename'),
                    "validation_errors": ["Stage 1A extraction failed - cannot validate"],
                    "confidence_score": 0.0,
                    "validation_timestamp": datetime.now().isoformat()
                }
            
            # Format validation prompt
            formatted_prompt = self.prompt_template.format(
                paper_title=paper_data.get('filename', 'Unknown'),
                paper_text=paper_data.get('full_text', '')[:15000],
                table_data=str(paper_data.get('table_data', [])[:3]),
                stage_1a_results=json.dumps(stage_1a_result, indent=2)
            )
            
            # Generate validation with strict temperature
            validation_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Ensure result is dict
            if not isinstance(validation_result, dict):
                validation_result = {"success": False, "error": "Invalid response format"}
            
            # Add validation metadata
            validation_result['success'] = validation_result.get('success', True)
            validation_result['stage'] = '1B'
            validation_result['paper_id'] = paper_data.get('filename')
            validation_result['validation_timestamp'] = datetime.now().isoformat()
            validation_result['temperature_used'] = self.temperature
            validation_result['validated_stage'] = '1A'
            
            logging.info(f"Successfully validated Stage 1A for {paper_data.get('filename')}")
            return validation_result
            
        except Exception as e:
            logging.error(f"Stage 1B validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stage": "1B",
                "paper_id": paper_data.get('filename'),
                "validation_confidence": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }