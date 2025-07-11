#!/usr/bin/env python3
"""
Stage 5A: Chunk Synthesis Script
Synthesizes individual thematic chunks from Stage 4.5 chunk extraction outputs
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import stage test framework
from stage_test_utils import StageTestFramework, calculate_stage_cost

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary synthesis engine components
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader


class Stage5AChunkSynthesizer:
    """Handles Stage 5A chunk synthesis processing"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.gemini_client = gemini_client
        self.prompt_loader = prompt_loader
        
    async def synthesize_chunk(self, chunk_number: int, chunk_data: dict) -> dict:
        """
        Synthesize a specific chunk using appropriate Stage 5A prompt
        
        Args:
            chunk_number: Chunk number (1-6)
            chunk_data: Chunk evidence data from Stage 4.5
            
        Returns:
            Synthesis results
        """
        # Map chunk numbers to stage prompts
        chunk_stage_map = {
            1: 'stage_5a_regional_synthesis',
            2: 'stage_5a_temporal_synthesis', 
            3: 'stage_5a_crop_specific_synthesis',
            4: 'stage_5a_crop_uptake_synthesis',
            5: 'stage_5a_manure_cycling_synthesis',
            6: 'stage_5a_residue_cycling_synthesis'
        }
        
        chunk_variable_map = {
            1: 'chunk1_regional_evidence',
            2: 'chunk2_temporal_evidence',
            3: 'chunk3_crop_evidence', 
            4: 'chunk4_uptake_evidence',
            5: 'chunk5_manure_evidence',
            6: 'chunk6_residue_evidence'
        }
        
        if chunk_number not in chunk_stage_map:
            raise ValueError(f"Invalid chunk number: {chunk_number}. Must be 1-6.")
            
        stage_prompt = chunk_stage_map[chunk_number]
        variable_name = chunk_variable_map[chunk_number]
        
        # Load prompt
        prompt_template = self.prompt_loader.load_prompt(stage_prompt)
        
        # Prepare evidence for prompt
        evidence_json = json.dumps(chunk_data, indent=2, ensure_ascii=False)
        
        # Replace template variable
        prompt = prompt_template.replace(f"{{{variable_name}}}", evidence_json)
        
        # Make AI call
        try:
            result = await self.gemini_client.generate_json_content(
                prompt=prompt,
                stage_name=f"stage_5a_chunk{chunk_number}",
                paper_id=f"chunk{chunk_number}"
            )
            
            # Check for API errors
            if 'error' in result:
                error_msg = f"Chunk {chunk_number} synthesis failed: {result['error']}"
                return {"error": error_msg, "raw_response": result}
            
            # Add stage metadata
            result['stage'] = f'5a_chunk{chunk_number}'
            result['chunk_number'] = chunk_number
            result['synthesis_timestamp'] = datetime.now().isoformat()
            
            return result
            
        # No need for JSON parsing since generate_json_content returns dict
        except Exception as e:
            error_msg = f"Chunk {chunk_number} synthesis failed: {str(e)}"
            return {"error": error_msg}


