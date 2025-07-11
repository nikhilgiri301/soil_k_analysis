#!/usr/bin/env python3
"""
Stage 7B: Distillation Validation Script
Validates and enhances the scientific distillation from Stage 7A into final scientific understanding
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


class Stage7BDistillationValidator:
    """Handles Stage 7B distillation validation processing"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.gemini_client = gemini_client
        self.prompt_loader = prompt_loader
        
    async def validate_distillation(self, enhanced_integration_results: dict, stage_7a_results: dict) -> dict:
        """
        Validate and enhance the scientific distillation
        
        Args:
            enhanced_integration_results: Enhanced integration synthesis from Stage 6B
            stage_7a_results: Stage 7A scientific distillation results
            
        Returns:
            Enhanced distillation validation results
        """
        # Load prompt
        prompt_template = self.prompt_loader.load_prompt('stage_7b_distillation_validation')
        
        # Prepare data for prompt
        integration_json = json.dumps(enhanced_integration_results, indent=2, ensure_ascii=False)
        distillation_json = json.dumps(stage_7a_results, indent=2, ensure_ascii=False)
        
        # Replace template variables
        prompt = prompt_template.replace("{stage_6b_integration_results}", integration_json)
        prompt = prompt.replace("{stage_7a_distillation_results}", distillation_json)
        
        # Make AI call
        try:
            response = await self.gemini_client.generate_response(prompt)
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add stage metadata
            result['stage'] = '7b'
            result['validation_timestamp'] = datetime.now().isoformat()
            
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from Gemini: {str(e)}"
            return {"error": error_msg, "raw_response": response}
        except Exception as e:
            error_msg = f"Distillation validation failed: {str(e)}"
            return {"error": error_msg}


