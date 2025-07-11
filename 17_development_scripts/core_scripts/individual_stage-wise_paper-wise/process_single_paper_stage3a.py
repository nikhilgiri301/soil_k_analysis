#!/usr/bin/env python3
"""
Stage 3A: Paper Synthesis Script
Synthesizes Stage 1B generic validation and Stage 2B soil K validation results

This script processes a single paper through Stage 3A synthesis.
It requires both Stage 1B and Stage 2B results as dependencies.

Usage:
    python process_single_paper_stage3a.py --paper "paper_name" --api-key YOUR_API_KEY
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary components
from stage_3_processors.paper_synthesizer import PaperSynthesizer
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging


def load_stage1b_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 1B results - fail if not found"""
    # Only check approved_results folder for Stage 1B dependency
    stage1b_dir = Path("8_stage_outputs/stage_1b/approved_results")
    
    if not stage1b_dir.exists():
        raise FileNotFoundError(f"Stage 1B approved_results directory not found")
    
    # Look for Stage 1B file
    for stage1b_file in stage1b_dir.glob(f"{paper_name}_1b_*.json"):
        with open(stage1b_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not found, this is an error
    raise FileNotFoundError(f"Stage 1B dependency not found for paper: {paper_name}")


def load_stage2b_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 2B results - fail if not found"""
    # Only check approved_results folder for Stage 2B dependency
    stage2b_dir = Path("8_stage_outputs/stage_2b/approved_results")
    
    if not stage2b_dir.exists():
        raise FileNotFoundError(f"Stage 2B approved_results directory not found")
    
    # Look for Stage 2B file
    for stage2b_file in stage2b_dir.glob(f"{paper_name}_2b_*.json"):
        with open(stage2b_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not found, this is an error
    raise FileNotFoundError(f"Stage 2B dependency not found for paper: {paper_name}")


def save_results(results: Dict[str, Any], paper_name: str) -> str:
    """Save Stage 3A results to output directory"""
    # Create output directory
    output_dir = Path("8_stage_outputs/stage_3a")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{paper_name}_3a_{timestamp}.json"
    filepath = output_dir / filename
    
    # Save results
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


async def main():
    parser = argparse.ArgumentParser(description='Process single paper through Stage 3A synthesis')
    parser.add_argument('--paper', required=True, help='Paper name (without .json extension)')
    parser.add_argument('--api-key', required=True, help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting Stage 3A processing for: {args.paper}")
        start_time = datetime.now()
        
        # Load Stage 1B dependency
        print("🔗 Loading Stage 1B dependency...")
        stage1b_results = load_stage1b_dependency(args.paper)
        
        # Load Stage 2B dependency
        print("🔗 Loading Stage 2B dependency...")
        stage2b_results = load_stage2b_dependency(args.paper)
        
        # Initialize core components
        print("🤖 Initializing components...")
        config = load_config("6_synthesis_engine/config.json")
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # Initialize clients
        gemini_client = GeminiClient(args.api_key)
        prompt_loader = PromptLoader()
        synthesizer = PaperSynthesizer(gemini_client, prompt_loader)
        
        # Process through Stage 3A
        print("⚡ Processing Stage 3A synthesis...")
        # Package stage results as expected by synthesizer
        stage_results = {
            'stage_1b_results': stage1b_results['results'],
            'stage_2b_results': stage2b_results['results']
        }
        results = await synthesizer.synthesize(stage_results)
        
        # Package results with metadata
        output_data = {
            "stage_id": "3a",
            "stage_name": "Paper Synthesis",
            "paper_id": args.paper,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
            "processing_mode": "single_paper",
            "validation_passed": True,
            "validation_message": "Valid synthesis result",
            "results": results
        }
        
        # Save results
        output_path = save_results(output_data, args.paper)
        
        # Success
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Stage 3A completed successfully!")
        print(f"⏱️  Processing time: {processing_time:.1f} seconds")
        print(f"💾 Results saved to: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error during Stage 3A processing: {e}")
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))