async def test_stage_5a(chunk_number: int, api_key: str, disable_cache: bool = False,
                       verbose: bool = False, save_debug: bool = False):
    """
    Test Stage 5A chunk synthesis
    
    Args:
        chunk_number: Which chunk to synthesize (1-6)
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework(f'5a_chunk{chunk_number}', f'Chunk {chunk_number} Synthesis')
    framework.logger.info(f"Starting Stage 5A Chunk {chunk_number} synthesis")
    
    try:
        # Load chunk data from Stage 4.5 outputs
        framework.logger.info(f"Loading chunk {chunk_number} data...")
        
        # Map chunk numbers to exact filenames - no stupid wildcards
        chunk_file_map = {
            1: "chunk1_regional_soil_k_supply.json",
            2: "chunk2_temporal_soil_k_supply.json", 
            3: "chunk3_crop_specific_soil_k_supply.json",
            4: "chunk4_crop_uptake_integration.json",
            5: "chunk5_manure_cycling_integration.json",
            6: "chunk6_residue_cycling_integration.json"
        }
        
        if chunk_number not in chunk_file_map:
            raise ValueError(f"Invalid chunk number: {chunk_number}")
            
        chunk_filename = chunk_file_map[chunk_number]
        chunk_file = Path("8_stage_outputs/stage_4_5_chunks") / chunk_filename
        
        if not chunk_file.exists():
            raise FileNotFoundError(f"Chunk data file not found: {chunk_file}")
        
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)
            
        print(f"\n📊 Processing Chunk {chunk_number}")
        print(f"   Source: {chunk_file.name}")
        print(f"   Evidence pieces: {len(chunk_data.get('evidence', []))}")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create synthesizer
        synthesizer = Stage5AChunkSynthesizer(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_key = f"chunk{chunk_number}_synthesis"
        
        if not disable_cache:
            print(f"\n🔍 Checking cache for chunk {chunk_number}...")
            
            if framework.cache_manager.is_stage_cached(cache_key, f'5a_chunk{chunk_number}'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_key, f'5a_chunk{chunk_number}')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 5A Chunk {chunk_number} results")
                    results = cached_result
                    # No new tokens used
                    framework.update_metrics({"input": 0, "output": 0}, 0.0)
                else:
                    results = None
            else:
                results = None
        else:
            print(f"\n🔄 Cache disabled, forcing fresh processing...")
            results = None
            
        # Process if no valid cached results
        if results is None:
            framework.logger.info(f"Processing Stage 5A Chunk {chunk_number} synthesis...")
            framework.start_tracking()
            
            print(f"\n🔄 Running Stage 5A: Chunk {chunk_number} Synthesis...")
            
            # Run synthesis
            results = await synthesizer.synthesize_chunk(chunk_number, chunk_data)
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                token_usage = {
                    "input": len(str(chunk_data)) // 4,  # Rough estimate
                    "output": len(str(results)) // 4,
                    "thinking": 0
                }
                
            # Calculate cost
            cost = calculate_stage_cost(
                token_usage['input'],
                token_usage['output'],
                token_usage['thinking']
            )
            
            # Update metrics
            framework.update_metrics(token_usage, cost)
            
            # Cache the results
            if not disable_cache and 'error' not in results:
                framework.logger.info("Caching successful results...")
                framework.cache_manager.cache_stage_result(cache_key, f'5a_chunk{chunk_number}', results, chunk_data)
                
        # Save output to standard pipeline location
        output_path = framework.save_stage_output(f"chunk{chunk_number}", results, run_type="chunk_synthesis")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='5a')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Stage 5A Chunk {chunk_number} output validation passed")
            
        # Display results
        if not results.get('error'):
            print(f"\n📊 Chunk {chunk_number} Synthesis Summary:")
            if 'synthesis_scope' in results:
                print(f"   Scope: {results['synthesis_scope']}")
            if 'papers_integrated' in results:
                print(f"   Papers: {results['papers_integrated']}")
            if 'evidence_pieces_synthesized' in results:
                print(f"   Evidence pieces: {results['evidence_pieces_synthesized']}")
            if 'synthesis_confidence' in results:
                print(f"   Confidence: {results['synthesis_confidence']:.1%}")
        else:
            print(f"\n❌ Synthesis Error: {results['error']}")
            
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "chunk_number": chunk_number,
                "chunk_stats": {
                    "evidence_count": len(chunk_data.get('evidence', [])),
                    "source_file": str(chunk_file)
                },
                "synthesis_stats": {
                    "result_sections": len(results) if isinstance(results, dict) else 0,
                    "has_error": 'error' in results
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / f"chunk{chunk_number}_5a_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "chunk_number": chunk_number,
            "output_path": output_path,
            "validation": {
                "passed": is_valid,
                "issues": validation_issues
            },
            "metrics": {
                "processing_time": framework.start_time and (datetime.now().timestamp() - framework.start_time),
                "token_usage": framework.token_usage,
                "cost": framework.cost
            }
        }
        
        print(f"\n📁 Results saved to: {output_path}")
        print(f"    Stage 5B will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 5A Chunk {chunk_number} synthesis failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 5A Chunk {chunk_number} synthesis failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": f"5a_chunk{chunk_number}",
            "chunk_number": chunk_number,
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output(f"chunk{chunk_number}", error_result, run_type="chunk_synthesis_error")
        
        return {
            "success": False,
            "error": str(e),
            "chunk_number": chunk_number
        }


def main():
    """Main entry point for Stage 5A chunk synthesis"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage 5A: Synthesize individual thematic chunks from Stage 4.5 outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--chunk", type=int, choices=[1, 2, 3, 4, 5, 6], required=True,
                      help="Chunk number to synthesize (1=Regional, 2=Temporal, 3=Crop-Specific, 4=Crop Uptake, 5=Manure Cycling, 6=Residue Cycling)")
    parser.add_argument("--api-key", required=True,
                      help="Gemini API key")
    
    # Optional arguments  
    parser.add_argument("--disable-cache", action="store_true",
                      help="Force fresh processing, ignore cache")
    parser.add_argument("--verbose", action="store_true",
                      help="Show detailed processing information")
    parser.add_argument("--save-debug", action="store_true",
                      help="Save debug information and intermediate states")
    
    args = parser.parse_args()
    
    # Map chunk numbers to names
    chunk_names = {
        1: "Regional", 2: "Temporal", 3: "Crop-Specific", 
        4: "Crop Uptake", 5: "Manure Cycling", 6: "Residue Cycling"
    }
    
    print(f"\n{'='*80}")
    print(f"STAGE 5A: {chunk_names[args.chunk]} Chunk Synthesis")
    print(f"{'='*80}")
    print(f"Processing Chunk {args.chunk}: {chunk_names[args.chunk]} evidence synthesis")
    
    # Run the synthesis
    result = asyncio.run(test_stage_5a(
        chunk_number=args.chunk,
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print(f"✅ Stage 5A Chunk {args.chunk} synthesis completed successfully")
    else:
        print(f"❌ Stage 5A Chunk {args.chunk} synthesis failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()