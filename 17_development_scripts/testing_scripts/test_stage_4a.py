#!/usr/bin/env python3
"""
Test Stage 4A: Client Mapping Testing
Maps validated synthesis results to client question architecture
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
from stage_4_processors.client_mapper import ClientMapper

async def test_stage_4a(paper_filename: str, api_key: str, disable_cache: bool = False, 
                       verbose: bool = False, save_debug: bool = False, 
                       use_main_cache: bool = False):
    """
    Test Stage 4A: Client Mapping in isolation
    
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
    framework = StageTestFramework('4a', 'Client Mapping')
    framework.logger.info(f"Starting Stage 4A test for paper: {paper_filename}")
    
    try:
        # Get paper ID
        paper_id = paper_filename.replace('.json', '').replace('.pdf', '')
        
        # Display paper info
        print(f"\n📄 Testing Paper: {paper_id}")
        print("   Stage 4A maps synthesis results to client question architecture")
        
        # Load Stage 3B dependency (validated synthesis only)
        framework.logger.info("Loading Stage 3B dependency (validated synthesis)...")
        stage_3b_results = load_stage_3b_dependency(
            paper_id, framework, use_main_cache
        )
        
        # Check for missing Stage 3B - fail if not available
        if not stage_3b_results:
            raise ValueError(
                f"Failed to fetch Stage 3B input - Stage 3B results not found. "
                f"Only validated synthesis (Stage 3B) is accepted for client mapping.\n"
                f"Please run Stage 3B first:\n"
                f"  python test_stage_3b.py --paper {paper_filename} --api-key YOUR_KEY"
            )
        
        print(f"   ✅ Found Stage 3B results ({len(str(stage_3b_results))} chars)")
        
        # Load client architecture
        framework.logger.info("Loading client architecture...")
        client_architecture = load_client_architecture()
        print(f"   ✅ Loaded client architecture ({len(str(client_architecture))} chars)")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create mapper
        mapper = ClientMapper(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_paper_id = f"test_{paper_id}" if not use_main_cache else paper_id
        
        if not disable_cache:
            cache_source = "main pipeline" if use_main_cache else "isolated test"
            print(f"\n🔍 Checking {cache_source} cache...")
            
            if framework.cache_manager.is_stage_cached(cache_paper_id, '4a'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_paper_id, '4a')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 4A results from {cache_source}")
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
            framework.logger.info("Processing Stage 4A client mapping...")
            framework.start_tracking()
            
            print("\n🔄 Running Stage 4A: Client Mapping...")
            print("   This maps synthesis results to client question architecture...")
            
            # Use enhanced synthesis from 3B (validated synthesis only)
            synthesis_input = stage_3b_results.get('enhanced_synthesis', stage_3b_results)
            
            # Run client mapping
            results = await mapper.map_to_client(synthesis_input, client_architecture)
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                input_size = len(str(synthesis_input)) + len(str(client_architecture))
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
                framework.cache_manager.cache_stage_result(cache_paper_id, '4a', results, {})
                
        # Save output to standard pipeline location with test metadata
        output_path = framework.save_stage_output(paper_id, results, run_type="stage_test")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='4a')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print("\n✅ Stage 4A output validation passed")
            
        # Display results
        framework.display_results(results, detailed=verbose)
        
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "paper_id": paper_id,
                "input_stats": {
                    "stage_3b_size": len(str(stage_3b_results)),
                    "client_architecture_size": len(str(client_architecture)),
                    "synthesis_input_used": "enhanced_synthesis" if stage_3b_results.get('enhanced_synthesis') else "stage_3b_results"
                },
                "mapping_stats": {
                    "client_questions_mapped": count_client_questions_mapped(results),
                    "parameter_mappings": count_parameter_mappings(results),
                    "mapping_success": results.get('success', False)
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                },
                "dependencies": {
                    "stage_3b_found": stage_3b_results is not None,
                    "client_architecture_loaded": client_architecture is not None
                }
            }
            
            debug_path = framework.stage_output_dir / f"{paper_id}_4a_debug.json"
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
                "stage_3b_loaded": stage_3b_results is not None,
                "client_architecture_loaded": client_architecture is not None
            }
        }
        
        print(f"\n📁 Results saved to standard pipeline: {output_path}")
        print(f"    Next stages will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 4A test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 4A test failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "4a",
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

def load_stage_3b_dependency(paper_id: str, framework: StageTestFramework, use_main_cache: bool):
    """
    Load Stage 3B results for client mapping (validated synthesis only)
    
    Args:
        paper_id: Paper identifier
        framework: Test framework instance
        use_main_cache: Whether to use main pipeline cache
        
    Returns:
        Stage 3B results or None if not found
    """
    cache_paper_id = f"test_{paper_id}" if not use_main_cache else paper_id
    
    stage_3b_results = None
    
    # Try to load from cache first
    print("\n🔍 Looking for Stage 3B dependency (validated synthesis only)...")
    
    # Load Stage 3B from cache
    if framework.cache_manager.is_stage_cached(cache_paper_id, '3b'):
        stage_3b_results = framework.cache_manager.get_cached_result(cache_paper_id, '3b')
        if stage_3b_results and 'error' not in stage_3b_results:
            print("   ✅ Found Stage 3B in cache")
        else:
            stage_3b_results = None
    
    # Fall back to stage outputs if not found in cache
    if not stage_3b_results:
        stage_3b_path = Path("8_stage_outputs") / f"{paper_id}_3b.json"
        if stage_3b_path.exists():
            with open(stage_3b_path, 'r', encoding='utf-8') as f:
                stage_3b_results = json.load(f)
            print("   ✅ Found Stage 3B in pipeline outputs")
        else:
            print("   ❌ Stage 3B not found")
    
    return stage_3b_results

def load_client_architecture():
    """Load client question architecture from configuration files"""
    
    try:
        # Load client architecture files
        client_arch_dir = Path("7_client_architecture")
        
        with open(client_arch_dir / "question_tree.json", 'r') as f:
            question_tree = json.load(f)
        
        with open(client_arch_dir / "parameter_definitions.json", 'r') as f:
            parameters = json.load(f)
            
        # Try to load confidence thresholds (may not exist)
        confidence_thresholds = {}
        confidence_file = client_arch_dir / "confidence_thresholds.json"
        if confidence_file.exists():
            with open(confidence_file, 'r') as f:
                confidence_thresholds = json.load(f)
        
        return {
            "question_tree": question_tree,
            "parameters": parameters,
            "thresholds": confidence_thresholds
        }
        
    except Exception as e:
        print(f"⚠️  Warning: Could not load client architecture: {str(e)}")
        return {
            "question_tree": {},
            "parameters": {},
            "thresholds": {}
        }

def count_client_questions_mapped(results: dict) -> int:
    """Count the number of client questions mapped in results"""
    if not isinstance(results, dict):
        return 0
        
    # Look for client question mappings in various result structures
    mapping_keys = [
        'client_mappings', 'question_mappings', 'mapped_questions',
        'client_questions', 'question_responses'
    ]
    
    total_questions = 0
    for key in mapping_keys:
        if key in results and isinstance(results[key], (dict, list)):
            if isinstance(results[key], dict):
                total_questions += len(results[key])
            else:
                total_questions += len(results[key])
    
    return total_questions

def count_parameter_mappings(results: dict) -> int:
    """Count the number of parameter mappings in results"""
    if not isinstance(results, dict):
        return 0
        
    # Look for parameter mappings in various result structures
    param_keys = [
        'parameter_mappings', 'mapped_parameters', 'parameter_responses',
        'client_parameters', 'parameter_values'
    ]
    
    total_parameters = 0
    for key in param_keys:
        if key in results and isinstance(results[key], (dict, list)):
            if isinstance(results[key], dict):
                total_parameters += len(results[key])
            else:
                total_parameters += len(results[key])
    
    return total_parameters

def main():
    """Main entry point for Stage 4A testing"""
    # Initialize framework for argument parsing
    framework = StageTestFramework('4a', 'Client Mapping')
    
    # Get command line arguments
    parser = framework.get_standard_args(
        "Map synthesis results to client question architecture"
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
    print(f"STAGE 4A TEST: Client Mapping")
    print(f"{'='*80}")
    
    # Show cache mode
    if args.use_main_cache:
        print("🔗 Using main pipeline cache namespace (may find existing results)")
    else:
        print("🏠 Using isolated test cache namespace (fresh testing)")
        
    print("📁 Saving to standard pipeline outputs (8_stage_outputs/) for natural stage chaining")
    print("📋 Dependencies: Requires Stage 3B results (validated synthesis only) + client architecture")
    
    # Run the test
    result = asyncio.run(test_stage_4a(
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
        print("✅ Stage 4A test completed successfully")
        if 'dependencies' in result:
            deps = result['dependencies']
            print(f"   Dependencies loaded: 3B={deps['stage_3b_loaded']}, Client={deps['client_architecture_loaded']}")
    else:
        print("❌ Stage 4A test failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()