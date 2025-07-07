# FILE: 6_synthesis_engine/utils/gemini_client.py
# ACTION: REPLACE ENTIRE FILE - Fix the import issues
# PURPOSE: Update imports to work with current google-generativeai version

"""
Enhanced Gemini API client with thinking mode support for complex literature synthesis
Updated to remove artificial token limits and add comprehensive usage tracking
Fixed imports for current google-generativeai version
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import google.generativeai as genai
from .config import GEMINI_CONFIG
from pathlib import Path

class TokenUsageTracker:
    """Simple token usage tracking integrated into existing GeminiClient"""
    
    def __init__(self, output_dir: str = "11_validation_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.usage_data = []
        self.INPUT_COST = 0.15
        self.OUTPUT_COST_THINKING = 3.50
        
    def track_usage(self, stage_name: str, paper_id: str, response: Any, 
                   prompt_length: int, processing_time: float, thinking_enabled: bool) -> Dict[str, Any]:
        """Track token usage for this API call"""
        
        usage_record = {
            'timestamp': datetime.now().isoformat(),
            'stage_name': stage_name,
            'paper_id': paper_id,
            'prompt_length_chars': prompt_length,
            'processing_time_seconds': round(processing_time, 2),
            'thinking_enabled': thinking_enabled
        }
        
        # Extract token usage
        if hasattr(response, 'usage_metadata'):
            metadata = response.usage_metadata
            usage_record.update({
                'input_tokens': getattr(metadata, 'prompt_token_count', 0),
                'output_tokens': getattr(metadata, 'candidates_token_count', 0),
                'thinking_tokens': getattr(metadata, 'thinking_token_count', 0),
            })
            
            # Calculate costs
            input_cost = usage_record['input_tokens'] * self.INPUT_COST / 1_000_000
            output_cost = usage_record['output_tokens'] * self.OUTPUT_COST_THINKING / 1_000_000
            thinking_cost = usage_record['thinking_tokens'] * self.OUTPUT_COST_THINKING / 1_000_000
            
            usage_record.update({
                'input_cost_usd': round(input_cost, 6),
                'output_cost_usd': round(output_cost, 6), 
                'thinking_cost_usd': round(thinking_cost, 6),
                'total_cost_usd': round(input_cost + output_cost + thinking_cost, 6)
            })
            
            # Log summary
            logging.info(
                f"{stage_name} | IN={usage_record['input_tokens']:,} "
                f"OUT={usage_record['output_tokens']:,} THINK={usage_record['thinking_tokens']:,} | "
                f"Cost=${usage_record['total_cost_usd']:.4f} | Time={processing_time:.1f}s"
            )
        
        self.usage_data.append(usage_record)
        return usage_record
    
    def save_summary(self):
        """Save usage summary at end of processing"""
        if not self.usage_data:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed data
        detail_file = self.output_dir / f"token_usage_{timestamp}.json"
        with open(detail_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
        
        # Generate summary
        total_cost = sum(record.get('total_cost_usd', 0) for record in self.usage_data)
        total_papers = len(set(record['paper_id'] for record in self.usage_data))
        
        summary = {
            'total_calls': len(self.usage_data),
            'total_papers': total_papers,
            'total_cost_usd': round(total_cost, 4),
            'cost_per_paper': round(total_cost / max(total_papers, 1), 4),
            'timestamp': timestamp
        }
        
        summary_file = self.output_dir / f"usage_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logging.info(f"USAGE SUMMARY: {summary['total_calls']} calls, "
                    f"${summary['total_cost_usd']} total, "
                    f"${summary['cost_per_paper']:.3f} per paper")
        
        return summary

class GeminiClient:
    """Enhanced Gemini API client with thinking mode for complex reasoning tasks"""
    
    def __init__(self, api_key: str, enable_thinking: bool = True):
        if not api_key:
            raise ValueError("Gemini API key is required")
            
        genai.configure(api_key=api_key)
        self.client = genai
        self.enable_thinking = enable_thinking
        self.rate_limiter = asyncio.Semaphore(GEMINI_CONFIG.get("rate_limit", 30))
        self.request_count = 0
        self.error_count = 0
        
        # Initialize model
        self.model = genai.GenerativeModel(GEMINI_CONFIG['model'])
        
        # Token usage tracking
        self.tracker = TokenUsageTracker()
        
        logging.info(f"GeminiClient initialized with model: {GEMINI_CONFIG['model']}")
        logging.info(f"Thinking mode: {'enabled' if enable_thinking else 'disabled'}")
        logging.info("Token limits: REMOVED - using system defaults")
        
    async def generate_json_content(self, prompt: str, temperature: float = 0.1, 
                                   max_retries: int = None, 
                                   enable_thinking_for_stage: bool = None,
                                   stage_name: str = "unknown",
                                   paper_id: str = "unknown") -> Dict[str, Any]:
        """Generate JSON content with thinking mode, tracking, and NO artificial token limits"""
        
        if max_retries is None:
            max_retries = GEMINI_CONFIG.get("retry_attempts", 3)
        
        # Determine if thinking should be used for this specific call
        use_thinking = enable_thinking_for_stage if enable_thinking_for_stage is not None else self.enable_thinking
        
        start_time = time.time()
        
        async with self.rate_limiter:
            
            for attempt in range(max_retries + 1):
                try:
                    self.request_count += 1
                    
                    # Enhanced prompt to ensure JSON output
                    enhanced_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just the JSON object."
                    
                    # Configure generation - using the current API structure
                    generation_config = {
                        'temperature': temperature,
                        'response_mime_type': 'application/json',
                    }
                    
                    # Add thinking mode if enabled (this will work with current API or gracefully degrade)
                    if use_thinking:
                        generation_config['thinking_budget'] = -1  # Unlimited thinking
                        logging.debug(f"Using thinking mode for {stage_name} (temperature: {temperature})")
                    
                    # Generate content with enhanced API
                    response = await asyncio.wait_for(
                        self._generate_async_enhanced(enhanced_prompt, generation_config),
                        timeout=GEMINI_CONFIG.get("timeout", 300)  # Longer timeout for thinking mode
                    )
                    
                    # Track usage
                    processing_time = time.time() - start_time
                    usage_record = self.tracker.track_usage(
                        stage_name=stage_name,
                        paper_id=paper_id, 
                        response=response,
                        prompt_length=len(enhanced_prompt),
                        processing_time=processing_time,
                        thinking_enabled=use_thinking
                    )
                    
                    # Parse JSON response
                    try:
                        # Handle both direct JSON and text responses
                        if hasattr(response, 'text'):
                            response_text = response.text
                        else:
                            response_text = str(response)
                            
                        result = json.loads(response_text)
                        
                        # Add thinking metadata if available
                        if use_thinking and hasattr(response, 'thinking_text') and response.thinking_text:
                            result['_thinking_metadata'] = {
                                'thinking_tokens_used': usage_record.get('thinking_tokens', 0),
                                'has_thinking_trace': True
                            }
                        
                        # Add usage metadata
                        result['_usage_metadata'] = usage_record
                        
                        return result
                        
                    except json.JSONDecodeError as e:
                        logging.warning(f"JSON decode error (attempt {attempt + 1}): {str(e)}")
                        
                        # Try to extract JSON from malformed response
                        extracted_json = self._extract_json_from_response(response_text)
                        if extracted_json:
                            try:
                                result = json.loads(extracted_json)
                                result['_usage_metadata'] = usage_record
                                return result
                            except:
                                pass
                        
                        if attempt == max_retries:
                            self.error_count += 1
                            return {
                                "error": "json_decode_failed", 
                                "raw_response": response_text[:500],
                                "attempt": attempt + 1, 
                                "thinking_enabled": use_thinking,
                                "_usage_metadata": usage_record
                            }
                        
                except asyncio.TimeoutError:
                    logging.warning(f"Timeout (attempt {attempt + 1}) for {stage_name}")
                    if attempt == max_retries:
                        processing_time = time.time() - start_time
                        self.error_count += 1
                        return {
                            "error": "timeout", 
                            "attempt": attempt + 1, 
                            "thinking_enabled": use_thinking,
                            "processing_time": processing_time
                        }
                        
                except Exception as e:
                    logging.error(f"API error (attempt {attempt + 1}) for {stage_name}: {str(e)}")
                    if attempt == max_retries:
                        processing_time = time.time() - start_time
                        self.error_count += 1
                        return {
                            "error": str(e), 
                            "attempt": attempt + 1, 
                            "thinking_enabled": use_thinking,
                            "processing_time": processing_time
                        }
                
                # Wait before retry with exponential backoff
                if attempt < max_retries:
                    wait_time = GEMINI_CONFIG.get("retry_delay", 2) * (2 ** attempt)
                    logging.info(f"Retrying {stage_name} in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
            
            return {"error": "max_retries_exceeded", "thinking_enabled": use_thinking}
    
    async def _generate_async_enhanced(self, prompt: str, config: dict):
        """Enhanced async wrapper for Gemini generation with thinking mode"""
        loop = asyncio.get_event_loop()
        
        # Use the current API structure
        return await loop.run_in_executor(
            None, 
            lambda: self.model.generate_content(
                contents=prompt,
                generation_config=config
            )
        )
    
    def _extract_json_from_response(self, response_text: str) -> Optional[str]:
        """Try to extract JSON from malformed response"""
        
        # Look for JSON object boundaries
        start_idx = response_text.find('{')
        if start_idx == -1:
            return None
            
        # Find matching closing brace
        brace_count = 0
        end_idx = -1
        
        for i, char in enumerate(response_text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        
        if end_idx != -1:
            return response_text[start_idx:end_idx + 1]
        
        return None
    
    def get_client_stats(self) -> Dict[str, Any]:
        """Get client usage statistics"""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "model": GEMINI_CONFIG["model"],
            "rate_limit": GEMINI_CONFIG["rate_limit"],
            "thinking_mode_enabled": self.enable_thinking,
            "token_limits": "REMOVED - using system defaults"
        }
    
    def set_thinking_mode(self, enabled: bool):
        """Dynamically enable/disable thinking mode"""
        
        self.enable_thinking = enabled
        logging.info(f"Thinking mode {'enabled' if enabled else 'disabled'}")
    
    async def generate_with_stage_optimization(self, prompt: str, stage_name: str, temperature: float = 0.1, paper_id: str = "unknown") -> Dict[str, Any]:
        """Generate content with maximum thinking for all stages and comprehensive tracking"""
        
        # Enable maximum thinking for ALL stages - quality over speed
        enable_thinking = True
        
        logging.debug(f"Using maximum thinking mode for stage: {stage_name}")
        
        return await self.generate_json_content(
            prompt=prompt,
            temperature=temperature,
            enable_thinking_for_stage=enable_thinking,
            stage_name=stage_name,
            paper_id=paper_id
        )
    
    def save_usage_analytics(self):
        """Save comprehensive usage analytics at end of processing"""
        return self.tracker.save_summary()

# Enhanced factory function for easy integration
def create_thinking_gemini_client(api_key: str, enable_thinking: bool = True) -> GeminiClient:
    """Factory function to create Gemini client with thinking mode"""
    
    return GeminiClient(api_key=api_key, enable_thinking=enable_thinking)