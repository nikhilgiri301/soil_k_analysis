#!/usr/bin/env python3
"""
Stage 3B: Synthesis Validation Script (Text Mode)
DIAGNOSTIC VERSION for problematic papers that fail JSON parsing

This script processes a single paper through Stage 3B validation using text mode
instead of JSON mode to diagnose JSON formatting issues.

Usage:
    python process_single_paper_stage3b_text.py --paper "paper_name" --api-key YOUR_API_KEY
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
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging, STAGE_TEMPERATURES


def load_paper_data(paper_name: str) -> Dict[str, Any]:
    """Load paper data from synthesis_ready directory"""
    paper_file = Path(f"3_synthesis_ready/{paper_name}.json")
    
    if not paper_file.exists():
        raise FileNotFoundError(f"Paper file not found: {paper_file}")
    
    with open(paper_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_stage1b_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 1B results - fail if not found"""
    stage1b_dir = Path("8_stage_outputs/stage_1b/approved_results")
    
    if not stage1b_dir.exists():
        raise FileNotFoundError(f"Stage 1B approved_results directory not found")
    
    for stage1b_file in stage1b_dir.glob(f"{paper_name}_1b_*.json"):
        with open(stage1b_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"Stage 1B dependency not found for paper: {paper_name}")


def load_stage2b_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 2B results - fail if not found"""
    stage2b_dir = Path("8_stage_outputs/stage_2b/approved_results")
    
    if not stage2b_dir.exists():
        raise FileNotFoundError(f"Stage 2B approved_results directory not found")
    
    for stage2b_file in stage2b_dir.glob(f"{paper_name}_2b_*.json"):
        with open(stage2b_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"Stage 2B dependency not found for paper: {paper_name}")


def load_stage3a_dependency(paper_name: str) -> Dict[str, Any]:
    """Load Stage 3A results - fail if not found"""
    # Only check approved_results folder for Stage 3A dependency
    stage3a_dir = Path("8_stage_outputs/stage_3a/approved_results")
    
    if not stage3a_dir.exists():
        raise FileNotFoundError(f"Stage 3A approved_results directory not found")
    
    # Look for Stage 3A file
    for stage3a_file in stage3a_dir.glob(f"{paper_name}_3a_*.json"):
        with open(stage3a_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # If not found, this is an error
    raise FileNotFoundError(f"Stage 3A dependency not found for paper: {paper_name}")


def save_text_results(text_content: str, paper_name: str) -> str:
    """Save Stage 3B raw text results to output directory"""
    # Create output directory
    output_dir = Path("8_stage_outputs/stage_3b")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp  
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{paper_name}_3b_text_{timestamp}.txt"
    filepath = output_dir / filename
    
    # Save raw text results
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    return str(filepath)


async def validate_with_text_mode(gemini_client: GeminiClient, prompt_loader: PromptLoader,
                                 stage_3a_result: Dict[str, Any], 
                                 stage_1b_result: Dict[str, Any],
                                 stage_2b_result: Dict[str, Any]) -> str:
    """Validate Stage 3A synthesis results using text mode (no JSON forcing)"""
    
    # Load the same prompt template as regular Stage 3B
    stage_name = "stage_3b_synthesis_validation"
    temperature = STAGE_TEMPERATURES.get(stage_name, 0.1)
    
    try:
        prompt_template = prompt_loader.load_prompt(stage_name)
        logging.info(f"Loaded synthesis validation prompt for {stage_name}")
    except Exception as e:
        logging.error(f"Failed to load synthesis validation prompt: {str(e)}")
        raise
    
    # Format validation prompt using string replacement (same as regular Stage 3B)
    formatted_prompt = prompt_template.replace(
        '{stage_1b_results}', json.dumps(stage_1b_result, indent=2)
    ).replace(
        '{stage_2b_results}', json.dumps(stage_2b_result, indent=2)
    ).replace(
        '{stage_3a_results}', json.dumps(stage_3a_result, indent=2)
    )
    
    # Add text mode instruction to prompt
    text_mode_instruction = "\n\nIMPORTANT: Provide your complete analysis and enhanced synthesis in natural text format. Do not attempt to format as JSON."
    formatted_prompt += text_mode_instruction
    
    try:
        # Use the model directly for text generation (bypass JSON forcing)
        import asyncio
        
        # Create generation config for text mode (no JSON constraint)
        generation_config = {
            'temperature': temperature,
            # Explicitly no response_mime_type - let AI respond naturally
        }
        
        # Generate content using the model directly
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: gemini_client.model.generate_content(
                contents=formatted_prompt,
                generation_config=generation_config
            )
        )
        
        # Get raw text response
        if hasattr(response, 'text'):
            text_result = response.text
        else:
            text_result = str(response)
        
        logging.info("Successfully generated text-mode validation response")
        return text_result
        
    except Exception as e:
        logging.error(f"Text-mode validation failed: {str(e)}")
        return f"ERROR: Text-mode validation failed: {str(e)}"


async def main():
    parser = argparse.ArgumentParser(description='Process single paper through Stage 3B validation (TEXT MODE)')
    parser.add_argument('--paper', required=True, help='Paper name (without .json extension)')
    parser.add_argument('--api-key', required=True, help='Gemini API key')
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Starting Stage 3B TEXT MODE processing for: {args.paper}")
        print("🔍 DIAGNOSTIC: This will show raw AI output without JSON formatting")
        start_time = datetime.now()
        
        # Load paper data
        print("📄 Loading paper data...")
        paper_data = load_paper_data(args.paper)
        
        # Load Stage 3A dependency
        print("🔗 Loading Stage 3A dependency...")
        stage3a_results = load_stage3a_dependency(args.paper)
        
        # Initialize core components
        print("🤖 Initializing components...")
        config = load_config("6_synthesis_engine/config.json")
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # Initialize clients
        gemini_client = GeminiClient(args.api_key)
        prompt_loader = PromptLoader()
        
        # Load Stage 1B and 2B dependencies
        print("🔗 Loading Stage 1B dependency...")
        stage1b_results = load_stage1b_dependency(args.paper)
        print("🔗 Loading Stage 2B dependency...")  
        stage2b_results = load_stage2b_dependency(args.paper)
        
        # Process through Stage 3B in text mode
        print("⚡ Processing Stage 3B validation in TEXT MODE...")
        text_result = await validate_with_text_mode(
            gemini_client, prompt_loader,
            stage3a_results['results'],
            stage1b_results['results'], 
            stage2b_results['results']
        )
        
        # Save raw text results
        output_path = save_text_results(text_result, args.paper)
        
        # Success
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Stage 3B TEXT MODE completed successfully!")
        print(f"⏱️  Processing time: {processing_time:.1f} seconds")
        print(f"💾 Raw text saved to: {output_path}")
        print(f"🔍 DIAGNOSTIC: Review the text file to understand JSON formatting issues")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error during Stage 3B TEXT MODE processing: {e}")
        return 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))