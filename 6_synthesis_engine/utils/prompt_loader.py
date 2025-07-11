"""
Prompt Loader for Soil K Analysis Synthesis Engine
Manages file-based prompt system for all 10 AI synthesis stages
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class PromptLoader:
    """File-based prompt management system for 10-pass synthesis"""
    
    def __init__(self, prompts_directory: str = "6_synthesis_engine/prompts"):
        self.prompts_dir = prompts_directory
        self.loaded_prompts = {}
        self.prompt_cache = {}
        
        # Define expected prompt files
        self.prompt_files = {
            "stage_1a_generic_extraction": "stage_1a_generic_extraction.txt",
            "stage_1b_generic_validation": "stage_1b_generic_validation.txt",
            "stage_2a_soilk_extraction": "stage_2a_soilk_extraction.txt",
            "stage_2b_soilk_validation": "stage_2b_soilk_validation.txt",
            "stage_3a_paper_synthesis": "stage_3a_paper_synthesis.txt",
            "stage_3b_synthesis_validation": "stage_3b_synthesis_validation.txt",
            "stage_4a_client_mapping": "stage_4a_client_mapping.txt",
            "stage_4b_mapping_validation": "stage_4b_mapping_validation.txt",
            # Gold Standard Architecture - Stage 5A Chunk Synthesis
            "stage_5a_regional_synthesis": "stage_5/stage_5a_regional_synthesis.txt",
            "stage_5a_temporal_synthesis": "stage_5/stage_5a_temporal_synthesis.txt", 
            "stage_5a_crop_specific_synthesis": "stage_5/stage_5a_crop_specific_synthesis.txt",
            "stage_5a_crop_uptake_synthesis": "stage_5/stage_5a_crop_uptake_synthesis.txt",
            "stage_5a_manure_cycling_synthesis": "stage_5/stage_5a_manure_cycling_synthesis.txt",
            "stage_5a_residue_cycling_synthesis": "stage_5/stage_5a_residue_cycling_synthesis.txt",
            # Gold Standard Architecture - Stage 5B Chunk Validation
            "stage_5b_regional_validation": "stage_5/stage_5b_regional_validation.txt",
            "stage_5b_temporal_validation": "stage_5/stage_5b_temporal_validation.txt",
            "stage_5b_crop_specific_validation": "stage_5/stage_5b_crop_specific_validation.txt",
            "stage_5b_crop_uptake_validation": "stage_5/stage_5b_crop_uptake_validation.txt",
            "stage_5b_manure_cycling_validation": "stage_5/stage_5b_manure_cycling_validation.txt",
            "stage_5b_residue_cycling_validation": "stage_5/stage_5b_residue_cycling_validation.txt",
            # Gold Standard Architecture - Stage 6 Cross-Chunk Integration
            "stage_6a_cross_chunk_integration": "stage_6/stage_6a_cross_chunk_integration.txt",
            "stage_6b_integration_validation": "stage_6/stage_6b_integration_validation.txt",
            # Gold Standard Architecture - Stage 7 Scientific Distillation
            "stage_7a_scientific_distillation": "stage_7/stage_7a_scientific_distillation.txt",
            "stage_7b_distillation_validation": "stage_7/stage_7b_distillation_validation.txt"
        }
        
        # Validate prompts directory
        self._validate_prompts_directory()
        
        logging.info(f"PromptLoader initialized with {len(self.prompt_files)} expected prompts")
    
    def _validate_prompts_directory(self):
        """Validate that prompts directory exists and is accessible"""
        
        if not os.path.exists(self.prompts_dir):
            logging.warning(f"Prompts directory does not exist: {self.prompts_dir}")
            try:
                os.makedirs(self.prompts_dir, exist_ok=True)
                logging.info(f"Created prompts directory: {self.prompts_dir}")
            except Exception as e:
                logging.error(f"Could not create prompts directory: {str(e)}")
                raise
        
        if not os.path.isdir(self.prompts_dir):
            raise ValueError(f"Prompts path is not a directory: {self.prompts_dir}")
    
    def load_prompt(self, stage_name: str) -> str:
        """Load prompt for specific stage"""
        
        # Check cache first
        if stage_name in self.prompt_cache:
            return self.prompt_cache[stage_name]
        
        # Get filename for stage
        if stage_name not in self.prompt_files:
            raise ValueError(f"Unknown stage name: {stage_name}")
        
        filename = self.prompt_files[stage_name]
        filepath = os.path.join(self.prompts_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
            
            if not prompt_content:
                raise ValueError(f"Empty prompt file: {filename}")
            
            # Cache the prompt
            self.prompt_cache[stage_name] = prompt_content
            
            logging.debug(f"Loaded prompt for {stage_name} ({len(prompt_content)} characters)")
            return prompt_content
            
        except FileNotFoundError:
            error_msg = f"Prompt file not found: {filepath}"
            logging.error(error_msg)
            
            # Create placeholder prompt file for development
            placeholder_prompt = self._create_placeholder_prompt(stage_name)
            self._save_placeholder_prompt(filepath, placeholder_prompt)
            
            return placeholder_prompt
            
        except Exception as e:
            error_msg = f"Error loading prompt {stage_name}: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
    
    def validate_all_prompts(self) -> Dict[str, bool]:
        """Validate that all required prompts exist and are loadable"""
        
        validation_results = {}
        
        for stage_name, filename in self.prompt_files.items():
            try:
                prompt = self.load_prompt(stage_name)
                
                # Basic validation
                if len(prompt) < 100:
                    logging.warning(f"Prompt {stage_name} seems very short ({len(prompt)} chars)")
                    validation_results[stage_name] = False
                elif "placeholder" in prompt.lower():
                    logging.warning(f"Prompt {stage_name} appears to be a placeholder")
                    validation_results[stage_name] = False
                else:
                    validation_results[stage_name] = True
                    
            except Exception as e:
                logging.error(f"Validation failed for {stage_name}: {str(e)}")
                validation_results[stage_name] = False
        
        successful = sum(1 for success in validation_results.values() if success)
        total = len(validation_results)
        
        logging.info(f"Prompt validation: {successful}/{total} prompts validated successfully")
        
        return validation_results
    
    def reload_prompt(self, stage_name: str) -> str:
        """Reload prompt from file (bypass cache)"""
        
        # Clear cache for this stage
        if stage_name in self.prompt_cache:
            del self.prompt_cache[stage_name]
        
        return self.load_prompt(stage_name)
    
    def reload_all_prompts(self):
        """Reload all prompts from files (clear cache)"""
        
        self.prompt_cache.clear()
        
        for stage_name in self.prompt_files:
            try:
                self.load_prompt(stage_name)
            except Exception as e:
                logging.error(f"Failed to reload prompt {stage_name}: {str(e)}")
    
    def get_prompt_info(self, stage_name: str) -> Dict[str, Any]:
        """Get information about a specific prompt"""
        
        if stage_name not in self.prompt_files:
            return {"error": f"Unknown stage: {stage_name}"}
        
        filename = self.prompt_files[stage_name]
        filepath = os.path.join(self.prompts_dir, filename)
        
        info = {
            "stage_name": stage_name,
            "filename": filename,
            "filepath": filepath,
            "exists": os.path.exists(filepath),
            "cached": stage_name in self.prompt_cache
        }
        
        if info["exists"]:
            try:
                stat = os.stat(filepath)
                info["size_bytes"] = stat.st_size
                info["modified_time"] = stat.st_mtime
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    info["content_length"] = len(content)
                    info["line_count"] = content.count('\n') + 1
                    
            except Exception as e:
                info["error"] = str(e)
        
        return info
    
    def list_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """List information about all prompts"""
        
        all_prompts_info = {}
        
        for stage_name in self.prompt_files:
            all_prompts_info[stage_name] = self.get_prompt_info(stage_name)
        
        return all_prompts_info
    
    def _create_placeholder_prompt(self, stage_name: str) -> str:
        """Create placeholder prompt for development"""
        
        stage_descriptions = {
            "stage_1a_generic_extraction": "Extract general paper information including methodology, findings, and metadata",
            "stage_1b_generic_validation": "Validate the generic extraction results for accuracy and completeness",
            "stage_2a_soilk_extraction": "Extract soil K specific data, parameters, and measurements",
            "stage_2b_soilk_validation": "Validate soil K extraction results for scientific accuracy",
            "stage_3a_paper_synthesis": "Synthesize generic and soil K extractions into comprehensive paper analysis",
            "stage_3b_synthesis_validation": "Validate the paper synthesis for coherence and accuracy",
            "stage_4a_client_mapping": "Map paper synthesis to client question architecture",
            "stage_4b_mapping_validation": "Validate client mapping for relevance and accuracy",
            "stage_5a_knowledge_synthesis": "Integrate paper mapping into evolving knowledge synthesis state",
            "stage_5b_final_validation": "Validate knowledge synthesis integration for coherence and quality"
        }
        
        description = stage_descriptions.get(stage_name, "Process the input data according to stage requirements")
        
        return f"""# PLACEHOLDER PROMPT FOR {stage_name.upper()}

