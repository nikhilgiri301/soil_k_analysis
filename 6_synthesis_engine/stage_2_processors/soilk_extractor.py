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
from utils.json_config import STAGE_TEMPERATURES

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
    
    def _format_tables_for_ai(self, table_data_list):
        """Format structured table data for optimal AI comprehension (Phase 2+3 fix)"""
        if not table_data_list:
            return "No tables available"
        
        formatted_tables = []
        for i, table in enumerate(table_data_list):
            formatted_table = {
                'table_id': table.get('table_id', f'table_{i}'),
                'page': table.get('page', 'unknown'),
                'extraction_accuracy': f"{table.get('accuracy', 0):.1f}%",
                'structured_data': self._convert_table_to_readable_format(table.get('data', []))
            }
            formatted_tables.append(formatted_table)
        
        # Create comprehensive table summary
        summary = f"Available Tables: {len(formatted_tables)} total\n\n"
        for i, table in enumerate(formatted_tables):
            summary += f"Table {i+1} (Page {table['page']}):\n"
            summary += f"ID: {table['table_id']}\n"
            summary += f"Extraction Accuracy: {table['extraction_accuracy']}\n"
            summary += f"Data:\n{table['structured_data']}\n\n"
        
        return summary
    
    def _convert_table_to_readable_format(self, table_data):
        """Convert table data arrays to readable table format"""
        if not table_data:
            return "No data available"
        
        # Convert structured data to readable table format
        formatted_rows = []
        for row in table_data:
            if isinstance(row, dict):
                # Extract values in order of keys
                row_values = []
                for key in sorted(row.keys(), key=lambda x: int(x) if x.isdigit() else float('inf')):
                    value = str(row[key]).strip()
                    if value:  # Only include non-empty values
                        row_values.append(value)
                if row_values:  # Only add non-empty rows
                    formatted_rows.append(' | '.join(row_values))
        
        return '\n'.join(formatted_rows) if formatted_rows else "No readable data available"
    
    async def extract(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract soil K specific information from paper"""
        
        try:
            # Format prompt with paper data
            formatted_prompt = self.prompt_template.format(
                paper_title=paper_data.get('filename', 'Unknown'),
                paper_text=paper_data.get('full_text', ''),  # Full text, no truncation (Phase 1 fix)
                table_data=self._format_tables_for_ai(paper_data.get('table_data', []))  # All tables, structured format (Phase 2+3 fix)
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
