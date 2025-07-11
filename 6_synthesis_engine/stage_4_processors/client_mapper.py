"""
Stage 4A: Client Question Mapper
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

class ClientMapper:
    """Stage 4A: Maps paper synthesis to client question architecture"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_4a_client_mapping"
        self.temperature = STAGE_TEMPERATURES[self.stage_name]
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded client mapping prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load client mapping prompt: {str(e)}")
            raise
    
    async def map_to_client(self, stage_3b_result: Dict[str, Any], 
                           client_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Map validated synthesis to client question architecture"""
        
        try:
            # Format mapping prompt using string replacement to avoid JSON brace conflicts
            formatted_prompt = self.prompt_template.replace(
                '{client_question_tree}', json.dumps(client_architecture.get('question_tree', {}), indent=2)
            ).replace(
                '{stage_3b_results}', json.dumps(stage_3b_result, indent=2)
            )
            
            # Generate mapping with precise temperature
            mapping_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Add metadata
            mapping_result['stage'] = '4A'
            mapping_result['paper_id'] = stage_3b_result.get('paper_id', 'unknown')
            mapping_result['mapping_timestamp'] = datetime.now().isoformat()
            mapping_result['temperature_used'] = self.temperature
            mapping_result['client_architecture_version'] = client_architecture.get('version', '1.0')
            
            logging.info(f"Successfully mapped to client questions: {stage_3b_result.get('paper_id')}")
            return mapping_result
            
        except Exception as e:
            logging.error(f"Stage 4A client mapping failed: {str(e)}")
            return {
                "error": str(e),
                "stage": "4A",
                "paper_id": stage_3b_result.get('paper_id', 'unknown'),
                "mapping_confidence": 0.0,
                "mapping_timestamp": datetime.now().isoformat()
            }
