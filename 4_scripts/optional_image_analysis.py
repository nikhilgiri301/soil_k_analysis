import os
import json
import pymupdf
import re
from datetime import datetime

class ImageAnalysisProcessor:
    def __init__(self, source_dir="1_source_pdfs", output_dir="5_optional_images"):
        self.source_dir = source_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def analyze_images_in_text(self, pdf_path):
        """Analyze if paper contains data-relevant images based on text context"""
        
        pdf = pymupdf.open(pdf_path)
        filename = os.path.basename(pdf_path)
        
        analysis_result = {
            "filename": filename,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_images": 0,
            "potentially_relevant_images": 0,
            "figure_references": [],
            "recommendation": "skip"  # skip, analyze, manual_review
        }
        
        # Count total images
        total_images = sum(len(page.get_images()) for page in pdf)
        analysis_result["total_images"] = total_images
        
        if total_images == 0:
            analysis_result["recommendation"] = "skip"
            return analysis_result
        
        # Analyze text for figure references and data indicators
        full_text = ""
        for page in pdf:
            full_text += page.get_text()
        
        # Look for figure references
        figure_patterns = [
            r'figure\s+\d+[:\.]?\s*([^\n\.]{0,100})',
            r'fig\.\s*\d+[:\.]?\s*([^\n\.]{0,100})',
        ]
        
        figure_refs = []
        for pattern in figure_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                figure_refs.append({
                    "reference": match.group(0),
                    "caption": match.group(1).strip()
                })
        
        analysis_result["figure_references"] = figure_refs
        
        # Check for data-related terms in figure contexts
        data_chart_indicators = [
            'correlation', 'regression', 'trend', 'versus', 'vs.', 
            'relationship', 'distribution', 'comparison', 'analysis',
            'plot', 'chart', 'graph', 'statistical'
        ]
        
        relevant_figures = 0
        for fig_ref in figure_refs:
            caption_lower = fig_ref["caption"].lower()
            if any(indicator in caption_lower for indicator in data_chart_indicators):
                relevant_figures += 1
        
        analysis_result["potentially_relevant_images"] = relevant_figures
        
        # Make recommendation
        if relevant_figures > 0:
            analysis_result["recommendation"] = "analyze"
        elif total_images > 20 and len(figure_refs) > 5:
            analysis_result["recommendation"] = "manual_review"
        else:
            analysis_result["recommendation"] = "skip"
        
        pdf.close()
        return analysis_result
    
    def analyze_all_papers(self):
        """Analyze all papers for image relevance"""
        pdf_files = [f for f in os.listdir(self.source_dir) if f.endswith('.pdf')]
        
        results = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.source_dir, pdf_file)
            analysis = self.analyze_images_in_text(pdf_path)
            results.append(analysis)
        
        # Save analysis results
        with open(f"{self.output_dir}/image_analysis_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate summary
        analyze_count = sum(1 for r in results if r["recommendation"] == "analyze")
        review_count = sum(1 for r in results if r["recommendation"] == "manual_review")
        skip_count = sum(1 for r in results if r["recommendation"] == "skip")
        
        summary = f"""
# Image Analysis Summary

## Recommendations:
- Analyze (likely contains data charts): {analyze_count} papers
- Manual review needed: {review_count} papers  
- Skip (photos/irrelevant): {skip_count} papers

## Papers recommended for image analysis:
"""
        
        for result in results:
            if result["recommendation"] == "analyze":
                summary += f"- {result['filename']} ({result['potentially_relevant_images']} relevant figures)\n"
        
        with open(f"{self.output_dir}/image_analysis_summary.md", 'w') as f:
            f.write(summary)
        
        print(f"Image analysis complete. Summary: {self.output_dir}/image_analysis_summary.md")
        return results

if __name__ == "__main__":
    analyzer = ImageAnalysisProcessor()
    results = analyzer.analyze_all_papers()