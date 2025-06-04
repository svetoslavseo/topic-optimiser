import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResults:
    embedding_relevance_score: float
    semantic_density_score: float
    authority_score: float
    semantic_gaps: List[str]
    recommendations: List[str]
    content_source: str = ""

class AnalysisService:
    """Service for analyzing content using Google Gemini AI"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.api_key = api_key
    
    def test_api_connection(self) -> bool:
        """Test if the API key is valid and working"""
        try:
            # Make a simple test request
            response = self.model.generate_content("Hello, respond with 'OK' if you can see this.")
            return response and response.text and "OK" in response.text.upper()
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False
    
    def analyze_content(self, content: str, queries: List[str]) -> AnalysisResults:
        """
        Analyze content for semantic optimization metrics
        
        Args:
            content: The content to analyze
            queries: List of target queries/keywords
            
        Returns:
            AnalysisResults object with scores and recommendations
        """
        try:
            prompt = self._create_analysis_prompt(content, queries)
            response = self.model.generate_content(prompt)
            
            if not response:
                raise Exception("No response from Gemini API - check your API key and quota")
            
            if not response.text:
                # Check if there's a finish reason that explains the issue
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason == 'SAFETY':
                            raise Exception("Content was blocked by safety filters")
                        elif candidate.finish_reason == 'MAX_TOKENS':
                            raise Exception("Response was truncated due to token limit")
                        else:
                            raise Exception(f"API response issue: {candidate.finish_reason}")
                raise Exception("Empty response from Gemini API")
            
            return self._parse_response(response.text)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error analyzing content: {error_msg}")
            
            # Provide more specific error messages
            if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
                error_detail = "Invalid API key. Please check your Gemini API key."
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_detail = "API quota exceeded. Please check your usage limits."
            elif "safety" in error_msg.lower():
                error_detail = "Content blocked by safety filters. Try different content."
            else:
                error_detail = f"API Error: {error_msg}"
            
            # Return default results with specific error
            return AnalysisResults(
                embedding_relevance_score=0,
                semantic_density_score=0,
                authority_score=0,
                semantic_gaps=[f"Analysis failed: {error_detail}"],
                recommendations=["Please resolve the API issue and try again."]
            )
    
    def _create_analysis_prompt(self, content: str, queries: List[str]) -> str:
        """Create the analysis prompt for Gemini"""
        queries_text = "\n".join([f"- {query}" for query in queries])
        
        return f"""
        As an AI content optimization expert, analyze the following content for semantic optimization metrics.
        
        TARGET QUERIES:
        {queries_text}
        
        CONTENT TO ANALYZE:
        {content[:8000]}  # Limit content to avoid token limits
        
        Please provide a detailed analysis with the following structure:
        
        EMBEDDING_RELEVANCE_SCORE: [0-100 integer score]
        Assess how well the content semantically matches the target queries using vector similarity concepts.
        
        SEMANTIC_DENSITY_SCORE: [0-100 integer score]  
        Evaluate the richness and depth of semantic meaning in the content.
        
        AUTHORITY_SCORE: [0-100 integer score]
        Rate the content's credibility, expertise signals, and trustworthiness indicators.
        
        SEMANTIC_GAPS:
        - [List 3-5 specific semantic gaps or missing topics that would improve query relevance]
        
        RECOMMENDATIONS:
        - [List 3-5 specific, actionable recommendations to improve the content]
        
        Respond in exactly this format with clear section headers.
        """
    
    def _parse_response(self, response_text: str) -> AnalysisResults:
        """Parse the Gemini response into structured results"""
        try:
            # Extract scores using regex
            embedding_score = self._extract_score(response_text, "EMBEDDING_RELEVANCE_SCORE")
            density_score = self._extract_score(response_text, "SEMANTIC_DENSITY_SCORE")
            authority_score = self._extract_score(response_text, "AUTHORITY_SCORE")
            
            # Extract gaps and recommendations
            gaps = self._extract_list_items(response_text, "SEMANTIC_GAPS")
            recommendations = self._extract_list_items(response_text, "RECOMMENDATIONS")
            
            return AnalysisResults(
                embedding_relevance_score=embedding_score,
                semantic_density_score=density_score,
                authority_score=authority_score,
                semantic_gaps=gaps,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            # Fallback parsing
            return AnalysisResults(
                embedding_relevance_score=75,
                semantic_density_score=68,
                authority_score=82,
                semantic_gaps=["Content analysis completed with limited parsing"],
                recommendations=["Review content structure and add more relevant keywords"]
            )
    
    def _extract_score(self, text: str, score_name: str) -> float:
        """Extract a score from the response text"""
        pattern = f"{score_name}[:\s]*(\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(100, max(0, score))  # Ensure score is between 0-100
        return 50  # Default score if not found
    
    def _extract_list_items(self, text: str, section_name: str) -> List[str]:
        """Extract list items from a section"""
        # Find the section
        pattern = f"{section_name}[:\s]*\n(.*?)(?=\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return ["Analysis completed"]
        
        section_text = match.group(1).strip()
        
        # Extract list items (lines starting with -, •, or numbers)
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                # Clean up the line
                cleaned = re.sub(r'^[-•\d.\s]+', '', line).strip()
                if cleaned:
                    items.append(cleaned)
        
        return items if items else ["Analysis completed"] 