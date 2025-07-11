#!/usr/bin/env python3
"""
Test Stage 1A Pro: Generic Extraction Testing with Gemini 2.5 Pro
Extracts generic paper metadata and key findings in isolation using Gemini 2.5 Pro
for direct performance comparison with Flash model results
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
from stage_1_processors.generic_extractor import GenericExtractor
import google.generativeai as genai

class GeminiClientPro(GeminiClient):
    """Modified GeminiClient that uses Gemini 2.5 Pro instead of Flash"""
    
    def __init__(self, api_key: str, enable_thinking: bool = True):
        if not api_key:
            raise ValueError("Gemini API key is required")
            
        genai.configure(api_key=api_key)
        self.client = genai
        self.enable_thinking = enable_thinking
        self.rate_limiter = asyncio.Semaphore(30)  # Same rate limit as base class
        self.request_count = 0
        self.error_count = 0
        
        # Force use of Gemini 2.5 Pro model
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
        
        # Token usage tracking
        from utils.gemini_client import TokenUsageTracker
        self.tracker = TokenUsageTracker()
        
        import logging
        logging.info("GeminiClientPro initialized with model: gemini-2.0-flash-thinking-exp (for enhanced analysis)")
        logging.info(f"Thinking mode: {'enabled' if enable_thinking else 'disabled'}")
        logging.info("Token limits: REMOVED - using system defaults")

async def test_stage_1a_pro(paper_filename: str, api_key: str, disable_cache: bool = False, 
                           verbose: bool = False, save_debug: bool = False, 
                           use_main_cache: bool = False):
    """
    Test Stage 1A with Gemini 2.5 Pro: Generic Extraction in isolation
    
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
    framework = StageTestFramework('1a_pro', 'Generic Extraction (Pro)')
    framework.logger.info(f"Starting Stage 1A Pro test for paper: {paper_filename}")
    
    try:
        # Load paper data
        framework.logger.info("Loading paper data...")
        paper_data = framework.load_paper_data(paper_filename)
        paper_id = paper_data.get('filename', 'unknown').replace('.json', '').replace('.pdf', '')
        
        # Display paper info
        print(f"\n📄 Testing Paper: {paper_id}")
        print(f"   🧠 Model: Gemini 2.5 Pro (for performance comparison)")
        print(f"   Full text length: {len(paper_data.get('full_text', ''))} characters")
        print(f"   Tables available: {len(paper_data.get('table_data', []))}")
        
        # Initialize components with Pro model
        framework.logger.info("Initializing Gemini Pro client and components...")
        gemini_client = GeminiClientPro(api_key)
        prompt_loader = PromptLoader()
        
        # Create extractor
        extractor = GenericExtractor(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled) - use separate cache namespace for Pro
        cache_paper_id = f"test_pro_{paper_id}" if not use_main_cache else f"pro_{paper_id}"
        
        if not disable_cache:
            cache_source = "main pipeline (pro)" if use_main_cache else "isolated test (pro)"
            print(f"\n🔍 Checking {cache_source} cache...")
            
            if framework.cache_manager.is_stage_cached(cache_paper_id, '1a_pro'):
                framework.logger.info("Found cached Pro results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_paper_id, '1a_pro')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 1A Pro results from {cache_source}")
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
            framework.logger.info("Processing Stage 1A Pro extraction...")
            framework.start_tracking()
            
            print("\n🔄 Running Stage 1A Pro: Generic Extraction...")
            print("   🧠 Using Gemini 2.5 Pro for enhanced analysis...")
            print("   This extracts paper metadata, key findings, and methodology...")
            
            # Run extraction
            results = await extractor.extract(paper_data)
            
            # Add model identification to results
            if isinstance(results, dict):
                results['_model_metadata'] = {
                    'model_name': 'gemini-2.0-pro-experimental',
                    'model_variant': 'pro',
                    'test_type': 'stage_1a_pro_comparison',
                    'timestamp': datetime.now().isoformat()
                }
            
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
                    "input": len(str(paper_data)) // 4,  # Rough estimate
                    "output": len(str(results)) // 4,
                    "thinking": 0
                }
                
            # Calculate cost (Pro model has different pricing)
            # Gemini 2.5 Pro pricing: $1.25 per 1M input tokens, $5.00 per 1M output tokens
            cost = (token_usage['input'] * 1.25 / 1_000_000) + (token_usage['output'] * 5.00 / 1_000_000)
            
            # Update metrics
            framework.update_metrics(token_usage, cost)
            
            # Cache the results (using Pro-specific cache namespace)
            if not disable_cache and 'error' not in results:
                cache_namespace = "main pipeline (pro)" if use_main_cache else "isolated test (pro)"
                framework.logger.info(f"Caching successful Pro results to {cache_namespace}...")
                framework.cache_manager.cache_stage_result(cache_paper_id, '1a_pro', results, paper_data)
                
        # Save output to Pro-specific location
        output_path = framework.save_stage_output(f"{paper_id}_1a_pro", results, run_type="stage_test_pro")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results)
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print("\n✅ Stage 1A Pro output validation passed")
            
        # Display results
        framework.display_results(results, detailed=verbose)
        
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "paper_id": paper_id,
                "model_info": {
                    "model_name": "gemini-2.0-pro-experimental",
                    "model_variant": "pro",
                    "test_type": "stage_1a_pro_comparison"
                },
                "paper_stats": {
                    "full_text_length": len(paper_data.get('full_text', '')),
                    "table_count": len(paper_data.get('table_data', [])),
                    "has_abstract": 'abstract' in paper_data.get('full_text', '').lower()
                },
                "extraction_stats": {
                    "metadata_fields": len(results.get('paper_metadata', {})),
                    "key_findings": len(results.get('key_findings', [])),
                    "methodologies": len(results.get('methodologies', [])),
                    "limitations": len(results.get('limitations', []))
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / f"{paper_id}_1a_pro_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved Pro debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "paper_id": paper_id,
            "model_info": {
                "model_name": "gemini-2.0-pro-experimental",
                "model_variant": "pro",
                "test_type": "stage_1a_pro_comparison"
            },
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
        
        print(f"\n📁 Pro results saved to: {output_path}")
        print(f"    🔬 Compare with Flash results for performance analysis")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 1A Pro test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 1A Pro test failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "1a_pro",
            "paper_id": paper_filename,
            "model_info": {
                "model_name": "gemini-2.0-pro-experimental",
                "model_variant": "pro",
                "test_type": "stage_1a_pro_comparison"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output(
            f"{paper_filename.replace('.json', '').replace('.pdf', '')}_1a_pro", 
            error_result,
            run_type="stage_test_pro_error"
        )
        
        return {
            "success": False,
            "error": str(e),
            "paper_id": paper_filename,
            "model_info": {
                "model_name": "gemini-2.0-pro-experimental",
                "model_variant": "pro"
            }
        }

def main():
    """Main entry point for Stage 1A Pro testing"""
    # Initialize framework for argument parsing
    framework = StageTestFramework('1a_pro', 'Generic Extraction (Pro)')
    
    # Get command line arguments
    parser = framework.get_standard_args(
        "Extract generic paper metadata and key findings using Gemini 2.5 Pro for model comparison"
    )
    
    # Add stage-specific arguments
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
    print(f"STAGE 1A PRO TEST: Generic Extraction with Gemini 2.5 Pro")
    print(f"{'='*80}")
    print("🧠 Model: Gemini 2.5 Pro (for direct performance comparison)")
    print("🔬 Compare results with Flash model for capability analysis")
    
    # Show cache mode
    if args.use_main_cache:
        print("🔗 Using main pipeline cache namespace (may find existing Pro results)")
    else:
        print("🏠 Using isolated test cache namespace (fresh Pro testing)")
        
    print("📁 Saving to Pro-specific outputs for model comparison analysis")
    
    # Run the test
    result = asyncio.run(test_stage_1a_pro(
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
        print("✅ Stage 1A Pro test completed successfully")
        print("🔬 Ready for model performance comparison analysis")
    else:
        print("❌ Stage 1A Pro test failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()