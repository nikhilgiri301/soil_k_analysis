"""
Iteration control and progress tracking for synthesis processing
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class IterationController:
    """Controls iteration flow and tracks progress through synthesis stages"""
    
    def __init__(self):
        self.tracking_dir = Path("13_iteration_tracking")
        self.logs_dir = self.tracking_dir / "integration_logs"
        self.evolution_dir = self.tracking_dir / "state_evolution"
        self.ensure_directories()
        
        self.current_iteration = 0
        self.total_papers = 0
        self.processing_start_time = None
        self.iteration_log = []
        
    def ensure_directories(self):
        """Ensure tracking directories exist"""
        dirs = [self.tracking_dir, self.logs_dir, self.evolution_dir]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def initialize_processing(self, total_papers: int) -> Dict[str, Any]:
        """Initialize processing session"""
        
        self.total_papers = total_papers
        self.current_iteration = 0
        self.processing_start_time = datetime.now()
        
        session_info = {
            "session_id": self.processing_start_time.strftime("%Y%m%d_%H%M%S"),
            "total_papers": total_papers,
            "start_time": self.processing_start_time.isoformat(),
            "estimated_duration_minutes": total_papers * 2,  # Rough estimate
            "processing_mode": "iterative_synthesis"
        }
        
        # Save session info
        session_file = self.tracking_dir / f"session_{session_info['session_id']}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2)
        
        logging.info(f"Processing session initialized: {total_papers} papers")
        return session_info
    
    def start_paper_iteration(self, paper_id: str, paper_index: int) -> Dict[str, Any]:
        """Start processing iteration for a paper"""
        
        self.current_iteration = paper_index
        
        iteration_info = {
            "iteration_number": paper_index + 1,
            "paper_id": paper_id,
            "paper_index": paper_index,
            "start_time": datetime.now().isoformat(),
            "progress_percentage": (paper_index / self.total_papers) * 100,
            "estimated_remaining_minutes": (self.total_papers - paper_index - 1) * 2
        }
        
        self.iteration_log.append(iteration_info)
        
        logging.info(f"Started iteration {iteration_info['iteration_number']}/{self.total_papers}: {paper_id}")
        return iteration_info
    
    def complete_paper_iteration(self, paper_id: str, paper_index: int, 
                                success: bool, processing_time_seconds: float) -> Dict[str, Any]:
        """Complete processing iteration for a paper"""
        
        completion_info = {
            "iteration_number": paper_index + 1,
            "paper_id": paper_id,
            "paper_index": paper_index,
            "completion_time": datetime.now().isoformat(),
            "success": success,
            "processing_time_seconds": processing_time_seconds,
            "cumulative_progress": (paper_index + 1) / self.total_papers
        }
        
        # Update iteration log
        for iteration in self.iteration_log:
            if iteration["paper_index"] == paper_index:
                iteration.update(completion_info)
                break
        
        # Save iteration details
        iteration_file = self.logs_dir / f"iteration_{paper_index:03d}_{paper_id.replace('.pdf', '')}.json"
        with open(iteration_file, 'w', encoding='utf-8') as f:
            json.dump(completion_info, f, indent=2)
        
        status = "✅" if success else "❌"
        logging.info(f"{status} Completed iteration {paper_index + 1}/{self.total_papers}: {paper_id} ({processing_time_seconds:.1f}s)")
        
        return completion_info
    
    def track_synthesis_evolution(self, paper_index: int, paper_id: str, 
                                 synthesis_state: Dict[str, Any]) -> None:
        """Track how synthesis state evolves with each paper"""
        
        evolution_snapshot = {
            "paper_index": paper_index,
            "paper_id": paper_id,
            "timestamp": datetime.now().isoformat(),
            "papers_integrated": synthesis_state.get("synthesis_metadata", {}).get("papers_integrated", 0),
            "overall_confidence": synthesis_state.get("confidence_tracking", {}).get("overall_confidence", 0.0),
            "pattern_count": len(synthesis_state.get("pattern_recognition", {}).get("emerging_patterns", [])),
            "conflict_count": len(synthesis_state.get("conflict_registry", {}).get("identified_conflicts", [])),
            "evidence_gap_count": len(synthesis_state.get("evidence_gaps", {}).get("critical_gaps", []))
        }
        
        evolution_file = self.evolution_dir / f"evolution_{paper_index:03d}.json"
        with open(evolution_file, 'w', encoding='utf-8') as f:
            json.dump(evolution_snapshot, f, indent=2)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        
        if not self.processing_start_time:
            return {"status": "not_started"}
        
        current_time = datetime.now()
        elapsed_time = (current_time - self.processing_start_time).total_seconds()
        
        completed_iterations = len([it for it in self.iteration_log if it.get("success", False)])
        failed_iterations = len([it for it in self.iteration_log if it.get("success") == False])
        
        return {
            "status": "in_progress" if self.current_iteration < self.total_papers else "completed",
            "total_papers": self.total_papers,
            "current_iteration": self.current_iteration + 1,
            "completed_successfully": completed_iterations,
            "failed": failed_iterations,
            "progress_percentage": (self.current_iteration / self.total_papers) * 100,
            "elapsed_time_minutes": elapsed_time / 60,
            "average_time_per_paper": elapsed_time / max(self.current_iteration, 1),
            "estimated_remaining_minutes": ((self.total_papers - self.current_iteration) * 
                                          (elapsed_time / max(self.current_iteration, 1))) / 60
        }
    
    def generate_processing_summary(self) -> Dict[str, Any]:
        """Generate final processing summary"""
        
        stats = self.get_processing_stats()
        
        summary = {
            "processing_summary": stats,
            "iteration_details": self.iteration_log,
            "session_start": self.processing_start_time.isoformat() if self.processing_start_time else None,
            "session_end": datetime.now().isoformat(),
            "total_processing_time_minutes": stats.get("elapsed_time_minutes", 0),
            "success_rate": stats.get("completed_successfully", 0) / self.total_papers if self.total_papers > 0 else 0
        }
        
        # Save summary
        summary_file = self.tracking_dir / f"processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logging.info(f"Processing summary generated: {summary['success_rate']:.1%} success rate")
        return summary 
