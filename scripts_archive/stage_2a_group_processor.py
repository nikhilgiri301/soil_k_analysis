#!/usr/bin/env python3
"""
Stage 2A Batch Processor
Soil K-Specific Extraction Batch Processing

This script processes raw papers through Stage 2A using individual API calls (group processing).
Ready to run - only requires API key.

Usage:
    python3 stage_2a_batch_processor.py --api-key YOUR_GEMINI_API_KEY
    python3 stage_2a_batch_processor.py --api-key YOUR_KEY --dry-run
"""

import asyncio
import argparse
import json
import logging
import os
import sys
import time
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary synthesis engine components
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging


class Stage2ABatchProcessor:
    """
    Stage 2A Batch Processor for Soil K-Specific Extraction
    Processes raw papers through Stage 2A using individual API calls (group processing)
    """
    
    def __init__(self, api_key: str, dry_run: bool = False):
        """
        Initialize the Stage 2A batch processor
        
        Args:
            api_key: Gemini API key
            dry_run: Show what would be processed without running
        """
        self.api_key = api_key
        self.dry_run = dry_run
        
        # Initialize core components
        self.config = load_config("6_synthesis_engine/config.json")
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize clients
        self.gemini_client = GeminiClient(api_key) if not dry_run else None
        self.prompt_loader = PromptLoader()
        
        # Processing state
        self.papers_to_process = []
        self.batch_results = {}
        self.processing_stats = {
            'total_papers': 0,
            'successful_papers': 0,
            'failed_papers': 0,
            'total_cost': 0.0,
            'batch_savings': 0.0,
            'processing_time': 0.0,
            'batch_job_id': None,
            'estimated_completion': None
        }
        
        # Output directories
        self.output_dir = Path("8_stage_outputs/stage_2a")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Batch processing specific
        self.batch_output_dir = Path("8_stage_outputs/stage_2a/batch_july10")
        self.batch_output_dir.mkdir(parents=True, exist_ok=True)
    
    def identify_papers_for_stage2a(self) -> List[str]:
        """Identify all papers that need Stage 2A processing"""
        self.logger.info("Identifying papers for Stage 2A processing...")
        
        # Get all papers from synthesis_ready (exclude archive folder)
        synthesis_ready_dir = Path("3_synthesis_ready")
        all_papers = []
        
        for paper_file in synthesis_ready_dir.glob("*.json"):
            paper_name = paper_file.stem
            all_papers.append(paper_name)
        
        # Get papers already processed in Stage 2A
        processed_papers = set()
        stage_2a_dir = Path("8_stage_outputs/stage_2a")
        if stage_2a_dir.exists():
            for processed_file in stage_2a_dir.glob("*_2a_*.json"):
                # Extract paper name from filename
                paper_name = processed_file.stem.split('_2a_')[0]
                processed_papers.add(paper_name)
        
        # Find remaining papers
        remaining_papers = [p for p in all_papers if p not in processed_papers]
        
        self.logger.info(f"Found {len(all_papers)} total papers")
        self.logger.info(f"Found {len(processed_papers)} already processed papers: {list(processed_papers)}")
        self.logger.info(f"Found {len(remaining_papers)} papers needing Stage 2A processing")
        
        return remaining_papers
    
    def load_paper_data(self, paper_names: List[str]) -> List[Dict[str, Any]]:
        """Load raw paper data for Stage 2A processing"""
        self.logger.info(f"Loading raw paper data for {len(paper_names)} papers...")
        
        papers_data = []
        synthesis_ready_dir = Path("3_synthesis_ready")
        
        for paper_name in paper_names:
            paper_file = synthesis_ready_dir / f"{paper_name}.json"
            
            if not paper_file.exists():
                self.logger.error(f"Paper file not found: {paper_file}")
                raise FileNotFoundError(f"Paper file not found: {paper_file}")
            
            try:
                with open(paper_file, 'r', encoding='utf-8') as f:
                    paper_data = json.load(f)
                    paper_data['paper_id'] = paper_name
                    papers_data.append(paper_data)
                    
                self.logger.debug(f"Loaded paper: {paper_name}")
                
            except Exception as e:
                self.logger.error(f"Error loading {paper_file}: {str(e)}")
                raise
        
        self.papers_to_process = papers_data
        self.processing_stats['total_papers'] = len(papers_data)
        
        return papers_data
    
    def create_stage_2a_batch_jsonl(self, papers_data: List[Dict[str, Any]]) -> str:
        """Create JSONL file for Stage 2A processing from raw papers"""
        self.logger.info(f"Creating Stage 2A batch file for {len(papers_data)} papers...")
        
        # Load Stage 2A prompt
        prompt_template = self.prompt_loader.load_prompt("stage_2a_soilk_extraction")
        
        batch_requests = []
        
        for paper in papers_data:
            paper_id = paper['paper_id']
            
            # Structure prompt for Stage 2A using RAW PAPER DATA
            content = f"""STAGE 2A: SOIL POTASSIUM SPECIFIC EXTRACTION

{prompt_template}

--- PAPER DATA FOR PROCESSING ---
PAPER ID: {paper_id}

FULL TEXT:
{paper.get('full_text', '')}

TABLE DATA:
{json.dumps(paper.get('table_data', []), indent=2)}

METADATA:
{json.dumps(paper.get('metadata', {}), indent=2)}"""
            
            # Create request optimized for individual processing
            request = {
                "contents": [{"parts": [{"text": content}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 8192,
                    "responseMimeType": "application/json"
                }
            }
            
            # Add to batch with paper ID as key
            batch_requests.append({
                f"{paper_id}_stage_2a": request
            })
        
        if len(batch_requests) == 0:
            raise ValueError("No papers found for Stage 2A processing")
        
        # Create temporary JSONL file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8')
        
        for request in batch_requests:
            temp_file.write(json.dumps(request, ensure_ascii=False) + '\n')
        
        temp_file.close()
        
        # Log batch file statistics
        batch_size_mb = os.path.getsize(temp_file.name) / (1024 * 1024)
        self.logger.info(f"Created batch file: {temp_file.name}")
        self.logger.info(f"Batch file size: {batch_size_mb:.2f} MB")
        self.logger.info(f"Valid papers in batch: {len(batch_requests)}")
        
        return temp_file.name
    
    async def submit_batch_job(self, jsonl_file: str) -> Dict[str, Any]:
        """Submit Stage 2A batch job to Gemini API"""
        self.logger.info("Submitting Stage 2A batch job...")
        
        if self.dry_run:
            self.logger.info("DRY RUN: Would submit batch job")
            return self._simulate_batch_results(jsonl_file)
        
        # For now, implement sequential processing
        # TODO: Replace with actual Gemini Batch API when available
        
        batch_results = {}
        processing_start = time.time()
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                try:
                    request_data = json.loads(line.strip())
                    
                    for paper_request_id, request in request_data.items():
                        paper_id = paper_request_id.split('_')[0]
                        
                        self.logger.info(f"Processing paper {line_num}: {paper_id}")
                        
                        try:
                            # Process request using Gemini client
                            result = await self.gemini_client.generate_json_content(
                                request['contents'][0]['parts'][0]['text'],
                                temperature=request.get('generationConfig', {}).get('temperature', 0.1),
                                stage_name='stage_2a',
                                paper_id=paper_id
                            )
                            
                            batch_results[paper_id] = result
                            self.processing_stats['successful_papers'] += 1
                            
                        except Exception as e:
                            self.logger.error(f"Error processing {paper_id}: {str(e)}")
                            batch_results[paper_id] = {"error": str(e)}
                            self.processing_stats['failed_papers'] += 1
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON on line {line_num}: {str(e)}")
                    continue
        
        self.processing_stats['processing_time'] = time.time() - processing_start
        
        # Clean up temporary file
        os.unlink(jsonl_file)
        
        self.logger.info(f"Batch job completed in {self.processing_stats['processing_time']:.1f}s")
        
        return batch_results
    
    def _simulate_batch_results(self, jsonl_file: str) -> Dict[str, Any]:
        """Simulate batch results for dry run mode"""
        batch_results = {}
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                request_data = json.loads(line.strip())
                for paper_request_id, request in request_data.items():
                    paper_id = paper_request_id.split('_')[0]
                    
                    # Simulate successful result
                    batch_results[paper_id] = {
                        "soil_k_specific_analysis": {
                            "k_cycling_mechanisms": ["Simulated mechanism 1", "Simulated mechanism 2"],
                            "k_availability_factors": ["Simulated factor 1", "Simulated factor 2"]
                        },
                        "simulation_mode": True
                    }
        
        # Clean up temporary file
        os.unlink(jsonl_file)
        
        return batch_results
    
    def save_batch_results(self, batch_results: Dict[str, Any]):
        """Save Stage 2A batch results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        saved_files = []
        
        for paper_id, result in batch_results.items():
            # Create output with metadata
            output_data = {
                "stage_id": "2a",
                "stage_name": "Soil K-Specific Extraction",
                "paper_id": paper_id,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_mode": "batch",
                "batch_test": True,
                "results": result
            }
            
            # Save to batch output directory
            output_file = self.batch_output_dir / f"{paper_id}_2a_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Also save to main stage output directory
            main_output_file = self.output_dir / f"{paper_id}_2a_{timestamp}.json"
            
            with open(main_output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            saved_files.append(str(output_file))
            
            self.logger.debug(f"Saved Stage 2A results for {paper_id}")
        
        self.logger.info(f"Saved {len(saved_files)} Stage 2A result files")
        return saved_files
    
    def validate_stage_2a_results(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Stage 2A batch results
        Uses realistic validation for our actual outputs
        """
        validation_results = {
            'total_papers': len(batch_results),
            'successful_papers': 0,
            'failed_papers': 0,
            'validation_issues': [],
            'quality_assessment': {
                'has_soil_k_analysis': 0,
                'has_k_cycling': 0,
                'has_availability_factors': 0,
                'valid_json_structure': 0
            }
        }
        
        for paper_id, result in batch_results.items():
            if 'error' in result:
                validation_results['failed_papers'] += 1
                validation_results['validation_issues'].append(f"{paper_id}: {result['error']}")
                continue
            
            validation_results['successful_papers'] += 1
            
            # Flexible validation - look for any soil K specific content
            if any(key in result for key in ['soil_k_specific_analysis', 'k_cycling_mechanisms', 'potassium_dynamics']):
                validation_results['quality_assessment']['has_soil_k_analysis'] += 1
            
            if any('cycling' in str(result).lower() or 'mechanism' in str(result).lower() for _ in [1]):
                validation_results['quality_assessment']['has_k_cycling'] += 1
            
            if any('availability' in str(result).lower() or 'bioavailable' in str(result).lower() for _ in [1]):
                validation_results['quality_assessment']['has_availability_factors'] += 1
            
            # Check if result is valid JSON structure
            if isinstance(result, dict) and len(result) > 0:
                validation_results['quality_assessment']['valid_json_structure'] += 1
        
        return validation_results
    
    def print_processing_summary(self, validation_results: Dict[str, Any]):
        """Print Stage 2A batch processing summary"""
        print(f"\n{'='*80}")
        print(f"🧪 STAGE 2A BATCH PROCESSING RESULTS")
        print(f"{'='*80}")
        
        # Processing Summary
        print(f"\n📊 Processing Summary:")
        print(f"  📄 Total Papers: {self.processing_stats['total_papers']}")
        print(f"  ✅ Successful: {self.processing_stats['successful_papers']}")
        print(f"  ❌ Failed: {self.processing_stats['failed_papers']}")
        
        if self.processing_stats['total_papers'] > 0:
            success_rate = (self.processing_stats['successful_papers'] / self.processing_stats['total_papers']) * 100
            print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        print(f"  ⏱️  Processing Time: {self.processing_stats['processing_time']:.1f}s")
        
        # Quality Assessment
        print(f"\n✅ Quality Assessment:")
        qa = validation_results['quality_assessment']
        total_successful = validation_results['successful_papers']
        
        if total_successful > 0:
            print(f"  🔬 Soil K Analysis: {(qa['has_soil_k_analysis'] / total_successful * 100):.1f}%")
            print(f"  🔄 K Cycling Content: {(qa['has_k_cycling'] / total_successful * 100):.1f}%")
            print(f"  📊 Availability Factors: {(qa['has_availability_factors'] / total_successful * 100):.1f}%")
            print(f"  📝 Valid JSON: {(qa['valid_json_structure'] / total_successful * 100):.1f}%")
        
        # Output Files
        print(f"\n📁 Output Files:")
        print(f"  📂 Batch Output: {self.batch_output_dir}")
        print(f"  📂 Main Output: {self.output_dir}")
        
        # Next Steps
        print(f"\n🚀 Next Steps:")
        if validation_results['successful_papers'] == self.processing_stats['total_papers']:
            print(f"  ✅ Stage 2A batch processing completed successfully!")
            print(f"  🎯 Ready to proceed with Stage 2B validation")
        else:
            print(f"  ⚠️  Review and address any failed papers")
            print(f"  🔧 Check paper inputs for failed cases")
        
        print(f"\n{'='*80}")
    
    async def run_stage_2a_batch_test(self) -> Dict[str, Any]:
        """Run complete Stage 2A batch processing test"""
        start_time = time.time()
        
        print(f"\n🚀 Starting Stage 2A Batch Processing")
        print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.dry_run:
            print(f"🔍 Dry run mode - no actual API calls")
        
        # Identify papers for Stage 2A processing
        paper_names = self.identify_papers_for_stage2a()
        
        if not paper_names:
            print("✅ No papers need Stage 2A processing - all already completed!")
            return {"success": True, "message": "All papers already processed"}
        
        print(f"\n📊 Found {len(paper_names)} papers for Stage 2A processing")
        
        # Load raw paper data
        papers_data = self.load_paper_data(paper_names)
        
        # Create batch JSONL file
        jsonl_file = self.create_stage_2a_batch_jsonl(papers_data)
        
        try:
            # Submit batch job
            batch_results = await self.submit_batch_job(jsonl_file)
            
            # Save results
            saved_files = self.save_batch_results(batch_results)
            
            # Validate results
            validation_results = self.validate_stage_2a_results(batch_results)
            
            # Print summary
            total_time = time.time() - start_time
            self.processing_stats['processing_time'] = total_time
            self.print_processing_summary(validation_results)
            
            return {
                "status": "completed",
                "processing_stats": self.processing_stats,
                "validation_results": validation_results,
                "saved_files": saved_files,
                "total_time": total_time
            }
            
        except Exception as e:
            self.logger.error(f"Stage 2A batch processing failed: {str(e)}")
            print(f"\n❌ Stage 2A batch processing failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Stage 2A Batch Processing - Soil K-Specific Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    
    # Optional arguments
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without running")
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = Stage2ABatchProcessor(
            api_key=args.api_key,
            dry_run=args.dry_run
        )
        
        # Run batch processing
        result = asyncio.run(processor.run_stage_2a_batch_test())
        
        if result['status'] == 'completed':
            print("\n🎯 Stage 2A batch processing completed successfully!")
            print("📊 Review the results above to validate the approach")
            print("🚀 Ready to proceed with remaining pipeline stages")
        else:
            print(f"\n⚠️  Processing completed with status: {result['status']}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Processing failed: {str(e)}")
        logging.error(f"Stage 2A batch processing failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()