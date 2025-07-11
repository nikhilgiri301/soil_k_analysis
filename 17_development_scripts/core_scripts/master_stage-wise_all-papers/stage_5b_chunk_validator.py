#!/usr/bin/env python3
"""
Stage 5B: Chunk Validation Script
Validates and enhances individual thematic chunks from Stage 5A synthesis outputs
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


class Stage5BChunkValidator:
    """Handles Stage 5B chunk validation processing"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.gemini_client = gemini_client
        self.prompt_loader = prompt_loader
        
    async def validate_chunk(self, chunk_number: int, chunk_evidence: dict, stage_5a_results: dict) -> dict:
        """
        Validate and enhance a specific chunk using appropriate Stage 5B prompt
        
        Args:
            chunk_number: Chunk number (1-6)
            chunk_evidence: Original chunk evidence data from Stage 4.5
            stage_5a_results: Stage 5A synthesis results
            
        Returns:
            Enhanced validation results
        """
        # Map chunk numbers to stage prompts
        chunk_stage_map = {
            1: 'stage_5b_regional_validation',
            2: 'stage_5b_temporal_validation',
            3: 'stage_5b_crop_specific_validation',
            4: 'stage_5b_crop_uptake_validation',
            5: 'stage_5b_manure_cycling_validation',
            6: 'stage_5b_residue_cycling_validation'
        }
        
        chunk_variable_map = {
            1: {'evidence': 'chunk1_regional_evidence', 'results': 'stage_5a_regional_results'},
            2: {'evidence': 'chunk2_temporal_evidence', 'results': 'stage_5a_temporal_results'},
            3: {'evidence': 'chunk3_crop_evidence', 'results': 'stage_5a_crop_results'},
            4: {'evidence': 'chunk4_uptake_evidence', 'results': 'stage_5a_uptake_results'},
            5: {'evidence': 'chunk5_manure_evidence', 'results': 'stage_5a_manure_results'},
            6: {'evidence': 'chunk6_residue_evidence', 'results': 'stage_5a_residue_results'}
        }
        
        if chunk_number not in chunk_stage_map:
            raise ValueError(f"Invalid chunk number: {chunk_number}. Must be 1-6.")
            
        stage_prompt = chunk_stage_map[chunk_number]
        variable_names = chunk_variable_map[chunk_number]
        
        # Load prompt
        prompt_template = self.prompt_loader.load_prompt(stage_prompt)
        
        # Prepare data for prompt
        evidence_json = json.dumps(chunk_evidence, indent=2, ensure_ascii=False)
        results_json = json.dumps(stage_5a_results, indent=2, ensure_ascii=False)
        
        # Replace template variables
        prompt = prompt_template.replace(f"{{{variable_names['evidence']}}}", evidence_json)
        prompt = prompt.replace(f"{{{variable_names['results']}}}", results_json)
        
        # Make AI call
        try:
            response = await self.gemini_client.generate_response(prompt)
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add stage metadata
            result['stage'] = f'5b_chunk{chunk_number}'
            result['chunk_number'] = chunk_number
            result['validation_timestamp'] = datetime.now().isoformat()
            
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from Gemini: {str(e)}"
            return {"error": error_msg, "raw_response": response}
        except Exception as e:
            error_msg = f"Chunk {chunk_number} validation failed: {str(e)}"
            return {"error": error_msg}


