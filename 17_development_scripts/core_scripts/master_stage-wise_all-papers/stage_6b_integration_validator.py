#!/usr/bin/env python3
"""
Stage 6B: Integration Validation Script
Validates and enhances the cross-chunk integration synthesis from Stage 6A
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


class Stage6BIntegrationValidator:
    """Handles Stage 6B integration validation processing"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.gemini_client = gemini_client
        self.prompt_loader = prompt_loader
        
    async def validate_integration(self, all_chunk_results: dict, stage_6a_results: dict) -> dict:
        """
        Validate and enhance the cross-chunk integration synthesis
        
        Args:
            all_chunk_results: All six enhanced chunk syntheses from Stage 5B
            stage_6a_results: Stage 6A cross-chunk integration results
            
        Returns:
            Enhanced integration validation results
        """
        # Load prompt
        prompt_template = self.prompt_loader.load_prompt('stage_6b_integration_validation')
        
        # Prepare data for prompt
        all_results_json = json.dumps(all_chunk_results, indent=2, ensure_ascii=False)
        integration_json = json.dumps(stage_6a_results, indent=2, ensure_ascii=False)
        
        # Replace template variables
        prompt = prompt_template.replace("{all_stage_5b_results}", all_results_json)
        prompt = prompt.replace("{stage_6a_integration_results}", integration_json)
        
        # Make AI call
        try:
            response = await self.gemini_client.generate_response(prompt)
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add stage metadata
            result['stage'] = '6b'
            result['validation_timestamp'] = datetime.now().isoformat()
            result['chunks_validated'] = list(all_chunk_results.keys())
            
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from Gemini: {str(e)}"
            return {"error": error_msg, "raw_response": response}
        except Exception as e:
            error_msg = f"Integration validation failed: {str(e)}"
            return {"error": error_msg}


async def test_stage_6b(api_key: str, disable_cache: bool = False,
                       verbose: bool = False, save_debug: bool = False):
    """
    Test Stage 6B integration validation
    
    Args:
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework('6b', 'Integration Validation')
    framework.logger.info("Starting Stage 6B integration validation")
    
    try:
        # Load dependency data
        framework.logger.info("Loading dependency data...")
        
        # Load all six enhanced chunk syntheses from Stage 5B
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
                framework.logger.info(f"Loaded enhanced chunk {chunk_num} ({chunk_names[chunk_num]})")
            else:
                # Fallback to full results if no enhanced section found
                chunk_results[chunk_num] = enhanced_results
                framework.logger.warning(f"No enhanced synthesis found for chunk {chunk_num}, using full results")
        
        if missing_chunks:
            error_msg = f"Missing Stage 5B results for chunks: {missing_chunks}. Run Stage 5B for all chunks first."
            raise FileNotFoundError(error_msg)
            
        # Load Stage 6A integration results
        stage_6a_files = list(Path("8_stage_outputs").glob("stage_6a/integration_6a_*.json"))
        if not stage_6a_files:
            raise FileNotFoundError("No Stage 6A integration results found. Run Stage 6A first.")
            
        stage_6a_file = max(stage_6a_files, key=lambda f: f.stat().st_mtime)
        
        with open(stage_6a_file, 'r', encoding='utf-8') as f:
            stage_6a_data = json.load(f)
            stage_6a_results = stage_6a_data.get('results', stage_6a_data)
            
        print(f"\n📊 Integration Validation")
        print(f"   Chunk syntheses: {len(chunk_results)}/6")
        print(f"   Stage 6A integration: {stage_6a_file.name}")
        for chunk_num in chunk_results.keys():
            print(f"   - Chunk {chunk_num}: {chunk_names[chunk_num]}")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create validator
        validator = Stage6BIntegrationValidator(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_key = "integration_validation"
        
        if not disable_cache:
            print(f"\n🔍 Checking cache for integration validation...")
            
            if framework.cache_manager.is_stage_cached(cache_key, '6b'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_key, '6b')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 6B validation results")
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
            framework.logger.info("Processing Stage 6B integration validation...")
            framework.start_tracking()
            
            print(f"\n🔄 Running Stage 6B: Integration Validation...")
            print("   Validating and enhancing cross-chunk integration...")
            
            # Run validation
            results = await validator.validate_integration(chunk_results, stage_6a_results)
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                input_size = len(str(chunk_results)) + len(str(stage_6a_results))
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
                cache_data = {"chunk_results": chunk_results, "stage_6a_results": stage_6a_results}
                framework.cache_manager.cache_stage_result(cache_key, '6b', results, cache_data)
                
        # Save output to standard pipeline location
        output_path = framework.save_stage_output("integration", results, run_type="integration_validation")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='6b')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Stage 6B integration validation output passed")
            
        # Display results
        if not results.get('error'):
            print(f"\n📊 Integration Validation Summary:")
            
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
                
            # Check enhanced integration synthesis
            if 'enhanced_integration_synthesis' in results:
                enhanced = results['enhanced_integration_synthesis']
                if isinstance(enhanced, dict):
                    print(f"   Enhanced Integration: {len(enhanced)} sections")
                    
                    # Integration metadata
                    if 'integration_synthesis_metadata' in enhanced:
                        meta = enhanced['integration_synthesis_metadata']
                        print(f"   Enhanced chunks: {meta.get('chunk_syntheses_integrated', 0)}")
                        print(f"   Enhanced confidence: {meta.get('integration_confidence', 0):.1%}")
                        
                    # Enhanced relationships
                    if 'enhanced_cross_chunk_relationships' in enhanced:
                        rel = enhanced['enhanced_cross_chunk_relationships']
                        rel_count = len([k for k in rel.keys() if not k.endswith('_quality')])
                        print(f"   Enhanced relationships: {rel_count}")
                        
                    # Enhanced system understanding
                    if 'enhanced_system_understanding' in enhanced:
                        sys_understanding = enhanced['enhanced_system_understanding']
                        understanding_sections = len(sys_understanding) if isinstance(sys_understanding, dict) else 0
                        print(f"   Enhanced system sections: {understanding_sections}")
                        
        else:
            print(f"\n❌ Validation Error: {results['error']}")
            
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "dependency_stats": {
                    "chunks_loaded": len(chunk_results),
                    "stage_6a_sections": len(stage_6a_results) if isinstance(stage_6a_results, dict) else 0,
                    "total_input_size": len(str(chunk_results)) + len(str(stage_6a_results))
                },
                "validation_stats": {
                    "result_sections": len(results) if isinstance(results, dict) else 0,
                    "has_error": 'error' in results,
                    "has_enhanced_integration": 'enhanced_integration_synthesis' in results,
                    "output_size": len(str(results))
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / "integration_6b_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "stage": "6b",
            "output_path": output_path,
            "chunks_validated": list(chunk_results.keys()),
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
        print(f"    Stage 7A will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 6B validation failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 6B validation failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "6b",
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output("integration", error_result, run_type="integration_validation_error")
        
        return {
            "success": False,
            "error": str(e),
            "stage": "6b"
        }


def main():
    """Main entry point for Stage 6B integration validation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage 6B: Validate and enhance cross-chunk integration synthesis from Stage 6A",
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
    print(f"STAGE 6B: Integration Validation")
    print(f"{'='*80}")
    print("Validating and enhancing cross-chunk integration synthesis")
    
    # Run the validation
    result = asyncio.run(test_stage_6b(
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print("✅ Stage 6B integration validation completed successfully")
        print(f"   Validated chunks: {result.get('chunks_validated', [])}")
    else:
        print("❌ Stage 6B integration validation failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()