#!/usr/bin/env python3
"""
Quick Batch Job Status Checker
Monitors the active Stage 1A batch job
"""

import sys
import os
import argparse
from datetime import datetime

try:
    import google.genai as genai
except ImportError:
    print("❌ google-genai package not installed")
    print("Run: pip install google-genai --break-system-packages")
    sys.exit(1)

def check_batch_status(api_key: str, job_id: str = "pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr"):
    """Check the status of the active batch job"""
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        
        # Get job status
        job_name = f"batches/{job_id}"
        current_job = client.batches.get(name=job_name)
        
        print(f"\n📋 Batch Job Status Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"═══════════════════════════════════════════════════════════")
        print(f"🆔 Job ID: {job_id}")
        print(f"📊 Status: {current_job.state.name}")
        print(f"📄 Papers: 22 papers in batch")
        print(f"📁 Display Name: {getattr(current_job.config, 'display_name', 'N/A')}")
        
        if hasattr(current_job, 'create_time'):
            print(f"⏰ Created: {current_job.create_time}")
        if hasattr(current_job, 'update_time'):
            print(f"🔄 Updated: {current_job.update_time}")
        
        if current_job.state.name == 'JOB_STATE_SUCCEEDED':
            print(f"\n🎉 BATCH JOB COMPLETED SUCCESSFULLY!")
            print(f"✅ Ready to download and process results")
            if hasattr(current_job, 'dest') and hasattr(current_job.dest, 'file_name'):
                print(f"📥 Result file: {current_job.dest.file_name}")
            print(f"\n🚀 Next Step: Run the batch processor to download results:")
            print(f"   python true_stage_1a_batch_processor.py --api-key YOUR_KEY --download-only")
        elif current_job.state.name == 'JOB_STATE_FAILED':
            print(f"\n❌ BATCH JOB FAILED!")
            print(f"🔍 Check job details for failure reason")
            if hasattr(current_job, 'error'):
                print(f"Error: {current_job.error}")
        elif current_job.state.name == 'JOB_STATE_RUNNING':
            print(f"\n🔄 BATCH JOB IS RUNNING")
            print(f"⏳ Processing papers... please wait")
            print(f"💡 Check again in 30-60 minutes")
        elif current_job.state.name == 'JOB_STATE_PENDING':
            print(f"\n⏳ BATCH JOB IS PENDING")
            print(f"🕐 Waiting in queue for processing to start")
            print(f"💡 Check again in 15-30 minutes")
        else:
            print(f"\n❓ Unknown status: {current_job.state.name}")
        
        print(f"\n🔄 Next recommended check: 15-30 minutes")
        print(f"💾 Job submitted: July 10, 2025 at 04:54:44 UTC")
        print(f"⏱️  Expected completion: 1-24 hours from submission")
        print(f"═══════════════════════════════════════════════════════════")
        
        return current_job.state.name
        
    except Exception as e:
        print(f"❌ Error checking batch job status: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Check Stage 1A batch job status")
    parser.add_argument("--api-key", required=True, help="Gemini API key")
    parser.add_argument("--job-id", default="pqa7ratq5qz7gs4b3ip3f8xfvn0o8jsr2etr", 
                       help="Batch job ID to check")
    
    args = parser.parse_args()
    
    status = check_batch_status(args.api_key, args.job_id)
    
    if status == 'JOB_STATE_SUCCEEDED':
        print("\n🎯 ACTION REQUIRED: Job completed! Download and process results.")
        sys.exit(0)
    elif status == 'JOB_STATE_FAILED':
        print("\n⚠️  ACTION REQUIRED: Job failed! Investigate and resubmit if needed.")
        sys.exit(1)
    elif status in ['JOB_STATE_RUNNING', 'JOB_STATE_PENDING']:
        print("\n✅ Job is progressing normally. Check again later.")
        sys.exit(0)
    else:
        print("\n❓ Unable to determine job status.")
        sys.exit(1)

if __name__ == "__main__":
    main()