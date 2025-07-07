import os
import json
import re
from datetime import datetime
from pathlib import Path

class SynthesisDataPreparator:
    def __init__(self, processed_dir="2_processed_data", synthesis_dir="3_synthesis_ready"):
        self.processed_dir = processed_dir
        self.synthesis_dir = synthesis_dir
        os.makedirs(synthesis_dir, exist_ok=True)
    
    def prepare_for_synthesis(self):
        """Combine all processed data into synthesis-ready format"""
        
        # Load all processing results
        results_dir = f"{self.processed_dir}/combined_outputs"
        all_papers = []
        
        for results_file in os.listdir(results_dir):
            if results_file.endswith('_results.json'):
                with open(f"{results_dir}/{results_file}", 'r', encoding='utf-8') as f:
                    paper_data = json.load(f)
                    
                # Load corresponding text and table data
                base_name = results_file.replace('_results.json', '')
                
                # Load text
                text_file = f"{self.processed_dir}/text_extracts/{base_name}.md"
                if os.path.exists(text_file):
                    with open(text_file, 'r', encoding='utf-8') as f:
                        paper_data['full_text'] = f.read()
                
                # Load tables
                table_file = f"{self.processed_dir}/table_data/{base_name}_tables.json"
                if os.path.exists(table_file):
                    with open(table_file, 'r', encoding='utf-8') as f:
                        paper_data['table_data'] = json.load(f)
                
                all_papers.append(paper_data)
        
        # Create synthesis-ready dataset
        synthesis_dataset = {
            "dataset_info": {
                "total_papers": len(all_papers),
                "creation_timestamp": datetime.now().isoformat(),
                "source": "soil_k_literature_processing"
            },
            "papers": all_papers
        }
        
        # Save complete dataset
        with open(f"{self.synthesis_dir}/complete_dataset.json", 'w', encoding='utf-8') as f:
            json.dump(synthesis_dataset, f, indent=2)
        
        # Create individual paper files for AI processing
        for paper in all_papers:
            filename = paper['filename'].replace('.pdf', '')
            paper_file = f"{self.synthesis_dir}/{filename}.json"
            with open(paper_file, 'w', encoding='utf-8') as f:
                json.dump(paper, f, indent=2)
        
        print(f"Synthesis preparation complete: {len(all_papers)} papers ready")
        print(f"Complete dataset: {self.synthesis_dir}/complete_dataset.json")
        
        return synthesis_dataset

if __name__ == "__main__":
    preparator = SynthesisDataPreparator()
    dataset = preparator.prepare_for_synthesis()