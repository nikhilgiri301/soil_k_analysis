#!/usr/bin/env python3
"""
Soil K Literature Synthesis Engine - Main Execution Script
Track 1, Bucket 4, Phase 2: 5-Stage, 10-Pass AI Synthesis System

Usage:
    python run_synthesis.py --api-key YOUR_GEMINI_API_KEY
    python run_synthesis.py --api-key YOUR_API_KEY --resume-from checkpoint_id
    python run_synthesis.py --config custom_config.json --api-key YOUR_API_KEY
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import synthesis engine components
from master_controller import SoilKAnalysisEngine
from utils.json_config import load_config, setup_logging
from validation_framework.quality_controller import QualityController
from validation_framework.confidence_scorer import ConfidenceScorer

class SynthesisRunner:
    """Main runner for soil K literature synthesis"""
    
    def __init__(self, api_key: str, config_path: str = None, resume_checkpoint: str = None, max_papers: int = None, enable_cache: bool = True):
        self.api_key = api_key
        self.config_path = config_path or "6_synthesis_engine/config.json"
        self.resume_checkpoint = resume_checkpoint
        self.max_papers = max_papers
        self.enable_cache = enable_cache
        
        # Load configuration
        self.config = load_config(self.config_path)
        
        # Setup logging with UTF-8 encoding
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        setup_logging(self.config)
        
        # Initialize components
        self.engine = None
        self.quality_controller = QualityController()
        self.confidence_scorer = ConfidenceScorer()
        
        logging.info("Synthesis Runner initialized")
    
    def validate_environment(self) -> bool:
        """Validate that environment is ready for synthesis"""
        
        validation_results = []
        
        # Check API key
        if not self.api_key:
            validation_results.append("❌ Gemini API key not provided")
        else:
            validation_results.append("✅ API key provided")
        
        # Check required directories
        required_dirs = [
            "3_synthesis_ready",
            "6_synthesis_engine",
            "7_client_architecture",
            "8_stage_outputs"
        ]
        
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                validation_results.append(f"✅ Directory exists: {dir_path}")
            else:
                validation_results.append(f"❌ Missing directory: {dir_path}")
                return False
        
        # Check for synthesis-ready data
        dataset_path = "3_synthesis_ready/complete_dataset.json"
        if os.path.exists(dataset_path):
            validation_results.append("✅ Phase 1 data available")
            
            # Load and validate dataset
            try:
                with open(dataset_path, 'r') as f:
                    dataset = json.load(f)
                
                paper_count = len(dataset.get('papers', []))
                validation_results.append(f"✅ Found {paper_count} papers ready for synthesis")
                
                if paper_count < 5:
                    validation_results.append("⚠️  Low paper count - results may have limited confidence")
                
            except Exception as e:
                validation_results.append(f"❌ Error reading dataset: {str(e)}")
                return False
        else:
            validation_results.append("❌ Phase 1 data not found - run PDF processing first")
            return False
        
        # Check client architecture files
        client_files = [
            "7_client_architecture/question_tree.json",
            "7_client_architecture/parameter_definitions.json",
            "7_client_architecture/confidence_thresholds.json"
        ]
        
        for file_path in client_files:
            if os.path.exists(file_path):
                validation_results.append(f"✅ Client file exists: {os.path.basename(file_path)}")
            else:
                validation_results.append(f"❌ Missing client file: {file_path}")
                return False
        
        # Print validation results
        print("\\n🔍 Environment Validation:")
        for result in validation_results:
            print(f"  {result}")
        
        return all("❌" not in result for result in validation_results)
    
    async def run_synthesis(self) -> dict:
        """Execute the complete 5-stage, 10-pass synthesis"""
        
        start_time = datetime.now()
        
        try:
            print("\\n🚀 Starting Soil K Literature Synthesis")
            print(f"📅 Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Initialize synthesis engine
            if self.max_papers:
                print(f"\\n🔧 Initializing synthesis engine (limiting to {self.max_papers} papers)...")
            else:
                print("\\n🔧 Initializing synthesis engine...")
            self.engine = SoilKAnalysisEngine(
                api_key=self.api_key,
                resume_from_checkpoint=self.resume_checkpoint,
                max_papers=self.max_papers,
                enable_cache=self.enable_cache
            )
            
            # Run synthesis
            print("\\n📊 Executing 10-pass synthesis...")
            synthesis_result = await self.engine.process_all_papers()
            
            # Validate results
            print("\\n✅ Validating synthesis results...")
            validation_result = self.quality_controller.validate_stage_output(
                "final_synthesis", synthesis_result
            )
            
            # Calculate final confidence
            print("\\n📈 Calculating confidence scores...")
            confidence_result = self.confidence_scorer.score_synthesis_confidence(
                synthesis_result, 
                synthesis_result.get('paper_confidences', [])
            )
            
            # Generate final deliverable
            final_deliverable = self._prepare_final_deliverable(
                synthesis_result, validation_result, confidence_result
            )
            
            # Save results
            await self._save_results(final_deliverable)
            
            # Print summary
            self._print_completion_summary(final_deliverable, start_time)
            
            return final_deliverable
            
        except Exception as e:
            error_msg = f"Synthesis failed: {str(e)}"
            logging.error(error_msg)
            print(f"\\n❌ {error_msg}")
            raise
    
    def _prepare_final_deliverable(self, synthesis_result: dict, 
                                 validation_result: dict,
                                 confidence_result: dict) -> dict:
        """Prepare final client deliverable"""
        
        return {
            "deliverable_metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "synthesis_engine_version": "2.0.0",
                "track_1_bucket_4_phase_2": True,
                "processing_approach": "5_stage_10_pass_ai_synthesis"
            },
            "executive_summary": {
                "total_papers_processed": synthesis_result.get('total_papers', 0),
                "parameters_analyzed": len(synthesis_result.get('parameter_analysis', {})),
                "overall_confidence": confidence_result.get('overall_confidence', 0.0),
                "evidence_quality": confidence_result.get('evidence_quality_summary', {}),
                "key_findings_count": len(synthesis_result.get('key_findings', []))
            },
            "client_question_responses": synthesis_result.get('client_question_responses', {}),
            "parameter_confidence_analysis": confidence_result.get('parameter_confidences', {}),
            "evidence_base_summary": {
                "regional_coverage": confidence_result.get('regional_coverage', {}),
                "temporal_coverage": synthesis_result.get('temporal_analysis', {}),
                "methodological_diversity": synthesis_result.get('methodology_analysis', {})
            },
            "uncertainty_analysis": {
                "confidence_calibration": confidence_result.get('overall_confidence', 0.0),
                "evidence_gaps": synthesis_result.get('evidence_gaps', []),
                "limitations": confidence_result.get('synthesis_limitations', []),
                "recommendation_confidence_levels": synthesis_result.get('recommendation_confidence', {})
            },
            "business_implications": {
                "critical_parameters_status": self._assess_critical_parameters(synthesis_result),
                "decision_support_readiness": validation_result.get('quality_score', 0.0),
                "risk_considerations": synthesis_result.get('risk_analysis', []),
                "next_steps_recommendations": synthesis_result.get('recommendations', [])
            },
            "technical_validation": {
                "quality_assessment": validation_result,
                "confidence_assessment": confidence_result,
                "audit_trail": synthesis_result.get('audit_trail', {}),
                "citation_traceability": synthesis_result.get('citations', {})
            },
            "appendices": {
                "detailed_parameter_analysis": synthesis_result.get('detailed_analysis', {}),
                "paper_by_paper_summary": synthesis_result.get('paper_summaries', []),
                "methodology_documentation": synthesis_result.get('methodology', {}),
                "validation_logs": validation_result
            }
        }
    
    async def _save_results(self, deliverable: dict):
        """Save synthesis results to multiple formats"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        os.makedirs("9_final_synthesis", exist_ok=True)
        
        # Save comprehensive deliverable
        deliverable_path = f"9_final_synthesis/soil_k_synthesis_deliverable_{timestamp}.json"
        with open(deliverable_path, 'w') as f:
            json.dump(deliverable, f, indent=2)
        
        # Save executive summary
        executive_summary = {
            "executive_summary": deliverable["executive_summary"],
            "key_findings": deliverable["client_question_responses"],
            "confidence_assessment": deliverable["uncertainty_analysis"],
            "business_implications": deliverable["business_implications"]
        }
        
        summary_path = f"9_final_synthesis/executive_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(executive_summary, f, indent=2)
        
        # Save client-ready report (simplified format)
        client_report = self._generate_client_report(deliverable)
        report_path = f"9_final_synthesis/client_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(client_report, f, indent=2)
        
        print(f"\\n💾 Results saved:")
        print(f"  📋 Full deliverable: {deliverable_path}")
        print(f"  📊 Executive summary: {summary_path}")
        print(f"  📄 Client report: {report_path}")
    
    def _generate_client_report(self, deliverable: dict) -> dict:
        """Generate simplified client-facing report"""
        
        return {
            "soil_k_intelligence_summary": {
                "analysis_scope": f"{deliverable['executive_summary']['total_papers_processed']} research papers",
                "confidence_level": f"{deliverable['executive_summary']['overall_confidence']:.1%}",
                "evidence_quality": "Systematic literature synthesis with conservative confidence calibration"
            },
            "key_parameter_findings": deliverable.get("client_question_responses", {}),
            "regional_insights": deliverable["evidence_base_summary"]["regional_coverage"],
            "uncertainty_assessment": {
                "confidence_explanation": "Conservative calibration prioritizing business decision safety",
                "evidence_limitations": deliverable["uncertainty_analysis"]["limitations"],
                "recommendation_reliability": deliverable["uncertainty_analysis"]["recommendation_confidence_levels"]
            },
            "business_recommendations": deliverable["business_implications"],
            "methodology_note": "5-stage AI synthesis with human validation checkpoints"
        }
    
    def _assess_critical_parameters(self, synthesis_result: dict) -> dict:
        """Assess status of critical business parameters"""
        
        critical_params = ["annual_kg_k2o_per_ha", "sustainability_years", "depletion_rate"]
        status = {}
        
        param_analysis = synthesis_result.get('parameter_analysis', {})
        
        for param in critical_params:
            if param in param_analysis:
                confidence = param_analysis[param].get('confidence', 0.0)
                if confidence >= 0.7:
                    status[param] = "high_confidence"
                elif confidence >= 0.5:
                    status[param] = "medium_confidence"
                elif confidence >= 0.3:
                    status[param] = "low_confidence"
                else:
                    status[param] = "insufficient_evidence"
            else:
                status[param] = "not_analyzed"
        
        return status
    
    def _print_completion_summary(self, deliverable: dict, start_time: datetime):
        """Print completion summary"""
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\\n🎉 Synthesis Complete!")
        print(f"⏱️  Total time: {duration}")
        print(f"📄 Papers processed: {deliverable['executive_summary']['total_papers_processed']}")
        print(f"📊 Parameters analyzed: {deliverable['executive_summary']['parameters_analyzed']}")
        print(f"🎯 Overall confidence: {deliverable['executive_summary']['overall_confidence']:.1%}")
        print(f"🏆 Quality score: {deliverable['technical_validation']['quality_assessment'].get('quality_score', 0):.1%}")
        
        # Show critical parameter status
        critical_status = deliverable["business_implications"]["critical_parameters_status"]
        print("\\n📈 Critical Parameters Status:")
        for param, status in critical_status.items():
            emoji = {"high_confidence": "🟢", "medium_confidence": "🟡", "low_confidence": "🟠", "insufficient_evidence": "🔴", "not_analyzed": "⚪"}.get(status, "❓")
            print(f"  {emoji} {param}: {status}")
        
        print("\\n✅ Synthesis deliverable ready for client review")

