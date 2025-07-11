#!/usr/bin/env python3
"""
Test Stage 3B: Synthesis Validation Testing
Validates Stage 3A synthesis results and produces enhanced synthesis output
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
from stage_test_utils import StageTestFramework, calculate_stage_cost, validate_paper_exists

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary synthesis engine components
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from stage_3_processors.synthesis_validator import SynthesisValidator

async def test_stage_3b(paper_filename: str, api_key: str, disable_cache: bool = False, 
                       verbose: bool = False, save_debug: bool = False, 
                       use_main_cache: bool = False):
    """
    Test Stage 3B: Synthesis Validation in isolation
    
    Args:
        paper_filename: Name of paper to test
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        use_main_cache: Use main pipeline cache namespace
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework('3b', 'Synthesis Validation')
    framework.logger.info(f"Starting Stage 3B test for paper: {paper_filename}")
    
    try:
        # Get paper ID
        paper_id = paper_filename.replace('.json', '').replace('.pdf', '')
        
        # Display paper info
        print(f"\n📄 Testing Paper: {paper_id}")
        print("   Stage 3B validates Stage 3A synthesis and produces enhanced output")
        
        # Load Stage 1B, 2B, and 3A dependencies
        framework.logger.info("Loading Stage 1B, 2B, and 3A dependencies...")
        stage_1b_results, stage_2b_results, stage_3a_results = load_stage_dependencies(
            paper_id, framework, use_main_cache
        )
        
        # Check for missing dependencies
        missing = []
        if not stage_1b_results:
            missing.append("Stage 1B")
        if not stage_2b_results:
            missing.append("Stage 2B")
        if not stage_3a_results:
            missing.append("Stage 3A")
            
        if missing:
            raise ValueError(
                f"Missing required dependencies: {', '.join(missing)}. "
                f"Please run the prerequisite stages first:\n"
                f"  python test_stage_1b.py --paper {paper_filename} --api-key YOUR_KEY\n"
                f"  python test_stage_2b.py --paper {paper_filename} --api-key YOUR_KEY\n"
                f"  python test_stage_3a.py --paper {paper_filename} --api-key YOUR_KEY"
            )
        
        print(f"   ✅ Found Stage 1B results ({len(str(stage_1b_results))} chars)")
        print(f"   ✅ Found Stage 2B results ({len(str(stage_2b_results))} chars)")
        print(f"   ✅ Found Stage 3A results ({len(str(stage_3a_results))} chars)")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create validator
        validator = SynthesisValidator(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_paper_id = f"test_{paper_id}" if not use_main_cache else paper_id
        
        if not disable_cache:
            cache_source = "main pipeline" if use_main_cache else "isolated test"
            print(f"\n🔍 Checking {cache_source} cache...")
            
            if framework.cache_manager.is_stage_cached(cache_paper_id, '3b'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_paper_id, '3b')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 3B results from {cache_source}")
                    results = cached_result
                    # Estimate metrics from cached data
                    framework.update_metrics(
                        {"input": 0, "output": 0},  # No new tokens used
                        0.0  # No cost for cache hit
                    )
                else:
                    # Cache might have error, proceed with fresh processing
                    results = None
            else:
                results = None
        else:
            print("\n🔄 Cache disabled, forcing fresh processing...")
            results = None
            
        # Process if no valid cached results
        if results is None:
            framework.logger.info("Processing Stage 3B validation...")
            framework.start_tracking()
            
            print("\n🔄 Running Stage 3B: Synthesis Validation...")
            print("   This validates Stage 3A synthesis and produces enhanced output...")
            
            # Run validation using enhanced method that accepts all dependencies
            results = await validate_enhanced_synthesis(
                validator, stage_1b_results, stage_2b_results, stage_3a_results
            )
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                input_size = len(str(stage_1b_results)) + len(str(stage_2b_results)) + len(str(stage_3a_results))
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
            
            # Cache the results (using appropriate cache namespace)
            if not disable_cache and 'error' not in results:
                cache_namespace = "main pipeline" if use_main_cache else "isolated test"
                framework.logger.info(f"Caching successful results to {cache_namespace}...")
                framework.cache_manager.cache_stage_result(cache_paper_id, '3b', results, {})
                
        # Save output to standard pipeline location with test metadata
        output_path = framework.save_stage_output(paper_id, results, run_type="stage_test")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='3b')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print("\n✅ Stage 3B output validation passed")
            
        # Display results
        framework.display_results(results, detailed=verbose)
        
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "paper_id": paper_id,
                "input_stats": {
                    "stage_1b_size": len(str(stage_1b_results)),
                    "stage_2b_size": len(str(stage_2b_results)),
                    "stage_3a_size": len(str(stage_3a_results)),
                    "stage_1b_fields": len(stage_1b_results) if isinstance(stage_1b_results, dict) else 0,
                    "stage_2b_fields": len(stage_2b_results) if isinstance(stage_2b_results, dict) else 0,
                    "stage_3a_fields": len(stage_3a_results) if isinstance(stage_3a_results, dict) else 0
                },
                "validation_stats": {
                    "validation_sections": count_validation_sections(results),
                    "enhanced_synthesis_present": 'enhanced_synthesis' in results,
                    "validation_success": results.get('success', False)
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                },
                "dependencies": {
                    "stage_1b_found": stage_1b_results is not None,
                    "stage_2b_found": stage_2b_results is not None,
                    "stage_3a_found": stage_3a_results is not None
                }
            }
            
            debug_path = framework.stage_output_dir / f"{paper_id}_3b_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "paper_id": paper_id,
            "output_path": output_path,
            "validation": {
                "passed": is_valid,
                "issues": validation_issues
            },
            "metrics": {
                "processing_time": framework.start_time and (datetime.now().timestamp() - framework.start_time),
                "token_usage": framework.token_usage,
                "cost": framework.cost
            },
            "dependencies": {
                "stage_1b_loaded": stage_1b_results is not None,
                "stage_2b_loaded": stage_2b_results is not None,
                "stage_3a_loaded": stage_3a_results is not None
            }
        }
        
        print(f"\n📁 Results saved to standard pipeline: {output_path}")
        print(f"    Next stages will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 3B test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 3B test failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "3b",
            "paper_id": paper_filename,
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output(
            paper_filename.replace('.json', '').replace('.pdf', ''), 
            error_result,
            run_type="stage_test_error"
        )
        
        return {
            "success": False,
            "error": str(e),
            "paper_id": paper_filename
        }

async def validate_enhanced_synthesis(validator, stage_1b_results, stage_2b_results, stage_3a_results):
    """
    Enhanced validation method that provides all dependencies to the validator
    
    This method works around the current SynthesisValidator limitation by manually
    formatting the prompt with all required dependencies.
    """
    try:
        # Load the prompt template and format it with all dependencies
        prompt_template = validator.prompt_template
        
        # Use string replacement to avoid JSON brace conflicts (same fix as Stage 3A)
        formatted_prompt = prompt_template.replace(
            '{stage_1b_results}', json.dumps(stage_1b_results, indent=2)
        ).replace(
            '{stage_2b_results}', json.dumps(stage_2b_results, indent=2)
        ).replace(
            '{stage_3a_results}', json.dumps(stage_3a_results, indent=2)
        )
        
        # Generate validation with all dependencies
        validation_result = await validator.client.generate_json_content(
            formatted_prompt,
            temperature=validator.temperature,
            stage_name="stage_3b_synthesis_validation",
            paper_id=stage_3a_results.get('paper_id', 'Unknown')
        )
        
        # Check if we got an error from the API
        if 'error' in validation_result:
            logging.error(f"API returned error: {validation_result.get('error')}")
            return validation_result
        
        # Add validation metadata
        validation_result['success'] = validation_result.get('success', True)
        validation_result['stage'] = '3B'
        validation_result['validation_timestamp'] = datetime.now().isoformat()
        validation_result['temperature_used'] = validator.temperature
        validation_result['validated_stage'] = '3A'
        
        return validation_result
        
    except Exception as e:
        logging.error(f"Enhanced validation failed: {str(e)}")
        return {
            "error": str(e),
            "stage": "3B",
            "paper_id": stage_3a_results.get('paper_id', 'Unknown'),
            "success": False,
            "validation_timestamp": datetime.now().isoformat()
        }

def load_stage_dependencies(paper_id: str, framework: StageTestFramework, use_main_cache: bool):
    """
    Load Stage 1B, 2B, and 3A results for synthesis validation
    
    Args:
        paper_id: Paper identifier
        framework: Test framework instance
        use_main_cache: Whether to use main pipeline cache
        
    Returns:
        Tuple of (stage_1b_results, stage_2b_results, stage_3a_results)
    """
    cache_paper_id = f"test_{paper_id}" if not use_main_cache else paper_id
    
    stage_1b_results = None
    stage_2b_results = None
    stage_3a_results = None
    
    # Try to load from cache first
    print("\n🔍 Looking for Stage 1B, 2B, and 3A dependencies...")
    
    # Load Stage 1B
    if framework.cache_manager.is_stage_cached(cache_paper_id, '1b'):
        stage_1b_results = framework.cache_manager.get_cached_result(cache_paper_id, '1b')
        if stage_1b_results and 'error' not in stage_1b_results:
            print("   ✅ Found Stage 1B in cache")
        else:
            stage_1b_results = None
    
    # Load Stage 2B
    if framework.cache_manager.is_stage_cached(cache_paper_id, '2b'):
        stage_2b_results = framework.cache_manager.get_cached_result(cache_paper_id, '2b')
        if stage_2b_results and 'error' not in stage_2b_results:
            print("   ✅ Found Stage 2B in cache")
        else:
            stage_2b_results = None
    
    # Load Stage 3A
    if framework.cache_manager.is_stage_cached(cache_paper_id, '3a'):
        stage_3a_results = framework.cache_manager.get_cached_result(cache_paper_id, '3a')
        if stage_3a_results and 'error' not in stage_3a_results:
            print("   ✅ Found Stage 3A in cache")
        else:
            stage_3a_results = None
    
    # Fall back to stage outputs if not found in cache
    if not stage_1b_results:
        stage_1b_path = Path("8_stage_outputs") / f"{paper_id}_1b.json"
        if stage_1b_path.exists():
            with open(stage_1b_path, 'r', encoding='utf-8') as f:
                stage_1b_results = json.load(f)
            print("   ✅ Found Stage 1B in pipeline outputs")
        else:
            print("   ❌ Stage 1B not found")
    
    if not stage_2b_results:
        stage_2b_path = Path("8_stage_outputs") / f"{paper_id}_2b.json"
        if stage_2b_path.exists():
            with open(stage_2b_path, 'r', encoding='utf-8') as f:
                stage_2b_results = json.load(f)
            print("   ✅ Found Stage 2B in pipeline outputs")
        else:
            print("   ❌ Stage 2B not found")
    
    if not stage_3a_results:
        stage_3a_path = Path("8_stage_outputs") / f"{paper_id}_3a.json"
        if stage_3a_path.exists():
            with open(stage_3a_path, 'r', encoding='utf-8') as f:
                stage_3a_results = json.load(f)
            print("   ✅ Found Stage 3A in pipeline outputs")
        else:
            print("   ❌ Stage 3A not found")
    
    return stage_1b_results, stage_2b_results, stage_3a_results

def count_validation_sections(results: dict) -> int:
    """Count the number of validation sections in results"""
    if not isinstance(results, dict):
        return 0
        
    validation_keys = [
        'integration_accuracy_validation', 'scientific_precision_validation', 
        'contribution_assessment_validation', 'uncertainty_validation',
        'agricultural_integration_validation', 'enhanced_synthesis'
    ]
    
    return sum(1 for key in validation_keys if key in results and results[key])

def main():
    """Main entry point for Stage 3B testing"""
    # Initialize framework for argument parsing
    framework = StageTestFramework('3b', 'Synthesis Validation')
    
    # Get command line arguments
    parser = framework.get_standard_args(
        "Validate Stage 3A synthesis results and produce enhanced synthesis output"
    )
    
    # Add stage-specific arguments if needed
    parser.add_argument("--show-prompt", action="store_true",
                      help="Display the prompt being sent to Gemini")
    parser.add_argument("--use-main-cache", action="store_true",
                      help="Use main pipeline cache namespace (may find existing results)")
    parser.add_argument("--fresh-cache", action="store_true", 
                      help="Use isolated test cache namespace (default behavior)")
    
    args = parser.parse_args()
    
    # Validate paper exists
    if not validate_paper_exists(args.paper):
        print(f"❌ Error: Paper '{args.paper}' not found in synthesis_ready directory")
        print("\nAvailable papers:")
        from stage_test_utils import load_paper_list
        papers = load_paper_list(limit=10)
        for i, paper in enumerate(papers[:10]):
            print(f"  {i+1}. {paper}")
        if len(papers) > 10:
            print(f"  ... and {len(papers) - 10} more")
        sys.exit(1)
        
    # Override output directory if specified
    if args.output_dir:
        framework.test_outputs_dir = args.output_dir
        framework.stage_output_dir = os.path.join(args.output_dir, f"stage_{framework.stage_id}")
        os.makedirs(framework.stage_output_dir, exist_ok=True)
        
    print(f"\n{'='*80}")
    print(f"STAGE 3B TEST: Synthesis Validation")
    print(f"{'='*80}")
    
    # Show cache mode
    if args.use_main_cache:
        print("🔗 Using main pipeline cache namespace (may find existing results)")
    else:
        print("🏠 Using isolated test cache namespace (fresh testing)")
        
    print("📁 Saving to standard pipeline outputs (8_stage_outputs/) for natural stage chaining")
    print("📋 Dependencies: Requires Stage 1B, 2B, and 3A results")
    
    # Run the test
    result = asyncio.run(test_stage_3b(
        paper_filename=args.paper,
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug,
        use_main_cache=args.use_main_cache
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print("✅ Stage 3B test completed successfully")
        if 'dependencies' in result:
            deps = result['dependencies']
            print(f"   Dependencies loaded: 1B={deps['stage_1b_loaded']}, 2B={deps['stage_2b_loaded']}, 3A={deps['stage_3a_loaded']}")
    else:
        print("❌ Stage 3B test failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()