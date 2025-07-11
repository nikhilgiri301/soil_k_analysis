"""
Stage-Level Caching Manager for Soil K Synthesis Engine
Implements intelligent caching, invalidation, and resume capabilities for efficient development
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

class StageCacheManager:
    """
    Manages stage-level caching and resume functionality for the synthesis engine.
    Provides cost optimization through intelligent API call caching.
    """
    
    def __init__(self, cache_base_dir: str = "10_stage_cache"):
        self.cache_base_dir = Path(cache_base_dir)
        self.cache_base_dir.mkdir(exist_ok=True)
        
        # Cache structure
        self.cache_index_file = self.cache_base_dir / "cache_index.json"
        self.integrity_file = self.cache_base_dir / "integrity_checks.json"
        
        # Cache configuration
        self.supported_stages = ['1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '5a', '5b']
        self.stage_dependencies = {
            '1b': ['1a'],
            '2b': ['2a'], 
            '3a': ['1a', '1b', '2a', '2b'],
            '3b': ['3a'],
            '4a': ['3a', '3b'],
            '4b': ['4a'],
            '5a': ['4a', '4b'],  # Plus all previous papers' stage 4 results
            '5b': ['5a']
        }
        
        # Initialize cache structures
        self.cache_index = self._load_cache_index()
        self.integrity_data = self._load_integrity_data()
        
        logging.info(f"StageCacheManager initialized with cache at {self.cache_base_dir}")
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """Load cache index tracking all cached results"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Could not load cache index: {e}")
        
        return {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "papers": {},
            "global_stats": {
                "total_cached_stages": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "cost_saved_usd": 0.0,
                "last_cleanup": None
            }
        }
    
    def _load_integrity_data(self) -> Dict[str, Any]:
        """Load integrity checking data for cache validation"""
        if self.integrity_file.exists():
            try:
                with open(self.integrity_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Could not load integrity data: {e}")
        
        return {
            "paper_hashes": {},
            "prompt_versions": {},
            "api_model_version": "gemini-2.5-flash",
            "last_integrity_check": None
        }
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        self.cache_index["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Could not save cache index: {e}")
    
    def _save_integrity_data(self):
        """Save integrity data to disk"""
        self.integrity_data["last_integrity_check"] = datetime.now().isoformat()
        try:
            with open(self.integrity_file, 'w', encoding='utf-8') as f:
                json.dump(self.integrity_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Could not save integrity data: {e}")
    
    def _generate_paper_hash(self, paper_data: Dict[str, Any]) -> str:
        """Generate hash of paper content for cache invalidation"""
        # Hash the essential paper content
        content_for_hash = {
            "filename": paper_data.get("filename", ""),
            "full_text": paper_data.get("full_text", "")[:1000],  # First 1000 chars
            "table_data": str(paper_data.get("table_data", [])[:3])  # First 3 tables
        }
        content_str = json.dumps(content_for_hash, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _get_paper_cache_dir(self, paper_id: str) -> Path:
        """Get cache directory for specific paper"""
        # Sanitize paper_id for filesystem
        safe_paper_id = "".join(c for c in paper_id if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_paper_id = safe_paper_id.replace(' ', '_')[:100]  # Limit length
        
        paper_dir = self.cache_base_dir / safe_paper_id
        paper_dir.mkdir(exist_ok=True)
        return paper_dir
    
    def _get_stage_cache_file(self, paper_id: str, stage_id: str) -> Path:
        """Get cache file path for specific paper and stage"""
        paper_dir = self._get_paper_cache_dir(paper_id)
        return paper_dir / f"stage_{stage_id}_result.json"
    
    def _get_metadata_file(self, paper_id: str) -> Path:
        """Get metadata file for paper cache"""
        paper_dir = self._get_paper_cache_dir(paper_id)
        return paper_dir / "cache_metadata.json"
    
    def is_stage_cached(self, paper_id: str, stage_id: str) -> bool:
        """Check if stage result is cached and valid"""
        cache_file = self._get_stage_cache_file(paper_id, stage_id)
        return cache_file.exists() and self._is_cache_valid(paper_id, stage_id)
    
    def _is_cache_valid(self, paper_id: str, stage_id: str) -> bool:
        """Check if cached result is still valid (not invalidated by changes)"""
        try:
            # Check if paper is in cache index
            if paper_id not in self.cache_index["papers"]:
                return False
            
            paper_cache_info = self.cache_index["papers"][paper_id]
            if stage_id not in paper_cache_info.get("stages", {}):
                return False
            
            # Check if the cached result indicates success
            stage_info = paper_cache_info["stages"][stage_id]
            if not stage_info.get("success", False):
                return False
            
            return True
        except Exception as e:
            logging.warning(f"Cache validation error for {paper_id} stage {stage_id}: {e}")
            return False
    
    def get_cached_result(self, paper_id: str, stage_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached stage result"""
        if not self.is_stage_cached(paper_id, stage_id):
            self.cache_index["global_stats"]["cache_misses"] += 1
            self._save_cache_index()
            return None
        
        try:
            cache_file = self._get_stage_cache_file(paper_id, stage_id)
            with open(cache_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            # Update cache hit statistics
            self.cache_index["global_stats"]["cache_hits"] += 1
            
            # Estimate cost savings (rough calculation based on stage complexity)
            stage_cost_estimates = {
                '1a': 0.025, '1b': 0.015, '2a': 0.025, '2b': 0.015,
                '3a': 0.030, '3b': 0.020, '4a': 0.025, '4b': 0.015,
                '5a': 0.040, '5b': 0.025
            }
            estimated_savings = stage_cost_estimates.get(stage_id, 0.020)
            self.cache_index["global_stats"]["cost_saved_usd"] += estimated_savings
            
            self._save_cache_index()
            
            logging.info(f"Cache HIT: {paper_id} stage {stage_id} (saved ~${estimated_savings:.3f})")
            return result
            
        except Exception as e:
            logging.error(f"Could not load cached result for {paper_id} stage {stage_id}: {e}")
            self.cache_index["global_stats"]["cache_misses"] += 1
            self._save_cache_index()
            return None
    
    def cache_stage_result(self, paper_id: str, stage_id: str, result: Dict[str, Any], 
                          paper_data: Dict[str, Any]) -> bool:
        """Cache stage result with metadata"""
        try:
            # Save the result
            cache_file = self._get_stage_cache_file(paper_id, stage_id)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Update cache index
            if paper_id not in self.cache_index["papers"]:
                self.cache_index["papers"][paper_id] = {
                    "stages": {},
                    "paper_hash": self._generate_paper_hash(paper_data),
                    "first_cached": datetime.now().isoformat()
                }
            
            # Determine if stage was successful
            # Primary success criteria: no error field and substantial content
            has_error = result.get("error") is not None
            has_content = len(str(result)) > 100
            
            # Additional success indicators for different stage types
            if stage_id in ['1a', '2a']:  # Extraction stages
                has_expected_structure = result.get("paper_metadata") is not None
            elif stage_id in ['1b', '2b', '3b', '4b', '5b']:  # Validation stages  
                has_expected_structure = (result.get("validation_quality") is not None or 
                                        result.get("validation_certification") is not None or
                                        result.get("success") is not None)
            else:
                has_expected_structure = True  # Other stages just need content
            
            stage_success = not has_error and has_content and has_expected_structure
            
            self.cache_index["papers"][paper_id]["stages"][stage_id] = {
                "cached_at": datetime.now().isoformat(),
                "result_size": len(json.dumps(result)),
                "has_error": "error" in result,
                "success": stage_success
            }
            
            self.cache_index["global_stats"]["total_cached_stages"] += 1
            self._save_cache_index()
            
            # Update paper hash in integrity data
            self.integrity_data["paper_hashes"][paper_id] = self._generate_paper_hash(paper_data)
            self._save_integrity_data()
            
            status = "SUCCESS" if stage_success else "ERROR"
            logging.info(f"Cache SAVE: {paper_id} stage {stage_id} ({status})")
            return True
            
        except Exception as e:
            logging.error(f"Could not cache result for {paper_id} stage {stage_id}: {e}")
            return False
    
    def get_paper_completion_status(self, paper_id: str) -> Dict[str, Any]:
        """Get completion status for all stages of a paper"""
        status = {
            "paper_id": paper_id,
            "stages_completed": [],
            "stages_pending": [],
            "completion_percentage": 0.0,
            "has_errors": False,
            "last_completed_stage": None,
            "next_stage_to_process": None
        }
        
        if paper_id in self.cache_index["papers"]:
            paper_info = self.cache_index["papers"][paper_id]
            cached_stages = paper_info.get("stages", {})
            
            for stage_id in self.supported_stages:
                if stage_id in cached_stages:
                    stage_info = cached_stages[stage_id]
                    if stage_info.get("success", False):
                        status["stages_completed"].append(stage_id)
                        status["last_completed_stage"] = stage_id
                    else:
                        status["has_errors"] = True
                        status["stages_pending"].append(stage_id)
                else:
                    status["stages_pending"].append(stage_id)
            
            status["completion_percentage"] = len(status["stages_completed"]) / len(self.supported_stages) * 100
            
            # Determine next stage to process
            status["next_stage_to_process"] = self.get_next_stage_to_process(paper_id)
        else:
            status["stages_pending"] = self.supported_stages.copy()
            status["next_stage_to_process"] = "1a"
        
        return status
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "cache_overview": {
                "total_papers": len(self.cache_index["papers"]),
                "total_cached_stages": self.cache_index["global_stats"]["total_cached_stages"],
                "cache_hits": self.cache_index["global_stats"]["cache_hits"],
                "cache_misses": self.cache_index["global_stats"]["cache_misses"],
                "cost_saved_usd": round(self.cache_index["global_stats"]["cost_saved_usd"], 3),
                "hit_rate": 0.0
            },
            "paper_completion": {},
            "stage_distribution": {},
            "cache_size": self._calculate_cache_size()
        }
        
        # Calculate hit rate
        total_requests = stats["cache_overview"]["cache_hits"] + stats["cache_overview"]["cache_misses"]
        if total_requests > 0:
            stats["cache_overview"]["hit_rate"] = round(stats["cache_overview"]["cache_hits"] / total_requests * 100, 1)
        
        # Paper completion statistics
        for paper_id in self.cache_index["papers"]:
            paper_status = self.get_paper_completion_status(paper_id)
            stats["paper_completion"][paper_id] = {
                "completed_stages": len(paper_status["stages_completed"]),
                "completion_percentage": round(paper_status["completion_percentage"], 1),
                "has_errors": paper_status["has_errors"],
                "next_stage": paper_status["next_stage_to_process"]
            }
        
        # Stage distribution
        stage_counts = {stage: 0 for stage in self.supported_stages}
        for paper_info in self.cache_index["papers"].values():
            for stage_id in paper_info.get("stages", {}):
                if stage_id in stage_counts and paper_info["stages"][stage_id].get("success", False):
                    stage_counts[stage_id] += 1
        stats["stage_distribution"] = stage_counts
        
        return stats
    
    def _calculate_cache_size(self) -> Dict[str, Any]:
        """Calculate total cache size on disk"""
        total_size = 0
        file_count = 0
        
        try:
            for file_path in self.cache_base_dir.rglob("*.json"):
                total_size += file_path.stat().st_size
                file_count += 1
        except Exception as e:
            logging.warning(f"Could not calculate cache size: {e}")
        
        return {
            "total_bytes": total_size,
            "total_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count
        }
    
    def clear_paper_cache(self, paper_id: str) -> bool:
        """Clear all cached results for a specific paper"""
        try:
            paper_dir = self._get_paper_cache_dir(paper_id)
            if paper_dir.exists():
                # Remove all files in paper directory
                for file_path in paper_dir.iterdir():
                    file_path.unlink()
                paper_dir.rmdir()
            
            # Remove from cache index
            if paper_id in self.cache_index["papers"]:
                del self.cache_index["papers"][paper_id]
                self._save_cache_index()
            
            # Remove from integrity data
            if paper_id in self.integrity_data["paper_hashes"]:
                del self.integrity_data["paper_hashes"][paper_id]
                self._save_integrity_data()
            
            logging.info(f"Cleared cache for paper: {paper_id}")
            return True
            
        except Exception as e:
            logging.error(f"Could not clear cache for paper {paper_id}: {e}")
            return False
    
    def clear_stage_cache(self, paper_id: str, stage_id: str) -> bool:
        """Clear cached result for specific paper and stage"""
        try:
            cache_file = self._get_stage_cache_file(paper_id, stage_id)
            if cache_file.exists():
                cache_file.unlink()
            
            # Update cache index
            if (paper_id in self.cache_index["papers"] and 
                stage_id in self.cache_index["papers"][paper_id].get("stages", {})):
                del self.cache_index["papers"][paper_id]["stages"][stage_id]
                self._save_cache_index()
            
            logging.info(f"Cleared cache for {paper_id} stage {stage_id}")
            return True
            
        except Exception as e:
            logging.error(f"Could not clear cache for {paper_id} stage {stage_id}: {e}")
            return False
    
    def get_next_stage_to_process(self, paper_id: str) -> Optional[str]:
        """Determine the next stage that needs to be processed for a paper"""
        for stage_id in self.supported_stages:
            if not self.is_stage_cached(paper_id, stage_id):
                # Check if dependencies are satisfied
                dependencies = self.stage_dependencies.get(stage_id, [])
                deps_satisfied = all(self.is_stage_cached(paper_id, dep) for dep in dependencies)
                
                if deps_satisfied:
                    return stage_id
                else:
                    # Return the first missing dependency
                    for dep in dependencies:
                        if not self.is_stage_cached(paper_id, dep):
                            return dep
        
        return None  # All stages completed
    
    def can_resume_from_stage(self, paper_id: str, stage_id: str) -> Tuple[bool, List[str]]:
        """Check if processing can resume from a specific stage"""
        if stage_id not in self.supported_stages:
            return False, [f"Invalid stage: {stage_id}"]
        
        dependencies = self.stage_dependencies.get(stage_id, [])
        missing_deps = []
        
        for dep_stage in dependencies:
            if not self.is_stage_cached(paper_id, dep_stage):
                missing_deps.append(dep_stage)
        
        can_resume = len(missing_deps) == 0
        return can_resume, missing_deps
    
    def get_all_papers_summary(self) -> Dict[str, Any]:
        """Get summary of all papers in cache"""
        summary = {
            "total_papers": len(self.cache_index["papers"]),
            "papers": {},
            "overall_progress": {
                "stages_completed": 0,
                "total_possible_stages": 0,
                "completion_percentage": 0.0
            }
        }
        
        total_completed = 0
        total_possible = len(self.cache_index["papers"]) * len(self.supported_stages)
        
        for paper_id in self.cache_index["papers"]:
            paper_status = self.get_paper_completion_status(paper_id)
            summary["papers"][paper_id] = {
                "completed": len(paper_status["stages_completed"]),
                "total": len(self.supported_stages),
                "percentage": paper_status["completion_percentage"],
                "next_stage": paper_status["next_stage_to_process"],
                "has_errors": paper_status["has_errors"]
            }
            total_completed += len(paper_status["stages_completed"])
        
        if total_possible > 0:
            summary["overall_progress"]["completion_percentage"] = round(total_completed / total_possible * 100, 1)
        
        summary["overall_progress"]["stages_completed"] = total_completed
        summary["overall_progress"]["total_possible_stages"] = total_possible
        
        return summary