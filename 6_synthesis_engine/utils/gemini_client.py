"""
Enhanced Gemini API client with thinking mode support for complex literature synthesis
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import GenerateContentConfig, ThinkingConfig
from .config import GEMINI_CONFIG
import time

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
        
        # Thinking configuration for complex tasks
        self.thinking_config = ThinkingConfig(
            thinking_budget=-1  # Unlimited thinking for quality
        ) if enable_thinking else None
        
        logging.info(f"GeminiClient initialized with model: {GEMINI_CONFIG['model']}")
        logging.info(f"Thinking mode: {'enabled' if enable_thinking else 'disabled'}")
        
    async def generate_json_content(self, prompt: str, temperature: float = 0.1, 
                                   max_retries: int = None, 
                                   enable_thinking_for_stage: bool = None) -> Dict[str, Any]:
        """Generate JSON content with thinking mode and error handling"""
        
        if max_retries is None:
            max_retries = GEMINI_CONFIG.get("retry_attempts", 3)
        
        # Determine if thinking should be used for this specific call
        use_thinking = enable_thinking_for_stage if enable_thinking_for_stage is not None else self.enable_thinking
        
        async with self.rate_limiter:
            
            for attempt in range(max_retries + 1):
                try:
                    self.request_count += 1
                    
                    # Enhanced prompt to ensure JSON output
                    enhanced_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just the JSON object."
                    
                    # Configure generation with thinking mode if enabled
                    if use_thinking and self.thinking_config:
                        generation_config = GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=GEMINI_CONFIG.get("max_tokens", 8192),
                            response_mime_type="application/json",
                            thinking_config=self.thinking_config
                        )
                        
                        logging.debug(f"Using thinking mode for complex reasoning (temperature: {temperature})")
                    else:
                        generation_config = GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=GEMINI_CONFIG.get("max_tokens", 8192),
                            response_mime_type="application/json"
                        )
                    
                    # Generate content with enhanced API
                    response = await asyncio.wait_for(
                        self._generate_async_enhanced(enhanced_prompt, generation_config),
                        timeout=GEMINI_CONFIG.get("timeout", 120)  # Longer timeout for thinking mode
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
                                'thinking_used': True,
                                'thinking_length': len(response.thinking_text),
                                'thinking_preview': response.thinking_text[:200] + "..." if len(response.thinking_text) > 200 else response.thinking_text
                            }
                        
                        logging.debug(f"Successful API call #{self.request_count}, temperature: {temperature}, thinking: {use_thinking}")
                        return result
                        
                    except json.JSONDecodeError as e:
                        logging.warning(f"JSON parsing failed (attempt {attempt + 1}): {str(e)}")
                        
                        # Try to extract JSON from response
                        cleaned_response = self._extract_json_from_response(response_text)
                        if cleaned_response:
                            try:
                                result = json.loads(cleaned_response)
                                if use_thinking:
                                    result['_thinking_metadata'] = {'thinking_used': True, 'json_extraction_applied': True}
                                return result
                            except json.JSONDecodeError:
                                pass
                        
                        if attempt == max_retries:
                            self.error_count += 1
                            return {
                                "error": "json_parse_error",
                                "raw_response": response_text[:1000],
                                "parse_error": str(e),
                                "attempt": attempt + 1,
                                "thinking_enabled": use_thinking
                            }
                            
                except asyncio.TimeoutError:
                    logging.error(f"API timeout (attempt {attempt + 1}) - thinking mode may need more time")
                    if attempt == max_retries:
                        self.error_count += 1
                        return {"error": "timeout", "attempt": attempt + 1, "thinking_enabled": use_thinking}
                        
                except Exception as e:
                    logging.error(f"API error (attempt {attempt + 1}): {str(e)}")
                    if attempt == max_retries:
                        self.error_count += 1
                        return {"error": str(e), "attempt": attempt + 1, "thinking_enabled": use_thinking}
                
                # Wait before retry with exponential backoff
                if attempt < max_retries:
                    wait_time = GEMINI_CONFIG.get("retry_delay", 2) * (2 ** attempt)
                    logging.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
            
            return {"error": "max_retries_exceeded", "thinking_enabled": use_thinking}
    
    async def _generate_async_enhanced(self, prompt: str, config: GenerateContentConfig):
        """Enhanced async wrapper for Gemini generation with thinking mode"""
        loop = asyncio.get_event_loop()
        
        # Use the enhanced API structure
        return await loop.run_in_executor(
            None, 
            lambda: self.client.GenerativeModel(GEMINI_CONFIG["model"]).generate_content(
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
            "thinking_mode_enabled": self.enable_thinking
        }
    
    def set_thinking_mode(self, enabled: bool, thinking_budget: int = -1):
        """Dynamically enable/disable thinking mode"""
        
        self.enable_thinking = enabled
        if enabled:
            self.thinking_config = ThinkingConfig(thinking_budget=thinking_budget)
            logging.info(f"Thinking mode enabled with budget: {thinking_budget}")
        else:
            self.thinking_config = None
            logging.info("Thinking mode disabled")
    
    async def generate_with_stage_optimization(self, prompt: str, stage_name: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Generate content with maximum thinking for all stages"""
        
        # Enable maximum thinking for ALL stages - quality over speed
        enable_thinking = True
        
        logging.debug(f"Using maximum thinking mode for stage: {stage_name}")
        
        return await self.generate_json_content(
            prompt=prompt,
            temperature=temperature,
            enable_thinking_for_stage=enable_thinking
        )

# Enhanced factory function for easy integration
def create_thinking_gemini_client(api_key: str, enable_thinking: bool = True) -> GeminiClient:
    """Factory function to create Gemini client with thinking mode"""
    
    return GeminiClient(api_key=api_key, enable_thinking=enable_thinking)