async def test_stage_5b(chunk_number: int, api_key: str, disable_cache: bool = False,
                       verbose: bool = False, save_debug: bool = False):
    """
    Test Stage 5B chunk validation
    
    Args:
        chunk_number: Which chunk to validate (1-6)
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework(f'5b_chunk{chunk_number}', f'Chunk {chunk_number} Validation')
    framework.logger.info(f"Starting Stage 5B Chunk {chunk_number} validation")
    
    try:
        # Load dependency data
        framework.logger.info(f"Loading dependency data for chunk {chunk_number}...")
        
        # Load original chunk evidence from Stage 4.5
        chunk_files = list(Path("8_stage_outputs/stage_4_5_chunks").glob(f"chunk{chunk_number}_*.json"))
        if not chunk_files:
            raise FileNotFoundError(f"No Stage 4.5 chunk {chunk_number} files found")
        chunk_file = max(chunk_files, key=lambda f: f.stat().st_mtime)
        
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_evidence = json.load(f)
            
        # Load Stage 5A results
        stage_5a_files = list(Path("8_stage_outputs").glob(f"stage_5a_chunk{chunk_number}/chunk{chunk_number}_5a_chunk{chunk_number}_*.json"))
        if not stage_5a_files:
            raise FileNotFoundError(f"No Stage 5A chunk {chunk_number} synthesis results found. Run Stage 5A first.")
        stage_5a_file = max(stage_5a_files, key=lambda f: f.stat().st_mtime)
        
        with open(stage_5a_file, 'r', encoding='utf-8') as f:
            stage_5a_data = json.load(f)
            stage_5a_results = stage_5a_data.get('results', stage_5a_data)
            
        print(f"\n📊 Validating Chunk {chunk_number}")
        print(f"   Original evidence: {chunk_file.name}")
        print(f"   Stage 5A results: {stage_5a_file.name}")
        print(f"   Evidence pieces: {len(chunk_evidence.get('evidence', []))}")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create validator
        validator = Stage5BChunkValidator(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_key = f"chunk{chunk_number}_validation"
        
        if not disable_cache:
            print(f"\n🔍 Checking cache for chunk {chunk_number} validation...")
            
            if framework.cache_manager.is_stage_cached(cache_key, f'5b_chunk{chunk_number}'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_key, f'5b_chunk{chunk_number}')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 5B Chunk {chunk_number} results")
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
            framework.logger.info(f"Processing Stage 5B Chunk {chunk_number} validation...")
            framework.start_tracking()
            
            print(f"\n🔄 Running Stage 5B: Chunk {chunk_number} Validation...")
            
            # Run validation
            results = await validator.validate_chunk(chunk_number, chunk_evidence, stage_5a_results)
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                input_size = len(str(chunk_evidence)) + len(str(stage_5a_results))
                token_usage = {
                    "input": input_size // 4,  # Rough estimate
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
                cache_data = {"chunk_evidence": chunk_evidence, "stage_5a_results": stage_5a_results}
                framework.cache_manager.cache_stage_result(cache_key, f'5b_chunk{chunk_number}', results, cache_data)
                
        # Save output to standard pipeline location
        output_path = framework.save_stage_output(f"chunk{chunk_number}", results, run_type="chunk_validation")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='5b')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Stage 5B Chunk {chunk_number} output validation passed")
            
        # Display results
        if not results.get('error'):
            print(f"\n📊 Chunk {chunk_number} Validation Summary:")
            
            # Check validation quality
            if 'validation_quality' in results:
                qual = results['validation_quality']
                print(f"   Validation Thoroughness: {qual.get('validation_thoroughness', 0):.1%}")
                enhancement_value = qual.get('enhancement_value', 'unknown')
                print(f"   Enhancement Value: {enhancement_value}")
                cert = qual.get('validation_certification', 'unknown')
                print(f"   Certification: {cert}")
                
            # Check accuracy verification
            if 'accuracy_verification' in results:
                acc = results['accuracy_verification']
                verified_sections = sum(1 for section in acc.values() 
                                      if isinstance(section, dict) and section.get('verification_status', False))
                print(f"   Verified Sections: {verified_sections}/{len(acc)}")
                
            # Check enhancements in enhanced synthesis
            enhanced_key = None
            for key in results.keys():
                if key.startswith('enhanced_') and key.endswith('_synthesis'):
                    enhanced_key = key
                    break
                    
            if enhanced_key:
                enhanced = results[enhanced_key]
                if isinstance(enhanced, dict):
                    print(f"   Enhanced Synthesis: {len(enhanced)} sections")
                    if 'enhancement_summary' in enhanced:
                        summary = enhanced['enhancement_summary']
                        if summary:
                            print(f"   Enhancement Summary: {summary[:100]}...")
        else:
            print(f"\n❌ Validation Error: {results['error']}")
            
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "chunk_number": chunk_number,
                "dependency_stats": {
                    "evidence_count": len(chunk_evidence.get('evidence', [])),
                    "stage_5a_sections": len(stage_5a_results) if isinstance(stage_5a_results, dict) else 0
                },
                "validation_stats": {
                    "result_sections": len(results) if isinstance(results, dict) else 0,
                    "has_error": 'error' in results,
                    "has_enhanced_synthesis": any(k.startswith('enhanced_') for k in results.keys())
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / f"chunk{chunk_number}_5b_debug.json"
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
        print(f"    Stage 6A will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 5B Chunk {chunk_number} validation failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 5B Chunk {chunk_number} validation failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": f"5b_chunk{chunk_number}",
            "chunk_number": chunk_number,
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output(f"chunk{chunk_number}", error_result, run_type="chunk_validation_error")
        
        return {
            "success": False,
            "error": str(e),
            "chunk_number": chunk_number
        }


def main():
    """Main entry point for Stage 5B chunk validation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage 5B: Validate and enhance individual thematic chunks from Stage 5A outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("--chunk", type=int, choices=[1, 2, 3, 4, 5, 6], required=True,
                      help="Chunk number to validate (1=Regional, 2=Temporal, 3=Crop-Specific, 4=Crop Uptake, 5=Manure Cycling, 6=Residue Cycling)")
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
    print(f"STAGE 5B: {chunk_names[args.chunk]} Chunk Validation")
    print(f"{'='*80}")
    print(f"Validating Chunk {args.chunk}: {chunk_names[args.chunk]} synthesis validation")
    
    # Run the validation
    result = asyncio.run(test_stage_5b(
        chunk_number=args.chunk,
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print(f"✅ Stage 5B Chunk {args.chunk} validation completed successfully")
    else:
        print(f"❌ Stage 5B Chunk {args.chunk} validation failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()