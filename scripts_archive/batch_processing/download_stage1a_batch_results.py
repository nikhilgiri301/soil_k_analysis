#!/usr/bin/env python3
"""
Download and Process Stage 1A TRUE Batch Results
Careful preservation of all data with multiple backups

Job ID: pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import google.genai as genai


def create_backup_directories():
    """Create directories for safe storage of results"""
    dirs = {
        'raw_download': Path('11_validation_logs/batch_downloads/stage_1a_batch_july10/raw'),
        'processed': Path('11_validation_logs/batch_downloads/stage_1a_batch_july10/processed'),
        'main_output': Path('8_stage_outputs/stage_1a/batch_july10_completed'),
        'backup': Path('11_validation_logs/batch_downloads/stage_1a_batch_july10/backup')
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def download_batch_results(api_key: str, job_id: str):
    """Download the batch results carefully"""
    print(f"\n📥 Downloading Stage 1A Batch Results")
    print(f"🆔 Job ID: {job_id}")
    print(f"📅 Download time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create directories
    dirs = create_backup_directories()
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        
        # Get the completed job
        job_name = f'batches/{job_id}'
        completed_job = client.batches.get(name=job_name)
        
        print(f"✅ Job Status: {completed_job.state.name}")
        
        if completed_job.state.name != 'JOB_STATE_SUCCEEDED':
            print(f"❌ Job not in succeeded state!")
            return
        
        # Get result file info
        result_file_name = completed_job.dest.file_name
        print(f"📄 Result file: {result_file_name}")
        
        # Download the raw results
        print(f"\n🔄 Downloading raw results...")
        file_content_bytes = client.files.download(file=result_file_name)
        
        # Save raw download immediately
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_file = dirs['raw_download'] / f'batch_results_raw_{timestamp}.jsonl'
        
        with open(raw_file, 'wb') as f:
            f.write(file_content_bytes)
        
        print(f"✅ Raw results saved to: {raw_file}")
        print(f"📊 File size: {len(file_content_bytes) / 1024:.1f} KB")
        
        # Create backup copy immediately
        backup_file = dirs['backup'] / f'batch_results_backup_{timestamp}.jsonl'
        shutil.copy2(raw_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
        
        # Parse and process results
        print(f"\n🔄 Processing results...")
        file_content = file_content_bytes.decode('utf-8')
        
        # Save decoded content
        decoded_file = dirs['raw_download'] / f'batch_results_decoded_{timestamp}.jsonl'
        with open(decoded_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # Process line by line
        results_summary = {
            'job_id': job_id,
            'download_timestamp': datetime.now().isoformat(),
            'total_papers': 0,
            'successful_papers': 0,
            'failed_papers': 0,
            'papers_processed': []
        }
        
        paper_results = {}
        
        for line_num, line in enumerate(file_content.splitlines(), 1):
            if not line.strip():
                continue
            
            try:
                result_data = json.loads(line)
                key = result_data.get('key', f'line_{line_num}')
                response = result_data.get('response', {})
                
                # Extract paper ID
                if '_stage_1a' in key:
                    paper_id = key.replace('_stage_1a', '')
                else:
                    paper_id = key
                
                results_summary['total_papers'] += 1
                
                # Check for errors
                if 'error' in response:
                    print(f"❌ Paper {paper_id} failed: {response['error']}")
                    paper_results[paper_id] = {"error": response['error']}
                    results_summary['failed_papers'] += 1
                else:
                    # Extract actual content
                    if 'candidates' in response and response['candidates']:
                        content = response['candidates'][0].get('content', {})
                        if 'parts' in content and content['parts']:
                            text_content = content['parts'][0].get('text', '')
                            try:
                                # Parse JSON content
                                parsed_content = json.loads(text_content)
                                paper_results[paper_id] = parsed_content
                                results_summary['successful_papers'] += 1
                                results_summary['papers_processed'].append(paper_id)
                                
                                # Save individual paper result
                                paper_file = dirs['processed'] / f"{paper_id}_1a_batch_{timestamp}.json"
                                output_data = {
                                    "stage_id": "1a",
                                    "stage_name": "Generic Extraction",
                                    "paper_id": paper_id,
                                    "processing_timestamp": datetime.now().isoformat(),
                                    "processing_mode": "true_batch",
                                    "batch_job_id": job_id,
                                    "results": parsed_content
                                }
                                
                                with open(paper_file, 'w', encoding='utf-8') as f:
                                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                                
                                # Also save to main pipeline directory
                                main_file = dirs['main_output'] / f"{paper_id}_1a_{timestamp}.json"
                                with open(main_file, 'w', encoding='utf-8') as f:
                                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                                
                                print(f"✅ Processed: {paper_id}")
                                
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON decode error for {paper_id}: {str(e)}")
                                paper_results[paper_id] = {"error": f"JSON decode error: {str(e)}"}
                                results_summary['failed_papers'] += 1
                        else:
                            paper_results[paper_id] = {"error": "No content parts in response"}
                            results_summary['failed_papers'] += 1
                    else:
                        paper_results[paper_id] = {"error": "No candidates in response"}
                        results_summary['failed_papers'] += 1
                        
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing line {line_num}: {str(e)}")
                continue
        
        # Save complete results summary
        summary_file = dirs['processed'] / f'batch_summary_{timestamp}.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        
        # Save all paper results in one file
        all_results_file = dirs['processed'] / f'all_paper_results_{timestamp}.json'
        with open(all_results_file, 'w', encoding='utf-8') as f:
            json.dump(paper_results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 DOWNLOAD AND PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"📄 Total papers: {results_summary['total_papers']}")
        print(f"✅ Successful: {results_summary['successful_papers']}")
        print(f"❌ Failed: {results_summary['failed_papers']}")
        print(f"\n📁 Files saved to:")
        print(f"  Raw download: {dirs['raw_download']}")
        print(f"  Processed results: {dirs['processed']}")
        print(f"  Main pipeline: {dirs['main_output']}")
        print(f"  Backup: {dirs['backup']}")
        print(f"\n📋 Summary file: {summary_file}")
        print(f"📋 All results: {all_results_file}")
        
        return results_summary
        
    except Exception as e:
        print(f"\n❌ Error downloading batch results: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python download_stage1a_batch_results.py YOUR_API_KEY")
        sys.exit(1)
    
    api_key = sys.argv[1]
    job_id = "pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr"
    
    download_batch_results(api_key, job_id)