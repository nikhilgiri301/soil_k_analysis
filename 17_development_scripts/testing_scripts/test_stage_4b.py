#!/usr/bin/env python3
"""
Test Script for Stage 4B: Mapping Validation
Tests the client mapping validation stage independently with proper dependency resolution
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import stage test framework
from stage_test_utils import StageTestFramework, calculate_stage_cost, validate_paper_exists

# Import necessary components
from utils.gemini_client import GeminiClient
from utils.prompt_loader import PromptLoader
from stage_4_processors.mapping_validator import MappingValidator

async def test_stage_4b(paper_filename: str, api_key: str, disable_cache: bool = False, 
                        verbose: bool = False):
    """Test Stage 4B mapping validation on a single paper"""
    
    # Initialize test framework
    framework = StageTestFramework('4b', 'Mapping Validation')
    framework.logger.info(f"Starting Stage 4B test for paper: {paper_filename}")
    
    try:
        # Load Stage 4A dependency (must have client mapping results)
        framework.logger.info("Loading Stage 4A dependency (client mapping)...")
        dependencies = framework.load_dependency_results(
            paper_filename.replace('.pdf', '').replace('.json', ''),
            ['4a'],
            use_cache=not disable_cache
        )
        
        if 'stage_4a_results' not in dependencies:
            raise ValueError("Stage 4A results not found - Stage 4B requires Stage 4A output")
        
        stage_4a_results = dependencies['stage_4a_results']
        framework.logger.info(f"✅ Found Stage 4A results ({len(str(stage_4a_results))} chars)")
        
        # We also need the original Stage 3B results to validate against
        framework.logger.info("Loading Stage 3B dependency (validated synthesis)...")
        stage_3b_deps = framework.load_dependency_results(
            paper_filename.replace('.pdf', '').replace('.json', ''),
            ['3b'],
            use_cache=not disable_cache
        )
        
        if 'stage_3b_results' not in stage_3b_deps:
            raise ValueError("Stage 3B results not found - Stage 4B requires both 3B and 4A")
        
        stage_3b_results = stage_3b_deps['stage_3b_results']
        framework.logger.info(f"✅ Found Stage 3B results ({len(str(stage_3b_results))} chars)")
        
        # Load client architecture
        framework.logger.info("Loading client architecture...")
        client_arch_path = Path("7_client_architecture") / "question_tree.json"
        if not client_arch_path.exists():
            raise FileNotFoundError(f"Client architecture not found at {client_arch_path}")
        
        with open(client_arch_path, 'r', encoding='utf-8') as f:
            client_architecture = json.load(f)
        
        framework.logger.info(f"✅ Loaded client architecture ({len(str(client_architecture))} chars)")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        client = GeminiClient(api_key=api_key)
        prompt_loader = PromptLoader()
        validator = MappingValidator(client, prompt_loader)
        
        # Check cache
        paper_id = paper_filename.replace('.pdf', '').replace('.json', '')
        
        if not disable_cache and framework.cache_manager.is_stage_cached(f"test_{paper_id}", '4b'):
            framework.logger.info("Found cached results, loading...")
            cached_result = framework.cache_manager.get_cached_result(f"test_{paper_id}", '4b')
            if cached_result:
                results = cached_result
                print("✅ Using cached Stage 4B results from isolated test")
                # Update metrics from cache metadata
                cache_metadata = framework.cache_manager.get_cache_metadata(f"test_{paper_id}", '4b')
                if cache_metadata and 'token_usage' in cache_metadata:
                    framework.update_metrics(cache_metadata['token_usage'], cache_metadata.get('cost', 0))
        else:
            # Process Stage 4B validation
            framework.logger.info("Processing Stage 4B mapping validation...")
            print("\n🔄 Running Stage 4B: Mapping Validation...")
            print("   This validates and enhances the client mapping...")
            
            framework.start_tracking()
            
            # Run validation with thinking mode
            results = await validator.validate(
                stage_4a_results, 
                stage_3b_results,
                client_architecture
            )
            
            # Calculate and update metrics based on usage metadata
            if '_usage_metadata' in results:
                usage = results['_usage_metadata']
                token_usage = {
                    'input': usage.get('input_tokens', 0),
                    'output': usage.get('output_tokens', 0),
                    'thinking': usage.get('thinking_tokens', 0)
                }
                cost = usage.get('total_cost_usd', 0.0)
                framework.update_metrics(token_usage, cost)
                
                # Cache the results (skip for now due to API mismatch)
                # TODO: Fix cache API to accept token_usage and cost
                pass
        
        # Save output
        output_file = framework.save_stage_output(paper_id, results)
        
        # Validate output structure
        is_valid, issues = framework.validate_stage_output(results)
        if not is_valid:
            print(f"\n⚠️  Validation issues found: {issues}")
        else:
            print("\n✅ Stage 4B output validation passed")
        
        # Display results
        if not verbose:
            framework.display_results(results, detailed=False)
        else:
            framework.display_results(results, detailed=True)
        
        return results, output_file
        
    except Exception as e:
        framework.logger.error(f"Stage 4B test failed: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        return None, None

def main():
    """Main entry point for Stage 4B testing"""
    parser = StageTestFramework('4b', 'Mapping Validation').get_standard_args(
        "Validate and enhance client mapping results"
    )
    
    # Add additional Stage 4B specific arguments if needed
    parser.add_argument("--show-enhancements", action="store_true",
                        help="Show detailed enhancement information")
    
    args = parser.parse_args()
    
    # Header
    print("=" * 80)
    print("STAGE 4B TEST: Mapping Validation")
    print("=" * 80)
    print("🏠 Using isolated test cache namespace (fresh testing)")
    print("📁 Saving to standard pipeline outputs (8_stage_outputs/) for natural stage chaining")
    print("📋 Dependencies: Requires Stage 3B, 4A results + client architecture")
    
    # Validate paper exists
    if not validate_paper_exists(args.paper):
        print(f"\n❌ Error: Paper '{args.paper}' not found in synthesis_ready directory")
        available = [f.name for f in Path("3_synthesis_ready").glob("*.json")][:5]
        print(f"   Available papers: {available}")
        sys.exit(1)
    
    print(f"\n📄 Testing Paper: {args.paper}")
    print("   Stage 4B validates and enhances client mapping")
    
    # Run test
    results, output_file = asyncio.run(test_stage_4b(
        args.paper, 
        args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose
    ))
    
    if results and output_file:
        print(f"\n📁 Results saved to standard pipeline: {output_file}")
        print("   Next stages will automatically find these results")
        
        # Show enhancement summary if requested
        if args.show_enhancements and 'enhanced_mapping' in results:
            print("\n📈 Enhancement Summary:")
            enhanced = results['enhanced_mapping']
            if 'enhancement_summary' in enhanced:
                summary = enhanced['enhancement_summary']
                print(f"   Corrections Applied: {len(summary.get('corrections_applied', []))}")
                print(f"   Mappings Enhanced: {len(summary.get('mappings_enhanced', []))}")
                print(f"   Gaps Filled: {len(summary.get('gaps_filled', []))}")
                print(f"   Confidence Adjustments: {len(summary.get('confidence_adjustments', []))}")
        
        print("\n" + "=" * 80)
        print("✅ Stage 4B test completed successfully")
        print(f"   Dependencies loaded: 3B={'stage_3b_results' in results if results else False}, 4A=True, Client=True")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ Stage 4B test failed")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()