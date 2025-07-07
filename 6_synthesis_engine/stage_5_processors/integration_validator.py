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
from utils.config import STAGE_TEMPERATURES

class IntegrationValidator:
    """Stage 5B: Validates iterative integration results with comprehensive quality checking"""
    
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.prompt_loader = PromptLoader()
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
    
    async def validate_integration(self, current_synthesis_state: Dict[str, Any],
                                  new_paper_mapping: Dict[str, Any],
                                  integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration result with comprehensive quality assessment"""
        
        paper_id = new_paper_mapping.get("paper_id", "unknown")
        
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
            formatted_prompt = self._format_validation_prompt(
                current_state, new_paper, integration_result, context
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
        
        # Validate synthesis_metadata structure
        if "synthesis_metadata" in integration_result:
            metadata = integration_result["synthesis_metadata"]
            required_metadata = ["last_integration_timestamp", "papers_integrated"]
            
            for meta_field in required_metadata:
                if meta_field not in metadata:
                    check_result["issues"].append(f"Missing metadata field: {meta_field}")
        
        return check_result
    
    def _validate_consistency(self, current_state: Dict[str, Any], 
                            integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency between states"""
        
        check_result = {
            "passed": True,
            "issues": [],
            "consistency_checks": {}
        }
        
        # Check paper count consistency
        current_papers = current_state.get("synthesis_metadata", {}).get("papers_integrated", 0)
        result_papers = integration_result.get("synthesis_metadata", {}).get("papers_integrated", 0)
        
        if result_papers != current_papers + 1:
            check_result["passed"] = False
            check_result["issues"].append(f"Paper count inconsistency: expected {current_papers + 1}, got {result_papers}")
        
        check_result["consistency_checks"]["paper_count"] = result_papers == current_papers + 1
        
        # Check evidence registry growth
        current_evidence = current_state.get("evidence_registry", {})
        result_evidence = integration_result.get("evidence_registry", {})
        
        evidence_growth_valid = self._validate_evidence_growth(current_evidence, result_evidence)
        check_result["consistency_checks"]["evidence_growth"] = evidence_growth_valid
        
        if not evidence_growth_valid:
            check_result["issues"].append("Evidence registry did not grow appropriately")
        
        return check_result
    
    def _validate_confidence_levels(self, integration_result: Dict[str, Any],
                                  new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Validate confidence levels are reasonable and conservative"""
        
        check_result = {
            "passed": True,
            "warnings": [],
            "confidence_checks": {}
        }
        
        # Check for confidence inflation
        paper_confidence = new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0)
        
        question_responses = integration_result.get("question_responses", {})
        for category, response_data in question_responses.items():
            if isinstance(response_data, dict) and "confidence" in response_data:
                response_confidence = response_data["confidence"]
                
                # Conservative bias check - integrated confidence shouldn't be much higher than paper confidence
                if response_confidence > paper_confidence + 0.2:
                    check_result["warnings"].append(
                        f"Potentially inflated confidence in {category}: {response_confidence} vs paper {paper_confidence}"
                    )
                
                # Sanity check - confidence should be between 0 and 1
                if not (0 <= response_confidence <= 1):
                    check_result["passed"] = False
                    check_result["warnings"].append(f"Invalid confidence value in {category}: {response_confidence}")
        
        return check_result
    
    def _validate_evidence_traceability(self, integration_result: Dict[str, Any],
                                      new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that evidence can be traced back to source papers"""
        
        check_result = {
            "passed": True,
            "issues": [],
            "traceability_checks": {}
        }
        
        paper_id = new_paper.get("paper_id", "unknown")
        evidence_registry = integration_result.get("evidence_registry", {})
        
        # Check that new paper is recorded in evidence registry
        paper_found_in_registry = False
        
        for registry_section, data in evidence_registry.items():
            if isinstance(data, dict):
                for key, papers_list in data.items():
                    if isinstance(papers_list, list) and paper_id in papers_list:
                        paper_found_in_registry = True
                        break
        
        check_result["traceability_checks"]["paper_in_registry"] = paper_found_in_registry
        
        if not paper_found_in_registry:
            check_result["passed"] = False
            check_result["issues"].append(f"Paper {paper_id} not found in evidence registry")
        
        # Check integration log
        integration_log = integration_result.get("integration_log", [])
        paper_in_log = any(entry.get("paper_id") == paper_id for entry in integration_log)
        
        check_result["traceability_checks"]["paper_in_log"] = paper_in_log
        
        if not paper_in_log:
            check_result["issues"].append(f"Paper {paper_id} not found in integration log")
        
        return check_result
    
    def _validate_completeness(self, integration_result: Dict[str, Any],
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate completeness of integration"""
        
        check_result = {
            "passed": True,
            "warnings": [],
            "completeness_checks": {}
        }
        
        # Check that confidence evolution was updated
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
        
        # Combine recommendations
        ai_recommendations = ai_validation.get("recommendations", [])
        rule_recommendations = rule_validation.get("recommendations", [])
        combined_result["recommendations"] = ai_recommendations + rule_recommendations
        
        # Calculate overall quality score
        ai_score = ai_validation.get("confidence_score", ai_validation.get("quality_score", 0.5))
        rule_score = rule_validation.get("quality_score", 0.5)
        
        # Weight rule-based validation higher for critical checks
        combined_result["overall_quality_score"] = (rule_score * 0.6) + (ai_score * 0.4)
        
        # Apply penalties for critical issues
        if combined_result["critical_issues"]:
            penalty = min(0.3, len(combined_result["critical_issues"]) * 0.1)
            combined_result["overall_quality_score"] = max(0.0, combined_result["overall_quality_score"] - penalty)
        
        # Final validation decision
        if combined_result["critical_issues"]:
            combined_result["validation_passed"] = False
        
        return combined_result
    
    def _format_validation_prompt(self, current_state: Dict[str, Any],
                                new_paper: Dict[str, Any],
                                integration_result: Dict[str, Any],
                                context: Dict[str, Any]) -> str:
        """Format the validation prompt for AI analysis"""
        
        try:
            # Prepare validation context for prompt
            validation_context = {
                "integration_complexity": context.get("integration_complexity", {}),
                "state_changes": context.get("state_changes", {}),
                "potential_issues": context.get("potential_quality_issues", []),
                "validation_priorities": context.get("validation_priorities", [])
            }
            
            formatted_prompt = self.prompt_template.format(
                current_synthesis_state=json.dumps(self._summarize_for_validation(current_state), indent=2),
                stage_4b_results=json.dumps(self._summarize_paper_for_validation(new_paper), indent=2),
                stage_5a_results=json.dumps(self._summarize_integration_for_validation(integration_result), indent=2),
                validation_context=json.dumps(validation_context, indent=2)
            )
            
            return formatted_prompt
            
        except Exception as e:
            logging.error(f"Validation prompt formatting failed: {str(e)}")
            return self._create_fallback_validation_prompt(current_state, new_paper, integration_result)
    
    def _assess_integration_complexity(self, current_state: Dict[str, Any],
                                     integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the complexity of the integration for validation prioritization"""
        
        current_responses = len(current_state.get("question_responses", {}))
        result_responses = len(integration_result.get("question_responses", {}))
        
        return {
            "new_question_categories": max(0, result_responses - current_responses),
            "state_size_growth": len(str(integration_result)) - len(str(current_state)),
            "expected_evolution_entries": 1,
            "complexity_level": "medium"  # Could be enhanced with more sophisticated assessment
        }
    
    def _analyze_state_changes(self, current_state: Dict[str, Any],
                             integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what changed between states"""
        
        changes = {
            "metadata_changes": {},
            "question_response_changes": {},
            "evidence_registry_changes": {},
            "total_changes": 0
        }
        
        # Analyze metadata changes
        current_meta = current_state.get("synthesis_metadata", {})
        result_meta = integration_result.get("synthesis_metadata", {})
        
        for key in set(list(current_meta.keys()) + list(result_meta.keys())):
            if current_meta.get(key) != result_meta.get(key):
                changes["metadata_changes"][key] = {
                    "from": current_meta.get(key),
                    "to": result_meta.get(key)
                }
                changes["total_changes"] += 1
        
        return changes
    
    def _analyze_confidence_changes(self, current_state: Dict[str, Any],
                                  integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence changes"""
        
        current_evolution = current_state.get("confidence_evolution", [])
        result_evolution = integration_result.get("confidence_evolution", [])
        
        return {
            "evolution_entries_added": len(result_evolution) - len(current_evolution),
            "confidence_trend": "analyzed",  # Could be enhanced
            "significant_changes": False  # Could be enhanced
        }
    
    def _determine_validation_priorities(self, current_state: Dict[str, Any],
                                       new_paper: Dict[str, Any],
                                       integration_result: Dict[str, Any]) -> List[str]:
        """Determine validation priorities based on context"""
        
        priorities = ["structure_validation", "consistency_validation"]
        
        # Add confidence validation if paper has low confidence
        paper_confidence = new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0)
        if paper_confidence < 0.5:
            priorities.append("confidence_validation")
        
        # Add traceability validation
        priorities.append("evidence_traceability")
        
        return priorities
    
    def _identify_potential_issues(self, current_state: Dict[str, Any],
                                 new_paper: Dict[str, Any],
                                 integration_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential quality issues for validation focus"""
        
        issues = []
        
        # Check for suspicious confidence increases
        paper_confidence = new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0)
        if paper_confidence < 0.4:
            issues.append({
                "type": "low_confidence_paper",
                "description": "Integration of low-confidence paper requires careful validation",
                "severity": "medium"
            })
        
        # Check for large state changes
        state_size_ratio = len(str(integration_result)) / max(len(str(current_state)), 1)
        if state_size_ratio > 2.0:
            issues.append({
                "type": "large_state_change",
                "description": "Integration resulted in unusually large state change",
                "severity": "high"
            })
        
        return issues
    
    def _validate_evidence_growth(self, current_evidence: Dict[str, Any],
                                result_evidence: Dict[str, Any]) -> bool:
        """Validate that evidence registry grew appropriately"""
        
        # Simple check - result should have at least as much evidence as current
        current_size = len(str(current_evidence))
        result_size = len(str(result_evidence))
        
        return result_size >= current_size
    
    def _calculate_rule_based_quality_score(self, rule_checks: Dict[str, Any]) -> float:
        """Calculate quality score from rule-based checks"""
        
        total_checks = len(rule_checks)
        if total_checks == 0:
            return 0.5
        
        passed_checks = sum(1 for check in rule_checks.values() if check.get("passed", False))
        
        return passed_checks / total_checks
    
    def _summarize_for_validation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise summary for validation prompt"""
        
        return {
            "papers_integrated": state.get("synthesis_metadata", {}).get("papers_integrated", 0),
            "question_categories": len(state.get("question_responses", {})),
            "evidence_summary": {
                "regions": len(state.get("evidence_registry", {}).get("papers_by_region", {})),
                "confidence_levels": len(state.get("evidence_registry", {}).get("confidence_levels", {}))
            }
        }
    
    def _summarize_paper_for_validation(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise paper summary for validation"""
        
        return {
            "paper_id": paper.get("paper_id"),
            "confidence": paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0),
            "quality_score": paper.get("quality_assessment", {}).get("quality_score", 0.0)
        }
    
    def _summarize_integration_for_validation(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise integration summary for validation"""
        
        return {
            "papers_integrated": integration.get("synthesis_metadata", {}).get("papers_integrated", 0),
            "question_categories": len(integration.get("question_responses", {})),
            "integration_log_entries": len(integration.get("integration_log", [])),
            "confidence_evolution_entries": len(integration.get("confidence_evolution", []))
        }
    
    def _create_fallback_validation(self, paper_id: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback validation result when validation fails"""
        
        return {
            "validation_timestamp": datetime.now().isoformat(),
            "paper_id": paper_id,
            "validation_passed": False,
            "overall_quality_score": 0.0,
            "critical_issues": [f"Validation failed: {error_msg}"],
            "warnings": ["Fallback validation applied"],
            "recommendations": ["Manual review required"],
            "fallback_validation": True,
            "error": error_msg
        }
    
    def _create_fallback_validation_prompt(self, current_state: Dict[str, Any],
                                         new_paper: Dict[str, Any],
                                         integration_result: Dict[str, Any]) -> str:
        """Create simplified validation prompt when formatting fails"""
        
        return f"""
        You are validating the integration of a research paper into soil K literature synthesis.
        
        Paper ID: {new_paper.get('paper_id', 'unknown')}
        Current papers in synthesis: {current_state.get('synthesis_metadata', {}).get('papers_integrated', 0)}
        Integration result papers: {integration_result.get('synthesis_metadata', {}).get('papers_integrated', 0)}
        
        Validate that:
        1. The integration is structurally sound
        2. Confidence levels are conservative and realistic
        3. Evidence traceability is maintained
        4. No critical errors were introduced
        
        Return JSON with validation results including validation_passed boolean and any issues found.
        """
    
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