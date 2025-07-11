#!/usr/bin/env python3
"""
Stage 7A: Scientific Distillation Script
Distills enhanced integrated systems synthesis into essential scientific understanding
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


class Stage7AScientificDistiller:
    """Handles Stage 7A scientific distillation processing"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.gemini_client = gemini_client
        self.prompt_loader = prompt_loader
        
    async def distill_scientific_knowledge(self, enhanced_integration_results: dict) -> dict:
        """
        Distill enhanced integrated synthesis into essential scientific understanding
        
        Args:
            enhanced_integration_results: Enhanced integration synthesis from Stage 6B
            
        Returns:
            Scientific distillation results
        """
        # Load prompt
        prompt_template = self.prompt_loader.load_prompt('stage_7a_scientific_distillation')
        
        # Prepare data for prompt
        integration_json = json.dumps(enhanced_integration_results, indent=2, ensure_ascii=False)
        
        # Replace template variable
        prompt = prompt_template.replace("{stage_6b_integration_results}", integration_json)
        
        # Make AI call
        try:
            response = await self.gemini_client.generate_response(prompt)
            
            # Parse JSON response
            result = json.loads(response)
            
            # Add stage metadata
            result['stage'] = '7a'
            result['distillation_timestamp'] = datetime.now().isoformat()
            
            return result
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from Gemini: {str(e)}"
            return {"error": error_msg, "raw_response": response}
        except Exception as e:
            error_msg = f"Scientific distillation failed: {str(e)}"
            return {"error": error_msg}