async def handle_audit_commands(args):
    """Handle audit and inspection commands"""
    
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))
    from utils.stage_cache_manager import StageCacheManager
    
    cache_manager = StageCacheManager()
    
    if args.cache_stats:
        print("\\n📊 Cache Statistics:")
        stats = cache_manager.get_cache_statistics()
        
        overview = stats["cache_overview"]
        print(f"  📄 Total papers: {overview['total_papers']}")
        print(f"  🎯 Total cached stages: {overview['total_cached_stages']}")
        print(f"  ✅ Cache hits: {overview['cache_hits']}")
        print(f"  ❌ Cache misses: {overview['cache_misses']}")
        print(f"  📈 Hit rate: {overview['hit_rate']:.1f}%")
        print(f"  💰 Cost saved: ${overview['cost_saved_usd']}")
        
        cache_size = stats["cache_size"]
        print(f"  💾 Cache size: {cache_size['total_mb']} MB ({cache_size['file_count']} files)")
        
        if overview['total_papers'] > 0:
            print("\\n📋 Stage Distribution:")
            for stage, count in stats["stage_distribution"].items():
                print(f"    Stage {stage}: {count} papers")
    
    elif args.stage_summary:
        print("\\n📋 Paper Completion Summary:")
        summary = cache_manager.get_all_papers_summary()
        
        print(f"  📄 Total papers: {summary['total_papers']}")
        progress = summary["overall_progress"]
        print(f"  🎯 Overall progress: {progress['stages_completed']}/{progress['total_possible_stages']} ({progress['completion_percentage']:.1f}%)")
        
        if summary['papers']:
            print("\\n📄 Individual Papers:")
            for paper_id, info in summary['papers'].items():
                status_emoji = "🟢" if info['percentage'] == 100 else "🟡" if info['percentage'] > 0 else "⚪"
                error_emoji = " ⚠️" if info['has_errors'] else ""
                next_stage = f" → {info['next_stage']}" if info['next_stage'] else " ✅"
                print(f"    {status_emoji} {paper_id[:50]}... ({info['completed']}/{info['total']} - {info['percentage']:.0f}%){next_stage}{error_emoji}")
    
    elif args.inspect_stage:
        stage_id = args.inspect_stage.lower()
        print(f"\\n🔍 Inspecting Stage {stage_id.upper()} Results:")
        
        found_any = False
        for paper_id in cache_manager.cache_index["papers"]:
            if cache_manager.is_stage_cached(paper_id, stage_id):
                result = cache_manager.get_cached_result(paper_id, stage_id)
                if result:
                    found_any = True
                    print(f"\\n📄 {paper_id}:")
                    
                    # Show key information depending on stage type
                    if "paper_metadata" in result:
                        print(f"  ✅ Title: {result['paper_metadata'].get('title', 'N/A')}")
                        print(f"  📅 Year: {result['paper_metadata'].get('publication_year', 'N/A')}")
                    
                    if "error" in result:
                        print(f"  ❌ Error: {result['error']}")
                    
                    # Show result size
                    result_size = len(str(result))
                    print(f"  📊 Result size: {result_size:,} characters")
        
        if not found_any:
            print(f"  ⚪ No cached results found for stage {stage_id.upper()}")
    
    elif args.clear_cache:
        stage_id, paper_id = args.clear_cache
        if stage_id.lower() == "all":
            success = cache_manager.clear_paper_cache(paper_id)
            if success:
                print(f"✅ Cleared all cache for paper: {paper_id}")
            else:
                print(f"❌ Failed to clear cache for paper: {paper_id}")
        else:
            success = cache_manager.clear_stage_cache(paper_id, stage_id.lower())
            if success:
                print(f"✅ Cleared cache for {paper_id} stage {stage_id.upper()}")
            else:
                print(f"❌ Failed to clear cache for {paper_id} stage {stage_id.upper()}")

