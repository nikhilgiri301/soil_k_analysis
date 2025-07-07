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
from utils.config import load_config, setup_logging
from validation_framework.quality_controller import QualityController
from validation_framework.confidence_scorer import ConfidenceScorer

class SynthesisRunner:
    """Main runner for soil K literature synthesis"""
    
    def __init__(self, api_key: str, config_path: str = None, resume_checkpoint: str = None):
        self.api_key = api_key
        self.config_path = config_path or "6_synthesis_engine/config.json"
        self.resume_checkpoint = resume_checkpoint
        
        # Load configuration
        self.config = load_config(self.config_path)
        
        # Setup logging
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
            print("\\n🔧 Initializing synthesis engine...")
            self.engine = SoilKAnalysisEngine(
                api_key=self.api_key,
                resume_from_checkpoint=self.resume_checkpoint
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

async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Soil K Literature Synthesis Engine")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    parser.add_argument("--config", help="Custom config file path")
    parser.add_argument("--resume-from", help="Resume from checkpoint ID")
    parser.add_argument("--validate-only", action="store_true", help="Only validate environment")
    
    args = parser.parse_args()
    
    try:
        # Initialize runner
        runner = SynthesisRunner(
            api_key=args.api_key,
            config_path=args.config,
            resume_checkpoint=args.resume_from
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