async def test_stage_7a(api_key: str, disable_cache: bool = False,
                       verbose: bool = False, save_debug: bool = False):
    """
    Test Stage 7A scientific distillation
    
    Args:
        api_key: Gemini API key
        disable_cache: Whether to bypass cache
        verbose: Show detailed output
        save_debug: Save debug information
        
    Returns:
        Test results dictionary
    """
    # Initialize test framework
    framework = StageTestFramework('7a', 'Scientific Distillation')
    framework.logger.info("Starting Stage 7A scientific distillation")
    
    try:
        # Load dependency data from Stage 6B
        framework.logger.info("Loading enhanced integration synthesis from Stage 6B...")
        
        # Look for Stage 6B enhanced integration results
        stage_6b_files = list(Path("8_stage_outputs").glob("stage_6b/integration_6b_*.json"))
        if not stage_6b_files:
            raise FileNotFoundError("No Stage 6B integration validation results found. Run Stage 6B first.")
            
        stage_6b_file = max(stage_6b_files, key=lambda f: f.stat().st_mtime)
        
        with open(stage_6b_file, 'r', encoding='utf-8') as f:
            stage_6b_data = json.load(f)
            
        # Extract enhanced integration synthesis
        stage_6b_results = stage_6b_data.get('results', stage_6b_data)
        
        # Look for enhanced integration synthesis section
        enhanced_integration = None
        if 'enhanced_integration_synthesis' in stage_6b_results:
            enhanced_integration = stage_6b_results['enhanced_integration_synthesis']
        else:
            # Fallback to full results if no enhanced section found
            enhanced_integration = stage_6b_results
            framework.logger.warning("No enhanced integration synthesis found, using full Stage 6B results")
            
        print(f"\n📊 Scientific Distillation")
        print(f"   Source: {stage_6b_file.name}")
        if isinstance(enhanced_integration, dict):
            print(f"   Integration sections: {len(enhanced_integration)}")
            if 'integration_synthesis_metadata' in enhanced_integration:
                meta = enhanced_integration['integration_synthesis_metadata']
                if 'total_evidence_pieces_represented' in meta:
                    print(f"   Evidence pieces: {meta['total_evidence_pieces_represented']}")
                if 'papers_represented' in meta:
                    print(f"   Papers: {meta['papers_represented']}")
        
        # Initialize components
        framework.logger.info("Initializing Gemini client and components...")
        gemini_client = GeminiClient(api_key)
        prompt_loader = PromptLoader()
        
        # Create distiller
        distiller = Stage7AScientificDistiller(gemini_client, prompt_loader)
        
        # Check cache first (unless disabled)
        cache_key = "scientific_distillation"
        
        if not disable_cache:
            print(f"\n🔍 Checking cache for scientific distillation...")
            
            if framework.cache_manager.is_stage_cached(cache_key, '7a'):
                framework.logger.info("Found cached results, loading...")
                cached_result = framework.cache_manager.get_cached_result(cache_key, '7a')
                if cached_result and 'error' not in cached_result:
                    print(f"✅ Using cached Stage 7A distillation results")
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
            framework.logger.info("Processing Stage 7A scientific distillation...")
            framework.start_tracking()
            
            print(f"\n🔄 Running Stage 7A: Scientific Distillation...")
            print("   Distilling essential scientific insights from integrated synthesis...")
            
            # Run distillation
            results = await distiller.distill_scientific_knowledge(enhanced_integration)
            
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
                    "input": len(str(enhanced_integration)) // 4,  # Rough estimate
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
                framework.cache_manager.cache_stage_result(cache_key, '7a', results, enhanced_integration)
                
        # Save output to standard pipeline location
        output_path = framework.save_stage_output("distillation", results, run_type="scientific_distillation")
        
        # Validate results
        is_valid, validation_issues = framework.validate_stage_output(results, expected_stage='7a')
        
        if not is_valid:
            framework.logger.warning(f"Validation issues found: {validation_issues}")
            print(f"\n⚠️  Validation Issues: {len(validation_issues)}")
            for issue in validation_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Stage 7A distillation output validation passed")
            
        # Display results
        if not results.get('error'):
            print(f"\n📊 Scientific Distillation Summary:")
            
            # Distillation metadata
            if 'scientific_distillation_metadata' in results:
                meta = results['scientific_distillation_metadata']
                print(f"   Distillation scope: {meta.get('distillation_scope', 'Unknown')}")
                if 'total_evidence_base_represented' in meta:
                    print(f"   Evidence base: {meta['total_evidence_base_represented']}")
                if 'papers_represented' in meta:
                    print(f"   Papers: {meta['papers_represented']}")
                print(f"   Distillation confidence: {meta.get('distillation_confidence', 0):.1%}")
                
            # Essential insights
            if 'essential_scientific_insights' in results:
                insights = results['essential_scientific_insights']
                insight_sections = 0
                total_items = 0
                
                for section_name, section_data in insights.items():
                    if isinstance(section_data, list):
                        insight_sections += 1
                        total_items += len(section_data)
                        
                print(f"   Essential insights: {total_items} items across {insight_sections} categories")
                
            # Distilled knowledge
            if 'distilled_scientific_knowledge' in results:
                knowledge = results['distilled_scientific_knowledge']
                knowledge_sections = len(knowledge) if isinstance(knowledge, dict) else 0
                print(f"   Knowledge sections: {knowledge_sections}")
                
            # Research priorities
            if 'scientific_priority_distillation' in results:
                priorities = results['scientific_priority_distillation']
                if 'research_priority_synthesis' in priorities:
                    research_priorities = priorities['research_priority_synthesis']
                    priority_count = len(research_priorities) if isinstance(research_priorities, list) else 0
                    print(f"   Research priorities: {priority_count}")
                    
            # Actionable intelligence
            if 'actionable_scientific_intelligence' in results:
                actionable = results['actionable_scientific_intelligence']
                actionable_sections = len(actionable) if isinstance(actionable, dict) else 0
                print(f"   Actionable intelligence: {actionable_sections} sections")
                
        else:
            print(f"\n❌ Distillation Error: {results['error']}")
            
        # Save debug information if requested
        if save_debug:
            debug_info = {
                "dependency_stats": {
                    "stage_6b_sections": len(enhanced_integration) if isinstance(enhanced_integration, dict) else 0,
                    "input_size": len(str(enhanced_integration))
                },
                "distillation_stats": {
                    "result_sections": len(results) if isinstance(results, dict) else 0,
                    "has_error": 'error' in results,
                    "output_size": len(str(results))
                },
                "validation": {
                    "is_valid": is_valid,
                    "issues": validation_issues
                }
            }
            
            debug_path = framework.stage_output_dir / "distillation_7a_debug.json"
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
            framework.logger.info(f"Saved debug information to: {debug_path}")
            
        # Generate test summary
        test_result = {
            "success": is_valid and 'error' not in results,
            "stage": "7a",
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
        print(f"    Stage 7B will automatically find these results")
        
        return test_result
        
    except Exception as e:
        framework.logger.error(f"Stage 7A distillation failed: {str(e)}", exc_info=True)
        print(f"\n❌ Stage 7A distillation failed: {str(e)}")
        
        # Save error information
        error_result = {
            "error": str(e),
            "stage": "7a",
            "timestamp": datetime.now().isoformat()
        }
        
        framework.save_stage_output("distillation", error_result, run_type="scientific_distillation_error")
        
        return {
            "success": False,
            "error": str(e),
            "stage": "7a"
        }


def main():
    """Main entry point for Stage 7A scientific distillation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stage 7A: Distill enhanced integrated synthesis into essential scientific understanding",
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
    print(f"STAGE 7A: Scientific Distillation")
    print(f"{'='*80}")
    print("Distilling essential scientific insights from integrated systems synthesis")
    
    # Run the distillation
    result = asyncio.run(test_stage_7a(
        api_key=args.api_key,
        disable_cache=args.disable_cache,
        verbose=args.verbose,
        save_debug=args.save_debug
    ))
    
    # Print final summary
    print(f"\n{'='*80}")
    if result['success']:
        print("✅ Stage 7A scientific distillation completed successfully")
    else:
        print("❌ Stage 7A scientific distillation failed")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()