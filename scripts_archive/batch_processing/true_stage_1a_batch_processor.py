#!/usr/bin/env python3
"""
TRUE Stage 1A Batch Processor
Uses actual Gemini Batch API with job submission and waiting

NO FALLBACKS - NO INDIVIDUAL PROCESSING - BATCH ONLY

Usage:
    python3 true_stage_1a_batch_processor.py --api-key YOUR_GEMINI_API_KEY
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

# Install required packages if missing
try:
    import google.genai as genai
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-genai")
    import google.genai as genai

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import synthesis engine components
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging


class TrueStage1ABatchProcessor:
    """
    TRUE Stage 1A Batch Processor using real Gemini Batch API
    
    NO INDIVIDUAL PROCESSING - NO FALLBACKS - BATCH ONLY
    """
    
    def __init__(self, api_key: str):
        """Initialize true batch processor"""
        self.api_key = api_key
        
        # Initialize core components
        self.config = load_config("6_synthesis_engine/config.json")
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize TRUE batch client
        self.genai_client = genai.Client(api_key=api_key)
        self.prompt_loader = PromptLoader()
        
        # Processing state
        self.papers_to_process = []
        self.batch_job = None
        self.processing_stats = {
            'total_papers': 0,
            'batch_job_id': None,
            'batch_job_name': None,
            'submission_time': None,
            'completion_time': None,
            'total_wait_time': 0,
            'estimated_cost': 0.0,
            'actual_cost': 0.0,
            'cost_savings': 0.0
        }
        
        # Output directories
        self.output_dir = Path("8_stage_outputs/stage_1a")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_output_dir = Path("8_stage_outputs/stage_1a/true_batch_july10")
        self.batch_output_dir.mkdir(parents=True, exist_ok=True)
    
    def identify_remaining_papers(self) -> List[str]:
        """Identify the 22 papers that need Stage 1A processing"""
        self.logger.info("Identifying papers that need Stage 1A processing...")
        
        # Get all papers from synthesis_ready (exclude consolidation file)
        synthesis_ready_dir = Path("3_synthesis_ready")
        all_papers = [p for p in synthesis_ready_dir.glob("*.json") if p.stem != "complete_dataset"]
        
        # Get papers already processed (from fresh folder)
        processed_papers = set()
        fresh_dir = Path("8_stage_outputs/stage_1a/fresh_july10")
        if fresh_dir.exists():
            for processed_file in fresh_dir.glob("*.json"):
                # Extract paper name from filename
                paper_name = processed_file.stem.split('_1a_')[0]
                processed_papers.add(paper_name)
        
        # Find remaining papers
        remaining_papers = []
        for paper_file in all_papers:
            paper_name = paper_file.stem
            if paper_name not in processed_papers:
                remaining_papers.append(paper_name)
        
        self.logger.info(f"Found {len(all_papers)} total papers")
        self.logger.info(f"Found {len(processed_papers)} already processed papers: {list(processed_papers)}")
        self.logger.info(f"Found {len(remaining_papers)} papers needing processing")
        
        return remaining_papers
    
    def load_paper_data(self, paper_names: List[str]) -> List[Dict[str, Any]]:
        """Load paper data for batch processing"""
        self.logger.info(f"Loading data for {len(paper_names)} papers...")
        
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
    
    def create_batch_jsonl_file(self, papers_data: List[Dict[str, Any]]) -> str:
        """Create JSONL file for TRUE batch processing"""
        self.logger.info(f"Creating TRUE batch JSONL file for {len(papers_data)} papers...")
        
        # Load Stage 1A prompt template
        prompt_template = self.prompt_loader.load_prompt("stage_1a_generic_extraction")
        
        # Create temporary JSONL file (use .json extension for better MIME detection)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        
        for paper in papers_data:
            paper_id = paper['paper_id']
            
            # Structure prompt for Stage 1A
            content = f"""STAGE 1A: GENERIC EXTRACTION

{prompt_template}

--- PAPER DATA FOR PROCESSING ---
PAPER ID: {paper_id}

FULL TEXT:
{paper.get('full_text', '')}

TABLE DATA:
{json.dumps(paper.get('table_data', []), indent=2)}

