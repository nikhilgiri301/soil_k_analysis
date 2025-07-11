#!/usr/bin/env python3
"""
Test Script for Batch-Enabled Stage-by-Stage Processor
Validates functionality before full 25-paper processing

Usage:
    python test_batch_processor.py --api-key YOUR_API_KEY
    python test_batch_processor.py --api-key YOUR_API_KEY --test-stage 1A
    python test_batch_processor.py --api-key YOUR_API_KEY --validate-dependencies
"""

import asyncio
import argparse
import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Import the batch processor
from process_all_papers_batch import BatchStageProcessor

class BatchProcessorTester:
    """Test harness for the batch processor"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        # Initialize logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _record_test_result(self, test_name: str, passed: bool, message: str, details: dict = None):
        """Record a test result"""
        self.test_results["tests_run"] += 1
        
        if passed:
            self.test_results["tests_passed"] += 1
            status = "PASSED"
            emoji = "✅"
        else:
            self.test_results["tests_failed"] += 1
            status = "FAILED"
            emoji = "❌"
        
        result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        
        self.test_results["test_details"].append(result)
        
        print(f"{emoji} {test_name}: {message}")
        
        if details and logging.getLogger().isEnabledFor(logging.DEBUG):
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def test_environment_setup(self) -> bool:
        """Test that environment is properly set up"""
        print("\n🔍 Testing Environment Setup...")
        
        # Test required directories
        required_dirs = [
            "3_synthesis_ready",
            "6_synthesis_engine",
            "7_client_architecture",
            "8_stage_outputs"
        ]
        
        all_passed = True
        
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                self._record_test_result(
                    f"Directory {dir_path} exists",
                    True,
                    f"Found required directory: {dir_path}"
                )
            else:
                self._record_test_result(
                    f"Directory {dir_path} exists",
                    False,
                    f"Missing required directory: {dir_path}"
                )
                all_passed = False
        
        # Test synthesis-ready papers
        try:
            synthesis_ready_dir = Path("3_synthesis_ready")
            paper_files = list(synthesis_ready_dir.glob("*.json"))
            
            if paper_files:
                self._record_test_result(
                    "Papers available",
                    True,
                    f"Found {len(paper_files)} papers in synthesis_ready",
                    {"paper_count": len(paper_files)}
                )
            else:
                self._record_test_result(
                    "Papers available",
                    False,
                    "No papers found in synthesis_ready directory"
                )
                all_passed = False
        except Exception as e:
            self._record_test_result(
                "Papers available",
                False,
                f"Error checking papers: {str(e)}"
            )
            all_passed = False
        
        # Test client architecture files
        client_files = [
            "7_client_architecture/question_tree.json",
            "7_client_architecture/parameter_definitions.json"
        ]
        
        for file_path in client_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    self._record_test_result(
                        f"Client file {os.path.basename(file_path)} valid",
                        True,
                        f"Valid JSON file: {file_path}"
                    )
                except json.JSONDecodeError as e:
                    self._record_test_result(
                        f"Client file {os.path.basename(file_path)} valid",
                        False,
                        f"Invalid JSON in {file_path}: {str(e)}"
                    )
                    all_passed = False
            else:
                self._record_test_result(
                    f"Client file {os.path.basename(file_path)} exists",
                    False,
                    f"Missing client file: {file_path}"
                )
                all_passed = False
        
        return all_passed
    
    def test_processor_initialization(self) -> bool:
        """Test that the batch processor initializes correctly"""
        print("\n🔧 Testing Processor Initialization...")
        
        try:
            processor = BatchStageProcessor(
                api_key=self.api_key,
                limit=2,  # Test with 2 papers
                test_mode=True
            )
            
            self._record_test_result(
                "Processor initialization",
                True,
                "Successfully initialized BatchStageProcessor"
            )
            
            # Test stage order
            expected_stages = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b']
            if processor.stage_order == expected_stages:
                self._record_test_result(
                    "Stage order correct",
                    True,
                    "Stage order matches expected sequence"
                )
            else:
                self._record_test_result(
                    "Stage order correct",
                    False,
                    f"Stage order mismatch: {processor.stage_order} != {expected_stages}"
                )
                return False
            
            # Test processor map
            if len(processor.processor_map) == 8:
                self._record_test_result(
                    "Processor map complete",
                    True,
                    "All 8 stage processors initialized"
                )
            else:
                self._record_test_result(
                    "Processor map complete",
                    False,
                    f"Only {len(processor.processor_map)} processors initialized (expected 8)"
                )
                return False
            
            return True
            
        except Exception as e:
            self._record_test_result(
                "Processor initialization",
                False,
                f"Failed to initialize processor: {str(e)}"
            )
            return False
    
    async def test_paper_loading(self) -> bool:
        """Test paper loading functionality"""
        print("\n📄 Testing Paper Loading...")
        
        try:
            processor = BatchStageProcessor(
                api_key=self.api_key,
                limit=3,  # Test with 3 papers
                test_mode=True
            )
            
            papers = await processor.load_papers()
            
            if papers:
                self._record_test_result(
                    "Paper loading",
                    True,
                    f"Successfully loaded {len(papers)} papers",
                    {"paper_count": len(papers)}
                )
                
                # Test paper structure
                first_paper = papers[0]
                required_fields = ['paper_id', 'full_text']
                
                for field in required_fields:
                    if field in first_paper:
                        self._record_test_result(
                            f"Paper has {field} field",
                            True,
                            f"Paper structure includes {field}"
                        )
                    else:
                        self._record_test_result(
                            f"Paper has {field} field",
                            False,
                            f"Paper missing required field: {field}"
                        )
                        return False
                
                return True
            else:
                self._record_test_result(
                    "Paper loading",
                    False,
                    "No papers loaded"
                )
                return False
                
        except Exception as e:
            self._record_test_result(
                "Paper loading",
                False,
                f"Error loading papers: {str(e)}"
            )
            return False
    
    def test_dependency_resolution(self) -> bool:
        """Test dependency resolution logic"""
        print("\n🔗 Testing Dependency Resolution...")
        
        try:
            processor = BatchStageProcessor(
                api_key=self.api_key,
                limit=1,
                test_mode=True
            )
            
            # Test dependency mapping
            test_cases = [
                ('1a', []),
                ('1b', ['1a']),
                ('2a', []),
                ('2b', ['2a']),
                ('3a', ['1b', '2b']),
                ('3b', ['3a']),
                ('4a', ['3b']),
                ('4b', ['4a', '3b'])
            ]
            
            all_passed = True
            
            for stage_id, expected_deps in test_cases:
                actual_deps = processor._get_stage_dependencies(stage_id)
                
                if actual_deps == expected_deps:
                    self._record_test_result(
                        f"Dependencies for {stage_id}",
                        True,
                        f"Correct dependencies: {expected_deps}"
                    )
                else:
                    self._record_test_result(
                        f"Dependencies for {stage_id}",
                        False,
                        f"Wrong dependencies: {actual_deps} != {expected_deps}"
                    )
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self._record_test_result(
                "Dependency resolution",
                False,
                f"Error testing dependencies: {str(e)}"
            )
            return False
    
    def test_completion_status_check(self) -> bool:
        """Test completion status checking"""
        print("\n📊 Testing Completion Status Check...")
        
        try:
            processor = BatchStageProcessor(
                api_key=self.api_key,
                limit=2,
                test_mode=True
            )
            
            # Load papers for testing
            asyncio.run(processor.load_papers())
            
            # Test completion check for Stage 1A
            status = processor._check_stage_completion('1a')
            
            required_keys = ['completed', 'failed', 'pending', 'completion_rate']
            
            for key in required_keys:
                if key in status:
                    self._record_test_result(
                        f"Status has {key} key",
                        True,
                        f"Status includes {key}"
                    )
                else:
                    self._record_test_result(
                        f"Status has {key} key",
                        False,
                        f"Status missing key: {key}"
                    )
                    return False
            
            # Test completion rate calculation
            total_papers = len(processor.papers)
            if total_papers > 0:
                expected_rate = len(status['completed']) / total_papers
                if abs(status['completion_rate'] - expected_rate) < 0.001:
                    self._record_test_result(
                        "Completion rate calculation",
                        True,
                        f"Correct completion rate: {status['completion_rate']:.1%}"
                    )
                else:
                    self._record_test_result(
                        "Completion rate calculation",
                        False,
                        f"Wrong completion rate: {status['completion_rate']} != {expected_rate}"
                    )
                    return False
            
            return True
            
        except Exception as e:
            self._record_test_result(
                "Completion status check",
                False,
                f"Error checking completion status: {str(e)}"
            )
            return False
    
    async def test_single_stage_processing(self, stage_id: str = '1a') -> bool:
        """Test processing a single stage with limited papers"""
        print(f"\n🔄 Testing Single Stage Processing ({stage_id.upper()})...")
        
        try:
            processor = BatchStageProcessor(
                api_key=self.api_key,
                limit=1,  # Test with just 1 paper
                test_mode=True
            )
            
            # Load papers
            await processor.load_papers()
            
            if not processor.papers:
                self._record_test_result(
                    f"Stage {stage_id} processing",
                    False,
                    "No papers loaded for testing"
                )
                return False
            
            # Test stage processing
            result = await processor.process_stage(stage_id)
            
            if isinstance(result, dict) and 'completion_rate' in result:
                self._record_test_result(
                    f"Stage {stage_id} processing",
                    True,
                    f"Stage processed with {result['completion_rate']:.1%} completion rate"
                )
                return True
            else:
                self._record_test_result(
                    f"Stage {stage_id} processing",
                    False,
                    f"Invalid result format: {type(result)}"
                )
                return False
                
        except Exception as e:
            self._record_test_result(
                f"Stage {stage_id} processing",
                False,
                f"Error processing stage: {str(e)}"
            )
            return False
    
    def test_output_directory_structure(self) -> bool:
        """Test output directory structure"""
        print("\n📁 Testing Output Directory Structure...")
        
        try:
            # Check main output directory
            output_dir = Path("8_stage_outputs")
            if output_dir.exists():
                self._record_test_result(
                    "Main output directory exists",
                    True,
                    "8_stage_outputs directory found"
                )
            else:
                self._record_test_result(
                    "Main output directory exists",
                    False,
                    "8_stage_outputs directory missing"
                )
                return False
            
            # Check stage subdirectories
            expected_stages = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b']
            
            for stage_id in expected_stages:
                stage_dir = output_dir / f"stage_{stage_id}"
                if stage_dir.exists():
                    self._record_test_result(
                        f"Stage {stage_id} directory exists",
                        True,
                        f"Found stage_{stage_id} directory"
                    )
                    
                    # Check archive subdirectory
                    archive_dir = stage_dir / "archive"
                    if archive_dir.exists():
                        self._record_test_result(
                            f"Stage {stage_id} archive exists",
                            True,
                            f"Found stage_{stage_id}/archive directory"
                        )
                    else:
                        self._record_test_result(
                            f"Stage {stage_id} archive exists",
                            False,
                            f"Missing stage_{stage_id}/archive directory"
                        )
                        return False
                else:
                    self._record_test_result(
                        f"Stage {stage_id} directory exists",
                        False,
                        f"Missing stage_{stage_id} directory"
                    )
                    return False
            
            return True
            
        except Exception as e:
            self._record_test_result(
                "Output directory structure",
                False,
                f"Error checking directories: {str(e)}"
            )
            return False
    
    def generate_test_report(self) -> dict:
        """Generate comprehensive test report"""
        success_rate = self.test_results["tests_passed"] / self.test_results["tests_run"] if self.test_results["tests_run"] > 0 else 0
        
        return {
            "test_summary": {
                "total_tests": self.test_results["tests_run"],
                "passed": self.test_results["tests_passed"],
                "failed": self.test_results["tests_failed"],
                "success_rate": success_rate,
                "overall_status": "PASSED" if success_rate == 1.0 else "FAILED"
            },
            "test_details": self.test_results["test_details"],
            "timestamp": self.test_results["timestamp"]
        }
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🧪 Starting Batch Processor Test Suite")
        print("=" * 60)
        
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Processor Initialization", self.test_processor_initialization),
            ("Paper Loading", self.test_paper_loading),
            ("Dependency Resolution", self.test_dependency_resolution),
            ("Completion Status Check", self.test_completion_status_check),
            ("Output Directory Structure", self.test_output_directory_structure),
            ("Single Stage Processing", lambda: asyncio.run(self.test_single_stage_processing()))
        ]
        
        overall_passed = True
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print('='*60)
            
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                    
                if not result:
                    overall_passed = False
                    
            except Exception as e:
                self._record_test_result(
                    test_name,
                    False,
                    f"Test failed with exception: {str(e)}"
                )
                overall_passed = False
        
        # Generate and save test report
        report = self.generate_test_report()
        
        report_file = Path("test_outputs") / "batch_processor_test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{'='*60}")
        print("🏁 Test Suite Complete")
        print(f"{'='*60}")
        print(f"📊 Results: {report['test_summary']['passed']}/{report['test_summary']['total_tests']} tests passed")
        print(f"✅ Success Rate: {report['test_summary']['success_rate']:.1%}")
        print(f"📄 Report saved to: {report_file}")
        
        if overall_passed:
            print("🎉 All tests passed! Batch processor is ready for use.")
        else:
            print("❌ Some tests failed. Please review and fix issues before proceeding.")
        
        return overall_passed

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test Batch-Enabled Stage-by-Stage Processor")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    parser.add_argument("--test-stage", help="Test specific stage only (e.g., 1A)")
    parser.add_argument("--validate-dependencies", action="store_true", help="Only validate dependencies")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    try:
        tester = BatchProcessorTester(args.api_key)
        
        if args.validate_dependencies:
            success = tester.test_dependency_resolution()
            sys.exit(0 if success else 1)
        
        if args.test_stage:
            success = asyncio.run(tester.test_single_stage_processing(args.test_stage.lower()))
            sys.exit(0 if success else 1)
        
        # Run all tests
        success = asyncio.run(tester.run_all_tests())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()