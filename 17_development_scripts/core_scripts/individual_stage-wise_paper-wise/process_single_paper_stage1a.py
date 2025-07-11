#!/usr/bin/env python3
"""
Process Single Paper for Stage 1A: Generic Extraction
Processes ONE specific paper through Stage 1A with real API call

NO FALLBACKS - NO SIMULATION - NO AUTO-DISCOVERY

Usage:
    python process_single_paper_stage1a.py --paper "paper_name.json" --api-key YOUR_KEY
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary components
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from utils.json_config import load_config, setup_logging


class SinglePaperStage1AProcessor:
    """Process a single paper through Stage 1A - NO FALLBACKS"""
    
    def __init__(self, api_key: str):
        """Initialize processor with ONLY real API capability"""
        self.api_key = api_key
        
        # Initialize core components
        self.config = load_config("6_synthesis_engine/config.json")
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize clients - NO conditional initialization
        self.gemini_client = GeminiClient(api_key)
        self.prompt_loader = PromptLoader()
        
        # Output directory
        self.output_dir = Path("8_stage_outputs/stage_1a")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_specific_paper(self, paper_name: str) -> Dict[str, Any]:
        """Load ONE specific paper - fail if not found"""
        # Clean paper name (remove .json if provided)
        if paper_name.endswith('.json'):
            paper_name = paper_name[:-5]
        
        paper_path = Path("3_synthesis_ready") / f"{paper_name}.json"
        
        if not paper_path.exists():
            error_msg = f"Paper not found: {paper_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(paper_path, 'r', encoding='utf-8') as f:
                paper_data = json.load(f)
            
            # Add paper ID
            paper_data['paper_id'] = paper_name
            self.logger.info(f"Successfully loaded paper: {paper_name}")
            return paper_data
            
        except Exception as e:
            error_msg = f"Failed to load paper {paper_name}: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    async def process_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the paper through Stage 1A with REAL API call"""
        paper_id = paper_data['paper_id']
        self.logger.info(f"Processing {paper_id} through Stage 1A")
        
        # Load Stage 1A prompt
        prompt_template = self.prompt_loader.load_prompt("stage_1a_generic_extraction")
        
        # Structure the prompt with raw paper data
        content = f"""STAGE 1A: GENERIC EXTRACTION

{prompt_template}

--- PAPER DATA FOR PROCESSING ---
PAPER ID: {paper_id}

FULL TEXT:
{paper_data.get('full_text', '')}

TABLE DATA:
{json.dumps(paper_data.get('table_data', []), indent=2)}

METADATA:
{json.dumps(paper_data.get('metadata', {}), indent=2)}"""
        
        # Process with Gemini - NO FALLBACK
        try:
            start_time = time.time()
            result = await self.gemini_client.generate_json_content(
                content,
                temperature=0.1,
                stage_name='stage_1a',
                paper_id=paper_id
            )
            processing_time = time.time() - start_time
            
            self.logger.info(f"Successfully processed {paper_id} in {processing_time:.1f}s")
            return result
            
        except Exception as e:
            error_msg = f"API processing failed for {paper_id}: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    def validate_results(self, results: Dict[str, Any]) -> Tuple[bool, str]:
        """Smart validation - flexible but with minimum threshold"""
        # Minimum requirement: Must have SOME generic content
        has_generic_content = False
        validation_message = ""
        
        # Check for various forms of generic content
        if isinstance(results, dict):
            # Look for generic extraction indicators
            generic_indicators = [
                'paper_metadata', 'research_methodology', 'quantitative_findings',
                'environmental_context', 'agricultural_systems', 'temporal_dynamics',
                'data_quality_assessment', 'literature_integration'
            ]
            
            # Check if any generic indicators exist in keys
            result_keys = set(results.keys())
            found_indicators = result_keys.intersection(generic_indicators)
            
            if found_indicators:
                has_generic_content = True
            
            # Also check for minimum content size
            result_str = json.dumps(results)
            if len(result_str) < 100:
                validation_message = "Result too small - likely incomplete extraction"
                return False, validation_message
        else:
            validation_message = "Result is not a valid dictionary"
            return False, validation_message
        
        if not has_generic_content:
            validation_message = "No generic research content found in extraction"
            return False, validation_message
        
        validation_message = "Valid generic extraction"
        return True, validation_message
    
    def save_results(self, paper_id: str, results: Dict[str, Any], 
                    processing_time: float, validation_passed: bool, 
                    validation_message: str) -> str:
        """Save results for the single paper"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output with metadata
        output_data = {
            "stage_id": "1a",
            "stage_name": "Generic Extraction",
            "paper_id": paper_id,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": processing_time,
            "processing_mode": "single_paper",
            "validation_passed": validation_passed,
            "validation_message": validation_message,
            "results": results
        }
        
        # Save to output directory
        output_file = self.output_dir / f"{paper_id}_1a_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved results to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            error_msg = f"Failed to save results: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    async def run(self, paper_name: str) -> Dict[str, Any]:
        """Main execution - process ONE paper"""
        start_time = time.time()
        
        try:
            # Load the specific paper
            paper_data = self.load_specific_paper(paper_name)
            paper_id = paper_data['paper_id']
            
            # Process through Stage 1A
            results = await self.process_paper(paper_data)
            
            # Validate results
            validation_passed, validation_message = self.validate_results(results)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Save results
            output_file = self.save_results(
                paper_id, results, processing_time, 
                validation_passed, validation_message
            )
            
            # Return status
            return {
                "success": True,
                "paper_id": paper_id,
                "output_file": output_file,
                "processing_time": processing_time,
                "validation_passed": validation_passed,
                "validation_message": validation_message
            }
            
        except Exception as e:
            # Any failure returns clear error
            return {
                "success": False,
                "paper_id": paper_name,
                "error": str(e),
                "processing_time": time.time() - start_time
            }


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Process Single Paper through Stage 1A - NO FALLBACKS",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--paper", required=True, 
                       help="Paper name to process (e.g., 'paper_name.json' or 'paper_name')")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = SinglePaperStage1AProcessor(args.api_key)
    
    print(f"\n🔄 Processing paper: {args.paper}")
    print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Process the paper
    result = await processor.run(args.paper)
    
    # Report results
    if result['success']:
        print(f"\n✅ SUCCESS: Paper processed successfully")
        print(f"📄 Paper ID: {result['paper_id']}")
        print(f"📁 Output: {result['output_file']}")
        print(f"⏱️  Time: {result['processing_time']:.1f}s")
        print(f"🔍 Validation: {'PASSED' if result['validation_passed'] else 'FAILED'}")
        print(f"💬 Message: {result['validation_message']}")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED: {result['error']}")
        print(f"📄 Paper: {result['paper_id']}")
        print(f"⏱️  Time: {result['processing_time']:.1f}s")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())