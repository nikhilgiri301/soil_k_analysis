"""
Configuration management for Soil K Analysis Synthesis Engine
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

# Default configuration values
DEFAULT_CONFIG = {
    "gemini_config": {
        "model": "gemini-2.0-flash-exp",
        "api_version": "v1",
        "rate_limit": 5,
        "max_tokens": 8192,
        "retry_attempts": 3,
        "timeout_seconds": 120
    },
    "stage_temperatures": {
        "stage_1a_generic_extraction": 0.1,
        "stage_1b_generic_validation": 0.05,
        "stage_2a_soilk_extraction": 0.15,
        "stage_2b_soilk_validation": 0.05,
        "stage_3a_paper_synthesis": 0.25,
        "stage_3b_synthesis_validation": 0.0,
        "stage_4a_client_mapping": 0.1,
        "stage_4b_mapping_validation": 0.0,
        "stage_5a_iterative_integration": 0.2,
        "stage_5b_integration_validation": 0.0
    },
    "file_paths": {
        "source_pdfs": "1_source_pdfs",
        "processed_data": "2_processed_data",
        "synthesis_ready": "3_synthesis_ready",
        "scripts": "4_scripts",
        "synthesis_engine": "6_synthesis_engine",
        "client_architecture": "7_client_architecture",
        "stage_outputs": "8_stage_outputs",
        "final_synthesis": "9_final_synthesis",
        "query_system": "10_query_system",
        "validation_logs": "11_validation_logs",
        "prompts": "6_synthesis_engine/prompts"
    }
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults"""
    
    if config_path is None:
        config_path = "6_synthesis_engine/config.json"
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults for any missing keys
            merged_config = _merge_configs(DEFAULT_CONFIG, config)
            return merged_config
        else:
            logging.warning(f"Config file not found: {config_path}. Using defaults.")
            return DEFAULT_CONFIG.copy()
            
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}. Using defaults.")
        return DEFAULT_CONFIG.copy()

