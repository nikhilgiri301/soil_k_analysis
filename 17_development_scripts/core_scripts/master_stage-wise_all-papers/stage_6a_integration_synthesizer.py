#!/usr/bin/env python3
"""
Stage 6A: Cross-Chunk Integration Script
Integrates all six enhanced chunk syntheses from Stage 5B into unified understanding
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


class Stage6AIntegrationSynthesizer:
    """Handles Stage 6A cross-chunk integration processing"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.gemini_client = gemini_client
        self.prompt_loader = prompt_loader
        
    async def integrate_chunks(self, chunk_results: dict) -> dict:
        """
        Integrate all six enhanced chunk syntheses into unified understanding
        
        Args:
            chunk_results: Dictionary mapping chunk numbers to Stage 5B enhanced results
            
        Returns:
            Cross-chunk integration results
        """
        # Load prompt
        prompt_template = self.prompt_loader.load_prompt('stage_6a_cross_chunk_integration')
        
        # Prepare chunk results for prompt
        chunk_variable_map = {
            1: 'stage_5b_regional_results',
            2: 'stage_5b_temporal_results', 
            3: 'stage_5b_crop_results',
            4: 'stage_5b_uptake_results',
            5: 'stage_5b_manure_results',
            6: 'stage_5b_residue_results'
        }
        
        # Replace template variables
        prompt = prompt_template
        for chunk_num, variable_name in chunk_variable_map.items():
            if chunk_num in chunk_results:
                chunk_json = json.dumps(chunk_results[chunk_num], indent=2, ensure_ascii=False)
                prompt = prompt.replace(f"{{{variable_name}}}", chunk_json)
            else:
                # Handle missing chunk data
                error_msg = f"Missing chunk {chunk_num} results"
                prompt = prompt.replace(f"{{{variable_name}}}", json.dumps({"error": error_msg}))
        
        # Make AI call
        try:
            response = await self.gemini_client.generate_response(prompt)
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add stage metadata
            result['stage'] = '6a'
            result['integration_timestamp'] = datetime.now().isoformat()
            result['chunks_integrated'] = list(chunk_results.keys())
            
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from Gemini: {str(e)}"
            return {"error": error_msg, "raw_response": response}
        except Exception as e:
            error_msg = f"Cross-chunk integration failed: {str(e)}"
            return {"error": error_msg}


