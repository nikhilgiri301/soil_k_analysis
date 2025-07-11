"""
Confidence Scorer for Soil K Analysis Synthesis Engine
Implements conservative confidence calibration based on evidence quality
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

class ConfidenceScorer:
    """Conservative confidence scoring system for soil K literature synthesis"""
    
    def __init__(self):
        self.confidence_history = []
        self.scoring_cache = {}
        
        # Load confidence calibration framework
        self.load_confidence_framework()
        
        logging.info("Confidence Scorer initialized with conservative calibration")
    
    def load_confidence_framework(self):
        """Load confidence thresholds and calibration rules"""
        try:
            with open(f"{PATHS['client_architecture']}/confidence_thresholds.json", 'r') as f:
                self.framework = json.load(f)
            
            self.confidence_levels = self.framework["confidence_levels"]
            self.quality_multipliers = self.framework["evidence_quality_multipliers"]
            self.parameter_thresholds = self.framework["parameter_specific_thresholds"]
            self.regional_adjustments = self.framework["regional_confidence_adjustments"]
            
        except Exception as e:
            logging.warning(f"Could not load confidence framework: {str(e)}")
            self.framework = self._default_confidence_framework()
            self._setup_default_parameters()
    
    def score_paper_confidence(self, paper_data: Dict[str, Any], 
                             extraction_quality: Dict[str, Any],
                             geographic_context: Optional[str] = None) -> Dict[str, Any]:
        """Score confidence for individual paper analysis"""
        
        confidence_assessment = {
            "paper_id": paper_data.get("filename", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "base_confidence": 0.0,
            "adjusted_confidence": 0.0,
            "confidence_factors": {},
            "limitations": [],
            "evidence_quality": "insufficient"
        }
        
        try:
            # Calculate base confidence from study characteristics
            base_score = self._calculate_base_confidence(paper_data, extraction_quality)
            confidence_assessment["base_confidence"] = base_score
            
            # Apply quality multipliers
            adjusted_score = self._apply_quality_multipliers(base_score, paper_data, extraction_quality)
            
            # Apply geographic adjustment
            if geographic_context:
                adjusted_score = self._apply_geographic_adjustment(adjusted_score, geographic_context)
            
            # Apply conservative bias
            adjusted_score = self._apply_conservative_bias(adjusted_score)
            
            confidence_assessment["adjusted_confidence"] = max(0.0, min(1.0, adjusted_score))
            confidence_assessment["evidence_quality"] = self._classify_evidence_quality(adjusted_score)
            
            # Document confidence factors
            confidence_assessment["confidence_factors"] = self._document_confidence_factors(
                paper_data, extraction_quality, geographic_context
            )
            
            # Identify limitations
            confidence_assessment["limitations"] = self._identify_limitations(
                paper_data, extraction_quality
            )
            
        except Exception as e:
            logging.error(f"Confidence scoring failed: {str(e)}")
            confidence_assessment["adjusted_confidence"] = 0.0
            confidence_assessment["limitations"].append(f"Scoring error: {str(e)}")
        
        return confidence_assessment
    
    def score_parameter_confidence(self, parameter_name: str, 
                                 supporting_papers: List[Dict[str, Any]],
                                 synthesis_context: Dict[str, Any]) -> Dict[str, Any]:
        """Score confidence for specific parameter across multiple papers"""
        
        parameter_confidence = {
            "parameter_name": parameter_name,
            "timestamp": datetime.now().isoformat(),
            "supporting_studies": len(supporting_papers),
            "base_confidence": 0.0,
            "final_confidence": 0.0,
            "confidence_breakdown": {},
            "evidence_consensus": "none",
            "critical_limitations": []
        }
        
        try:
            # Check if parameter has specific requirements
            param_requirements = self.parameter_thresholds.get(parameter_name, {})
            
            # Calculate base confidence from study coverage
            base_score = self._calculate_parameter_base_confidence(
                parameter_name, supporting_papers, param_requirements
            )
            parameter_confidence["base_confidence"] = base_score
            
            # Assess evidence consensus
            consensus_score, consensus_type = self._assess_evidence_consensus(supporting_papers)
            parameter_confidence["evidence_consensus"] = consensus_type
            
            # Apply consensus adjustment
            consensus_adjusted = base_score * consensus_score
            
            # Apply parameter-specific requirements
            final_score = self._apply_parameter_requirements(
                consensus_adjusted, parameter_name, supporting_papers, param_requirements
            )
            
            # Apply conservative calibration
            final_score = self._apply_conservative_calibration(final_score, parameter_name)
            
            parameter_confidence["final_confidence"] = max(0.0, min(1.0, final_score))
            
            # Document confidence breakdown
            parameter_confidence["confidence_breakdown"] = {
                "base_score": base_score,
                "consensus_adjustment": consensus_score,
                "requirements_check": final_score / max(consensus_adjusted, 0.001),
                "conservative_bias": "applied"
            }
            
            # Identify critical limitations
            parameter_confidence["critical_limitations"] = self._identify_parameter_limitations(
                parameter_name, supporting_papers, param_requirements
            )
            
        except Exception as e:
            logging.error(f"Parameter confidence scoring failed: {str(e)}")
            parameter_confidence["final_confidence"] = 0.0
            parameter_confidence["critical_limitations"].append(f"Scoring error: {str(e)}")
        
        return parameter_confidence
    
    def score_synthesis_confidence(self, synthesis_data: Dict[str, Any],
                                 paper_confidences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score confidence for overall synthesis across all papers and parameters"""
        
        synthesis_confidence = {
            "timestamp": datetime.now().isoformat(),
            "total_papers": len(paper_confidences),
            "overall_confidence": 0.0,
            "parameter_confidences": {},
            "regional_coverage": {},
            "evidence_quality_summary": {},
            "synthesis_limitations": []
        }
        
        try:
            # Extract parameter confidences
            parameter_scores = {}
            for param_name in synthesis_data.get("question_responses", {}):
                supporting_papers = [p for p in paper_confidences 
                                   if self._paper_supports_parameter(p, param_name)]
                
                if supporting_papers:
                    param_conf = self.score_parameter_confidence(
                        param_name, supporting_papers, synthesis_data
                    )
                    parameter_scores[param_name] = param_conf["final_confidence"]
                    synthesis_confidence["parameter_confidences"][param_name] = param_conf
            
            # Calculate weighted overall confidence
            if parameter_scores:
                # Weight critical parameters more heavily
                critical_params = ["annual_kg_k2o_per_ha", "sustainability_years", "depletion_rate"]
                
                weighted_scores = []
                weights = []
                
                for param, score in parameter_scores.items():
                    weight = 2.0 if param in critical_params else 1.0
                    weighted_scores.append(score * weight)
                    weights.append(weight)
                
                overall_score = sum(weighted_scores) / sum(weights) if weights else 0.0
                synthesis_confidence["overall_confidence"] = overall_score
            
            # Assess regional coverage
            synthesis_confidence["regional_coverage"] = self._assess_regional_coverage(paper_confidences)
            
            # Summarize evidence quality
            synthesis_confidence["evidence_quality_summary"] = self._summarize_evidence_quality(paper_confidences)
            
            # Identify synthesis-level limitations
            synthesis_confidence["synthesis_limitations"] = self._identify_synthesis_limitations(
                synthesis_data, paper_confidences, parameter_scores
            )
            
        except Exception as e:
            logging.error(f"Synthesis confidence scoring failed: {str(e)}")
            synthesis_confidence["overall_confidence"] = 0.0
            synthesis_confidence["synthesis_limitations"].append(f"Scoring error: {str(e)}")
        
        return synthesis_confidence
    
    def _calculate_base_confidence(self, paper_data: Dict[str, Any], 
                                 extraction_quality: Dict[str, Any]) -> float:
        """Calculate base confidence score from study characteristics"""
        
        score = 0.5  # Start with neutral confidence
        
        # Study design quality
        study_type = extraction_quality.get("methodology", {}).get("study_type", "unknown")
        if study_type in self.quality_multipliers["study_design"]:
            score *= self.quality_multipliers["study_design"][study_type]
        else:
            score *= 0.6  # Unknown study type penalty
        
        # Sample size
        sample_info = extraction_quality.get("sample_characteristics", {})
        if "sample_size" in sample_info:
            sample_size = sample_info["sample_size"]
            if sample_size >= 100:
                score *= self.quality_multipliers["sample_size"]["large_n_gt_100"]
            elif sample_size >= 30:
                score *= self.quality_multipliers["sample_size"]["medium_n_30_100"]
            elif sample_size >= 10:
                score *= self.quality_multipliers["sample_size"]["small_n_10_30"]
            else:
                score *= self.quality_multipliers["sample_size"]["very_small_n_lt_10"]
        
        # Temporal coverage
        temporal_info = extraction_quality.get("temporal_context", {})
        if "study_duration" in temporal_info:
            duration = temporal_info["study_duration"]
            if "year" in duration.lower():
                if "10" in duration or int(any(c.isdigit() for c in duration)) >= 10:
                    score *= self.quality_multipliers["temporal_coverage"]["gt_10_years"]
                elif "5" in duration:
                    score *= self.quality_multipliers["temporal_coverage"]["5_10_years"]
                else:
                    score *= self.quality_multipliers["temporal_coverage"]["1_2_years"]
        
        return min(1.0, score)
    
    def _apply_quality_multipliers(self, base_score: float, paper_data: Dict[str, Any],
                                 extraction_quality: Dict[str, Any]) -> float:
        """Apply evidence quality multipliers"""
        
        adjusted_score = base_score
        
        # Publication quality (assume peer-reviewed if not specified)
        pub_type = paper_data.get("publication_type", "peer_reviewed_journal")
        if pub_type in self.quality_multipliers["publication_quality"]:
            adjusted_score *= self.quality_multipliers["publication_quality"][pub_type]
        
        return adjusted_score
    
    def _apply_geographic_adjustment(self, score: float, geographic_context: str) -> float:
        """Apply geographic relevance adjustment"""
        
        # Simple geographic mapping for major regions
        region_mapping = {
            "china": "china",
            "india": "india", 
            "brazil": "brazil",
            "europe": "europe",
            "usa": "usa",
            "united_states": "usa"
        }
        
        context_lower = geographic_context.lower()
        region = None
        
        for key, mapped_region in region_mapping.items():
            if key in context_lower:
                region = mapped_region
                break
        
        if region and region in self.regional_adjustments:
            multiplier = self.regional_adjustments[region]["confidence_multiplier"]
            return score * multiplier
        else:
            # Unknown region - apply penalty
            return score * 0.7
    
    def _apply_conservative_bias(self, score: float) -> float:
        """Apply conservative bias to prevent overconfidence"""
        
        # Conservative scaling: reduce confidence by 10-20%
        if score > 0.8:
            return score * 0.85  # High confidence gets more conservative
        elif score > 0.6:
            return score * 0.9   # Medium confidence gets modest reduction
        else:
            return score * 0.95  # Low confidence gets minimal reduction
    
    def _calculate_parameter_base_confidence(self, parameter_name: str,
                                           supporting_papers: List[Dict[str, Any]],
                                           requirements: Dict[str, Any]) -> float:
        """Calculate base confidence for parameter from supporting studies"""
        
        # Start with study count
        study_count = len(supporting_papers)
        min_studies = requirements.get("minimum_studies", 3)
        
        if study_count >= min_studies:
            base_score = 0.7  # Good starting point
        elif study_count >= min_studies // 2:
            base_score = 0.5  # Partial coverage
        else:
            base_score = 0.3  # Insufficient coverage
        
        return base_score
    
    def _assess_evidence_consensus(self, supporting_papers: List[Dict[str, Any]]) -> Tuple[float, str]:
        """Assess consensus across supporting papers"""
        
        if len(supporting_papers) <= 1:
            return 1.0, "single_study"
        
        # Simple consensus assessment based on confidence scores
        confidences = [p.get("confidence_score", 0.5) for p in supporting_papers]
        
        if confidences:
            mean_conf = statistics.mean(confidences)
            std_conf = statistics.stdev(confidences) if len(confidences) > 1 else 0
            
            # High consensus if low variability
            if std_conf < 0.1:
                return 1.0, "strong_consensus"
            elif std_conf < 0.2:
                return 0.9, "moderate_consensus"
            elif std_conf < 0.3:
                return 0.8, "weak_consensus"
            else:
                return 0.6, "conflicting_evidence"
        
        return 0.5, "insufficient_data"
    
    def _apply_parameter_requirements(self, score: float, parameter_name: str,
                                    supporting_papers: List[Dict[str, Any]],
                                    requirements: Dict[str, Any]) -> float:
        """Apply parameter-specific requirements"""
        
        # Check minimum confidence requirement
        min_confidence = requirements.get("minimum_confidence_required", 0.4)
        
        if score < min_confidence:
            # Significant penalty for not meeting minimum
            score = score * 0.5
        
        # Check evidence requirements
        evidence_req = requirements.get("evidence_requirements", {})
        
        if "minimum_studies" in evidence_req:
            min_studies = evidence_req["minimum_studies"]
            if len(supporting_papers) < min_studies:
                penalty = 0.8 ** (min_studies - len(supporting_papers))
                score *= penalty
        
        return score
    
    def _apply_conservative_calibration(self, score: float, parameter_name: str) -> float:
        """Apply final conservative calibration"""
        
        # Critical parameters get extra conservative treatment
        critical_params = ["annual_kg_k2o_per_ha", "sustainability_years", "depletion_rate"]
        
        if parameter_name in critical_params:
            return score * 0.9  # 10% additional conservatism
        else:
            return score * 0.95  # 5% additional conservatism
    
    def _classify_evidence_quality(self, confidence_score: float) -> str:
        """Classify evidence quality based on confidence score"""
        
        if confidence_score >= 0.8:
            return "high"
        elif confidence_score >= 0.6:
            return "medium"
        elif confidence_score >= 0.4:
            return "low"
        elif confidence_score >= 0.2:
            return "very_low"
        else:
            return "insufficient"
    
    def _document_confidence_factors(self, paper_data: Dict[str, Any],
                                   extraction_quality: Dict[str, Any],
                                   geographic_context: Optional[str]) -> Dict[str, Any]:
        """Document factors contributing to confidence score"""
        
        return {
            "study_design": extraction_quality.get("methodology", {}).get("study_type", "unknown"),
            "sample_size": extraction_quality.get("sample_characteristics", {}).get("sample_size", "unknown"),
            "study_duration": extraction_quality.get("temporal_context", {}).get("study_duration", "unknown"),
            "geographic_context": geographic_context or "not_specified",
            "publication_type": paper_data.get("publication_type", "assumed_peer_reviewed"),
            "conservative_bias": "applied"
        }
    
    def _identify_limitations(self, paper_data: Dict[str, Any],
                            extraction_quality: Dict[str, Any]) -> List[str]:
        """Identify study limitations affecting confidence"""
        
        limitations = []
        
        # Check for common limitations
        if not extraction_quality.get("methodology", {}).get("study_type"):
            limitations.append("Study design not clearly specified")
        
        if not extraction_quality.get("sample_characteristics", {}).get("sample_size"):
            limitations.append("Sample size not reported")
        
        if not extraction_quality.get("temporal_context", {}).get("study_duration"):
            limitations.append("Study duration not specified")
        
        if not extraction_quality.get("geographic_context"):
            limitations.append("Geographic context unclear")
        
        return limitations
    
    def _paper_supports_parameter(self, paper_confidence: Dict[str, Any], parameter_name: str) -> bool:
        """Check if paper provides evidence for specific parameter"""
        
        # Simple check - look for parameter in paper data
        # This would be enhanced with actual parameter mapping logic
        return True  # Placeholder - implement actual logic
    
    def _assess_regional_coverage(self, paper_confidences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess geographic coverage of evidence base"""
        
        regions = {}
        for paper in paper_confidences:
            region = paper.get("geographic_context", "unknown")
            if region not in regions:
                regions[region] = 0
            regions[region] += 1
        
        return {
            "regions_covered": list(regions.keys()),
            "regional_distribution": regions,
            "coverage_quality": "good" if len(regions) >= 3 else "limited"
        }
    
    def _summarize_evidence_quality(self, paper_confidences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize evidence quality across all papers"""
        
        if not paper_confidences:
            return {"status": "no_evidence"}
        
        quality_levels = {}
        confidence_scores = []
        
        for paper in paper_confidences:
            quality = paper.get("evidence_quality", "unknown")
            confidence = paper.get("adjusted_confidence", 0.0)
            
            if quality not in quality_levels:
                quality_levels[quality] = 0
            quality_levels[quality] += 1
            confidence_scores.append(confidence)
        
        return {
            "quality_distribution": quality_levels,
            "average_confidence": statistics.mean(confidence_scores),
            "confidence_range": [min(confidence_scores), max(confidence_scores)],
            "total_papers": len(paper_confidences)
        }
    
    def _identify_parameter_limitations(self, parameter_name: str,
                                      supporting_papers: List[Dict[str, Any]],
                                      requirements: Dict[str, Any]) -> List[str]:
        """Identify parameter-specific limitations"""
        
        limitations = []
        
        # Check study count
        min_studies = requirements.get("minimum_studies", 3)
        if len(supporting_papers) < min_studies:
            limitations.append(f"Insufficient studies: {len(supporting_papers)} vs {min_studies} required")
        
        # Check confidence threshold
        min_confidence = requirements.get("minimum_confidence_required", 0.4)
        avg_confidence = statistics.mean([p.get("adjusted_confidence", 0.0) for p in supporting_papers])
        if avg_confidence < min_confidence:
            limitations.append(f"Below confidence threshold: {avg_confidence:.2f} vs {min_confidence} required")
        
        return limitations
    
    def _identify_synthesis_limitations(self, synthesis_data: Dict[str, Any],
                                      paper_confidences: List[Dict[str, Any]],
                                      parameter_scores: Dict[str, float]) -> List[str]:
        """Identify synthesis-level limitations"""
        
        limitations = []
        
        # Check overall paper count
        if len(paper_confidences) < 5:
            limitations.append("Limited number of supporting studies")
        
        # Check parameter coverage
        critical_params = ["annual_kg_k2o_per_ha", "sustainability_years", "depletion_rate"]
        missing_critical = [p for p in critical_params if p not in parameter_scores]
        
        if missing_critical:
            limitations.append(f"Missing critical parameters: {', '.join(missing_critical)}")
        
        # Check confidence levels
        low_confidence_params = [p for p, score in parameter_scores.items() if score < 0.4]
        if low_confidence_params:
            limitations.append(f"Low confidence parameters: {', '.join(low_confidence_params)}")
        
        return limitations
    
    def _default_confidence_framework(self) -> Dict[str, Any]:
        """Default confidence framework if none can be loaded"""
        return {
            "confidence_levels": {
                "high_confidence": {"range": "0.8-1.0"},
                "medium_confidence": {"range": "0.6-0.79"},
                "low_confidence": {"range": "0.4-0.59"},
                "very_low_confidence": {"range": "0.2-0.39"},
                "insufficient_evidence": {"range": "0.0-0.19"}
            }
        }
    
    def _setup_default_parameters(self):
        """Setup default parameters when framework loading fails"""
        self.confidence_levels = self.framework["confidence_levels"]
        self.quality_multipliers = {
            "study_design": {"field_study": 1.0, "laboratory": 0.8, "modeling": 0.6},
            "publication_quality": {"peer_reviewed_journal": 1.0, "report": 0.8},
            "sample_size": {"large_n_gt_100": 1.0, "medium_n_30_100": 0.9, "small_n_10_30": 0.8},
            "temporal_coverage": {"gt_10_years": 1.0, "5_10_years": 0.9, "1_2_years": 0.7}
        }
        self.parameter_thresholds = {}
        self.regional_adjustments = {"china": {"confidence_multiplier": 1.0}} 
