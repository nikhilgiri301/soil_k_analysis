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
from utils.json_config import STAGE_TEMPERATURES

class PaperSynthesizer:
    """Stage 3A: Synthesizes generic and soil K extractions into coherent paper understanding"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_3a_paper_synthesis"
        self.temperature = STAGE_TEMPERATURES[self.stage_name]
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded paper synthesis prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load synthesis prompt: {str(e)}")
            raise
    
    async def synthesize(self, stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize validated generic and soil K extractions"""
        
        try:
            # Extract stage results
            stage_1a_results = stage_results.get('stage_1a_results', {})
            stage_1b_results = stage_results.get('stage_1b_results', {})
            stage_2a_results = stage_results.get('stage_2a_results', {})
            stage_2b_results = stage_results.get('stage_2b_results', {})
            
            logging.info(f"Formatting prompt with 1B data: {len(str(stage_1b_results))} chars, 2B data: {len(str(stage_2b_results))} chars")
            
            # Format synthesis prompt with both validated extractions
            # Use simple string replacement instead of .format() to avoid issues with JSON braces
            try:
                formatted_prompt = self.prompt_template.replace(
                    '{stage_1b_results}', json.dumps(stage_1b_results, indent=2)
                ).replace(
                    '{stage_2b_results}', json.dumps(stage_2b_results, indent=2)
                )
            except Exception as format_error:
                logging.error(f"Prompt formatting failed: {str(format_error)}")
                raise
            
            # Generate synthesis with creative temperature
            logging.info(f"Sending synthesis prompt of length: {len(formatted_prompt)} characters")
            synthesis_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature,
                stage_name="stage_3a_paper_synthesis",
                paper_id=stage_1a_results.get('paper_id', 'Unknown')
            )
            
            # Check if we got an error from the API
            if 'error' in synthesis_result:
                logging.error(f"API returned error: {synthesis_result.get('error')}")
                return synthesis_result
            
            # Add synthesis metadata
            synthesis_result['stage'] = '3A'
            synthesis_result['paper_id'] = stage_1a_results.get('paper_id', 'Unknown')
            synthesis_result['synthesis_timestamp'] = datetime.now().isoformat()
            synthesis_result['temperature_used'] = self.temperature
            synthesis_result['input_stages'] = ['1B', '2B']
            
            logging.info(f"Successfully synthesized paper: {stage_1a_results.get('paper_id', 'Unknown')}")
            return synthesis_result
            
        except Exception as e:
            logging.error(f"Stage 3A synthesis failed: {str(e)}")
            return {
                "error": str(e),
                "stage": "3A",
                "paper_id": stage_results.get('stage_1a_results', {}).get('paper_id', 'Unknown'),
                "synthesis_confidence": 0.0,
                "synthesis_timestamp": datetime.now().isoformat()
            }

