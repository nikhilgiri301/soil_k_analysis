"""
Stage 2A: Soil K Specific Information Extractor
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

class SoilKExtractor:
    """Stage 2A: Soil K specific information extractor"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_2a_soilk_extraction"
        self.temperature = STAGE_TEMPERATURES[self.stage_name]
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded soil K extraction prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load soil K prompt: {str(e)}")
            raise
    
    async def extract(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract soil K specific information from paper"""
        
        try:
            # Format prompt with paper data
            formatted_prompt = self.prompt_template.format(
                paper_title=paper_data.get('filename', 'Unknown'),
                paper_text=paper_data.get('full_text', '')[:15000],
                table_data=str(paper_data.get('table_data', [])[:3])
            )
            
            # Generate soil K extraction
            result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Add metadata
            result['stage'] = '2A'
            result['paper_id'] = paper_data.get('filename')
            result['processing_timestamp'] = datetime.now().isoformat()
            result['temperature_used'] = self.temperature
            result['extraction_type'] = 'soil_k_specific'
            
            logging.info(f"Successfully processed Stage 2A for {paper_data.get('filename')}")
            return result
            
        except Exception as e:
            logging.error(f"Stage 2A soil K extraction failed: {str(e)}")
            return {
                "error": str(e),
                "stage": "2A",
                "paper_id": paper_data.get('filename'),
                "extraction_confidence": 0.0,
                "processing_timestamp": datetime.now().isoformat()
            }