METADATA:
{json.dumps(paper.get('metadata', {}), indent=2)}"""
            
            # Create batch request entry
            batch_entry = {
                "key": f"{paper_id}_stage_1a",
                "request": {
                    "contents": [{"parts": [{"text": content}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "topP": 0.8,
                        "topK": 40,
                        "maxOutputTokens": 8192,
                        "responseMimeType": "application/json"
                    }
                }
            }
            
            # Write to JSONL file
            temp_file.write(json.dumps(batch_entry, ensure_ascii=False) + '\n')
        
        temp_file.close()
        
        # Log batch file statistics
        batch_size_mb = os.path.getsize(temp_file.name) / (1024 * 1024)
        self.logger.info(f"Created TRUE batch JSONL file: {temp_file.name}")
        self.logger.info(f"Batch file size: {batch_size_mb:.2f} MB")
        self.logger.info(f"Papers in batch: {len(papers_data)}")
        
        return temp_file.name
    
    def submit_true_batch_job(self, jsonl_file_path: str) -> Any:
        """Submit TRUE batch job to Gemini Batch API"""
        self.logger.info("Submitting TRUE batch job to Gemini Batch API...")
        
        try:
            # Upload JSONL file to Gemini 
            self.logger.info("Uploading batch file...")
            # Try without mime_type first, let it auto-detect
            uploaded_batch_file = self.genai_client.files.upload(file=jsonl_file_path)
            self.logger.info(f"Uploaded file: {uploaded_batch_file.name}")
            
            # Create TRUE batch job
            self.logger.info("Creating batch job...")
            batch_job = self.genai_client.batches.create(
                model="gemini-2.5-flash",
                src=uploaded_batch_file.name,
                config={
                    'display_name': f"stage_1a_true_batch_{len(self.papers_to_process)}_papers",
                },
            )
            
            # Extract job ID and details
            self.batch_job = batch_job
            self.processing_stats['batch_job_id'] = batch_job.name.split('/')[-1]
            self.processing_stats['batch_job_name'] = batch_job.name
            self.processing_stats['submission_time'] = datetime.now().isoformat()
            
            self.logger.info(f"✅ TRUE BATCH JOB SUBMITTED!")
            self.logger.info(f"Job Name: {batch_job.name}")
            self.logger.info(f"Job ID: {self.processing_stats['batch_job_id']}")
            self.logger.info(f"Job State: {batch_job.state.name}")
            self.logger.info(f"Submission Time: {self.processing_stats['submission_time']}")
            
            # Clean up local JSONL file
            os.unlink(jsonl_file_path)
            
            return batch_job
            
        except Exception as e:
            self.logger.error(f"Failed to submit batch job: {str(e)}")
            # Clean up local JSONL file
            if os.path.exists(jsonl_file_path):
                os.unlink(jsonl_file_path)
            raise
    
    def wait_for_batch_completion(self, check_interval: int = 300) -> Any:
        """Wait for TRUE batch job completion with status monitoring"""
        self.logger.info("Waiting for TRUE batch job completion...")
        self.logger.info(f"Check interval: {check_interval/60:.1f} minutes")
        
        wait_start = time.time()
        
        while True:
            try:
                # Get current job status
                current_job = self.genai_client.batches.get(name=self.batch_job.name)
                
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elapsed_minutes = (time.time() - wait_start) / 60
                
                print(f"\n[{current_time}] Batch Job Status Check:")
                print(f"  📋 Job ID: {self.processing_stats['batch_job_id']}")
                print(f"  📊 Status: {current_job.state.name}")
                print(f"  ⏱️  Elapsed: {elapsed_minutes:.1f} minutes")
                print(f"  📄 Papers: {self.processing_stats['total_papers']}")
                
                if current_job.state.name == 'JOB_STATE_SUCCEEDED':
                    self.processing_stats['completion_time'] = datetime.now().isoformat()
                    self.processing_stats['total_wait_time'] = time.time() - wait_start
                    
                    print(f"\n🎉 BATCH JOB COMPLETED SUCCESSFULLY!")
                    print(f"⏱️  Total wait time: {self.processing_stats['total_wait_time']/60:.1f} minutes")
                    return current_job
                    
                elif current_job.state.name == 'JOB_STATE_FAILED':
                    print(f"\n❌ BATCH JOB FAILED!")
                    print(f"Check job details for failure reason")
                    raise Exception(f"Batch job failed with state: {current_job.state.name}")
                    
                elif current_job.state.name in ['JOB_STATE_PENDING', 'JOB_STATE_RUNNING']:
                    if current_job.state.name == 'JOB_STATE_RUNNING':
                        print(f"  🔄 Status: Job is actively running")
                    else:
                        print(f"  ⏳ Status: Job is pending/queued")
                    
                    print(f"  🕐 Next check: {check_interval/60:.1f} minutes")
                    time.sleep(check_interval)
                    
                else:
                    print(f"  ❓ Unknown state: {current_job.state.name}")
                    time.sleep(check_interval)
                    
            except Exception as e:
                self.logger.error(f"Error checking job status: {str(e)}")
                print(f"❌ Error checking job status: {str(e)}")
                time.sleep(check_interval)
    
    def download_and_process_results(self, completed_job: Any) -> Dict[str, Any]:
        """Download and process TRUE batch results"""
        self.logger.info("Downloading TRUE batch results...")
        
        try:
            # Get result file name
            result_file_name = completed_job.dest.file_name
            self.logger.info(f"Result file: {result_file_name}")
            
            # Download results JSONL file
            file_content_bytes = self.genai_client.files.download(file=result_file_name)
            file_content = file_content_bytes.decode('utf-8')
            
            # Process JSONL results
            batch_results = {}
            successful_papers = 0
            failed_papers = 0
            
            for line_num, line in enumerate(file_content.splitlines(), 1):
                if not line.strip():
                    continue
                
                try:
                    result_data = json.loads(line)
                    key = result_data.get('key', f'line_{line_num}')
                    response = result_data.get('response', {})
                    
                    # Extract paper ID from key
                    if '_stage_1a' in key:
                        paper_id = key.replace('_stage_1a', '')
                    else:
                        paper_id = key
                    
                    # Check if response contains error
                    if 'error' in response:
                        self.logger.warning(f"Paper {paper_id} failed: {response['error']}")
                        batch_results[paper_id] = {"error": response['error']}
                        failed_papers += 1
                    else:
                        # Extract actual content from response
                        if 'candidates' in response and response['candidates']:
                            content = response['candidates'][0].get('content', {})
                            if 'parts' in content and content['parts']:
                                text_content = content['parts'][0].get('text', '')
                                try:
                                    # Parse JSON content
                                    parsed_content = json.loads(text_content)
                                    batch_results[paper_id] = parsed_content
                                    successful_papers += 1
                                except json.JSONDecodeError:
                                    batch_results[paper_id] = {"error": "Invalid JSON in response"}
                                    failed_papers += 1
                            else:
                                batch_results[paper_id] = {"error": "No content parts in response"}
                                failed_papers += 1
                        else:
                            batch_results[paper_id] = {"error": "No candidates in response"}
                            failed_papers += 1
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing result line {line_num}: {str(e)}")
                    failed_papers += 1
                    continue
            
            self.logger.info(f"Processed {successful_papers} successful results")
            self.logger.info(f"Found {failed_papers} failed results")
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Failed to download/process results: {str(e)}")
            raise
    
    def validate_and_save_results(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and save batch results using flexible validation"""
        self.logger.info("Validating and saving TRUE batch results...")
        
        # Import flexible validation
        from stage_test_utils import StageTestFramework
        
        validation_framework = StageTestFramework(
            stage_id='1a',
            stage_name='Generic Extraction'
        )
        
        validation_stats = {
            'total_papers': len(batch_results),
            'successful_papers': 0,
            'failed_papers': 0,
            'validation_passed': 0,
            'validation_failed': 0,
            'saved_files': []
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for paper_id, result in batch_results.items():
            
            if 'error' in result:
                validation_stats['failed_papers'] += 1
                self.logger.warning(f"Paper {paper_id} failed processing: {result['error']}")
                continue
                
            validation_stats['successful_papers'] += 1
            
            # Validate using flexible validation logic
            is_valid, validation_issues = validation_framework.validate_stage_output(result, '1a')
            
            if is_valid:
                validation_stats['validation_passed'] += 1
                self.logger.debug(f"Paper {paper_id} passed validation")
            else:
                validation_stats['validation_failed'] += 1
                self.logger.warning(f"Paper {paper_id} failed validation: {validation_issues}")
            
            # Save result regardless of validation (flexible approach)
            output_data = {
                "stage_id": "1a",
                "stage_name": "Generic Extraction",
                "paper_id": paper_id,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_mode": "true_batch",
                "batch_job_id": self.processing_stats['batch_job_id'],
                "validation_passed": is_valid,
                "validation_issues": validation_issues,
                "results": result
            }
            
            # Save to batch output directory
            batch_output_file = self.batch_output_dir / f"{paper_id}_1a_{timestamp}.json"
            with open(batch_output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Save to main pipeline directory
            main_output_file = self.output_dir / f"{paper_id}_1a_{timestamp}.json"
            with open(main_output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            validation_stats['saved_files'].append(str(main_output_file))
            
        self.logger.info(f"Saved {len(validation_stats['saved_files'])} result files")
        
        return validation_stats
    
    def print_final_summary(self, validation_stats: Dict[str, Any]):
        """Print comprehensive batch processing summary"""
        print(f"\n{'='*80}")
        print(f"🎉 TRUE STAGE 1A BATCH PROCESSING COMPLETED")
        print(f"{'='*80}")
        
        # Job Details
        print(f"\n📋 Batch Job Details:")
        print(f"  🆔 Job ID: {self.processing_stats['batch_job_id']}")
        print(f"  📄 Papers Processed: {self.processing_stats['total_papers']}")
        print(f"  ⏱️  Total Wait Time: {self.processing_stats['total_wait_time']/60:.1f} minutes")
        print(f"  🕐 Submitted: {self.processing_stats['submission_time']}")
        print(f"  ✅ Completed: {self.processing_stats['completion_time']}")
        
        # Processing Results
        print(f"\n📊 Processing Results:")
        print(f"  ✅ Successful: {validation_stats['successful_papers']}")
        print(f"  ❌ Failed: {validation_stats['failed_papers']}")
        success_rate = (validation_stats['successful_papers'] / validation_stats['total_papers']) * 100
        print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Validation Results
        print(f"\n🔍 Validation Results:")
        print(f"  ✅ Passed: {validation_stats['validation_passed']}")
        print(f"  ⚠️  Failed: {validation_stats['validation_failed']}")
        if validation_stats['successful_papers'] > 0:
            validation_rate = (validation_stats['validation_passed'] / validation_stats['successful_papers']) * 100
            print(f"  📈 Validation Rate: {validation_rate:.1f}%")
        
        # Cost Analysis (estimated)
        estimated_individual_cost = self.processing_stats['total_papers'] * 0.025  # ~$0.025 per paper
        estimated_batch_cost = estimated_individual_cost * 0.5  # 50% savings
        estimated_savings = estimated_individual_cost - estimated_batch_cost
        
        print(f"\n💰 Cost Analysis (Estimated):")
        print(f"  💳 Individual Cost: ~${estimated_individual_cost:.2f}")
        print(f"  🎉 Batch Cost: ~${estimated_batch_cost:.2f}")
        print(f"  💰 Savings: ~${estimated_savings:.2f} (50%)")
        
        # Output Files
        print(f"\n📁 Output Files:")
        print(f"  📂 Main Pipeline: {self.output_dir}")
        print(f"  📂 Batch Archive: {self.batch_output_dir}")
        print(f"  📄 Files Saved: {len(validation_stats['saved_files'])}")
        
        # Success Assessment
        print(f"\n🏆 TRUE BATCH PROCESSING ASSESSMENT:")
        if success_rate >= 90 and validation_stats['validation_passed'] >= validation_stats['successful_papers'] * 0.8:
            print(f"  🎉 EXCELLENT: TRUE batch processing working perfectly!")
            print(f"  💰 Cost savings achieved: 50% vs individual processing")
            print(f"  🚀 Ready for production batch workflows")
        elif success_rate >= 75:
            print(f"  ✅ GOOD: TRUE batch processing working with minor issues")
            print(f"  🔧 Review failed papers and validation issues")
        else:
            print(f"  ⚠️  NEEDS IMPROVEMENT: Success rate below 75%")
            print(f"  🛠️  Investigate batch processing issues")
        
        print(f"\n{'='*80}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TRUE Stage 1A Batch Processor - No Fallbacks",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    
    args = parser.parse_args()
    
    try:
        print(f"\n🚀 STARTING TRUE STAGE 1A BATCH PROCESSING")
        print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚠️  NO FALLBACKS - BATCH ONLY")
        
        # Initialize processor
        processor = TrueStage1ABatchProcessor(api_key=args.api_key)
        
        # Step 3: Identify remaining papers
        remaining_papers = processor.identify_remaining_papers()
        
        if not remaining_papers:
            print(f"\n✅ No papers need Stage 1A processing - all already completed!")
            return
        
        print(f"\n📊 Found {len(remaining_papers)} papers for TRUE batch processing")
        
        # Load paper data
        papers_data = processor.load_paper_data(remaining_papers)
        
        # Create batch JSONL file
        jsonl_file = processor.create_batch_jsonl_file(papers_data)
        
        # Step 4: Submit TRUE batch job
        batch_job = processor.submit_true_batch_job(jsonl_file)
        
        # Wait for completion
        completed_job = processor.wait_for_batch_completion(check_interval=300)  # 5 minutes
        
        # Download and process results
        batch_results = processor.download_and_process_results(completed_job)
        
        # Validate and save results
        validation_stats = processor.validate_and_save_results(batch_results)
        
        # Print final summary
        processor.print_final_summary(validation_stats)
        
        print(f"\n🎯 TRUE BATCH PROCESSING COMPLETED SUCCESSFULLY!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TRUE BATCH PROCESSING FAILED: {str(e)}")
        logging.error(f"True batch processing failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())