def _merge_configs(default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
    """Merge custom config with defaults"""
    
    merged = default.copy()
    
    for key, value in custom.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged

def setup_logging(config: Dict[str, Any]):
    """Setup logging configuration"""
    
    logging_config = config.get("logging_config", {})
    
    log_level = logging_config.get("log_level", "INFO")
    log_file = logging_config.get("log_file", "11_validation_logs/synthesis_engine.log")
    log_format = logging_config.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    handlers = []
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {str(e)}")
    
    # Console handler
    if logging_config.get("enable_console_logging", True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        format=log_format
    )

# Load configuration on import
_config = load_config()

# Export commonly used configuration sections
GEMINI_CONFIG = _config.get("gemini_config", DEFAULT_CONFIG["gemini_config"])
STAGE_TEMPERATURES = _config.get("stage_temperatures", DEFAULT_CONFIG["stage_temperatures"])
PATHS = _config.get("file_paths", DEFAULT_CONFIG["file_paths"])

# Additional configuration sections
PROCESSING_CONFIG = _config.get("processing_config", {
    "max_concurrent_papers": 3,
    "batch_size": 5,
    "enable_parallel_processing": True,
    "checkpoint_frequency": 5,
    "auto_retry_failed": True,
    "save_intermediate_results": True
})

VALIDATION_CONFIG = _config.get("validation_config", {
    "enable_quality_validation": True,
    "enable_confidence_scoring": True,
    "minimum_quality_threshold": 0.6,
    "require_citation_traceability": True,
    "conservative_confidence_bias": True
})

ERROR_HANDLING_CONFIG = _config.get("error_handling", {
    "max_retry_attempts": 3,
    "retry_delay_seconds": 2,
    "escalate_after_failures": 5,
    "save_error_outputs": True,
    "continue_on_single_failure": True,
    "graceful_degradation": True
})

OUTPUT_CONFIG = _config.get("output_config", {
    "save_stage_outputs": True,
    "compress_large_outputs": False,
    "include_debug_info": True,
    "generate_audit_trail": True,
    "format_outputs_for_client": True,
    "include_confidence_metadata": True
})

# Business context configuration
BUSINESS_CONTEXT = _config.get("business_context", {
    "decision_timeframe": "2_7_years",
    "capital_allocation_focus": True,
    "risk_tolerance": "conservative",
    "uncertainty_preference": "explicit_over_hidden",
    "transparency_priority": "high"
})

# Parameter priorities
PARAMETER_PRIORITIES = _config.get("parameter_priorities", {
    "critical_parameters": [
        "annual_kg_k2o_per_ha",
        "sustainability_years", 
        "depletion_rate"
    ],
    "important_parameters": [
        "recovery_potential",
        "seasonal_patterns",
        "irrigation_effects"
    ],
    "secondary_parameters": [
        "clay_mineral_effects",
        "organic_matter_contributions",
        "crop_system_variations"
    ]
})

# Geographic regions configuration
GEOGRAPHIC_CONFIG = _config.get("geographic_regions", {
    "priority_regions": ["china", "india", "brazil", "usa"],
    "secondary_regions": ["iran", "europe", "australia"],
    "region_confidence_adjustments": True,
    "require_regional_validation": False
})

# Quality thresholds
QUALITY_THRESHOLDS = _config.get("quality_thresholds", {
    "minimum_study_duration_months": 6,
    "minimum_sample_size": 10,
    "require_statistical_analysis": True,
    "require_methodology_description": True,
    "require_uncertainty_quantification": False
})

def get_config() -> Dict[str, Any]:
    """Get the complete configuration"""
    return _config.copy()

def update_config(new_config: Dict[str, Any]):
    """Update configuration at runtime"""
    global _config, GEMINI_CONFIG, STAGE_TEMPERATURES, PATHS
    
    _config = _merge_configs(_config, new_config)
    
    # Update exported sections
    GEMINI_CONFIG.update(_config.get("gemini_config", {}))
    STAGE_TEMPERATURES.update(_config.get("stage_temperatures", {}))
    PATHS.update(_config.get("file_paths", {}))

def save_config(config_path: str = None):
    """Save current configuration to file"""
    
    if config_path is None:
        config_path = "6_synthesis_engine/config.json"
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(_config, f, indent=2)
            
        logging.info(f"Configuration saved to {config_path}")
        
    except Exception as e:
        logging.error(f"Failed to save configuration: {str(e)}")

def validate_config() -> bool:
    """Validate configuration for required fields"""
    
    required_sections = ["gemini_config", "stage_temperatures", "file_paths"]
    
    for section in required_sections:
        if section not in _config:
            logging.error(f"Missing required config section: {section}")
            return False
    
    # Validate Gemini config
    gemini_required = ["model", "rate_limit", "max_tokens", "retry_attempts"]
    for field in gemini_required:
        if field not in GEMINI_CONFIG:
            logging.error(f"Missing required Gemini config field: {field}")
            return False
    
    # Validate stage temperatures
    required_stages = [
        "stage_1a_generic_extraction",
        "stage_1b_generic_validation",
        "stage_2a_soilk_extraction",
        "stage_2b_soilk_validation",
        "stage_3a_paper_synthesis",
        "stage_3b_synthesis_validation",
        "stage_4a_client_mapping",
        "stage_4b_mapping_validation",
        "stage_5a_iterative_integration",
        "stage_5b_integration_validation"
    ]
    
    for stage in required_stages:
        if stage not in STAGE_TEMPERATURES:
            logging.warning(f"Missing temperature config for stage: {stage}")
    
    # Validate paths
    required_paths = ["synthesis_ready", "client_architecture", "stage_outputs", "prompts"]
    for path_key in required_paths:
        if path_key not in PATHS:
            logging.error(f"Missing required path config: {path_key}")
            return False
    
    logging.info("Configuration validation passed")
    return True

def get_stage_temperature(stage_name: str) -> float:
    """Get temperature for specific stage"""
    return STAGE_TEMPERATURES.get(stage_name, 0.1)  # Default conservative temperature

def get_path(path_key: str) -> str:
    """Get path for specific component"""
    return PATHS.get(path_key, "")

def is_critical_parameter(parameter_name: str) -> bool:
    """Check if parameter is critical for business decisions"""
    return parameter_name in PARAMETER_PRIORITIES["critical_parameters"]

def get_regional_priority(region_name: str) -> str:
    """Get priority level for geographic region"""
    if region_name.lower() in [r.lower() for r in GEOGRAPHIC_CONFIG["priority_regions"]]:
        return "priority"
    elif region_name.lower() in [r.lower() for r in GEOGRAPHIC_CONFIG["secondary_regions"]]:
        return "secondary"
    else:
        return "other"

# Initialize logging if this module is imported
if __name__ != "__main__":
    setup_logging(_config)