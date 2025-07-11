#!/usr/bin/env python3
"""
Test Flash vs Pro: Automated Model Comparison
Runs the same paper through both Gemini 2.5 Flash and Pro models
then generates a comparison report
"""

import asyncio
import subprocess
import sys
import os
import argparse
from datetime import datetime

def run_test_script(script_name: str, paper: str, api_key: str, additional_args: list = None) -> dict:
    """Run a test script and return the result"""
    
    cmd = [
        sys.executable, script_name,
        "--paper", paper,
        "--api-key", api_key,
        "--verbose",
        "--save-debug"
    ]
    
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"🔄 Running: {' '.join(cmd[:4])} ...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": ' '.join(cmd)
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Process timed out after 10 minutes",
            "command": ' '.join(cmd)
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "command": ' '.join(cmd)
        }

def main():
    parser = argparse.ArgumentParser(description="Compare Flash vs Pro models on the same paper")
    parser.add_argument("paper", help="Paper filename to test")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    parser.add_argument("--disable-cache", action="store_true", help="Force fresh processing")
    parser.add_argument("--flash-only", action="store_true", help="Only run Flash model")
    parser.add_argument("--pro-only", action="store_true", help="Only run Pro model")
    parser.add_argument("--skip-comparison", action="store_true", help="Skip comparison report generation")
    parser.add_argument("--verbose", action="store_true", help="Show detailed comparison")
    
    args = parser.parse_args()
    
    # Extract paper ID for comparison
    paper_id = args.paper.replace('.json', '').replace('.pdf', '')
    
    print(f"\n{'='*80}")
    print(f"FLASH VS PRO MODEL COMPARISON")
    print(f"{'='*80}")
    print(f"📄 Paper: {args.paper}")
    print(f"🆔 Paper ID: {paper_id}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Additional arguments
    additional_args = []
    if args.disable_cache:
        additional_args.append("--disable-cache")
    
    results = {}
    
    # Run Flash model (unless pro-only)
    if not args.pro_only:
        print(f"\n{'='*40}")
        print("RUNNING FLASH MODEL")
        print(f"{'='*40}")
        
        flash_result = run_test_script(
            "test_stage_1a.py", 
            args.paper, 
            args.api_key, 
            additional_args
        )
        
        results['flash'] = flash_result
        
        if flash_result['success']:
            print("✅ Flash model completed successfully")
        else:
            print("❌ Flash model failed")
            print(f"   Error: {flash_result['stderr']}")
            if not args.pro_only:
                print("   Flash output:", flash_result['stdout'])
    
    # Run Pro model (unless flash-only)
    if not args.flash_only:
        print(f"\n{'='*40}")
        print("RUNNING PRO MODEL")
        print(f"{'='*40}")
        
        pro_result = run_test_script(
            "test_stage_1a_pro.py", 
            args.paper, 
            args.api_key, 
            additional_args
        )
        
        results['pro'] = pro_result
        
        if pro_result['success']:
            print("✅ Pro model completed successfully")
        else:
            print("❌ Pro model failed")
            print(f"   Error: {pro_result['stderr']}")
            if not args.flash_only:
                print("   Pro output:", pro_result['stdout'])
    
    # Generate comparison report (if both models ran successfully)
    if not args.skip_comparison:
        if (not args.flash_only and not args.pro_only and 
            results.get('flash', {}).get('success') and 
            results.get('pro', {}).get('success')):
            
            print(f"\n{'='*40}")
            print("GENERATING COMPARISON REPORT")
            print(f"{'='*40}")
            
            comparison_cmd = [
                sys.executable, "compare_flash_pro_results.py",
                paper_id,
                "--save-report"
            ]
            
            if args.verbose:
                comparison_cmd.append("--verbose")
            
            try:
                comparison_result = subprocess.run(comparison_cmd, capture_output=True, text=True, timeout=60)
                
                if comparison_result.returncode == 0:
                    print("✅ Comparison report generated successfully")
                    print(comparison_result.stdout)
                else:
                    print("❌ Comparison report generation failed")
                    print(f"   Error: {comparison_result.stderr}")
                    
            except Exception as e:
                print(f"❌ Error generating comparison report: {str(e)}")
        else:
            print("\n⚠️  Skipping comparison report - not both models successful")
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}")
    
    if 'flash' in results:
        status = "✅ Success" if results['flash']['success'] else "❌ Failed"
        print(f"Flash Model: {status}")
        
    if 'pro' in results:
        status = "✅ Success" if results['pro']['success'] else "❌ Failed"
        print(f"Pro Model: {status}")
    
    # Determine overall success
    overall_success = True
    if not args.pro_only and not results.get('flash', {}).get('success', False):
        overall_success = False
    if not args.flash_only and not results.get('pro', {}).get('success', False):
        overall_success = False
    
    if overall_success:
        print(f"\n🎉 All requested tests completed successfully!")
        print(f"📊 Check 8_stage_outputs/ for detailed results")
        print(f"📋 Check comparison_report_*.json for analysis")
    else:
        print(f"\n⚠️  Some tests failed - check error messages above")
    
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()