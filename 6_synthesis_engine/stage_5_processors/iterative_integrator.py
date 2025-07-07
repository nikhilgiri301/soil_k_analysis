"""
Stage 5A: Iterative Integrator
Iteratively integrates individual paper mappings into evolving synthesis state
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import statistics
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_loader import PromptLoader
from utils.gemini_client import GeminiClient
from utils.config import STAGE_TEMPERATURES

class IterativeIntegrator:
    """Stage 5A: Iterative paper integration with synthesis state management"""
    
    def __init__(self, gemini_client: GeminiClient, prompt_loader: PromptLoader):
        self.client = gemini_client
        self.prompt_loader = prompt_loader
        self.stage_name = "stage_5a_knowledge_synthesis"
        self.temperature = STAGE_TEMPERATURES.get("stage_5a_iterative_integration", 0.2)
        
        # Integration tracking
        self.integration_history = []
        self.conflict_resolutions = []
        self.confidence_evolution = []
        
        try:
            self.prompt_template = self.prompt_loader.load_prompt(self.stage_name)
            logging.info(f"Loaded iterative integration prompt for {self.stage_name}")
        except Exception as e:
            logging.error(f"Failed to load integration prompt: {str(e)}")
            raise
    
    async def integrate_paper(self, current_synthesis_state: Dict[str, Any], 
                             new_paper_mapping: Dict[str, Any], 
                             client_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate single paper into current synthesis state"""
        
        paper_id = new_paper_mapping.get("paper_id", "unknown")
        
        try:
            logging.info(f"Integrating paper {paper_id} into synthesis state")
            
            # Pre-integration analysis
            integration_context = self._analyze_integration_context(
                current_synthesis_state, new_paper_mapping, client_architecture
            )
            
            # Format prompt with current state + new paper
            formatted_prompt = self._format_integration_prompt(
                current_synthesis_state, new_paper_mapping, client_architecture, integration_context
            )
            
            # Generate integration with appropriate temperature
            integration_result = await self.client.generate_json_content(
                formatted_prompt,
                temperature=self.temperature
            )
            
            # Post-process integration result
            processed_result = self._post_process_integration(
                integration_result, current_synthesis_state, new_paper_mapping, integration_context
            )
            
            # Update integration tracking
            self._update_integration_tracking(paper_id, processed_result, integration_context)
            
            logging.info(f"Successfully integrated paper: {paper_id}")
            return processed_result
            
        except Exception as e:
            logging.error(f"Integration failed for paper {paper_id}: {str(e)}")
            return self._create_fallback_integration(current_synthesis_state, new_paper_mapping, str(e))
    
    def _analyze_integration_context(self, current_state: Dict[str, Any], 
                                   new_paper: Dict[str, Any],
                                   client_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze integration context to guide synthesis"""
        
        context = {
            "papers_already_integrated": current_state.get("synthesis_metadata", {}).get("papers_integrated", 0),
            "new_paper_confidence": new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0),
            "existing_parameters": list(current_state.get("question_responses", {}).keys()),
            "new_parameters": [],
            "potential_conflicts": [],
            "geographic_coverage": self._assess_geographic_coverage(current_state, new_paper),
            "temporal_coverage": self._assess_temporal_coverage(current_state, new_paper),
            "methodological_diversity": self._assess_methodological_diversity(current_state, new_paper)
        }
        
        # Identify new parameters from incoming paper
        new_mapping = new_paper.get("stage_4b_mapping", {})
        if "parameter_assignments" in new_mapping:
            for assignment in new_mapping["parameter_assignments"]:
                param_name = assignment.get("parameter_name")
                if param_name and param_name not in context["existing_parameters"]:
                    context["new_parameters"].append(param_name)
        
        # Detect potential conflicts
        context["potential_conflicts"] = self._detect_potential_conflicts(current_state, new_paper)
        
        return context
    
    def _format_integration_prompt(self, current_state: Dict[str, Any],
                                 new_paper: Dict[str, Any],
                                 client_architecture: Dict[str, Any],
                                 integration_context: Dict[str, Any]) -> str:
        """Format the integration prompt with all necessary context"""
        
        # Prepare context sections for prompt
        synthesis_state_summary = self._summarize_synthesis_state(current_state)
        new_paper_summary = self._summarize_new_paper(new_paper)
        integration_guidance = self._generate_integration_guidance(integration_context)
        
        try:
            formatted_prompt = self.prompt_template.format(
                client_question_tree=json.dumps(client_architecture.get('question_tree', {}), indent=2),
                current_synthesis_state=json.dumps(synthesis_state_summary, indent=2),
                stage_4b_results=json.dumps(new_paper_summary, indent=2),
                integration_context=json.dumps(integration_context, indent=2),
                integration_guidance=integration_guidance
            )
            
            return formatted_prompt
            
        except Exception as e:
            logging.error(f"Prompt formatting failed: {str(e)}")
            # Fallback to simpler format
            return self._create_fallback_prompt(current_state, new_paper, client_architecture)
    
    def _post_process_integration(self, ai_result: Dict[str, Any],
                                current_state: Dict[str, Any],
                                new_paper: Dict[str, Any],
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process AI integration result to ensure quality and consistency"""
        
        # Start with current state as base
        enhanced_result = current_state.copy() if current_state else {}
        
        # Update synthesis metadata
        if "synthesis_metadata" not in enhanced_result:
            enhanced_result["synthesis_metadata"] = {}
        
        enhanced_result["synthesis_metadata"].update({
            "last_integration_timestamp": datetime.now().isoformat(),
            "papers_integrated": context.get("papers_already_integrated", 0) + 1,
            "latest_paper_id": new_paper.get("paper_id", "unknown"),
            "integration_temperature": self.temperature
        })
        
        # Merge question responses from AI result
        if "question_responses" in ai_result:
            if "question_responses" not in enhanced_result:
                enhanced_result["question_responses"] = {}
            
            enhanced_result["question_responses"] = self._merge_question_responses(
                enhanced_result["question_responses"],
                ai_result["question_responses"],
                new_paper,
                context
            )
        
        # Update evidence registry
        enhanced_result["evidence_registry"] = self._update_evidence_registry(
            enhanced_result.get("evidence_registry", {}),
            new_paper,
            ai_result
        )
        
        # Track confidence evolution
        enhanced_result["confidence_evolution"] = self._update_confidence_evolution(
            enhanced_result.get("confidence_evolution", []),
            new_paper,
            ai_result
        )
        
        # Record integration log
        if "integration_log" not in enhanced_result:
            enhanced_result["integration_log"] = []
        
        enhanced_result["integration_log"].append({
            "timestamp": datetime.now().isoformat(),
            "paper_id": new_paper.get("paper_id"),
            "integration_summary": ai_result.get("integration_summary", "AI integration completed"),
            "conflicts_resolved": len(context.get("potential_conflicts", [])),
            "new_parameters_added": len(context.get("new_parameters", [])),
            "confidence_impact": self._calculate_confidence_impact(ai_result, context)
        })
        
        return enhanced_result
    
    def _merge_question_responses(self, existing_responses: Dict[str, Any],
                                new_responses: Dict[str, Any],
                                new_paper: Dict[str, Any],
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently merge question responses from new paper"""
        
        merged_responses = existing_responses.copy()
        paper_confidence = new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0)
        
        for question_category, new_data in new_responses.items():
            if question_category not in merged_responses:
                # New question category - add directly
                merged_responses[question_category] = new_data
            else:
                # Existing category - merge intelligently
                merged_responses[question_category] = self._merge_category_data(
                    merged_responses[question_category],
                    new_data,
                    paper_confidence,
                    context
                )
        
        return merged_responses
    
    def _merge_category_data(self, existing_data: Any, new_data: Any,
                           paper_confidence: float, context: Dict[str, Any]) -> Any:
        """Merge data for a specific question category"""
        
        # Handle different data types
        if isinstance(existing_data, dict) and isinstance(new_data, dict):
            merged = existing_data.copy()
            
            for key, value in new_data.items():
                if key not in merged:
                    merged[key] = value
                else:
                    # Key exists - need conflict resolution
                    merged[key] = self._resolve_data_conflict(
                        merged[key], value, paper_confidence, context
                    )
            
            return merged
            
        elif isinstance(existing_data, list) and isinstance(new_data, list):
            # Merge lists, avoiding duplicates
            merged_list = existing_data.copy()
            for item in new_data:
                if item not in merged_list:
                    merged_list.append(item)
            return merged_list
            
        else:
            # Different types or simple values - use confidence-weighted selection
            if paper_confidence > 0.6:
                return new_data  # High confidence new data takes precedence
            else:
                return existing_data  # Keep existing data
    
    def _resolve_data_conflict(self, existing_value: Any, new_value: Any,
                             paper_confidence: float, context: Dict[str, Any]) -> Any:
        """Resolve conflicts between existing and new data"""
        
        # Record conflict for tracking
        conflict_record = {
            "existing_value": existing_value,
            "new_value": new_value,
            "paper_confidence": paper_confidence,
            "resolution_strategy": "confidence_weighted",
            "timestamp": datetime.now().isoformat()
        }
        
        self.conflict_resolutions.append(conflict_record)
        
        # Simple conflict resolution based on confidence
        if paper_confidence > 0.7:
            conflict_record["resolution"] = "used_new_value"
            return new_value
        elif paper_confidence < 0.4:
            conflict_record["resolution"] = "kept_existing_value"
            return existing_value
        else:
            # Medium confidence - attempt to merge or average
            if isinstance(existing_value, (int, float)) and isinstance(new_value, (int, float)):
                # Average numeric values weighted by confidence
                weighted_value = (existing_value * (1 - paper_confidence) + new_value * paper_confidence)
                conflict_record["resolution"] = "weighted_average"
                conflict_record["resolved_value"] = weighted_value
                return weighted_value
            else:
                # Non-numeric - keep existing
                conflict_record["resolution"] = "kept_existing_value"
                return existing_value
    
    def _update_evidence_registry(self, existing_registry: Dict[str, Any],
                                new_paper: Dict[str, Any],
                                ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Update evidence registry with new paper information"""
        
        updated_registry = existing_registry.copy()
        
        # Initialize registry structure if needed
        for key in ["papers_by_region", "papers_by_timeframe", "methodological_approaches", "confidence_levels"]:
            if key not in updated_registry:
                updated_registry[key] = {}
        
        # Add paper to regional registry
        paper_id = new_paper.get("paper_id", "unknown")
        geographic_context = new_paper.get("confidence_assessment", {}).get("confidence_factors", {}).get("geographic_context", "unknown")
        
        if geographic_context not in updated_registry["papers_by_region"]:
            updated_registry["papers_by_region"][geographic_context] = []
        updated_registry["papers_by_region"][geographic_context].append(paper_id)
        
        # Add to confidence level registry
        confidence = new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0)
        confidence_level = self._classify_confidence_level(confidence)
        
        if confidence_level not in updated_registry["confidence_levels"]:
            updated_registry["confidence_levels"][confidence_level] = []
        updated_registry["confidence_levels"][confidence_level].append(paper_id)
        
        return updated_registry
    
    def _update_confidence_evolution(self, existing_evolution: List[Dict[str, Any]],
                                   new_paper: Dict[str, Any],
                                   ai_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Track how confidence evolves as papers are integrated"""
        
        evolution_entry = {
            "timestamp": datetime.now().isoformat(),
            "paper_id": new_paper.get("paper_id"),
            "paper_confidence": new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0),
            "synthesis_impact": ai_result.get("confidence_updates", {}),
            "cumulative_papers": len(existing_evolution) + 1
        }
        
        updated_evolution = existing_evolution.copy()
        updated_evolution.append(evolution_entry)
        
        return updated_evolution
    
    def _calculate_confidence_impact(self, ai_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the impact of this integration on overall confidence"""
        
        return {
            "new_parameters_added": len(context.get("new_parameters", [])),
            "conflicts_resolved": len(context.get("potential_conflicts", [])),
            "geographic_coverage_improved": context.get("geographic_coverage", {}).get("coverage_improved", False),
            "methodological_diversity_increased": context.get("methodological_diversity", {}).get("diversity_increased", False)
        }
    
    def _assess_geographic_coverage(self, current_state: Dict[str, Any], new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Assess geographic coverage impact"""
        
        existing_regions = set()
        evidence_registry = current_state.get("evidence_registry", {})
        if "papers_by_region" in evidence_registry:
            existing_regions = set(evidence_registry["papers_by_region"].keys())
        
        new_region = new_paper.get("confidence_assessment", {}).get("confidence_factors", {}).get("geographic_context", "unknown")
        
        return {
            "existing_regions": list(existing_regions),
            "new_region": new_region,
            "coverage_improved": new_region not in existing_regions,
            "total_regions_after": len(existing_regions) + (1 if new_region not in existing_regions else 0)
        }
    
    def _assess_temporal_coverage(self, current_state: Dict[str, Any], new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Assess temporal coverage impact"""
        
        # Simple temporal assessment - would be enhanced with actual publication dates
        return {
            "temporal_diversity": "assessed",
            "coverage_status": "maintaining_temporal_coverage"
        }
    
    def _assess_methodological_diversity(self, current_state: Dict[str, Any], new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Assess methodological diversity impact"""
        
        # Simple methodological assessment
        return {
            "methodological_diversity": "assessed",
            "diversity_status": "maintaining_methodological_diversity"
        }
    
    def _detect_potential_conflicts(self, current_state: Dict[str, Any], new_paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential conflicts between existing state and new paper"""
        
        conflicts = []
        
        # Check for parameter value conflicts
        existing_responses = current_state.get("question_responses", {})
        new_mapping = new_paper.get("stage_4b_mapping", {})
        
        if "parameter_assignments" in new_mapping:
            for assignment in new_mapping["parameter_assignments"]:
                param_name = assignment.get("parameter_name")
                if param_name in existing_responses:
                    conflicts.append({
                        "type": "parameter_conflict",
                        "parameter": param_name,
                        "conflict_severity": "potential",
                        "requires_resolution": True
                    })
        
        return conflicts
    
    def _summarize_synthesis_state(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise summary of current synthesis state for AI prompt"""
        
        return {
            "papers_integrated": current_state.get("synthesis_metadata", {}).get("papers_integrated", 0),
            "question_categories": list(current_state.get("question_responses", {}).keys()),
            "evidence_summary": {
                "regions_covered": len(current_state.get("evidence_registry", {}).get("papers_by_region", {})),
                "confidence_distribution": current_state.get("evidence_registry", {}).get("confidence_levels", {})
            }
        }
    
    def _summarize_new_paper(self, new_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise summary of new paper for AI prompt"""
        
        return {
            "paper_id": new_paper.get("paper_id"),
            "confidence": new_paper.get("confidence_assessment", {}).get("adjusted_confidence", 0.0),
            "geographic_context": new_paper.get("confidence_assessment", {}).get("confidence_factors", {}).get("geographic_context"),
            "parameter_assignments": new_paper.get("stage_4b_mapping", {}).get("parameter_assignments", [])
        }
    
    def _generate_integration_guidance(self, context: Dict[str, Any]) -> str:
        """Generate specific guidance for the AI integration process"""
        
        guidance_points = []
        
        if context.get("new_parameters"):
            guidance_points.append(f"New parameters to integrate: {', '.join(context['new_parameters'])}")
        
        if context.get("potential_conflicts"):
            guidance_points.append(f"Resolve {len(context['potential_conflicts'])} potential conflicts")
        
        if context.get("geographic_coverage", {}).get("coverage_improved"):
            guidance_points.append("Geographic coverage will be improved")
        
        guidance_points.append("Apply conservative confidence calibration")
        guidance_points.append("Maintain evidence traceability")
        
        return "\n".join(f"- {point}" for point in guidance_points)
    
    def _classify_confidence_level(self, confidence: float) -> str:
        """Classify confidence score into categories"""
        
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        elif confidence >= 0.2:
            return "very_low"
        else:
            return "insufficient"
    
    def _create_fallback_integration(self, current_state: Dict[str, Any],
                                   new_paper: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Create fallback integration when AI processing fails"""
        
        # Return current state with minimal updates
        fallback_state = current_state.copy() if current_state else {
            "synthesis_metadata": {},
            "question_responses": {},
            "evidence_registry": {},
            "confidence_evolution": [],
            "integration_log": []
        }
        
        # Update metadata to reflect attempted integration
        fallback_state["synthesis_metadata"].update({
            "last_integration_timestamp": datetime.now().isoformat(),
            "integration_error": error_msg,
            "fallback_integration_applied": True
        })
        
        # Log the failure
        if "integration_log" not in fallback_state:
            fallback_state["integration_log"] = []
        
        fallback_state["integration_log"].append({
            "timestamp": datetime.now().isoformat(),
            "paper_id": new_paper.get("paper_id"),
            "status": "integration_failed",
            "error": error_msg,
            "fallback_applied": True
        })
        
        return fallback_state
    
    def _create_fallback_prompt(self, current_state: Dict[str, Any],
                              new_paper: Dict[str, Any],
                              client_architecture: Dict[str, Any]) -> str:
        """Create simplified fallback prompt when formatting fails"""
        
        return f"""
        You are integrating a new research paper into an existing soil K literature synthesis.
        
        Current synthesis has {current_state.get('synthesis_metadata', {}).get('papers_integrated', 0)} papers integrated.
        
        New paper ID: {new_paper.get('paper_id', 'unknown')}
        New paper confidence: {new_paper.get('confidence_assessment', {}).get('adjusted_confidence', 0.0)}
        
        Please integrate this paper's findings into the synthesis state, maintaining conservative confidence calibration.
        
        Return JSON with updated synthesis state including:
        - synthesis_metadata
        - question_responses  
        - evidence_registry
        - confidence_evolution
        - integration_log
        """
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get statistics about integration performance"""
        
        return {
            "total_integrations": len(self.integration_history),
            "conflict_resolutions": len(self.conflict_resolutions),
            "confidence_evolution_entries": len(self.confidence_evolution),
            "average_integration_time": "not_tracked",  # Could be enhanced
            "success_rate": "tracked_in_logs"
        }
    
    def _update_integration_tracking(self, paper_id: str, result: Dict[str, Any], context: Dict[str, Any]):
        """Update internal tracking of integration performance"""
        
        self.integration_history.append({
            "timestamp": datetime.now().isoformat(),
            "paper_id": paper_id,
            "success": True,
            "context": context,
            "result_size": len(str(result))
        })