async def test_stage_7b(api_key: str, disable_cache: bool = False,
                       verbose: bool = False, save_debug: bool = False):
    """
    Test Stage 7B distillation validation
    
    Args:
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework('7b', 'Distillation Validation')
    framework.logger.info("Starting Stage 7B distillation validation")
    
    try:
        # Load dependency data from Stage 6B and Stage 7A
        framework.logger.info("Loading dependency data from Stage 6B and Stage 7A...")
        
        # Load Stage 6B enhanced integration results
        stage_6b_files = list(Path("8_stage_outputs").glob("stage_6b/integration_6b_*.json"))
        if not stage_6b_files:
            raise FileNotFoundError("No Stage 6B integration validation results found. Run Stage 6B first.")
            
        stage_6b_file = max(stage_6b_files, key=lambda f: f.stat().st_mtime)
        
        with open(stage_6b_file, 'r', encoding='utf-8') as f:
            stage_6b_data = json.load(f)
            
        # Extract enhanced integration synthesis
        stage_6b_results = stage_6b_data.get('results', stage_6b_data)
        enhanced_integration = None
        if 'enhanced_integration_synthesis' in stage_6b_results:
            enhanced_integration = stage_6b_results['enhanced_integration_synthesis']
        else:
            enhanced_integration = stage_6b_results
            framework.logger.warning("No enhanced integration synthesis found, using full Stage 6B results")
            
        # Load Stage 7A distillation results
        stage_7a_files = list(Path("8_stage_outputs").glob("stage_7a/distillation_7a_*.json"))
        if not stage_7a_files:
            raise FileNotFoundError("No Stage 7A distillation results found. Run Stage 7A first.")
            
        stage_7a_file = max(stage_7a_files, key=lambda f: f.stat().st_mtime)
        
        with open(stage_7a_file, 'r', encoding='utf-8') as f:
            stage_7a_data = json.load(f)
            stage_7a_results = stage_7a_data.get('results', stage_7a_data)
            
        print(f"\n📊 Distillation Validation")
        print(f"   Stage 6B integration: {stage_6b_file.name}")
        print(f"   Stage 7A distillation: {stage_7a_file.name}")
        if isinstance(enhanced_integration, dict):
            print(f"   Integration sections: {len(enhanced_integration)}")
        if isinstance(stage_7a_results, dict):
            print(f"   Distillation sections: {len(stage_7a_results)}")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create validator
        validator = Stage7BDistillationValidator(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_key = "distillation_validation"
        
        if not disable_cache:
            print(f"\n🔍 Checking cache for distillation validation...")
            
            if framework.cache_manager.is_stage_cached(cache_key, '7b'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_key, '7b')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 7B validation results")
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
            framework.logger.info("Processing Stage 7B distillation validation...")
            framework.start_tracking()
            
            print(f"\n🔄 Running Stage 7B: Distillation Validation...")
            print("   Validating and enhancing scientific distillation...")
            
            # Run validation
            results = await validator.validate_distillation(enhanced_integration, stage_7a_results)
            
            # Get token usage from Gemini client
            if hasattr(gemini_client, 'last_token_count'):
                token_usage = {
                    "input": gemini_client.last_token_count.get('input_tokens', 0),
                    "output": gemini_client.last_token_count.get('output_tokens', 0),
                    "thinking": gemini_client.last_token_count.get('thinking_tokens', 0)
                }
            else:
                # Estimate based on text lengths
                input_size = len(str(enhanced_integration)) + len(str(stage_7a_results))
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
                cache_data = {"stage_6b_results": enhanced_integration, "stage_7a_results": stage_7a_results}
                framework.cache_manager.cache_stage_result(cache_key, '7b', results, cache_data)
                
        # Save output to standard pipeline location
        output_path = framework.save_stage_output("distillation", results, run_type="distillation_validation")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='7b')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Stage 7B distillation validation output passed")
            
        # Display results
        if not results.get('error'):
            print(f"\n📊 Distillation Validation Summary:")
            
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
                
            # Check enhanced scientific distillation
            if 'enhanced_scientific_distillation' in results:
                enhanced = results['enhanced_scientific_distillation']
                if isinstance(enhanced, dict):
                    print(f"   Enhanced Distillation: {len(enhanced)} sections")
                    
                    # Distillation metadata
                    if 'enhanced_distillation_metadata' in enhanced:
                        meta = enhanced['enhanced_distillation_metadata']
                        print(f"   Enhanced evidence base: {meta.get('total_evidence_base_represented', 0)}")
                        print(f"   Enhanced confidence: {meta.get('enhanced_distillation_confidence', 0):.1%}")
                        
                    # Essential insights
                    if 'enhanced_essential_insights' in enhanced:
                        insights = enhanced['enhanced_essential_insights']
                        insight_sections = len(insights) if isinstance(insights, dict) else 0
                        print(f"   Enhanced insights: {insight_sections} categories")
                        
                    # Validated knowledge
                    if 'validated_scientific_knowledge' in enhanced:
                        knowledge = enhanced['validated_scientific_knowledge']
                        knowledge_sections = len(knowledge) if isinstance(knowledge, dict) else 0
                        print(f"   Validated knowledge: {knowledge_sections} sections")
                        
                    # Final intelligence
                    if 'final_actionable_intelligence' in enhanced:
                        final_intel = enhanced['final_actionable_intelligence']
                        intel_sections = len(final_intel) if isinstance(final_intel, dict) else 0
                        print(f"   Final intelligence: {intel_sections} sections")
                        
        else:
            print(f"\n❌ Validation Error: {results['error']}")
            
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "dependency_stats": {
                    "stage_6b_sections": len(enhanced_integration) if isinstance(enhanced_integration, dict) else 0,
                    "stage_7a_sections": len(stage_7a_results) if isinstance(stage_7a_results, dict) else 0,
                    "total_input_size": len(str(enhanced_integration)) + len(str(stage_7a_results))
                },
                "validation_stats": {
                    "result_sections": len(results) if isinstance(results, dict) else 0,
                    "has_error": 'error' in results,
                    "has_enhanced_distillation": 'enhanced_scientific_distillation' in results,
                    "output_size": len(str(results))
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / "distillation_7b_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "stage": "7b",
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
        print(f"    This is the final output of the Gold Standard Architecture")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 7B validation failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 7B validation failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "7b",
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output("distillation", error_result, run_type="distillation_validation_error")
        
        return {
            "success": False,
            "error": str(e),
            "stage": "7b"
        }


def main():
    """Main entry point for Stage 7B distillation validation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage 7B: Validate and enhance scientific distillation from Stage 7A",
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
    print(f"STAGE 7B: Distillation Validation")
    print(f"{'='*80}")
    print("Validating and enhancing scientific distillation into final understanding")
    
    # Run the validation
    result = asyncio.run(test_stage_7b(
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print("✅ Stage 7B distillation validation completed successfully")
        print("   🎯 Gold Standard Architecture pipeline complete!")
    else:
        print("❌ Stage 7B distillation validation failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()