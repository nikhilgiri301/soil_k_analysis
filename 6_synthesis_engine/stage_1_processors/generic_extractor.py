"""
Stage 1A: Generic Paper Information Extractor
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_loader import PromptLoader
from utils.gemini_client import GeminiClient
from utils.config import STAGE_TEMPERATURES

class GenericExtractor:
    """Stage 1A: Generic paper information extractor using file-based prompts"""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.prompt_loader = PromptLoader()
        self.stage_name = "stage_1a_generic_extraction"
        self.temperature = STAGE_TEMPERATURES[self.stage_name]
        
        # Load prompt template from file
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded prompt template for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load prompt for {self.stage_name}: {str(e)}")
            raise
    
    async def extract(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract generic paper information without soil K bias"""
        
        try:
            # Format prompt with paper data using file-based template
            formatted_prompt = self.prompt_template.format(
                paper_title=paper_data.get('filename', 'Unknown'),
                paper_text=paper_data.get('full_text', '')[:15000],  # Use Gemini's large context
                table_data=str(paper_data.get('table_data', [])[:3])  # First 3 tables for context
            )
            
            # Generate content using Gemini with proper temperature
            result = await self.client.generate_json_content(
                formatted_prompt, 
                temperature=self.temperature
            )
            
            # Add metadata
            result['stage'] = '1A'
            result['paper_id'] = paper_data.get('filename')
            result['processing_timestamp'] = datetime.now().isoformat()
            result['temperature_used'] = self.temperature
            
            logging.info(f"Successfully processed Stage 1A for {paper_data.get('filename')}")
            return result
            
        except Exception as e:
            logging.error(f"Stage 1A extraction failed for {paper_data.get('filename')}: {str(e)}")
            return {
                "error": str(e),
                "stage": "1A",
                "paper_id": paper_data.get('filename'),
                "extraction_confidence": 0.0,
                "processing_timestamp": datetime.now().isoformat()
            }