## Objective
{description}

## Instructions
You are an AI assistant helping with soil K literature synthesis. This is a placeholder prompt that needs to be replaced with the actual detailed prompt for this stage.

## Input Format
Analyze the provided input data according to the stage requirements.

## Output Format
Return a JSON object with the analysis results appropriate for this stage.

## Important Notes
- This is a PLACEHOLDER prompt for development purposes
- Replace with actual detailed prompt before production use
- Maintain JSON output format for system compatibility

## Processing Steps
1. Analyze the input data
2. Extract relevant information
3. Format results as JSON
4. Ensure all required fields are present

Please analyze the input and provide appropriate results for {stage_name}."""
    
    def _save_placeholder_prompt(self, filepath: str, prompt_content: str):
        """Save placeholder prompt to file for development"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(prompt_content)
            
            logging.info(f"Created placeholder prompt: {filepath}")
            
        except Exception as e:
            logging.error(f"Could not save placeholder prompt {filepath}: {str(e)}")
    
    def create_all_placeholder_prompts(self):
        """Create placeholder prompts for all missing stages (development helper)"""
        
        created_count = 0
        
        for stage_name, filename in self.prompt_files.items():
            filepath = os.path.join(self.prompts_dir, filename)
            
            if not os.path.exists(filepath):
                try:
                    placeholder = self._create_placeholder_prompt(stage_name)
                    self._save_placeholder_prompt(filepath, placeholder)
                    created_count += 1
                except Exception as e:
                    logging.error(f"Failed to create placeholder for {stage_name}: {str(e)}")
        
        logging.info(f"Created {created_count} placeholder prompt files")
        return created_count
    
    def validate_prompt_formatting(self, stage_name: str) -> Dict[str, Any]:
        """Validate prompt formatting and structure"""
        
        try:
            prompt = self.load_prompt(stage_name)
            
            validation_result = {
                "stage_name": stage_name,
                "length_ok": len(prompt) >= 100,
                "has_instructions": "instructions" in prompt.lower(),
                "has_format_specification": "format" in prompt.lower() or "json" in prompt.lower(),
                "has_objective": "objective" in prompt.lower() or "purpose" in prompt.lower(),
                "appears_complete": "placeholder" not in prompt.lower(),
                "character_count": len(prompt),
                "line_count": prompt.count('\n') + 1,
                "validation_passed": True
            }
            
            # Check for common issues
            issues = []
            
            if validation_result["character_count"] < 200:
                issues.append("Prompt seems very short")
                validation_result["validation_passed"] = False
            
            if not validation_result["has_format_specification"]:
                issues.append("No clear output format specification")
            
            if not validation_result["appears_complete"]:
                issues.append("Appears to be placeholder prompt")
                validation_result["validation_passed"] = False
            
            validation_result["issues"] = issues
            
            return validation_result
            
        except Exception as e:
            return {
                "stage_name": stage_name,
                "validation_passed": False,
                "error": str(e)
            }
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get prompt cache status"""
        
        return {
            "cached_prompts": list(self.prompt_cache.keys()),
            "cache_size": len(self.prompt_cache),
            "total_prompts": len(self.prompt_files),
            "cache_hit_rate": len(self.prompt_cache) / len(self.prompt_files) if self.prompt_files else 0
        }
    
    def clear_cache(self):
        """Clear prompt cache"""
        
        cache_size = len(self.prompt_cache)
        self.prompt_cache.clear()
        
        logging.info(f"Cleared prompt cache ({cache_size} prompts)")
    
    def export_prompts_info(self) -> Dict[str, Any]:
        """Export comprehensive information about all prompts"""
        
        return {
            "prompts_directory": self.prompts_dir,
            "total_prompt_files": len(self.prompt_files),
            "validation_results": self.validate_all_prompts(),
            "individual_prompt_info": self.list_all_prompts(),
            "cache_status": self.get_cache_status(),
            "export_timestamp": str(Path(self.prompts_dir).stat().st_mtime) if os.path.exists(self.prompts_dir) else None
        }

# Utility functions for standalone usage
def validate_prompts_directory(prompts_dir: str = "6_synthesis_engine/prompts") -> bool:
    """Standalone function to validate prompts directory"""
    
    try:
        loader = PromptLoader(prompts_dir)
        validation_results = loader.validate_all_prompts()
        
        success_count = sum(1 for success in validation_results.values() if success)
        total_count = len(validation_results)
        
        print(f"Prompts validation: {success_count}/{total_count} prompts valid")
        
        for stage_name, is_valid in validation_results.items():
            status = "✅" if is_valid else "❌"
            print(f"  {status} {stage_name}")
        
        return success_count == total_count
        
    except Exception as e:
        print(f"Error validating prompts: {str(e)}")
        return False

def create_development_prompts(prompts_dir: str = "6_synthesis_engine/prompts") -> int:
    """Standalone function to create placeholder prompts for development"""
    
    try:
        loader = PromptLoader(prompts_dir)
        created_count = loader.create_all_placeholder_prompts()
        
        print(f"Created {created_count} placeholder prompt files in {prompts_dir}")
        return created_count
        
    except Exception as e:
        print(f"Error creating development prompts: {str(e)}")
        return 0

if __name__ == "__main__":
    # Development helper - create placeholder prompts
    print("Creating development placeholder prompts...")
    created = create_development_prompts()
    
    print("Validating prompts...")
    validate_prompts_directory()