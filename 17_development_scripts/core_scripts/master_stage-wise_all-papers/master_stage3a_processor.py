#!/usr/bin/env python3
"""
Master Stage 3A Processor
Orchestrates processing of all papers through Stage 3A by calling single paper processor

This is a simple orchestration script - no complex logic, just calls the individual processor
Automatically skips papers that have already been successfully processed
Only processes papers that have both Stage 1B and Stage 2B dependencies in approved_results

Usage:
    python master_stage3a_processor.py --api-key YOUR_KEY
    python master_stage3a_processor.py --api-key YOUR_KEY --papers paper1.json paper2.json
    python master_stage3a_processor.py --api-key YOUR_KEY --limit 5
    python master_stage3a_processor.py --api-key YOUR_KEY --force-reprocess
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


class MasterStage3AProcessor:
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
        """Check if Stage 3A results already exist in APPROVED_RESULTS folder only"""
        approved_dir = Path("8_stage_outputs/stage_3a/approved_results")
        
        if not approved_dir.exists():
            return False
        
        # Look for any Stage 3A file for this paper
        for result_file in approved_dir.glob(f"{paper_name}_3a_*.json"):
            return True
        
        return False
    
    def check_stage1b_dependency(self, paper_name: str) -> bool:
        """Check if Stage 1B dependency exists for this paper"""
        stage1b_approved_dir = Path("8_stage_outputs/stage_1b/approved_results")
        
        if not stage1b_approved_dir.exists():
            return False
        
        # Look for Stage 1B file for this paper
        for stage1b_file in stage1b_approved_dir.glob(f"{paper_name}_1b_*.json"):
            return True
        
        return False
    
    def check_stage2b_dependency(self, paper_name: str) -> bool:
        """Check if Stage 2B dependency exists for this paper"""
        stage2b_approved_dir = Path("8_stage_outputs/stage_2b/approved_results")
        
        if not stage2b_approved_dir.exists():
            return False
        
        # Look for Stage 2B file for this paper
        for stage2b_file in stage2b_approved_dir.glob(f"{paper_name}_2b_*.json"):
            return True
        
        return False
    
    def check_all_dependencies(self, paper_name: str) -> tuple[bool, List[str]]:
        """Check if all dependencies exist for this paper"""
        missing_deps = []
        
        if not self.check_stage1b_dependency(paper_name):
            missing_deps.append("Stage 1B")
        
        if not self.check_stage2b_dependency(paper_name):
            missing_deps.append("Stage 2B")
        
        return len(missing_deps) == 0, missing_deps
    
    def filter_papers(self, papers: List[str], force_reprocess: bool = False) -> List[str]:
        """Filter papers to only include those needing processing with all dependencies"""
        print(f"📋 Found {len(papers)} papers in synthesis_ready/")
        
        unprocessed = []
        already_processed = []
        missing_dependencies = {}
        
        for paper in papers:
            # Check if all dependencies exist
            has_deps, missing_deps = self.check_all_dependencies(paper)
            
            if not has_deps:
                missing_dependencies[paper] = missing_deps
                continue
                
            # Check if already processed (unless force reprocess)
            if not force_reprocess and self.check_existing_results(paper):
                already_processed.append(paper)
            else:
                unprocessed.append(paper)
        
        if missing_dependencies:
            print(f"⚠️  Found {len(missing_dependencies)} papers missing dependencies:")
            for paper, deps in list(missing_dependencies.items())[:5]:  # Show first 5
                print(f"   - {paper}: missing {', '.join(deps)}")
            if len(missing_dependencies) > 5:
                print(f"   ... and {len(missing_dependencies) - 5} more")
        
        if already_processed:
            print(f"✅ Found {len(already_processed)} papers already processed:")
            for paper in already_processed:
                print(f"   - {paper}")
        
        if unprocessed:
            print(f"📋 Will process {len(unprocessed)} new papers:")
            for paper in unprocessed:
                print(f"   - {paper}")
        else:
            if not missing_dependencies:
                print(f"✅ All papers have already been processed successfully!")
            else:
                print(f"⚠️  No papers available for processing (missing dependencies or already completed)")
        
        return unprocessed
    
    async def process_single_paper(self, paper_name: str) -> Dict[str, Any]:
        """Call the single paper processor for one paper"""
        print(f"\n{'='*60}")
        print(f"📄 Processing paper: {paper_name}")
        print(f"{'='*60}")
        
        # Construct command
        cmd = [
            sys.executable,  # Use same Python interpreter
            "process_single_paper_stage3a.py",
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
                stdout_text = stdout.decode('utf-8')
                print(f"✅ {paper_name}: SUCCESS")
                # Print last few lines of output for visibility
                lines = stdout_text.strip().split('\n')
                for line in lines[-3:]:
                    if line.strip():
                        print(f"   {line}")
                
                result = {
                    "paper": paper_name,
                    "status": "SUCCESS",
                    "output": stdout_text
                }
            else:
                # Failure
                stderr_text = stderr.decode('utf-8')
                stdout_text = stdout.decode('utf-8')
                print(f"❌ {paper_name}: FAILED")
                print(f"   Error: {stderr_text}")
                
                result = {
                    "paper": paper_name,
                    "status": "FAILED",
                    "output": stdout_text,
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
                "error": "Process timed out after 5 minutes"
            }
            
        except Exception as e:
            print(f"💥 {paper_name}: EXCEPTION - {str(e)}")
            return {
                "paper": paper_name,
                "status": "EXCEPTION",
                "error": str(e)
            }
    
    async def process_all_papers(self, papers: List[str]):
        """Process all papers through Stage 3A in parallel"""
        if not papers:
            print("No papers to process.")
            return
        
        print(f"\n📊 Filtered {len(papers)} papers to process")
        print(f"\n🚀 Starting Stage 3A processing for {len(papers)} papers")
        print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Processing mode: Parallel ({len(papers)} papers simultaneously)")
        
        # Process all papers in parallel
        tasks = [self.process_single_paper(paper) for paper in papers]
        self.results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Summary
        print(f"\n{'='*80}")
        print(f"📊 STAGE 3A PROCESSING COMPLETE")
        print(f"{'='*80}")
        
        successful = sum(1 for r in self.results if isinstance(r, dict) and r.get('status') == 'SUCCESS')
        failed = len(self.results) - successful
        
        print(f"📄 Total papers: {len(papers)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        # Show failed papers if any
        if failed > 0:
            print(f"\n❌ Failed papers:")
            for result in self.results:
                if isinstance(result, dict) and result.get('status') != 'SUCCESS':
                    print(f"   - {result.get('paper', 'Unknown')}: {result.get('status', 'Unknown')}")
        
        # Save summary
        self.save_summary()
    
    def save_summary(self):
        """Save processing summary to logs"""
        log_dir = Path("11_validation_logs/stage_3a_processing")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = log_dir / f"stage_3a_master_summary_{timestamp}.json"
        
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_papers": len(self.results),
            "successful": sum(1 for r in self.results if isinstance(r, dict) and r.get('status') == 'SUCCESS'),
            "failed": sum(1 for r in self.results if isinstance(r, dict) and r.get('status') != 'SUCCESS'),
            "results": self.results
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Summary saved to: {summary_file}")


async def main():
    parser = argparse.ArgumentParser(description='Master Stage 3A processor for all papers')
    parser.add_argument('--api-key', required=True, help='Gemini API key')
    parser.add_argument('--papers', nargs='*', help='Specific papers to process (optional)')
    parser.add_argument('--limit', type=int, help='Limit number of papers to process')
    parser.add_argument('--force-reprocess', action='store_true', 
                       help='Force reprocessing of papers even if results exist')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = MasterStage3AProcessor(args.api_key)
    
    # Get papers to process
    if args.papers:
        # Use specified papers
        papers = args.papers
    else:
        # Get all papers
        papers = processor.get_all_papers()
    
    # Apply limit if specified
    if args.limit:
        papers = papers[:args.limit]
    
    # Filter papers (check dependencies and existing results)
    papers_to_process = processor.filter_papers(papers, args.force_reprocess)
    
    # Process papers
    if papers_to_process:
        await processor.process_all_papers(papers_to_process)
        print(f"\n✅ All papers processed successfully!")
    else:
        print(f"\n⚠️  No papers to process.")


if __name__ == "__main__":
    asyncio.run(main())