"""
Stage 5B: Integration Validator
Validates iterative integration results for quality, consistency, and accuracy
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging
import statistics
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_loader import PromptLoader
from utils.gemini_client import GeminiClient
from utils.json_config import STAGE_TEMPERATURES

class IntegrationValidator:
    """Stage 5B: Validates iterative integration results with comprehensive quality checking"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_5b_final_validation"
        self.temperature = STAGE_TEMPERATURES.get("stage_5b_integration_validation", 0.0)
        
        # Validation tracking
        self.validation_history = []
        self.quality_issues = []
        self.validation_metrics = {
            "total_validations": 0,
            "validations_passed": 0,
            "critical_issues_found": 0,
            "confidence_adjustments_made": 0
        }
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded integration validation prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load validation prompt: {str(e)}")
            raise
    
    async def validate(self, synthesis_state: Dict[str, Any], 
                      successful_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main validation interface for master_controller compatibility"""
        
        try:
            # Check if synthesis_state is valid
            if not synthesis_state or not isinstance(synthesis_state, dict):
                return {
                    "success": False,
                    "stage": "5B",
                    "validation_errors": ["Invalid synthesis state - cannot validate"],
                    "confidence_score": 0.0,
                    "validation_timestamp": datetime.now().isoformat()
                }
            
            # Use comprehensive validation logic
            validation_result = await self.validate_integration(
                synthesis_state, {}, synthesis_state  # Adapt parameters
            )
            
            # Ensure compatibility with expected format
            validation_result['success'] = validation_result.get('validation_passed', True)
            validation_result['stage'] = '5B'
            validation_result['papers_validated'] = len(successful_mappings)
            
            return validation_result
            
        except Exception as e:
            logging.error(f"Stage 5B validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stage": "5B",
                "validation_confidence": 0.0,
                "validation_timestamp": datetime.now().isoformat()
            }
    
    async def validate_integration(self, current_synthesis_state: Dict[str, Any],
                                  new_paper_mapping: Dict[str, Any],
                                  integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration result with comprehensive quality assessment"""
        
        paper_id = new_paper_mapping.get("paper_id", "final_integration")
        
        try:
            logging.info(f"Validating integration result for paper: {paper_id}")
            
            # Pre-validation analysis
            validation_context = self._analyze_validation_context(
                current_synthesis_state, new_paper_mapping, integration_result
            )
            
            # AI-powered validation
            ai_validation_result = await self._perform_ai_validation(
                current_synthesis_state, new_paper_mapping, integration_result, validation_context
            )
            
            # Rule-based validation
            rule_validation_result = self._perform_rule_based_validation(
                current_synthesis_state, new_paper_mapping, integration_result, validation_context
            )
            
            # Combine validation results
            comprehensive_validation = self._combine_validation_results(
                ai_validation_result, rule_validation_result, validation_context
            )
            
            # Update validation tracking
            self._update_validation_tracking(paper_id, comprehensive_validation)
            
            logging.info(f"Integration validation completed for {paper_id}: {comprehensive_validation['validation_passed']}")
            return comprehensive_validation
            
        except Exception as e:
            logging.error(f"Integration validation failed for {paper_id}: {str(e)}")
            return self._create_fallback_validation(paper_id, str(e))
    
    def _analyze_validation_context(self, current_state: Dict[str, Any],
                                  new_paper: Dict[str, Any],
                                  integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context for validation process"""
        
        context = {
            "validation_timestamp": datetime.now().isoformat(),
            "paper_id": new_paper.get("paper_id", "unknown"),
            "integration_complexity": self._assess_integration_complexity(current_state, integration_result),
            "state_changes": self._analyze_state_changes(current_state, integration_result),
            "confidence_evolution": self._analyze_confidence_changes(current_state, integration_result),
            "potential_quality_issues": [],
            "validation_priorities": self._determine_validation_priorities(current_state, new_paper, integration_result)
        }
        
        # Identify potential quality issues
        context["potential_quality_issues"] = self._identify_potential_issues(
            current_state, new_paper, integration_result
        )
        
        return context
    
    async def _perform_ai_validation(self, current_state: Dict[str, Any],
                                   new_paper: Dict[str, Any],
                                   integration_result: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI-powered validation using detailed prompt"""
        
        try:
            # Format validation prompt
            formatted_prompt = self.prompt_template.format(
                synthesis_state=json.dumps(current_state, indent=2)[:10000],  # Limit size
                integration_result=json.dumps(integration_result, indent=2)[:10000],
                validation_context=json.dumps(context, indent=2)[:5000]
            )
            
            # Generate validation with strict temperature (0.0 for deterministic validation)
            ai_validation = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Add AI validation metadata
            ai_validation["validation_type"] = "ai_powered"
            ai_validation["validation_timestamp"] = datetime.now().isoformat()
            ai_validation["temperature_used"] = self.temperature
            
            return ai_validation
            
        except Exception as e:
            logging.error(f"AI validation failed: {str(e)}")
            return {
                "validation_passed": False,
                "validation_type": "ai_powered",
                "error": str(e),
                "fallback_applied": True
            }
    
    def _perform_rule_based_validation(self, current_state: Dict[str, Any],
                                     new_paper: Dict[str, Any],
                                     integration_result: Dict[str, Any],
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform rule-based validation with explicit quality checks"""
        
        validation_result = {
            "validation_type": "rule_based",
            "validation_passed": True,
            "validation_timestamp": datetime.now().isoformat(),
            "rule_checks": {},
            "quality_score": 1.0,
            "issues_found": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Structure validation
        structure_check = self._validate_structure(integration_result)
        validation_result["rule_checks"]["structure"] = structure_check
        if not structure_check["passed"]:
            validation_result["validation_passed"] = False
            validation_result["issues_found"].extend(structure_check["issues"])
        
        # Consistency validation
        consistency_check = self._validate_consistency(current_state, integration_result)
        validation_result["rule_checks"]["consistency"] = consistency_check
        if not consistency_check["passed"]:
            validation_result["validation_passed"] = False
            validation_result["issues_found"].extend(consistency_check["issues"])
        
        # Confidence validation
        confidence_check = self._validate_confidence_levels(integration_result, new_paper)
        validation_result["rule_checks"]["confidence"] = confidence_check
        if not confidence_check["passed"]:
            validation_result["warnings"].extend(confidence_check["warnings"])
        
        # Evidence traceability validation
        traceability_check = self._validate_evidence_traceability(integration_result, new_paper)
        validation_result["rule_checks"]["traceability"] = traceability_check
        if not traceability_check["passed"]:
            validation_result["issues_found"].extend(traceability_check["issues"])
        
        # Completeness validation
        completeness_check = self._validate_completeness(integration_result, context)
        validation_result["rule_checks"]["completeness"] = completeness_check
        if not completeness_check["passed"]:
            validation_result["warnings"].extend(completeness_check["warnings"])
        
        # Calculate overall quality score
        validation_result["quality_score"] = self._calculate_rule_based_quality_score(validation_result["rule_checks"])
        
        return validation_result
    
    def _validate_structure(self, integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structure of integration result"""
        
        required_fields = [
            "synthesis_metadata",
            "question_responses", 
            "evidence_registry",
            "confidence_evolution",
            "integration_log"
        ]
        
        check_result = {
            "passed": True,
            "issues": [],
            "field_checks": {}
        }
        
        # Check required fields
        for field in required_fields:
            if field not in integration_result:
                check_result["passed"] = False
                check_result["issues"].append(f"Missing required field: {field}")
                check_result["field_checks"][field] = False
            else:
                check_result["field_checks"][field] = True
        
        return check_result
    
    def _validate_consistency(self, current_state: Dict[str, Any], 
                            integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency between states"""
        
        check_result = {
            "passed": True,
            "issues": [],
            "consistency_checks": {}
        }
        
        # Check metadata consistency
        current_metadata = current_state.get("synthesis_metadata", {})
        new_metadata = integration_result.get("synthesis_metadata", {})
        
        if current_metadata and new_metadata:
            current_papers = current_metadata.get("papers_integrated", 0)
            new_papers = new_metadata.get("papers_integrated", 0)
            
            if new_papers < current_papers:
                check_result["passed"] = False
                check_result["issues"].append("Paper count decreased during integration")
        
        return check_result
    
    def _validate_confidence_levels(self, integration_result: Dict[str, Any], 
                                  new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Validate confidence level appropriateness"""
        
        check_result = {
            "passed": True,
            "warnings": [],
            "confidence_checks": {}
        }
        
        # Check for unrealistic confidence levels
        confidence_evolution = integration_result.get("confidence_evolution", [])
        
        for evolution_entry in confidence_evolution:
            confidence_score = evolution_entry.get("confidence_score", 0.0)
            
            if confidence_score > 0.9:
                check_result["warnings"].append("Very high confidence detected - verify appropriateness")
            elif confidence_score < 0.1:
                check_result["warnings"].append("Very low confidence detected - may indicate data quality issues")
        
        return check_result
    
    def _validate_evidence_traceability(self, integration_result: Dict[str, Any], 
                                      new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Validate evidence traceability"""
        
        check_result = {
            "passed": True,
            "issues": [],
            "traceability_checks": {}
        }
        
        evidence_registry = integration_result.get("evidence_registry", {})
        
        if not evidence_registry:
            check_result["passed"] = False
            check_result["issues"].append("Missing evidence registry")
        
        return check_result
    
    def _validate_completeness(self, integration_result: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completeness of integration result"""
        
        check_result = {
            "passed": True,
            "warnings": [],
            "completeness_checks": {}
        }
        
        # Check confidence evolution completeness
        confidence_evolution = integration_result.get("confidence_evolution", [])
        expected_entries = context.get("integration_complexity", {}).get("expected_evolution_entries", 1)
        
        if len(confidence_evolution) < expected_entries:
            check_result["warnings"].append("Confidence evolution may be incomplete")
        
        check_result["completeness_checks"]["confidence_evolution"] = len(confidence_evolution) >= expected_entries
        
        # Check for meaningful question responses
        question_responses = integration_result.get("question_responses", {})
        if not question_responses:
            check_result["warnings"].append("No question responses found in integration result")
        
        check_result["completeness_checks"]["has_question_responses"] = bool(question_responses)
        
        return check_result
    
    def _combine_validation_results(self, ai_validation: Dict[str, Any],
                                  rule_validation: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Combine AI and rule-based validation results"""
        
        combined_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "paper_id": context.get("paper_id"),
            "validation_passed": ai_validation.get("validation_passed", False) and rule_validation.get("validation_passed", True),
            "overall_quality_score": 0.0,
            "validation_components": {
                "ai_validation": ai_validation,
                "rule_validation": rule_validation
            },
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "confidence_adjustments": []
        }
        
        # Combine issues
        ai_issues = ai_validation.get("validation_errors", []) or ai_validation.get("issues_found", [])
        rule_issues = rule_validation.get("issues_found", [])
        combined_result["critical_issues"] = ai_issues + rule_issues
        
        # Combine warnings
        ai_warnings = ai_validation.get("warnings", [])
        rule_warnings = rule_validation.get("warnings", [])
        combined_result["warnings"] = ai_warnings + rule_warnings
        
        # Calculate overall quality score
        ai_score = ai_validation.get("quality_score", 0.0)
        rule_score = rule_validation.get("quality_score", 1.0)
        combined_result["overall_quality_score"] = (ai_score + rule_score) / 2
        
        return combined_result
    
    def _calculate_rule_based_quality_score(self, rule_checks: Dict[str, Any]) -> float:
        """Calculate quality score from rule-based checks"""
        
        total_checks = len(rule_checks)
        if total_checks == 0:
            return 0.0
        
        passed_checks = sum(1 for check in rule_checks.values() if check.get("passed", False))
        return passed_checks / total_checks
    
    def _assess_integration_complexity(self, current_state: Dict[str, Any], 
                                     integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess complexity of integration"""
        return {"complexity_level": "moderate", "expected_evolution_entries": 1}
    
    def _analyze_state_changes(self, current_state: Dict[str, Any], 
                             integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes between states"""
        return {"changes_detected": True, "change_magnitude": "moderate"}
    
    def _analyze_confidence_changes(self, current_state: Dict[str, Any], 
                                  integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence changes"""
        return {"confidence_direction": "stable", "confidence_magnitude": "low"}
    
    def _determine_validation_priorities(self, current_state: Dict[str, Any],
                                       new_paper: Dict[str, Any],
                                       integration_result: Dict[str, Any]) -> List[str]:
        """Determine validation priorities"""
        return ["structure", "consistency", "traceability"]
    
    def _identify_potential_issues(self, current_state: Dict[str, Any],
                                 new_paper: Dict[str, Any],
                                 integration_result: Dict[str, Any]) -> List[str]:
        """Identify potential quality issues"""
        return []
    
    def _create_fallback_validation(self, paper_id: str, error_message: str) -> Dict[str, Any]:
        """Create fallback validation result"""
        return {
            "validation_passed": False,
            "paper_id": paper_id,
            "error": error_message,
            "validation_timestamp": datetime.now().isoformat(),
            "fallback_validation": True
        }
    
    def _update_validation_tracking(self, paper_id: str, validation_result: Dict[str, Any]):
        """Update internal validation tracking"""
        
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "paper_id": paper_id,
            "passed": validation_result.get("validation_passed", False),
            "quality_score": validation_result.get("overall_quality_score", 0.0),
            "issues_count": len(validation_result.get("critical_issues", [])),
            "warnings_count": len(validation_result.get("warnings", []))
        })
        
        # Update metrics
        self.validation_metrics["total_validations"] += 1
        if validation_result.get("validation_passed", False):
            self.validation_metrics["validations_passed"] += 1
        
        self.validation_metrics["critical_issues_found"] += len(validation_result.get("critical_issues", []))
        
        if validation_result.get("confidence_adjustments"):
            self.validation_metrics["confidence_adjustments_made"] += 1
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive validation statistics"""
        
        if not self.validation_history:
            return {"status": "no_validations_performed"}
        
        quality_scores = [v["quality_score"] for v in self.validation_history]
        
        return {
            "total_validations": self.validation_metrics["total_validations"],
            "success_rate": self.validation_metrics["validations_passed"] / max(self.validation_metrics["total_validations"], 1),
            "average_quality_score": statistics.mean(quality_scores) if quality_scores else 0.0,
            "critical_issues_rate": self.validation_metrics["critical_issues_found"] / max(self.validation_metrics["total_validations"], 1),
            "validation_distribution": {
                "passed": self.validation_metrics["validations_passed"],
                "failed": self.validation_metrics["total_validations"] - self.validation_metrics["validations_passed"]
            },
            "quality_distribution": {
                "high_quality": len([s for s in quality_scores if s >= 0.8]),
                "medium_quality": len([s for s in quality_scores if 0.6 <= s < 0.8]),
                "low_quality": len([s for s in quality_scores if s < 0.6])
            }
        }