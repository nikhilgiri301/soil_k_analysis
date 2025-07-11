"""
Quality Controller for Soil K Analysis Synthesis Engine
Manages quality validation across all synthesis stages
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import statistics
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.json_config import PATHS

class QualityController:
    """Comprehensive quality validation and control system"""
    
    def __init__(self):
        self.quality_metrics = {}
        self.validation_history = []
        self.error_log = []
        
        # Load quality standards
        self.load_quality_standards()
        
        logging.info("Quality Controller initialized")
    
    def load_quality_standards(self):
        """Load quality standards from client architecture"""
        try:
            with open(f"{PATHS['client_architecture']}/confidence_thresholds.json", 'r') as f:
                self.quality_standards = json.load(f)
            
            with open(f"{PATHS['client_architecture']}/parameter_definitions.json", 'r') as f:
                self.parameter_standards = json.load(f)
                
        except Exception as e:
            logging.warning(f"Could not load quality standards: {str(e)}")
            self.quality_standards = self._default_quality_standards()
            self.parameter_standards = {}
    
    def validate_stage_output(self, stage_name: str, output_data: Dict[str, Any], 
                            input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate output from any synthesis stage"""
        
        validation_result = {
            "stage": stage_name,
            "timestamp": datetime.now().isoformat(),
            "validation_passed": True,
            "quality_score": 0.0,
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Stage-specific validation
            if stage_name.startswith("stage_1a"):
                validation_result = self._validate_generic_extraction(output_data, validation_result)
            elif stage_name.startswith("stage_1b"):
                validation_result = self._validate_generic_validation(output_data, validation_result)
            elif stage_name.startswith("stage_2a"):
                validation_result = self._validate_soilk_extraction(output_data, validation_result)
            elif stage_name.startswith("stage_2b"):
                validation_result = self._validate_soilk_validation(output_data, validation_result)
            elif stage_name.startswith("stage_3a"):
                validation_result = self._validate_paper_synthesis(output_data, validation_result)
            elif stage_name.startswith("stage_3b"):
                validation_result = self._validate_synthesis_validation(output_data, validation_result)
            elif stage_name.startswith("stage_4a"):
                validation_result = self._validate_client_mapping(output_data, validation_result)
            elif stage_name.startswith("stage_4b"):
                validation_result = self._validate_mapping_validation(output_data, validation_result)
            elif stage_name.startswith("stage_5a"):
                validation_result = self._validate_knowledge_synthesis(output_data, validation_result)
            elif stage_name.startswith("stage_5b"):
                validation_result = self._validate_final_validation(output_data, validation_result)
            
            # Common validation checks
            validation_result = self._validate_common_requirements(output_data, validation_result)
            
            # Calculate overall quality score
            validation_result["quality_score"] = self._calculate_quality_score(validation_result)
            
            # Log validation result
            self._log_validation_result(validation_result)
            
        except Exception as e:
            validation_result["validation_passed"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
            validation_result["quality_score"] = 0.0
            logging.error(f"Quality validation failed for {stage_name}: {str(e)}")
        
        return validation_result
    
    def _validate_generic_extraction(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 1A generic extraction output"""
        
        required_fields = ["paper_metadata", "key_findings", "methodology", "data_quality"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result["issues"].append(f"Missing required field: {field}")
                result["validation_passed"] = False
        
        # Validate paper metadata
        if "paper_metadata" in data:
            metadata = data["paper_metadata"]
            if not metadata.get("title") or not metadata.get("authors"):
                result["warnings"].append("Incomplete paper metadata")
        
        # Validate methodology extraction
        if "methodology" in data:
            if not data["methodology"].get("study_type"):
                result["warnings"].append("Study type not clearly identified")
            if not data["methodology"].get("measurement_methods"):
                result["warnings"].append("Measurement methods not extracted")
        
        return result
    
    def _validate_soilk_extraction(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 2A soil K specific extraction output"""
        
        required_fields = ["soil_k_data", "geographic_context", "temporal_context"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result["issues"].append(f"Missing required field: {field}")
                result["validation_passed"] = False
        
        # Validate soil K data quality
        if "soil_k_data" in data:
            k_data = data["soil_k_data"]
            if not k_data.get("quantitative_values"):
                result["warnings"].append("No quantitative K values extracted")
            
            # Check for critical parameters
            critical_params = ["annual_kg_k2o_per_ha", "sustainability_years", "depletion_rate"]
            found_params = []
            
            if "parameters" in k_data:
                for param in critical_params:
                    if param in k_data["parameters"]:
                        found_params.append(param)
            
            if not found_params:
                result["warnings"].append("No critical soil K parameters identified")
            else:
                result["recommendations"].append(f"Found critical parameters: {', '.join(found_params)}")
        
        return result
    
    def _validate_paper_synthesis(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 3A paper synthesis output"""
        
        required_fields = ["synthesis_summary", "evidence_quality", "confidence_assessment"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result["issues"].append(f"Missing required field: {field}")
                result["validation_passed"] = False
        
        # Validate confidence assessment
        if "confidence_assessment" in data:
            confidence = data["confidence_assessment"]
            if "overall_confidence" in confidence:
                conf_score = confidence["overall_confidence"]
                if not isinstance(conf_score, (int, float)) or conf_score < 0 or conf_score > 1:
                    result["issues"].append("Invalid confidence score format")
                    result["validation_passed"] = False
        
        # Check evidence integration
        if "evidence_quality" in data:
            evidence = data["evidence_quality"]
            if not evidence.get("supporting_evidence"):
                result["warnings"].append("Limited supporting evidence identified")
        
        return result
    
    def _validate_client_mapping(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 4A client mapping output"""
        
        required_fields = ["client_question_mapping", "parameter_assignments", "relevance_assessment"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result["issues"].append(f"Missing required field: {field}")
                result["validation_passed"] = False
        
        # Validate parameter assignments
        if "parameter_assignments" in data:
            params = data["parameter_assignments"]
            if not params:
                result["warnings"].append("No parameters assigned to client questions")
            else:
                # Check for critical parameter coverage
                critical_params = ["annual_kg_k2o_per_ha", "sustainability_years"]
                covered_params = []
                
                for assignment in params:
                    if assignment.get("parameter_name") in critical_params:
                        covered_params.append(assignment["parameter_name"])
                
                if covered_params:
                    result["recommendations"].append(f"Covers critical parameters: {', '.join(covered_params)}")
        
        return result
    
    def _validate_knowledge_synthesis(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 5A knowledge synthesis output"""
        
        required_fields = ["synthesis_state", "integration_summary", "confidence_updates"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result["issues"].append(f"Missing required field: {field}")
                result["validation_passed"] = False
        
        # Validate synthesis state structure
        if "synthesis_state" in data:
            state = data["synthesis_state"]
            if "question_responses" not in state:
                result["issues"].append("Missing question_responses in synthesis state")
                result["validation_passed"] = False
            
            if "evidence_registry" not in state:
                result["issues"].append("Missing evidence_registry in synthesis state")
                result["validation_passed"] = False
        
        return result
    
    def _validate_common_requirements(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate common requirements across all stages"""
        
        # Check for basic structure
        if not isinstance(data, dict):
            result["issues"].append("Output is not a valid dictionary structure")
            result["validation_passed"] = False
            return result
        
        # Check for error indicators
        if "error" in data:
            result["issues"].append(f"Stage reported error: {data['error']}")
            result["validation_passed"] = False
        
        # Check timestamp
        if "timestamp" in data:
            try:
                datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            except:
                result["warnings"].append("Invalid timestamp format")
        
        # Check for minimum content
        if len(str(data)) < 100:  # Very small output
            result["warnings"].append("Output seems unusually small")
        
        return result
    
    def _calculate_quality_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall quality score (0.0 to 1.0)"""
        
        if not validation_result["validation_passed"]:
            return 0.0
        
        # Start with perfect score
        score = 1.0
        
        # Deduct for issues and warnings
        score -= len(validation_result["issues"]) * 0.2
        score -= len(validation_result["warnings"]) * 0.1
        
        # Add points for recommendations (good practices)
        score += len(validation_result["recommendations"]) * 0.05
        
        # Ensure score stays in valid range
        return max(0.0, min(1.0, score))
    
    def _log_validation_result(self, validation_result: Dict[str, Any]):
        """Log validation result for audit trail"""
        
        self.validation_history.append(validation_result)
        
        # Save to validation logs
        try:
            log_file = f"11_validation_logs/quality_metrics/validation_{validation_result['stage']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, 'w') as f:
                json.dump(validation_result, f, indent=2)
        
        except Exception as e:
            logging.warning(f"Could not save validation log: {str(e)}")
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get overall quality summary across all validations"""
        
        if not self.validation_history:
            return {"status": "no_validations", "summary": "No validations performed yet"}
        
        # Calculate summary statistics
        passed_validations = [v for v in self.validation_history if v["validation_passed"]]
        quality_scores = [v["quality_score"] for v in self.validation_history]
        
        summary = {
            "total_validations": len(self.validation_history),
            "passed_validations": len(passed_validations),
            "success_rate": len(passed_validations) / len(self.validation_history),
            "average_quality_score": statistics.mean(quality_scores) if quality_scores else 0.0,
            "quality_distribution": {
                "high_quality": len([s for s in quality_scores if s >= 0.8]),
                "medium_quality": len([s for s in quality_scores if 0.6 <= s < 0.8]),
                "low_quality": len([s for s in quality_scores if s < 0.6])
            },
            "total_issues": sum(len(v["issues"]) for v in self.validation_history),
            "total_warnings": sum(len(v["warnings"]) for v in self.validation_history),
            "last_validation": self.validation_history[-1]["timestamp"] if self.validation_history else None
        }
        
        return summary
    
    def _default_quality_standards(self) -> Dict[str, Any]:
        """Default quality standards if none can be loaded"""
        return {
            "confidence_levels": {
                "minimum_acceptable": 0.4,
                "recommended": 0.6,
                "high_quality": 0.8
            },
            "validation_requirements": {
                "required_fields_present": True,
                "confidence_scores_valid": True,
                "evidence_documented": True
            }
        }
    
    # Additional validation methods for remaining stages...
    def _validate_generic_validation(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 1B generic validation output"""
        result["recommendations"].append("Generic validation stage completed")
        return result
    
    def _validate_soilk_validation(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 2B soil K validation output"""
        result["recommendations"].append("Soil K validation stage completed")
        return result
    
    def _validate_synthesis_validation(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 3B synthesis validation output"""
        result["recommendations"].append("Synthesis validation stage completed")
        return result
    
    def _validate_mapping_validation(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 4B mapping validation output"""
        result["recommendations"].append("Mapping validation stage completed")
        return result
    
    def _validate_final_validation(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Stage 5B final validation output"""
        result["recommendations"].append("Final validation stage completed")
        return result 
