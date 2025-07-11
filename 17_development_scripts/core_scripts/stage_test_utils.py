"""
Shared Utilities for Stage-by-Stage Testing
Provides common framework for all individual stage test scripts
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import time

# Add synthesis engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '6_synthesis_engine'))

# Import necessary components
from utils.stage_cache_manager import StageCacheManager
from utils.json_config import setup_logging

class StageTestFramework:
    """Common framework for stage-by-stage testing"""
    
    def __init__(self, stage_id: str, stage_name: str):
        """
        Initialize the test framework for a specific stage
        
        Args:
            stage_id: Stage identifier (e.g., '1a', '1b', '2a', etc.)
            stage_name: Human-readable stage name
        """
        self.stage_id = stage_id.lower()
        self.stage_name = stage_name
        self.test_outputs_dir = Path("test_outputs")
        self.stage_output_dir = self.test_outputs_dir / f"stage_{self.stage_id}"
        self.cache_manager = StageCacheManager()
        # Note: data_adapter removed - we now load papers individually for efficiency
        
        # Ensure output directories exist
        self.test_outputs_dir.mkdir(exist_ok=True)
        self.stage_output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_stage_logging()
        
        # Performance tracking
        self.start_time = None
        self.token_usage = {"input": 0, "output": 0}
        self.cost = 0.0
        
    def setup_stage_logging(self):
        """Setup logging specific to this stage"""
        log_file = self.stage_output_dir / f"stage_{self.stage_id}_test.log"
        
        # Create file handler with UTF-8 encoding
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Get logger
        logger = logging.getLogger(f"stage_{self.stage_id}_test")
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers = []
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.logger = logger
        
    def load_paper_data(self, paper_filename: str) -> Dict[str, Any]:
        """
        Load single paper data directly from synthesis_ready directory
        
        Args:
            paper_filename: Name of the paper file (with or without .json extension)
            
        Returns:
            Dictionary containing paper data
        """
        try:
            # Handle both .pdf and .json extensions
            if paper_filename.endswith('.pdf'):
                json_filename = paper_filename.replace('.pdf', '.json')
            elif not paper_filename.endswith('.json'):
                json_filename = f"{paper_filename}.json"
            else:
                json_filename = paper_filename
            
            # Load directly from file (efficient single-paper loading)
            synthesis_ready_dir = Path("3_synthesis_ready")
            paper_file = synthesis_ready_dir / json_filename
            
            if not paper_file.exists():
                # Try to find paper by partial name match
                available_papers = [f.name for f in synthesis_ready_dir.glob("*.json")]
                matches = [p for p in available_papers if json_filename.replace('.json', '') in p.replace('.json', '')]
                
                if matches:
                    paper_file = synthesis_ready_dir / matches[0]
                    json_filename = matches[0]
                else:
                    raise FileNotFoundError(f"Paper not found: {json_filename}\nAvailable papers: {available_papers[:5]}...")
            
            # Load single paper efficiently
            with open(paper_file, 'r', encoding='utf-8') as f:
                paper_data = json.load(f)
            
            # Add filename metadata if missing
            if 'filename' not in paper_data:
                paper_data['filename'] = json_filename
                
            self.logger.info(f"Successfully loaded single paper: {json_filename}")
            return paper_data
            
        except Exception as e:
            self.logger.error(f"Failed to load paper data: {str(e)}")
            raise
            
    def load_dependency_results(self, paper_id: str, dependency_stages: List[str], 
                              use_cache: bool = True) -> Dict[str, Any]:
        """
        Load results from dependency stages (prioritizes standard pipeline locations)
        
        Args:
            paper_id: Paper identifier
            dependency_stages: List of dependency stage IDs (e.g., ['1a', '1b'])
            use_cache: Whether to use cached results as fallback
            
        Returns:
            Dictionary mapping stage_id to results
        """
        dependency_results = {}
        
        for dep_stage in dependency_stages:
            result = None
            source = None
            
            # First try standard pipeline output directory (most recent file)
            main_stage_dir = Path("8_stage_outputs") / f"stage_{dep_stage}"
            if main_stage_dir.exists():
                # Find most recent file for this paper
                pattern = f"{paper_id}_{dep_stage}_*.json"
                matching_files = list(main_stage_dir.glob(pattern))
                if matching_files:
                    # Get most recent file
                    latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                    # Extract results from metadata wrapper if present
                    result = file_data.get('results', file_data)
                    source = f"standard pipeline output ({latest_file.name})"
                    
            # Then try cache if enabled and no standard output found
            if result is None and use_cache and self.cache_manager.is_stage_cached(paper_id, dep_stage):
                cached_result = self.cache_manager.get_cached_result(paper_id, dep_stage)
                if cached_result:
                    result = cached_result
                    source = "cache"
                    
            # Finally try test_outputs directory as fallback
            if result is None:
                test_output_file = self.test_outputs_dir / f"stage_{dep_stage}" / f"{paper_id}_{dep_stage}_output.json"
                if test_output_file.exists():
                    with open(test_output_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                    # Extract results from metadata wrapper if present
                    result = file_data.get('results', file_data)
                    source = "test outputs"
                    
            if result is not None:
                self.logger.info(f"Loaded {dep_stage} results from {source} for {paper_id}")
                dependency_results[f"stage_{dep_stage}_results"] = result
            else:
                # If not found anywhere, error
                self.logger.error(f"Could not find {dep_stage} results for {paper_id}")
                raise FileNotFoundError(f"Dependency stage {dep_stage} results not found for {paper_id}")
                
        return dependency_results
        
    def save_stage_output(self, paper_id: str, results: Dict[str, Any], 
                         include_metadata: bool = True, run_type: str = "stage_test") -> str:
        """
        Save stage output to standard pipeline locations with metadata
        
        Args:
            paper_id: Paper identifier
            results: Stage processing results
            include_metadata: Whether to include processing metadata
            run_type: Type of run ("stage_test", "full_pipeline", etc.)
            
        Returns:
            Path to saved output file
        """
        try:
            # Add metadata if requested
            if include_metadata:
                output = {
                    "stage_id": self.stage_id,
                    "stage_name": self.stage_name,
                    "paper_id": paper_id,
                    "run_type": run_type,
                    "processing_timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": time.time() - self.start_time if self.start_time else 0,
                    "token_usage": self.token_usage,
                    "estimated_cost_usd": self.cost,
                    "results": results
                }
            else:
                output = results
                
            # Save to standard pipeline location for natural stage dependency resolution
            main_output_dir = Path("8_stage_outputs") / f"stage_{self.stage_id}"
            main_output_dir.mkdir(parents=True, exist_ok=True)
            main_output_file = main_output_dir / f"{paper_id}_{self.stage_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(main_output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved stage output to: {main_output_file}")
            
            # Also save to test outputs directory for test-specific tracking
            test_output_file = self.stage_output_dir / f"{paper_id}_{self.stage_id}_output.json"
            with open(test_output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            return str(main_output_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save stage output: {str(e)}")
            raise
            
    def display_results(self, results: Dict[str, Any], detailed: bool = False):
        """
        Display results in a user-friendly format
        
        Args:
            results: Stage processing results
            detailed: Whether to show detailed output
        """
        print(f"\n{'='*80}")
        print(f"STAGE {self.stage_id.upper()}: {self.stage_name}")
        print(f"{'='*80}\n")
        
        # Display based on stage type
        if self.stage_id in ['1a', '2a']:  # Extraction stages
            self._display_extraction_results(results, detailed)
        elif self.stage_id in ['1b', '2b', '3b', '4b']:  # Validation stages
            self._display_validation_results(results, detailed)
        elif self.stage_id == '3a':  # Synthesis stage
            self._display_synthesis_results(results, detailed)
        elif self.stage_id == '4a':  # Client mapping stage
            self._display_mapping_results(results, detailed)
        else:
            # Generic display
            self._display_generic_results(results, detailed)
            
        # Display performance metrics
        self._display_performance_metrics()
        
    def _display_extraction_results(self, results: Dict[str, Any], detailed: bool):
        """Display extraction stage results"""
        if 'error' in results:
            print(f"❌ ERROR: {results['error']}")
            return
            
        # Paper metadata
        if 'paper_metadata' in results:
            metadata = results['paper_metadata']
            print("📄 Paper Metadata:")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Year: {metadata.get('publication_year', 'N/A')}")
            print(f"   Authors: {', '.join(metadata.get('authors', []))[:80]}...")
            print(f"   DOI: {metadata.get('doi', 'N/A')}")
            
        # Key findings (check multiple possible field names)
        findings_field = None
        if 'quantitative_findings' in results:
            findings_field = 'quantitative_findings'
        elif 'key_findings' in results:
            findings_field = 'key_findings'
            
        if findings_field:
            findings_data = results[findings_field]
            if isinstance(findings_data, dict):
                print(f"\n🔍 Quantitative Findings: {len(findings_data)} categories extracted")
                if detailed:
                    for category, data in list(findings_data.items())[:3]:
                        print(f"   - {category}: {str(data)[:100]}...")
            elif isinstance(findings_data, list):
                print(f"\n🔍 Key Findings: {len(findings_data)} items extracted")
                if detailed and findings_data:
                    for i, finding in enumerate(findings_data[:3]):
                        if isinstance(finding, dict):
                            print(f"   {i+1}. {finding.get('finding', str(finding))[:100]}...")
                        else:
                            print(f"   {i+1}. {str(finding)[:100]}...")
                    
        # For soil K extraction specifically
        if self.stage_id == '2a' and 'soil_k_parameters' in results:
            params = results['soil_k_parameters']
            print(f"\n🌱 Soil K Parameters: {len(params)} parameters extracted")
            if detailed:
                for param_name, param_data in list(params.items())[:3]:
                    print(f"   - {param_name}: {param_data.get('value', 'N/A')} {param_data.get('unit', '')}")
                    
    def _display_validation_results(self, results: Dict[str, Any], detailed: bool):
        """Display validation stage results"""
        if 'error' in results:
            print(f"❌ ERROR: {results['error']}")
            return
            
        # Validation quality
        if 'validation_quality' in results:
            quality = results['validation_quality']
            print(f"✅ Validation Quality: {quality.get('overall_score', 0):.1%}")
            print(f"   Completeness: {quality.get('completeness', 0):.1%}")
            print(f"   Accuracy: {quality.get('accuracy_confidence', 0):.1%}")
            print(f"   Consistency: {quality.get('consistency', 0):.1%}")
            
        # Validation issues
        if 'validation_issues' in results and results['validation_issues']:
            print(f"\n⚠️  Issues Found: {len(results['validation_issues'])}")
            if detailed:
                for issue in results['validation_issues'][:3]:
                    print(f"   - {issue}")
                    
        # Success status
        success = results.get('success', False) or results.get('validation_success', False)
        print(f"\n{'✅ Validation PASSED' if success else '❌ Validation FAILED'}")
        
    def _display_synthesis_results(self, results: Dict[str, Any], detailed: bool):
        """Display synthesis stage results"""
        if 'error' in results:
            print(f"❌ ERROR: {results['error']}")
            return
            
        print("🔄 Paper Synthesis Results:")
        
        # Paper authority
        if 'paper_authority' in results:
            auth = results['paper_authority']
            print(f"   Paper Authority: {len(auth)} authority dimensions")
            if detailed and isinstance(auth, dict):
                for key in list(auth.keys())[:3]:
                    value = auth[key]
                    if isinstance(value, str) and len(value) > 0:
                        print(f"   - {key}: {value[:100]}...")
        
        # Integrated soil K findings
        if 'integrated_soil_k_findings' in results:
            findings = results['integrated_soil_k_findings']
            print(f"   Soil K Findings: {len(findings)} synthesis sections")
            if detailed and isinstance(findings, dict):
                for section in ['contextualized_measurements', 'process_understanding', 'temporal_dynamics_synthesis']:
                    if section in findings and isinstance(findings[section], list):
                        print(f"   - {section}: {len(findings[section])} items")
        
        # Scientific contributions
        if 'scientific_contribution_assessment' in results:
            contrib = results['scientific_contribution_assessment']
            print(f"   Scientific Contributions: {len(contrib)} contribution types")
            
        # Synthesis confidence
        if 'synthesis_confidence' in results:
            conf = results.get('synthesis_confidence', 0.0)
            print(f"   Synthesis Confidence: {conf:.1%}")
            
        # Stage metadata
        if 'stage' in results:
            print(f"   Stage: {results['stage']}")
        if 'synthesis_timestamp' in results:
            print(f"   Processed: {results['synthesis_timestamp'][:16]}")
            
        # Fallback for legacy format
        if 'synthesized_findings' in results:
            findings = results['synthesized_findings']
            print(f"   Legacy Synthesized Findings: {len(findings)} items")
            
        if 'parameter_synthesis' in results:
            params = results['parameter_synthesis']
            print(f"   Legacy Parameter Synthesis: {len(params)} parameters integrated")
            
    def _display_mapping_results(self, results: Dict[str, Any], detailed: bool):
        """Display client mapping results"""
        if 'error' in results:
            print(f"❌ ERROR: {results['error']}")
            return
            
        print("🎯 Client Mapping Results:")
        
        if 'paper_identification' in results:
            paper_id = results['paper_identification']
            print(f"   Paper Title: {paper_id.get('title', 'N/A')[:80]}...")
            print(f"   Geographic Coverage: {', '.join(paper_id.get('geographic_coverage', []))}")
            print(f"   Temporal Scope: {paper_id.get('temporal_scope', 'N/A')}")
        
        if 'direct_evidence_mapping' in results:
            mapping = results['direct_evidence_mapping']
            if 'quantitative_parameters' in mapping:
                params = mapping['quantitative_parameters']
                print(f"   Quantitative Parameters: {len(params)} parameters mapped")
                if detailed:
                    for param in params[:3]:
                        branch = param.get('question_branch', 'N/A')
                        strength = param.get('evidence_strength', 'N/A')
                        print(f"   - {branch}: {strength} evidence")
                        
        if 'indirect_evidence_mapping' in results:
            indirect = results['indirect_evidence_mapping']
            if isinstance(indirect, dict) and 'supporting_information' in indirect:
                supporting = indirect['supporting_information']
                print(f"   Supporting Information: {len(supporting)} items")
                
        if 'confidence_assessment' in results:
            conf = results['confidence_assessment']
            overall_conf = conf.get('overall_mapping_confidence', 0)
            print(f"   Overall Mapping Confidence: {overall_conf:.1%}")
            
        if 'coverage_analysis' in results:
            coverage = results['coverage_analysis']
            total_questions = coverage.get('total_questions_in_architecture', 0)
            addressed = coverage.get('questions_with_evidence', 0)
            print(f"   Coverage: {addressed}/{total_questions} questions addressed")
            
    def _display_generic_results(self, results: Dict[str, Any], detailed: bool):
        """Generic result display"""
        print(f"📊 Results Summary:")
        print(f"   Total fields: {len(results)}")
        print(f"   Has error: {'Yes' if 'error' in results else 'No'}")
        
        if detailed:
            print("\n📋 Result Structure:")
            for key in list(results.keys())[:10]:
                value_type = type(results[key]).__name__
                print(f"   - {key}: {value_type}")
                
    def _display_performance_metrics(self):
        """Display performance metrics"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"\n⏱️  Performance Metrics:")
            print(f"   Processing Time: {elapsed:.1f} seconds")
            print(f"   Input Tokens: {self.token_usage['input']:,}")
            print(f"   Output Tokens: {self.token_usage['output']:,}")
            print(f"   Estimated Cost: ${self.cost:.4f}")
            
    def validate_stage_output(self, results: Dict[str, Any], expected_stage: str = None) -> Tuple[bool, List[str]]:
        """
        Validate stage output structure and content
        
        Args:
            results: Stage processing results
            expected_stage: Override stage for validation (useful for testing)
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        stage_to_validate = expected_stage or self.stage_id
        
        # Check for error
        if 'error' in results:
            issues.append(f"Stage returned error: {results['error']}")
            return False, issues
            
        # Stage-specific validation
        if stage_to_validate in ['1a', '2a']:  # Extraction stages
            required_fields = ['paper_metadata']
            if stage_to_validate == '1a':
                # Generic extraction produces these fields
                required_fields.extend(['research_methodology', 'quantitative_findings'])
            elif stage_to_validate == '2a':
                # Soil K extraction produces these fields
                required_fields.extend(['quantitative_soil_k_data', 'methodological_details'])
        elif stage_to_validate in ['1b', '2b', '3b', '4b']:  # Validation stages
            # Validation stages now checked for validation_quality, validation_certification, or success fields
            required_fields = ['success']
        elif stage_to_validate == '3a':  # Synthesis stage
            required_fields = ['paper_authority', 'integrated_soil_k_findings']
        elif stage_to_validate == '4a':  # Client mapping stage
            required_fields = ['paper_identification', 'direct_evidence_mapping']
        else:
            required_fields = []
            
        # Check required fields
        for field in required_fields:
            if field not in results:
                issues.append(f"Missing required field: {field}")
                
        # Stage 3A specific validation
        if stage_to_validate == '3a':
            # Check for key synthesis sections
            if 'paper_authority' in results:
                auth = results['paper_authority']
                if not isinstance(auth, dict) or len(auth) == 0:
                    issues.append("paper_authority section is empty or malformed")
                    
            if 'integrated_soil_k_findings' in results:
                findings = results['integrated_soil_k_findings']
                if not isinstance(findings, dict) or len(findings) == 0:
                    issues.append("integrated_soil_k_findings section is empty or malformed")
                    
            # Check for synthesis confidence
            if 'synthesis_confidence' in results:
                conf = results.get('synthesis_confidence', 0.0)
                if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                    issues.append("synthesis_confidence must be a number between 0 and 1")
                    
        # Check for substantial content
        if len(str(results)) < 100:
            issues.append("Results appear to have insufficient content")
            
        is_valid = len(issues) == 0
        return is_valid, issues
        
    def generate_summary_report(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report across multiple test runs
        
        Args:
            all_results: List of results from multiple test runs
            
        Returns:
            Summary report dictionary
        """
        summary = {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "test_summary": {
                "total_tests": len(all_results),
                "successful_tests": sum(1 for r in all_results if 'error' not in r),
                "failed_tests": sum(1 for r in all_results if 'error' in r),
                "average_processing_time": 0,
                "total_cost": 0,
                "total_tokens": {"input": 0, "output": 0}
            },
            "papers_tested": [],
            "common_issues": [],
            "test_timestamp": datetime.now().isoformat()
        }
        
        # Calculate averages and totals
        total_time = 0
        for result in all_results:
            if 'processing_time_seconds' in result:
                total_time += result['processing_time_seconds']
            if 'estimated_cost_usd' in result:
                summary['test_summary']['total_cost'] += result['estimated_cost_usd']
            if 'token_usage' in result:
                summary['test_summary']['total_tokens']['input'] += result['token_usage'].get('input', 0)
                summary['test_summary']['total_tokens']['output'] += result['token_usage'].get('output', 0)
            if 'paper_id' in result:
                summary['papers_tested'].append(result['paper_id'])
                
        if len(all_results) > 0:
            summary['test_summary']['average_processing_time'] = total_time / len(all_results)
            
        # Save summary
        summary_file = self.test_outputs_dir / f"stage_{self.stage_id}_test_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        return summary
        
    def start_tracking(self):
        """Start performance tracking"""
        self.start_time = time.time()
        
    def update_metrics(self, token_usage: Dict[str, int], cost: float):
        """Update performance metrics"""
        self.token_usage = token_usage
        self.cost = cost
        
    def get_standard_args(self, stage_description: str) -> argparse.ArgumentParser:
        """
        Get standard command-line argument parser
        
        Args:
            stage_description: Description of the stage for help text
            
        Returns:
            Configured ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description=f"Test Stage {self.stage_id.upper()}: {stage_description}",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Required arguments
        parser.add_argument("--paper", required=True, 
                          help="Paper filename to test (e.g., 'paper_name.pdf' or 'paper_name.json')")
        parser.add_argument("--api-key", required=True,
                          help="Gemini API key")
        
        # Optional arguments
        parser.add_argument("--disable-cache", action="store_true",
                          help="Force fresh processing, ignore cache")
        parser.add_argument("--use-cached-deps", action="store_true",
                          help="Use cached results from dependency stages")
        parser.add_argument("--output-dir", 
                          help="Override default test_outputs/ directory")
        parser.add_argument("--verbose", action="store_true",
                          help="Show detailed processing information")
        parser.add_argument("--save-debug", action="store_true",
                          help="Save debug information and intermediate states")
        parser.add_argument("--no-display", action="store_true",
                          help="Don't display results (only save)")
        
        return parser

# Utility functions for common operations

def load_paper_list(limit: Optional[int] = None) -> List[str]:
    """Load list of available papers efficiently from filesystem"""
    synthesis_ready_dir = Path("3_synthesis_ready")
    
    # Get all JSON files directly from filesystem
    paper_files = [f.name for f in synthesis_ready_dir.glob("*.json")]
    paper_files.sort()  # Consistent ordering
    
    # Apply limit if specified
    if limit:
        paper_files = paper_files[:limit]
        logging.info(f"Limiting to first {limit} papers")
    
    # Convert to .pdf names for consistency with existing interface
    paper_names = [f.replace('.json', '.pdf') for f in paper_files]
    
    logging.info(f"Successfully loaded {len(paper_names)} papers from individual files")
    return paper_names

def format_json_output(data: Dict[str, Any], indent: int = 2) -> str:
    """Format JSON for display"""
    return json.dumps(data, indent=indent, ensure_ascii=False)

def calculate_stage_cost(input_tokens: int, output_tokens: int, thinking_tokens: int = 0) -> float:
    """Calculate estimated cost for Gemini API usage"""
    # Gemini pricing (approximate)
    input_cost_per_1k = 0.00275  # $2.75 per 1M tokens
    output_cost_per_1k = 0.011   # $11 per 1M tokens
    
    total_cost = (input_tokens / 1000 * input_cost_per_1k) + (output_tokens / 1000 * output_cost_per_1k)
    return total_cost

def validate_paper_exists(paper_filename: str) -> bool:
    """Check if paper exists in synthesis_ready directory"""
    synthesis_ready_dir = Path("3_synthesis_ready")
    
    # Handle both .pdf and .json extensions
    if paper_filename.endswith('.pdf'):
        json_filename = paper_filename.replace('.pdf', '.json')
    elif not paper_filename.endswith('.json'):
        json_filename = f"{paper_filename}.json"
    else:
        json_filename = paper_filename
    
    # Check if file exists directly
    paper_file = synthesis_ready_dir / json_filename
    if paper_file.exists():
        return True
        
    # Try partial name match
    available_papers = [f.name for f in synthesis_ready_dir.glob("*.json")]
    matches = [p for p in available_papers if json_filename.replace('.json', '') in p.replace('.json', '')]
    
    return len(matches) > 0

# Test result aggregation utilities

class TestResultAggregator:
    """Aggregate results across multiple stage tests"""
    
    def __init__(self):
        self.results_dir = Path("test_outputs")
        
    def collect_stage_results(self, stage_id: str) -> List[Dict[str, Any]]:
        """Collect all test results for a specific stage"""
        stage_dir = self.results_dir / f"stage_{stage_id}"
        if not stage_dir.exists():
            return []
            
        results = []
        for output_file in stage_dir.glob("*_output.json"):
            with open(output_file, 'r', encoding='utf-8') as f:
                results.append(json.load(f))
                
        return results
        
    def generate_pipeline_report(self) -> Dict[str, Any]:
        """Generate report across all stages"""
        report = {
            "pipeline_test_summary": {
                "timestamp": datetime.now().isoformat(),
                "stages_tested": {},
                "total_cost": 0,
                "total_processing_time": 0,
                "papers_processed": set()
            }
        }
        
        # Collect data from all stages
        for stage_id in ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b']:
            stage_results = self.collect_stage_results(stage_id)
            if stage_results:
                stage_summary = {
                    "tests_run": len(stage_results),
                    "successful": sum(1 for r in stage_results if 'error' not in r.get('results', {})),
                    "failed": sum(1 for r in stage_results if 'error' in r.get('results', {})),
                    "avg_time": sum(r.get('processing_time_seconds', 0) for r in stage_results) / len(stage_results),
                    "total_cost": sum(r.get('estimated_cost_usd', 0) for r in stage_results)
                }
                
                report['pipeline_test_summary']['stages_tested'][stage_id] = stage_summary
                report['pipeline_test_summary']['total_cost'] += stage_summary['total_cost']
                report['pipeline_test_summary']['total_processing_time'] += stage_summary['avg_time'] * stage_summary['tests_run']
                
                # Collect paper IDs
                for result in stage_results:
                    if 'paper_id' in result:
                        report['pipeline_test_summary']['papers_processed'].add(result['paper_id'])
                        
        # Convert set to list for JSON serialization
        report['pipeline_test_summary']['papers_processed'] = list(report['pipeline_test_summary']['papers_processed'])
        
        # Save report
        report_file = self.results_dir / "pipeline_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return report

# Example usage function for reference
def example_stage_test():
    """Example of how to use the framework in a stage test script"""
    # Initialize framework
    framework = StageTestFramework('1a', 'Generic Extraction')
    
    # Get command line arguments
    parser = framework.get_standard_args("Extract generic paper metadata and findings")
    args = parser.parse_args()
    
    # Load paper data
    paper_data = framework.load_paper_data(args.paper)
    paper_id = paper_data.get('filename', 'unknown')
    
    # Start tracking
    framework.start_tracking()
    
    # Process stage (stage-specific logic would go here)
    results = {"paper_metadata": {"title": "Example"}, "key_findings": []}
    
    # Update metrics
    framework.update_metrics({"input": 1000, "output": 500}, 0.01)
    
    # Save output
    framework.save_stage_output(paper_id, results)
    
    # Display results
    if not args.no_display:
        framework.display_results(results, detailed=args.verbose)
    
    # Validate output
    is_valid, issues = framework.validate_stage_output(results)
    if not is_valid:
        framework.logger.warning(f"Validation issues: {issues}")