async def test_stage_6a(api_key: str, disable_cache: bool = False,
                       verbose: bool = False, save_debug: bool = False):
    """
    Test Stage 6A cross-chunk integration
    
    Args:
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework('6a', 'Cross-Chunk Integration')
    framework.logger.info("Starting Stage 6A cross-chunk integration")
    
    try:
        # Load all six enhanced chunk syntheses from Stage 5B
        framework.logger.info("Loading all six enhanced chunk syntheses...")
        
        chunk_results = {}
        chunk_names = {
            1: "Regional", 2: "Temporal", 3: "Crop-Specific", 
            4: "Crop Uptake", 5: "Manure Cycling", 6: "Residue Cycling"
        }
        
        missing_chunks = []
        
        for chunk_num in range(1, 7):
            # Look for Stage 5B enhanced results
            stage_5b_files = list(Path("8_stage_outputs").glob(f"stage_5b_chunk{chunk_num}/chunk{chunk_num}_5b_chunk{chunk_num}_*.json"))
            
            if not stage_5b_files:
                missing_chunks.append(chunk_num)
                framework.logger.warning(f"No Stage 5B chunk {chunk_num} results found")
                continue
                
            # Use most recent file
            stage_5b_file = max(stage_5b_files, key=lambda f: f.stat().st_mtime)
            
            with open(stage_5b_file, 'r', encoding='utf-8') as f:
                stage_5b_data = json.load(f)
                
            # Extract enhanced synthesis results
            enhanced_results = stage_5b_data.get('results', stage_5b_data)
            
            # Look for enhanced synthesis section
            enhanced_key = None
            for key in enhanced_results.keys():
                if key.startswith('enhanced_') and key.endswith('_synthesis'):
                    enhanced_key = key
                    break
                    
            if enhanced_key:
                chunk_results[chunk_num] = enhanced_results[enhanced_key]
                framework.logger.info(f"Loaded enhanced chunk {chunk_num} ({chunk_names[chunk_num]}) from {stage_5b_file.name}")
            else:
                # Fallback to full results if no enhanced section found
                chunk_results[chunk_num] = enhanced_results
                framework.logger.warning(f"No enhanced synthesis found for chunk {chunk_num}, using full results")
        
        if missing_chunks:
            error_msg = f"Missing Stage 5B results for chunks: {missing_chunks}. Run Stage 5B for all chunks first."
            raise FileNotFoundError(error_msg)
            
        print(f"\n📊 Cross-Chunk Integration")
        print(f"   Loaded chunks: {len(chunk_results)}/6")
        for chunk_num in chunk_results.keys():
            print(f"   - Chunk {chunk_num}: {chunk_names[chunk_num]}")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create integrator
        integrator = Stage6AIntegrationSynthesizer(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_key = "cross_chunk_integration"
        
        if not disable_cache:
            print(f"\n🔍 Checking cache for cross-chunk integration...")
            
            if framework.cache_manager.is_stage_cached(cache_key, '6a'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_key, '6a')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 6A integration results")
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
            framework.logger.info("Processing Stage 6A cross-chunk integration...")
            framework.start_tracking()
            
            print(f"\n🔄 Running Stage 6A: Cross-Chunk Integration...")
            print("   Integrating all six enhanced chunk syntheses...")
            
            # Run integration
            results = await integrator.integrate_chunks(chunk_results)
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                input_size = sum(len(str(chunk)) for chunk in chunk_results.values())
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
                framework.cache_manager.cache_stage_result(cache_key, '6a', results, chunk_results)
                
        # Save output to standard pipeline location
        output_path = framework.save_stage_output("integration", results, run_type="cross_chunk_integration")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='6a')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Stage 6A integration output validation passed")
            
        # Display results
        if not results.get('error'):
            print(f"\n📊 Cross-Chunk Integration Summary:")
            
            # Integration metadata
            if 'cross_chunk_integration_metadata' in results:
                meta = results['cross_chunk_integration_metadata']
                print(f"   Chunks integrated: {meta.get('chunk_syntheses_integrated', 0)}")
                print(f"   Total evidence: {meta.get('total_evidence_pieces_represented', 0)}")
                print(f"   Papers: {meta.get('papers_represented', 0)}")
                print(f"   Integration confidence: {meta.get('integration_confidence', 0):.1%}")
                
            # Cross-chunk relationships
            if 'cross_chunk_relationship_synthesis' in results:
                relationships = results['cross_chunk_relationship_synthesis']
                relationship_count = len([k for k in relationships.keys() if not k.endswith('_quality')])
                print(f"   Cross-chunk relationships: {relationship_count}")
                
            # System insights
            if 'emergent_system_insights' in results:
                insights = results['emergent_system_insights']
                if 'system_level_patterns' in insights:
                    patterns = insights['system_level_patterns']
                    print(f"   Emergent patterns: {len(patterns) if isinstance(patterns, list) else 0}")
                    
            # System understanding
            if 'integrated_system_understanding' in results:
                understanding = results['integrated_system_understanding']
                understanding_sections = len([k for k in understanding.keys() if isinstance(understanding[k], dict)])
                print(f"   System understanding sections: {understanding_sections}")
                
        else:
            print(f"\n❌ Integration Error: {results['error']}")
            
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "integration_stats": {
                    "chunks_loaded": len(chunk_results),
                    "chunk_sizes": {f"chunk_{num}": len(str(data)) for num, data in chunk_results.items()},
                    "total_input_size": sum(len(str(chunk)) for chunk in chunk_results.values())
                },
                "result_stats": {
                    "result_sections": len(results) if isinstance(results, dict) else 0,
                    "has_error": 'error' in results,
                    "output_size": len(str(results))
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / "integration_6a_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "stage": "6a",
            "output_path": output_path,
            "chunks_integrated": list(chunk_results.keys()),
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
        print(f"    Stage 6B will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 6A integration failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 6A integration failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "6a",
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output("integration", error_result, run_type="cross_chunk_integration_error")
        
        return {
            "success": False,
            "error": str(e),
            "stage": "6a"
        }


def main():
    """Main entry point for Stage 6A cross-chunk integration"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage 6A: Integrate all six enhanced chunk syntheses into unified understanding",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
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
    
    print(f"\n{'='*80}")
    print(f"STAGE 6A: Cross-Chunk Integration Synthesis")
    print(f"{'='*80}")
    print("Integrating all six enhanced chunk syntheses into unified systems understanding")
    
    # Run the integration
    result = asyncio.run(test_stage_6a(
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print("✅ Stage 6A cross-chunk integration completed successfully")
        print(f"   Integrated chunks: {result.get('chunks_integrated', [])}")
    else:
        print("❌ Stage 6A cross-chunk integration failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()