# 6_synthesis_engine/utils/data_adapter.py

import json
import os
import logging
from typing import Dict, List, Any

class Phase1DataAdapter:
    """Adapter to convert Phase 1 data to Phase 2 expected format"""
    
    def __init__(self, synthesis_ready_dir="3_synthesis_ready"):
        self.synthesis_ready_dir = synthesis_ready_dir
    
    def load_and_adapt_papers(self) -> List[Dict[str, Any]]:
        """Load Phase 1 data and adapt to Phase 2 format"""
        
        papers = []
        synthesis_file = os.path.join(self.synthesis_ready_dir, "synthesis_ready_data.json")
        
        if not os.path.exists(synthesis_file):
            logging.error(f"Synthesis ready file not found: {synthesis_file}")
            return []
        
        try:
            with open(synthesis_file, 'r', encoding='utf-8') as f:
                phase1_data = json.load(f)
            
            for paper_id, paper_data in phase1_data.items():
                adapted_paper = self.adapt_paper_structure(paper_id, paper_data)
                papers.append(adapted_paper)
            
            logging.info(f"Successfully adapted {len(papers)} papers from Phase 1 data")
            return papers
            
        except Exception as e:
            logging.error(f"Failed to load/adapt Phase 1 data: {str(e)}")
            return []
    
    def adapt_paper_structure(self, paper_id: str, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Phase 1 paper structure to Phase 2 expected format"""
        
        # Extract table data and count
        tables = paper_data.get('table_data', [])
        table_count = len(tables) if isinstance(tables, list) else 0
        
        # Ensure full_text exists
        full_text = paper_data.get('full_text', '')
        if not full_text and 'text_extract' in paper_data:
            full_text = paper_data['text_extract']
        
        adapted = {
            'filename': paper_id,
            'full_text': full_text,
            'table_data': tables,
            'table_count': table_count,
            'processing_quality': paper_data.get('processing_quality', {}),
            'metadata': {
                'extracted_timestamp': paper_data.get('processing_timestamp'),
                'text_length': len(full_text),
                'tables_found': table_count
            }
        }
        
        return adapted