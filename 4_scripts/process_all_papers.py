import os
import json
import pymupdf4llm
import camelot
import pandas as pd
from datetime import datetime
import logging

# Create directories first (before logging setup)
base_dirs = [
    "2_processed_data/text_extracts",
    "2_processed_data/table_data", 
    "2_processed_data/processing_logs",
    "2_processed_data/combined_outputs",
    "3_synthesis_ready"
]
for d in base_dirs:
    os.makedirs(d, exist_ok=True)

# Setup logging (after directories exist)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('2_processed_data/processing_logs/master_log.log'),
        logging.StreamHandler()
    ]
)

class SoilKProcessor:
    def __init__(self, source_dir="1_source_pdfs", output_dir="2_processed_data"):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.ensure_directories()
        
    def ensure_directories(self):
        # Directories already created at startup, but double-check
        dirs = [
            f"{self.output_dir}/text_extracts",
            f"{self.output_dir}/table_data", 
            f"{self.output_dir}/processing_logs",
            f"{self.output_dir}/combined_outputs",
            "3_synthesis_ready"
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def process_single_paper(self, pdf_path):
        """Process one PDF file through complete pipeline"""
        filename = os.path.basename(pdf_path)
        base_name = filename.replace('.pdf', '')
        
        logging.info(f"Processing: {filename}")
        
        results = {
            "filename": filename,
            "processing_timestamp": datetime.now().isoformat(),
            "text_extraction": {},
            "table_extraction": {},
            "quality_metrics": {},
            "errors": []
        }
        
        try:
            # Extract text using pymupdf4llm
            markdown_text = pymupdf4llm.to_markdown(pdf_path)
            
            # Save text extraction
            text_file = f"{self.output_dir}/text_extracts/{base_name}.md"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            results["text_extraction"] = {
                "success": True,
                "character_count": len(markdown_text),
                "output_file": text_file
            }
            
            logging.info(f"Text extracted: {len(markdown_text)} characters")
            
        except Exception as e:
            results["errors"].append(f"Text extraction failed: {str(e)}")
            results["text_extraction"]["success"] = False
        
        try:
            # Extract tables using camelot
            tables = camelot.read_pdf(pdf_path, pages='all')
            
            # Process and save tables
            table_data = []
            for i, table in enumerate(tables):
                table_info = {
                    "table_id": f"{base_name}_table_{i}",
                    "page": table.page,
                    "accuracy": table.accuracy,
                    "data": table.df.to_dict('records'),
                    "shape": table.df.shape
                }
                table_data.append(table_info)
            
            # Save table data
            table_file = f"{self.output_dir}/table_data/{base_name}_tables.json"
            with open(table_file, 'w', encoding='utf-8') as f:
                json.dump(table_data, f, indent=2)
            
            results["table_extraction"] = {
                "success": True,
                "table_count": len(tables),
                "output_file": table_file,
                "tables_summary": [{"id": t["table_id"], "shape": t["shape"], "accuracy": t["accuracy"]} for t in table_data]
            }
            
            logging.info(f"Tables extracted: {len(tables)} tables")
            
        except Exception as e:
            results["errors"].append(f"Table extraction failed: {str(e)}")
            results["table_extraction"]["success"] = False
            results["table_extraction"]["table_count"] = 0
        
        # Generate quality metrics
        results["quality_metrics"] = self.calculate_quality_metrics(results)
        
        # Save combined results
        results_file = f"{self.output_dir}/combined_outputs/{base_name}_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def calculate_quality_metrics(self, results):
        """Calculate processing quality metrics"""
        metrics = {
            "text_success": results["text_extraction"].get("success", False),
            "table_success": results["table_extraction"].get("success", False),
            "character_count": results["text_extraction"].get("character_count", 0),
            "table_count": results["table_extraction"].get("table_count", 0),
            "error_count": len(results["errors"]),
            "processing_completeness": 0
        }
        
        # Calculate completeness score
        completeness = 0
        if metrics["text_success"]:
            completeness += 0.7  # Text is 70% of importance
        if metrics["table_success"] and metrics["table_count"] > 0:
            completeness += 0.3  # Tables are 30% of importance
        
        metrics["processing_completeness"] = completeness
        
        return metrics
    
    def process_all_papers(self):
        """Process all PDFs in source directory"""
        pdf_files = [f for f in os.listdir(self.source_dir) if f.endswith('.pdf')]
        
        logging.info(f"Found {len(pdf_files)} PDF files to process")
        
        summary_results = []
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.source_dir, pdf_file)
            try:
                result = self.process_single_paper(pdf_path)
                summary_results.append(result)
                
                logging.info(f"Completed: {pdf_file} - Quality: {result['quality_metrics']['processing_completeness']:.2f}")
                
            except Exception as e:
                logging.error(f"Failed to process {pdf_file}: {str(e)}")
                summary_results.append({
                    "filename": pdf_file,
                    "processing_timestamp": datetime.now().isoformat(),
                    "errors": [f"Complete processing failure: {str(e)}"],
                    "quality_metrics": {"processing_completeness": 0}
                })
        
        # Save master summary
        summary_file = f"{self.output_dir}/processing_logs/master_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_results, f, indent=2)
        
        # Generate processing report
        self.generate_processing_report(summary_results)
        
        return summary_results
    
    def generate_processing_report(self, results):
        """Generate human-readable processing report"""
        total_papers = len(results)
        successful_text = sum(1 for r in results if r.get('quality_metrics', {}).get('text_success', False))
        successful_tables = sum(1 for r in results if r.get('quality_metrics', {}).get('table_success', False))
        total_tables = sum(r.get('quality_metrics', {}).get('table_count', 0) for r in results)
        
        report = f"""
# Soil K Literature Processing Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Total papers processed: {total_papers}
- Successful text extractions: {successful_text}/{total_papers} ({successful_text/total_papers*100:.1f}%)
- Successful table extractions: {successful_tables}/{total_papers} ({successful_tables/total_papers*100:.1f}%)
- Total tables extracted: {total_tables}

## Paper-by-Paper Results
"""
        
        for result in results:
            metrics = result.get('quality_metrics', {})
            report += f"""
### {result['filename']}
- Text extraction: {'✅' if metrics.get('text_success') else '❌'}
- Table extraction: {'✅' if metrics.get('table_success') else '❌'} ({metrics.get('table_count', 0)} tables)
- Character count: {metrics.get('character_count', 0):,}
- Completeness: {metrics.get('processing_completeness', 0):.1%}
- Errors: {len(result.get('errors', []))}
"""
        
        report_file = f"{self.output_dir}/processing_logs/processing_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nProcessing complete! Report saved to: {report_file}")

# Main execution
if __name__ == "__main__":
    processor = SoilKProcessor()
    results = processor.process_all_papers()