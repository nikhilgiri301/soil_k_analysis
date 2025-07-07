"""
Stage 3A: Paper Synthesizer - Merges parallel extraction tracks
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

class PaperSynthesizer:
    """Stage 3A: Synthesizes generic and soil K extractions into coherent paper understanding"""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.prompt_loader = PromptLoader()
        self.stage_name = "stage_3a_paper_synthesis"
        self.temperature = STAGE_TEMPERATURES[self.stage_name]
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded paper synthesis prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load synthesis prompt: {str(e)}")
            raise
    
    async def synthesize(self, stage_1b_result: Dict[str, Any], stage_2b_result: Dict[str, Any], 
                        paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize validated generic and soil K extractions"""
        
        try:
            # Format synthesis prompt with both validated extractions
            formatted_prompt = self.prompt_template.format(
                paper_title=paper_data.get('filename', 'Unknown'),
                validated_generic_extraction=json.dumps(stage_1b_result, indent=2),
                validated_soilk_extraction=json.dumps(stage_2b_result, indent=2)
            )
            
            # Generate synthesis with creative temperature
            synthesis_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Add synthesis metadata
            synthesis_result['stage'] = '3A'
            synthesis_result['paper_id'] = paper_data.get('filename')
            synthesis_result['synthesis_timestamp'] = datetime.now().isoformat()
            synthesis_result['temperature_used'] = self.temperature
            synthesis_result['input_stages'] = ['1B', '2B']
            
            logging.info(f"Successfully synthesized paper: {paper_data.get('filename')}")
            return synthesis_result
            
        except Exception as e:
            logging.error(f"Stage 3A synthesis failed: {str(e)}")
            return {
                "error": str(e),
                "stage": "3A",
                "paper_id": paper_data.get('filename'),
                "synthesis_confidence": 0.0,
                "synthesis_timestamp": datetime.now().isoformat()
            }

