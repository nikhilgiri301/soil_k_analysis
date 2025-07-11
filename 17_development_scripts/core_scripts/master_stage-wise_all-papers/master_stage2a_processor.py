#!/usr/bin/env python3
"""
Master Stage 2A Processor
Orchestrates processing of all papers through Stage 2A by calling single paper processor

This is a simple orchestration script - no complex logic, just calls the individual processor
Automatically skips papers that have already been successfully processed

Usage:
    python master_stage2a_processor.py --api-key YOUR_KEY
    python master_stage2a_processor.py --api-key YOUR_KEY --papers paper1.json paper2.json
    python master_stage2a_processor.py --api-key YOUR_KEY --limit 5
    python master_stage2a_processor.py --api-key YOUR_KEY --force-reprocess
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class MasterStage2AProcessor:
    """Orchestrates calling single paper processor for multiple papers"""
    
    def __init__(self, api_key: str):
        """Initialize master processor"""
        self.api_key = api_key
        self.results = []
        
    def get_all_papers(self) -> List[str]:
        """Get list of all papers from synthesis_ready directory"""
        synthesis_ready_dir = Path("3_synthesis_ready")
        papers = []
        
        for paper_file in synthesis_ready_dir.glob("*.json"):
            papers.append(paper_file.stem)
        
        # Sort for consistent ordering
        papers.sort()
        return papers
    
    def check_existing_results(self, paper_name: str) -> bool:
        """Check if Stage 2A results already exist in APPROVED_RESULTS folder only"""
        approved_dir = Path("8_stage_outputs/stage_2a/approved_results")
        
        # Look for any existing result file for this paper in approved_results ONLY
        pattern = f"{paper_name}_2a_*.json"
        existing_files = list(approved_dir.glob(pattern))
        
        if existing_files:
            # Sort by modification time to check newest first
            existing_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for result_file in existing_files:
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    
                    # If it's in approved_results, it's already human-validated
                    print(f"✅ Found approved result for {paper_name} ({result_file.name})")
                    return True
                        
                except Exception as e:
                    print(f"⚠️  Error reading approved result {result_file.name}: {e}")
                    continue
        
        # No approved results found - need to process
        return False
    
    def filter_unprocessed_papers(self, papers: List[str], force_reprocess: bool = False) -> List[str]:
        """Filter out papers that have already been successfully processed"""
        if force_reprocess:
            print(f"🔄 Force reprocess enabled - will process all {len(papers)} papers")
            return papers
        
        unprocessed = []
        already_processed = []
        
        for paper in papers:
            if self.check_existing_results(paper):
                already_processed.append(paper)
            else:
                unprocessed.append(paper)
        
        if already_processed:
            print(f"✅ Found {len(already_processed)} papers already processed:")
            for paper in already_processed:
                print(f"   - {paper}")
        
        if unprocessed:
            print(f"📋 Will process {len(unprocessed)} new papers:")
            for paper in unprocessed:
                print(f"   - {paper}")
        else:
            print(f"✅ All papers have already been processed successfully!")
        
        return unprocessed
    
    async def process_single_paper(self, paper_name: str) -> Dict[str, Any]:
        """Call the single paper processor for one paper"""
        print(f"\n{'='*60}")
        print(f"📄 Processing paper: {paper_name}")
        print(f"{'='*60}")
        
        # Construct command
        cmd = [
            sys.executable,  # Use same Python interpreter
            "process_single_paper_stage2a.py",
            "--paper", paper_name,
            "--api-key", self.api_key
        ]
        
        try:
            # Run the single paper processor
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout (5 minutes total - buffer over API timeout)
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=300  # 5 minutes
            )
            
            # Parse result based on exit code
            if process.returncode == 0:
                # Success
                result = {
                    "paper": paper_name,
                    "status": "SUCCESS",
                    "output": stdout.decode('utf-8'),
                    "error": None
                }
                print(f"✅ {paper_name}: SUCCESS")
            else:
                # Failure - log stderr
                stderr_text = stderr.decode('utf-8')
                print(f"❌ {paper_name}: FAILED - {stderr_text}")
                result = {
                    "paper": paper_name,
                    "status": "FAILED", 
                    "output": stdout.decode('utf-8'),
                    "error": stderr_text
                }
                
            return result
            
        except asyncio.TimeoutError:
            # Subprocess timed out
            print(f"⏰ {paper_name}: TIMEOUT after 5 minutes")
            try:
                process.kill()
                await process.wait()
            except:
                pass
            return {
                "paper": paper_name,
                "status": "TIMEOUT",
                "output": None,
                "error": "Processing timed out after 10 minutes"
            }
        except Exception as e:
            # Subprocess failed to run
            print(f"💥 {paper_name}: ERROR - {str(e)}")
            return {
                "paper": paper_name,
                "status": "ERROR",
                "output": None,
                "error": str(e)
            }
    
    async def process_all_papers(self, papers: List[str]):
        """Process all papers through Stage 2A in parallel"""
        print(f"\n🚀 Starting Stage 2A processing for {len(papers)} papers")
        print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Processing mode: Parallel ({len(papers)} papers simultaneously)")
        
        start_time = datetime.now()
        
        # Process all papers in parallel automatically
        tasks = [self.process_single_paper(paper) for paper in papers]
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        for i, result in enumerate(self.results):
            if isinstance(result, Exception):
                print(f"💥 {papers[i]}: EXCEPTION - {str(result)}")
                self.results[i] = {
                    "paper": papers[i],
                    "status": "EXCEPTION",
                    "output": None,
                    "error": str(result)
                }
        
        # Calculate summary
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Count successes and failures
        successful = sum(1 for r in self.results if r['status'] == 'SUCCESS')
        failed = sum(1 for r in self.results if r['status'] in ['FAILED', 'ERROR', 'TIMEOUT', 'EXCEPTION'])
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 STAGE 2A PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"📄 Total papers: {len(papers)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Total time: {total_time:.1f}s")
        print(f"⏱️  Average per paper: {total_time/len(papers):.1f}s")
        
        # List failed papers
        if failed > 0:
            print(f"\n❌ Failed papers:")
            for result in self.results:
                if result['status'] in ['FAILED', 'ERROR', 'TIMEOUT', 'EXCEPTION']:
                    print(f"  - {result['paper']} ({result['status']}): {result.get('error', 'Unknown error')}")
        
        # Save summary
        self.save_summary(successful, failed, total_time)
        
        return successful, failed
    
    def save_summary(self, successful: int, failed: int, total_time: float):
        """Save processing summary"""
        summary = {
            "processing_timestamp": datetime.now().isoformat(),
            "total_papers": len(self.results),
            "successful": successful,
            "failed": failed,
            "total_time_seconds": total_time,
            "results": self.results
        }
        
        # Save to logs directory
        logs_dir = Path("11_validation_logs/stage_2a_processing")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = logs_dir / f"stage_2a_master_summary_{timestamp}.json"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Summary saved to: {summary_file}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Master Stage 2A Processor - Orchestrates processing all papers",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    
    # Optional arguments
    parser.add_argument("--papers", nargs='+', 
                       help="Specific papers to process (default: all papers)")
    parser.add_argument("--limit", type=int,
                       help="Limit to first N papers")
    parser.add_argument("--force-reprocess", action="store_true",
                       help="Force reprocessing of papers even if results already exist")
    
    args = parser.parse_args()
    
    # Initialize master processor
    master = MasterStage2AProcessor(args.api_key)
    
    # Determine which papers to process
    if args.papers:
        # Specific papers requested
        papers = args.papers
        print(f"📋 Processing specific papers: {papers}")
    else:
        # All papers
        papers = master.get_all_papers()
        print(f"📋 Found {len(papers)} papers in synthesis_ready/")
        
        if args.limit:
            papers = papers[:args.limit]
            print(f"📋 Limited to first {args.limit} papers")
    
    # Filter out already processed papers (unless force reprocess)
    original_count = len(papers)
    papers = master.filter_unprocessed_papers(papers, args.force_reprocess)
    
    if len(papers) == 0:
        print(f"\n✅ No papers need processing!")
        if not args.force_reprocess:
            print(f"💡 Use --force-reprocess to reprocess all papers anyway")
        sys.exit(0)
    elif len(papers) < original_count:
        print(f"\n📊 Filtered {original_count} → {len(papers)} papers to process")
    
    # Process all papers
    successful, failed = await master.process_all_papers(papers)
    
    # Exit with appropriate code
    if failed == 0:
        print(f"\n✅ All papers processed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some papers failed processing")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())