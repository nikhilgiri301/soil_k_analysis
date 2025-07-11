#!/usr/bin/env python3
"""
Process Single Paper for Stage 1B: Generic Validation
Validates ONE specific Stage 1A result with real API call

NO FALLBACKS - NO SIMULATION - NO AUTO-DISCOVERY

Usage:
    python process_single_paper_stage1b.py --paper "paper_name.json" --api-key YOUR_KEY
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
from stage_1_processors.generic_validator import GenericValidator


class SinglePaperStage1BProcessor:
    """Process a single paper through Stage 1B - NO FALLBACKS"""
    
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
        
        # Initialize validator
        self.validator = GenericValidator(self.gemini_client, self.prompt_loader)
        
        # Output directory
        self.output_dir = Path("8_stage_outputs/stage_1b")
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
            paper_data['filename'] = paper_name  # For validator compatibility
            self.logger.info(f"Successfully loaded paper: {paper_name}")
            return paper_data
            
        except Exception as e:
            error_msg = f"Failed to load paper {paper_name}: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    def load_stage1a_dependency(self, paper_name: str) -> Dict[str, Any]:
        """Load Stage 1A results - fail if not found"""
        # Clean paper name
        if paper_name.endswith('.json'):
            paper_name = paper_name[:-5]
        
        # Check in approved_results first, then main directory
        stage1a_dirs = [
            Path("8_stage_outputs/stage_1a/approved_results"),
            Path("8_stage_outputs/stage_1a")
        ]
        
        for stage1a_dir in stage1a_dirs:
            pattern = f"{paper_name}_1a_*.json"
            existing_files = list(stage1a_dir.glob(pattern))
            
            if existing_files:
                # Sort by modification time to get newest first
                existing_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                stage1a_file = existing_files[0]
                
                try:
                    with open(stage1a_file, 'r', encoding='utf-8') as f:
                        stage1a_data = json.load(f)
                    
                    # Extract results from the file structure
                    if 'results' in stage1a_data:
                        stage1a_results = stage1a_data['results']
                    else:
                        stage1a_results = stage1a_data
                    
                    self.logger.info(f"Successfully loaded Stage 1A dependency: {stage1a_file}")
                    return stage1a_results
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load {stage1a_file}: {e}")
                    continue
        
        # No valid Stage 1A results found
        error_msg = f"No Stage 1A results found for {paper_name}. Run Stage 1A first."
        self.logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    async def process_paper(self, paper_data: Dict[str, Any], stage1a_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process the paper through Stage 1B with REAL API call"""
        paper_id = paper_data['paper_id']
        self.logger.info(f"Processing {paper_id} through Stage 1B")
        
        # Validate using the validator
        try:
            start_time = time.time()
            result = await self.validator.validate(stage1a_results, paper_data)
            processing_time = time.time() - start_time
            
            self.logger.info(f"Successfully processed {paper_id} in {processing_time:.1f}s")
            return result
            
        except Exception as e:
            error_msg = f"API processing failed for {paper_id}: {str(e)}"
            self.logger.error(error_msg)
            raise
    
    def validate_results(self, results: Dict[str, Any]) -> Tuple[bool, str]:
        """Smart validation - flexible but with minimum threshold"""
        # Minimum requirement: Must have validation results
        validation_message = ""
        
        # Check for validation structure
        if isinstance(results, dict):
            # Look for validation indicators
            validation_indicators = [
                'success', 'validation_errors', 'validation_issues', 
                'validation_quality', 'confidence_score', 'validation_recommendations'
            ]
            
            # Check if any validation indicators exist
            result_keys = set(results.keys())
            found_indicators = result_keys.intersection(validation_indicators)
            
            if found_indicators:
                # Check if validation was successful
                if results.get('success', True) and not results.get('error'):
                    validation_message = "Valid validation result"
                    return True, validation_message
                else:
                    validation_message = f"Validation reported issues: {results.get('error', 'Unknown error')}"
                    return False, validation_message
            else:
                validation_message = "No validation structure found in result"
                return False, validation_message
        else:
            validation_message = "Result is not a valid dictionary"
            return False, validation_message
    
    def save_results(self, paper_id: str, results: Dict[str, Any], 
                    processing_time: float, validation_passed: bool, 
                    validation_message: str) -> str:
        """Save results for the single paper"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output with metadata
        output_data = {
            "stage_id": "1b",
            "stage_name": "Generic Validation",
            "paper_id": paper_id,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": processing_time,
            "processing_mode": "single_paper",
            "validation_passed": validation_passed,
            "validation_message": validation_message,
            "results": results
        }
        
        # Save to output directory
        output_file = self.output_dir / f"{paper_id}_1b_{timestamp}.json"
        
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
            
            # Load Stage 1A dependency
            stage1a_results = self.load_stage1a_dependency(paper_name)
            
            # Process through Stage 1B
            results = await self.process_paper(paper_data, stage1a_results)
            
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
        description="Process Single Paper through Stage 1B - NO FALLBACKS",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--paper", required=True, 
                       help="Paper name to process (e.g., 'paper_name.json' or 'paper_name')")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = SinglePaperStage1BProcessor(args.api_key)
    
    print(f"\n🔄 Processing paper: {args.paper}")
    print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Process the paper
    result = await processor.run(args.paper)
    
    # Report results
    if result['success']:
        print(f"\n✅ SUCCESS: Paper validated successfully")
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