async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Soil K Literature Synthesis Engine")
    parser.add_argument("--api-key", help="Gemini API key")
    parser.add_argument("--config", help="Custom config file path")
    parser.add_argument("--resume-from", help="Resume from checkpoint ID")
    parser.add_argument("--validate-only", action="store_true", help="Only validate environment")
    parser.add_argument("--limit", type=int, help="Process only the first N papers (useful for testing)")
    
    # Checkpoint/Resume commands (Phase 2B)
    parser.add_argument("--resume", action="store_true", help="Resume from last successful stage")
    parser.add_argument("--from-stage", help="Resume from specific stage (e.g., 3A)")
    parser.add_argument("--force-recache", action="store_true", help="Force recache (ignore existing cache)")
    parser.add_argument("--disable-cache", action="store_true", help="Disable stage-level caching")
    
    # Audit and inspection commands
    parser.add_argument("--inspect-stage", help="Inspect cached stage results (e.g., 1A)")
    parser.add_argument("--stage-summary", action="store_true", help="Show completion status across papers")
    parser.add_argument("--cache-stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--clear-cache", nargs=2, metavar=('STAGE', 'PAPER'), help="Clear cache for stage/paper")
    parser.add_argument("--test-stage", help="Test individual stage on specific paper")
    parser.add_argument("--paper", help="Specify paper for stage testing")
    
    args = parser.parse_args()
    
    try:
        # Handle audit commands that don't require API key
        if args.cache_stats or args.stage_summary or args.inspect_stage or args.clear_cache:
            await handle_audit_commands(args)
            return
        
        # Ensure API key is provided for synthesis operations
        if not args.api_key:
            print("❌ Gemini API key is required for synthesis operations.")
            print("Use --api-key YOUR_API_KEY")
            sys.exit(1)
        
        # Initialize runner
        enable_cache = not args.disable_cache
        runner = SynthesisRunner(
            api_key=args.api_key,
            config_path=args.config,
            resume_checkpoint=args.resume_from,
            max_papers=args.limit,
            enable_cache=enable_cache
        )
        
        # Validate environment
        if not runner.validate_environment():
            print("\\n❌ Environment validation failed. Please fix issues and try again.")
            sys.exit(1)
        
        if args.validate_only:
            print("\\n✅ Environment validation passed!")
            sys.exit(0)
        
        # Run synthesis
        result = await runner.run_synthesis()
        
        print("\\n🎯 Synthesis completed successfully!")
        print("📁 Check 9_final_synthesis/ directory for results")
        
    except KeyboardInterrupt:
        print("\\n⏹️  Synthesis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Synthesis failed: {str(e)}")
        logging.error(f"Synthesis execution failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())