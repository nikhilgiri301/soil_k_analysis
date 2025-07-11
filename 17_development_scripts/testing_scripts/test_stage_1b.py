#!/usr/bin/env python3
"""
Test Stage 1B: Generic Validation Testing
Validates generic extraction results from Stage 1A in isolation
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import stage test framework
from stage_test_utils import StageTestFramework, calculate_stage_cost, validate_paper_exists

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary synthesis engine components
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from stage_1_processors.generic_validator import GenericValidator

async def test_stage_1b(paper_filename: str, api_key: str, disable_cache: bool = False, 
                       verbose: bool = False, save_debug: bool = False, 
                       use_main_cache: bool = False):
    """
    Test Stage 1B: Generic Validation in isolation
    
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
    framework = StageTestFramework('1b', 'Generic Validation')
    framework.logger.info(f"Starting Stage 1B test for paper: {paper_filename}")
    
    try:
        # Load paper data (needed for validation context)
        framework.logger.info("Loading paper data...")
        paper_data = framework.load_paper_data(paper_filename)
        paper_id = paper_data.get('filename', 'unknown').replace('.json', '').replace('.pdf', '')
        
        # Load Stage 1A dependency results
        framework.logger.info("Loading Stage 1A dependency results...")
        dependency_results = framework.load_dependency_results(paper_id, ['1a'], use_cache=True)
        stage_1a_results = dependency_results['stage_1a_results']
        
        # Display dependency info
        print(f"\n📄 Testing Paper: {paper_id}")
        print(f"   Stage 1A dependency: ✅ Found")
        if 'paper_metadata' in stage_1a_results:
            title = stage_1a_results['paper_metadata'].get('title', 'N/A')
            print(f"   Paper title: {title[:80]}...")
        print(f"   1A result size: {len(str(stage_1a_results))} characters")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create validator
        validator = GenericValidator(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_paper_id = f"test_{paper_id}" if not use_main_cache else paper_id
        
        if not disable_cache:
            cache_source = "main pipeline" if use_main_cache else "isolated test"
            print(f"\n🔍 Checking {cache_source} cache...")
            
            if framework.cache_manager.is_stage_cached(cache_paper_id, '1b'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_paper_id, '1b')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 1B results from {cache_source}")
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
            framework.logger.info("Processing Stage 1B validation...")
            framework.start_tracking()
            
            print("\n🔄 Running Stage 1B: Generic Validation...")
            print("   This validates extraction quality, completeness, and consistency...")
            
            # Run validation
            results = await validator.validate(stage_1a_results, paper_data)
            
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
                    "input": (len(str(stage_1a_results)) + len(str(paper_data))) // 4,  # Rough estimate
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
                framework.cache_manager.cache_stage_result(cache_paper_id, '1b', results, paper_data)
                
        # Save output to standard pipeline location with test metadata
        output_path = framework.save_stage_output(paper_id, results, run_type="stage_test")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results)
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print("\n✅ Stage 1B output validation passed")
            
        # Display results
        framework.display_results(results, detailed=verbose)
        
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "paper_id": paper_id,
                "validation_input_stats": {
                    "stage_1a_result_size": len(str(stage_1a_results)),
                    "paper_data_size": len(str(paper_data)),
                    "has_paper_metadata": 'paper_metadata' in stage_1a_results,
                    "has_quantitative_findings": 'quantitative_findings' in stage_1a_results,
                    "stage_1a_fields": list(stage_1a_results.keys()) if isinstance(stage_1a_results, dict) else []
                },
                "validation_output_stats": {
                    "validation_quality": results.get('validation_quality', {}),
                    "issues_found": len(results.get('validation_issues', [])),
                    "recommendations_given": len(results.get('validation_recommendations', [])),
                    "overall_success": results.get('validation_success', False)
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / f"{paper_id}_1b_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "paper_id": paper_id,
            "output_path": output_path,
            "dependency_found": True,
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
        
        print(f"\n📁 Results saved to standard pipeline: {output_path}")
        print(f"    Next stages will automatically find these results")
        
        return test_result
        
    except FileNotFoundError as e:
        error_msg = f"Dependency not found: {str(e)}"
        framework.logger.error(error_msg)
        print(f"\n❌ Stage 1B test failed: {error_msg}")
        print(f"   💡 Run Stage 1A first: python test_stage_1a.py --paper \"{paper_filename}\" --api-key YOUR_KEY")
        
        # Save error information
        error_result = {
            "error": error_msg,
            "stage": "1b",
            "paper_id": paper_filename,
            "dependency_missing": "stage_1a",
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output(
            paper_filename.replace('.json', '').replace('.pdf', ''), 
            error_result,
            run_type="stage_test_error"
        )
        
        return {
            "success": False,
            "error": error_msg,
            "paper_id": paper_filename,
            "dependency_found": False
        }
        
    except Exception as e:
        framework.logger.error(f"Stage 1B test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 1B test failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "1b",
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
            "paper_id": paper_filename,
            "dependency_found": True
        }

def main():
    """Main entry point for Stage 1B testing"""
    # Initialize framework for argument parsing
    framework = StageTestFramework('1b', 'Generic Validation')
    
    # Get command line arguments
    parser = framework.get_standard_args(
        "Validate generic extraction results from Stage 1A for quality and completeness"
    )
    
    # Add stage-specific arguments if needed
    parser.add_argument("--show-prompt", action="store_true",
                      help="Display the validation prompt being sent to Gemini")
    parser.add_argument("--use-main-cache", action="store_true",
                      help="Use main pipeline cache namespace (may find existing results)")
    parser.add_argument("--show-1a-results", action="store_true",
                      help="Display the Stage 1A results being validated")
    
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
    print(f"STAGE 1B TEST: Generic Validation")
    print(f"{'='*80}")
    
    # Show cache mode
    if args.use_main_cache:
        print("🔗 Using main pipeline cache namespace (may find existing results)")
    else:
        print("🏠 Using isolated test cache namespace (fresh testing)")
        
    print("📁 Saving to standard pipeline outputs (8_stage_outputs/) for natural stage chaining")
    print("🔗 Will automatically find Stage 1A dependency results")
    
    # Run the test
    result = asyncio.run(test_stage_1b(
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
        print("✅ Stage 1B test completed successfully")
        if result.get('dependency_found'):
            print("✅ Stage 1A dependency automatically found and used")
    else:
        print("❌ Stage 1B test failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        if not result.get('dependency_found', True):
            print("   💡 Suggestion: Run Stage 1A first to generate dependency")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()