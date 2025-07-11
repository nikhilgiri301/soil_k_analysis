"""
JSON-based configuration management for Soil K Analysis Synthesis Engine
Replaces config.py to use config.json as single source of truth
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    
    if config_path is None:
        config_path = "6_synthesis_engine/config.json"
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        else:
            logging.warning(f"Config file not found: {config_path}")
            return {}
            
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        return {}

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
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
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

def get_stage_temperature(config: Dict[str, Any], stage_name: str) -> float:
    """Get temperature for specific stage"""
    stage_temperatures = config.get("stage_temperatures", {})
    return stage_temperatures.get(stage_name, 0.1)  # Default conservative temperature

def get_path(config: Dict[str, Any], path_key: str) -> str:
    """Get path for specific component"""
    file_paths = config.get("file_paths", {})
    return file_paths.get(path_key, "")

# Load configuration on import for convenience
_config = load_config()

# Export commonly used configuration sections for backward compatibility
GEMINI_CONFIG = _config.get("gemini_config", {})
STAGE_TEMPERATURES = _config.get("stage_temperatures", {})
PATHS = _config.get("file_paths", {})
PROCESSING_CONFIG = _config.get("processing_config", {})
VALIDATION_CONFIG = _config.get("validation_config", {})
ERROR_HANDLING_CONFIG = _config.get("error_handling", {})
OUTPUT_CONFIG = _config.get("output_config", {})
LOGGING_CONFIG = _config.get("logging_config", {})
CLIENT_SPECIFIC_CONFIG = _config.get("client_specific_config", {})
SYNTHESIS_PARAMETERS = _config.get("synthesis_parameters", {})
THINKING_OPTIMIZATION = _config.get("thinking_optimization", {})
SYSTEM_CONFIG = _config.get("system_config", {})

def get_config() -> Dict[str, Any]:
    """Get the complete configuration"""
    return _config.copy()

def update_config(new_config: Dict[str, Any]):
    """Update configuration at runtime"""
    global _config, GEMINI_CONFIG, STAGE_TEMPERATURES, PATHS
    global PROCESSING_CONFIG, VALIDATION_CONFIG, ERROR_HANDLING_CONFIG
    global OUTPUT_CONFIG, LOGGING_CONFIG, CLIENT_SPECIFIC_CONFIG
    global SYNTHESIS_PARAMETERS, THINKING_OPTIMIZATION, SYSTEM_CONFIG
    
    _config.update(new_config)
    
    # Update exported sections
    GEMINI_CONFIG.update(_config.get("gemini_config", {}))
    STAGE_TEMPERATURES.update(_config.get("stage_temperatures", {}))
    PATHS.update(_config.get("file_paths", {}))
    PROCESSING_CONFIG.update(_config.get("processing_config", {}))
    VALIDATION_CONFIG.update(_config.get("validation_config", {}))
    ERROR_HANDLING_CONFIG.update(_config.get("error_handling", {}))
    OUTPUT_CONFIG.update(_config.get("output_config", {}))
    LOGGING_CONFIG.update(_config.get("logging_config", {}))
    CLIENT_SPECIFIC_CONFIG.update(_config.get("client_specific_config", {}))
    SYNTHESIS_PARAMETERS.update(_config.get("synthesis_parameters", {}))
    THINKING_OPTIMIZATION.update(_config.get("thinking_optimization", {}))
    SYSTEM_CONFIG.update(_config.get("system_config", {}))

# Initialize logging if this module is imported
if __name__ != "__main__":
    setup_logging(_config)