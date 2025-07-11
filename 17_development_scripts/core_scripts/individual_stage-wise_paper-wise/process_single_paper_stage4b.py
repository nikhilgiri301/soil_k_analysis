#!/usr/bin/env python3
"""
Stage 4B: Mapping Validation Script
Validates Stage 4A client mapping results

This script processes a single paper through Stage 4B validation.
It requires Stage 4A results, Stage 3B results, and client architecture.

Usage:
    python process_single_paper_stage4b.py --paper "paper_name" --api-key YOUR_API_KEY
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
from stage_4_processors.mapping_validator import MappingValidator
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging


def load_client_architecture() -> Dict[str, Any]:
    """Load client question architecture"""
    question_tree_file = Path("7_client_architecture/question_tree.json")
    
    if not question_tree_file.exists():
        raise FileNotFoundError(f"Client question tree not found: {question_tree_file}")
    
    with open(question_tree_file, 'r', encoding='utf-8') as f:
        return {'question_tree': json.load(f)}


def load_stage3b_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 3B results - fail if not found"""
    # Only check approved_results folder for Stage 3B dependency
    stage3b_dir = Path("8_stage_outputs/stage_3b/approved_results")
    
    if not stage3b_dir.exists():
        raise FileNotFoundError(f"Stage 3B approved_results directory not found")
    
    # Look for Stage 3B file
    for stage3b_file in stage3b_dir.glob(f"{paper_name}_3b_*.json"):
        with open(stage3b_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not found, this is an error
    raise FileNotFoundError(f"Stage 3B dependency not found for paper: {paper_name}")


def load_stage4a_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 4A results - fail if not found"""
    # Only check approved_results folder for Stage 4A dependency
    stage4a_dir = Path("8_stage_outputs/stage_4a/approved_results")
    
    if not stage4a_dir.exists():
        raise FileNotFoundError(f"Stage 4A approved_results directory not found")
    
    # Look for Stage 4A file
    for stage4a_file in stage4a_dir.glob(f"{paper_name}_4a_*.json"):
        with open(stage4a_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not found, this is an error
    raise FileNotFoundError(f"Stage 4A dependency not found for paper: {paper_name}")


def save_results(results: Dict[str, Any], paper_name: str) -> str:
    """Save Stage 4B results to output directory"""
    # Create output directory
    output_dir = Path("8_stage_outputs/stage_4b")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{paper_name}_4b_{timestamp}.json"
    filepath = output_dir / filename
    
    # Save results
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


async def main():
    parser = argparse.ArgumentParser(description='Process single paper through Stage 4B validation')
    parser.add_argument('--paper', required=True, help='Paper name (without .json extension)')
    parser.add_argument('--api-key', required=True, help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting Stage 4B processing for: {args.paper}")
        start_time = datetime.now()
        
        # Load client architecture
        print("📋 Loading client architecture...")
        client_architecture = load_client_architecture()
        
        # Load Stage 3B dependency
        print("🔗 Loading Stage 3B dependency...")
        stage3b_results = load_stage3b_dependency(args.paper)
        
        # Load Stage 4A dependency
        print("🔗 Loading Stage 4A dependency...")
        stage4a_results = load_stage4a_dependency(args.paper)
        
        # Initialize core components
        print("🤖 Initializing components...")
        config = load_config("6_synthesis_engine/config.json")
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # Initialize clients
        gemini_client = GeminiClient(args.api_key)
        prompt_loader = PromptLoader()
        validator = MappingValidator(gemini_client, prompt_loader)
        
        # Process through Stage 4B
        print("⚡ Processing Stage 4B validation...")
        results = await validator.validate(
            stage4a_results['results'],
            stage3b_results['results'],
            client_architecture
        )
        
        # Package results with metadata
        output_data = {
            "stage_id": "4b",
            "stage_name": "Mapping Validation",
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
        
        print(f"✅ Stage 4B completed successfully!")
        print(f"⏱️  Processing time: {processing_time:.1f} seconds")
        print(f"💾 Results saved to: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error during Stage 4B processing: {e}")
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))