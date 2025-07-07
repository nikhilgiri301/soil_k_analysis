"""
Stage 2B: Soil K Extraction Validator
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

class SoilKValidator:
    """Stage 2B: Validates soil K specific extraction"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_2b_soilk_validation"
        self.temperature = STAGE_TEMPERATURES.get(self.stage_name, 0.1)
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded soil K validation prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load soil K validation prompt: {str(e)}")
            raise
    
    async def validate(self, stage_2a_result: Dict[str, Any], paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 2A soil K extraction"""
        
        try:
            # Check if stage_2a failed
            if not stage_2a_result.get('success', False):
                return {
                    "success": False,
                    "stage": "2B",
                    "paper_id": paper_data.get('filename'),
                    "validation_errors": ["Stage 2A soil K extraction failed - cannot validate"],
                    "confidence_score": 0.0,
                    "validation_timestamp": datetime.now().isoformat()
                }
            
            # Format validation prompt
            formatted_prompt = self.prompt_template.format(
                paper_title=paper_data.get('filename', 'Unknown'),
                paper_text=paper_data.get('full_text', '')[:15000],
                table_data=str(paper_data.get('table_data', [])[:3]),
                stage_2a_results=json.dumps(stage_2a_result, indent=2)
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
            validation_result['stage'] = '2B'
            validation_result['paper_id'] = paper_data.get('filename')
            validation_result['validation_timestamp'] = datetime.now().isoformat()
            validation_result['temperature_used'] = self.temperature
            validation_result['validated_stage'] = '2A'
            
            logging.info(f"Successfully validated Stage 2A for {paper_data.get('filename')}")
            return validation_result
            
        except Exception as e:
            logging.error(f"Stage 2B validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stage": "2B",
                "paper_id": paper_data.get('filename'),
                "validation_confidence": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }