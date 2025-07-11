#!/usr/bin/env python3
"""
Analyze Stage 1A batch processing token usage patterns
"""

import json
import re
from pathlib import Path

def analyze_batch_tokens():
    """Analyze token usage patterns in batch processing results"""
    
    # Read the batch results
    batch_file = Path("11_validation_logs/batch_downloads/stage_1a_batch_july10/raw/batch_results_decoded_20250710_074458.jsonl")
    
    if not batch_file.exists():
        print(f"Error: {batch_file} not found")
        return
    
    results = []
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            
            # Extract key information
            paper_key = data.get('key', 'unknown')
            response = data.get('response', {})
            usage = response.get('usageMetadata', {})
            
            candidates = response.get('candidates', [])
            finish_reason = candidates[0].get('finishReason', 'unknown') if candidates else 'unknown'
            
            # Extract token counts
            prompt_tokens = usage.get('promptTokenCount', 0)
            response_tokens = usage.get('candidatesTokenCount', 0)
            total_tokens = usage.get('totalTokenCount', 0)
            thoughts_tokens = usage.get('thoughtsTokenCount', 0)
            
            # Check if content was generated
            has_content = False
            if candidates and candidates[0].get('content'):
                parts = candidates[0]['content'].get('parts', [])
                if parts and parts[0].get('text'):
                    has_content = True
            
            results.append({
                'paper': paper_key,
                'finish_reason': finish_reason,
                'prompt_tokens': prompt_tokens,
                'response_tokens': response_tokens,
                'total_tokens': total_tokens,
                'thoughts_tokens': thoughts_tokens,
                'has_content': has_content
            })
    
    # Analyze patterns
    print("=" * 80)
    print("STAGE 1A BATCH TOKEN ANALYSIS")
    print("=" * 80)
    
    # Separate successful and failed
    successful = [r for r in results if r['finish_reason'] != 'MAX_TOKENS']
    failed = [r for r in results if r['finish_reason'] == 'MAX_TOKENS']
    
    print(f"\nSUMMARY:")
    print(f"Total papers: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed (MAX_TOKENS): {len(failed)}")
    print(f"Success rate: {len(successful)/len(results)*100:.1f}%")
    
    # Analyze successful paper
    print(f"\nSUCCESSFUL PAPER:")
    if successful:
        s = successful[0]
        print(f"Paper: {s['paper']}")
        print(f"Prompt tokens: {s['prompt_tokens']:,}")
        print(f"Response tokens: {s['response_tokens']:,}")
        print(f"Total tokens: {s['total_tokens']:,}")
        print(f"Thoughts tokens: {s['thoughts_tokens']:,}")
    
    # Analyze failed papers
    print(f"\nFAILED PAPERS TOKEN DISTRIBUTION:")
    
    if failed:
        failed_sorted = sorted(failed, key=lambda x: x['total_tokens'])
        
        print(f"Minimum total tokens (failed): {failed_sorted[0]['total_tokens']:,}")
        print(f"Maximum total tokens (failed): {failed_sorted[-1]['total_tokens']:,}")
        print(f"Average total tokens (failed): {sum(r['total_tokens'] for r in failed)/len(failed):,.0f}")
        
        print(f"\nTOKEN LIMIT ANALYSIS:")
        print(f"Papers with total tokens > 8,192: {len([r for r in failed if r['total_tokens'] > 8192])}")
        print(f"Papers with total tokens > 16,384: {len([r for r in failed if r['total_tokens'] > 16384])}")
        print(f"Papers with total tokens > 32,768: {len([r for r in failed if r['total_tokens'] > 32768])}")
        print(f"Papers with total tokens > 65,536: {len([r for r in failed if r['total_tokens'] > 65536])}")
        print(f"Papers with total tokens > 131,072: {len([r for r in failed if r['total_tokens'] > 131072])}")
        
        # Show token distribution
        print(f"\nFAILED PAPERS BY TOKEN COUNT:")
        print("Paper                                    | Prompt  | Response | Total   | Thoughts")
        print("-" * 80)
        for r in failed_sorted:
            paper_name = r['paper'][:35] + "..." if len(r['paper']) > 35 else r['paper']
            print(f"{paper_name:40} | {r['prompt_tokens']:7,} | {r['response_tokens']:8,} | {r['total_tokens']:7,} | {r['thoughts_tokens']:8,}")
    
    # Analyze prompt token sizes
    print(f"\nPROMPT TOKEN ANALYSIS:")
    all_prompt_tokens = [r['prompt_tokens'] for r in results]
    print(f"Minimum prompt tokens: {min(all_prompt_tokens):,}")
    print(f"Maximum prompt tokens: {max(all_prompt_tokens):,}")
    print(f"Average prompt tokens: {sum(all_prompt_tokens)/len(all_prompt_tokens):,.0f}")
    
    # Identify potential token limit
    print(f"\nTOKEN LIMIT HYPOTHESIS:")
    if successful:
        successful_max = successful[0]['total_tokens']
        failed_min = min(r['total_tokens'] for r in failed)
        print(f"Successful paper total tokens: {successful_max:,}")
        print(f"Minimum failed paper total tokens: {failed_min:,}")
        print(f"Gap: {failed_min - successful_max:,} tokens")
        
        # Check for common limits
        likely_limits = [8192, 16384, 32768, 65536, 131072]
        for limit in likely_limits:
            if successful_max <= limit < failed_min:
                print(f"LIKELY TOKEN LIMIT: {limit:,} tokens")
                break
    
    # Check for papers that generated no content
    no_content = [r for r in failed if not r['has_content']]
    if no_content:
        print(f"\nPAPERS WITH NO CONTENT GENERATED:")
        print(f"Count: {len(no_content)}")
        for r in no_content:
            print(f"  {r['paper']}: {r['total_tokens']:,} total tokens")

if __name__ == "__main__":
    analyze_batch_tokens()