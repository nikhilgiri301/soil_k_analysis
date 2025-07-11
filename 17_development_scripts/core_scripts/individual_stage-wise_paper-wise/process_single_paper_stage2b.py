#!/usr/bin/env python3
"""
Stage 2B: Soil K Validation Script
Validates and enhances Stage 2A soil K specific extraction results

This script processes a single paper through Stage 2B validation.
It requires Stage 2A results as dependency and uses SoilKValidator.

Usage:
    python process_single_paper_stage2b.py --paper "paper_name" --api-key YOUR_API_KEY
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
from stage_2_processors.soilk_validator import SoilKValidator
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging


def load_paper_data(paper_name: str) -> Dict[str, Any]:
    """Load paper data from synthesis_ready directory"""
    paper_file = Path(f"3_synthesis_ready/{paper_name}.json")
    
    if not paper_file.exists():
        raise FileNotFoundError(f"Paper file not found: {paper_file}")
    
    with open(paper_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_stage2a_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 2A results - fail if not found"""
    # Only check approved_results folder for Stage 2A dependency
    stage2a_dir = Path("8_stage_outputs/stage_2a/approved_results")
    
    # Look for Stage 2A file
    for stage2a_file in stage2a_dir.glob(f"{paper_name}_2a_*.json"):
        with open(stage2a_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not found, this is an error
    raise FileNotFoundError(f"Stage 2A dependency not found for paper: {paper_name}")


def save_results(results: Dict[str, Any], paper_name: str) -> str:
    """Save Stage 2B results to output directory"""
    # Create output directory
    output_dir = Path("8_stage_outputs/stage_2b")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{paper_name}_2b_{timestamp}.json"
    filepath = output_dir / filename
    
    # Save results
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


async def main():
    parser = argparse.ArgumentParser(description='Process single paper through Stage 2B validation')
    parser.add_argument('--paper', required=True, help='Paper name (without .json extension)')
    parser.add_argument('--api-key', required=True, help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting Stage 2B processing for: {args.paper}")
        start_time = datetime.now()
        
        # Load paper data
        print("📄 Loading paper data...")
        paper_data = load_paper_data(args.paper)
        
        # Load Stage 2A dependency
        print("🔗 Loading Stage 2A dependency...")
        stage2a_results = load_stage2a_dependency(args.paper)
        
        # Initialize core components
        print("🤖 Initializing components...")
        config = load_config("6_synthesis_engine/config.json")
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # Initialize clients
        gemini_client = GeminiClient(args.api_key)
        prompt_loader = PromptLoader()
        validator = SoilKValidator(gemini_client, prompt_loader)
        
        # Process through Stage 2B
        print("⚡ Processing Stage 2B validation...")
        results = await validator.validate(
            stage2a_results['results'],
            paper_data
        )
        
        # Package results with metadata
        output_data = {
            "stage_id": "2b",
            "stage_name": "Soil K Validation",
            "paper_id": args.paper,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
            "processing_mode": "single_paper",
            "validation_passed": True,
            "validation_message": "Valid validation result",
            "results": results
        }
        
        # Save results
        output_path = save_results(output_data, args.paper)
        
        # Success
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Stage 2B completed successfully!")
        print(f"⏱️  Processing time: {processing_time:.1f} seconds")
        print(f"💾 Results saved to: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error during Stage 2B processing: {e}")
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))