# 6_synthesis_engine/utils/data_adapter.py

import json
import os
import logging
from typing import Dict, List, Any

class Phase1DataAdapter:
    """Adapter to convert Phase 1 data to Phase 2 expected format"""
    
    def __init__(self, synthesis_ready_dir="3_synthesis_ready"):
        self.synthesis_ready_dir = synthesis_ready_dir
    
    def load_and_adapt_papers(self, max_papers: int = None) -> List[Dict[str, Any]]:
        """Load Phase 1 data from individual paper files and adapt to Phase 2 format"""
        
        papers = []
        
        if not os.path.exists(self.synthesis_ready_dir):
            logging.error(f"Synthesis ready directory not found: {self.synthesis_ready_dir}")
            return []
        
        try:
            # Get all individual paper JSON files (exclude complete_dataset.json)
            paper_files = [f for f in os.listdir(self.synthesis_ready_dir) 
                          if f.endswith('.json') and f != 'complete_dataset.json']
            
            # Sort files for consistent ordering
            paper_files.sort()
            
            # Apply limit if specified
            if max_papers:
                paper_files = paper_files[:max_papers]
                logging.info(f"Limiting to first {max_papers} papers")
            
            # Load each paper file
            for paper_file in paper_files:
                paper_path = os.path.join(self.synthesis_ready_dir, paper_file)
                try:
                    with open(paper_path, 'r', encoding='utf-8') as f:
                        paper_data = json.load(f)
                    
                    # The paper data is already in the right format from prepare_synthesis_data.py
                    # Just ensure it has the required fields
                    adapted_paper = self.ensure_paper_format(paper_data)
                    papers.append(adapted_paper)
                    
                except Exception as e:
                    logging.warning(f"Failed to load paper {paper_file}: {str(e)}")
                    continue
            
            logging.info(f"Successfully loaded {len(papers)} papers from individual files")
            return papers
            
        except Exception as e:
            logging.error(f"Failed to load papers from directory: {str(e)}")
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
    
    def ensure_paper_format(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure paper data has all required fields for synthesis engine"""
        
        # The individual paper files from prepare_synthesis_data.py already contain
        # full_text and table_data, so we just need to ensure consistency
        
        # Extract filename without .pdf extension for consistency
        filename = paper_data.get('filename', 'unknown')
        if filename.endswith('.pdf'):
            base_filename = filename
        else:
            base_filename = filename + '.pdf'  # Add .pdf if missing
        
        # Extract table data and count
        tables = paper_data.get('table_data', [])
        
        # Get table count from either table_data length or table_extraction info
        if isinstance(tables, list):
            table_count = len(tables)
        elif 'table_extraction' in paper_data:
            table_count = paper_data['table_extraction'].get('table_count', 0)
        else:
            table_count = 0
        
        # Ensure full_text exists
        full_text = paper_data.get('full_text', '')
        
        ensured = {
            'filename': base_filename,
            'full_text': full_text,
            'table_data': tables,
            'table_count': table_count,
            'processing_quality': paper_data.get('quality_metrics', {}),
            'metadata': {
                'extracted_timestamp': paper_data.get('processing_timestamp'),
                'text_length': len(full_text),
                'tables_found': table_count,
                'source_file': filename
            }
        }
        
        return ensured