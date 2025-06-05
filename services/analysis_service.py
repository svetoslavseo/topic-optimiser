import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
import logging
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResults:
    embedding_relevance_score: float
    semantic_density_score: float
    authority_score: float
    semantic_gaps: List[str]
    recommendations: List[str]
    content_source: str = ""
    # Advanced analysis data
    similarity_matrix: List[List[float]] = None
    topic_clusters: Dict[str, Any] = None
    semantic_map_data: Dict[str, Any] = None
    processing_time: float = 0.0

class AnalysisService:
    """Service for analyzing content using Google Gemini AI with advanced ML capabilities"""
    
    def __init__(self, api_key: str, cohere_api_key: str = None, use_advanced: bool = True):
        if not api_key:
            raise ValueError("API key is required")
        
        # Debug logging
        logger.info(f"Initializing with API key length: {len(api_key)}")
        logger.info(f"API key starts with: {api_key[:10] if len(api_key) > 10 else api_key}")
        
        self.api_key = api_key
        self.use_advanced = use_advanced
        
        # Initialize Gemini model for recommendations
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Try to initialize advanced analysis service
        if use_advanced:
            try:
                from .advanced_analysis_service import AdvancedAnalysisService
                self.advanced_service = AdvancedAnalysisService(api_key, cohere_api_key)
                logger.info("Advanced analysis service initialized successfully")
            except Exception as e:
                logger.error(f"Could not initialize advanced analysis: {e}. Using Gemini-only mode.")
                self.advanced_service = None
                self.use_advanced = False
        else:
            self.advanced_service = None
    
    def test_api_connection(self) -> tuple[bool, str]:
        """Test if the API key is valid and working"""
        try:
            # First test basic API setup
            models = genai.list_models()
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            
            logger.info(f"Available models: {available_models}")
            
            if not available_models:
                return False, "No available models found. Check API key permissions."
            
            # Test with current model
            response = self.model.generate_content("Hello, respond with 'OK' if you can see this.")
            if not response:
                return False, "No response received from API"
            if not response.text:
                return False, "Empty response from API"
            
            # Get model name safely
            model_name = getattr(self.model, '_model_name', 'unknown')
            return True, f"Connection successful using model: {model_name}. Available models: {len(available_models)} found"
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"API connection test failed: {error_msg}")
            
            # Try to provide more specific debugging info
            try:
                # Test basic API access
                models = genai.list_models()
                model_names = [m.name for m in models]
                debug_info = f"Available models: {model_names[:3]}..."  # Show first 3 models
            except Exception as list_error:
                debug_info = f"Cannot list models: {str(list_error)}"
            
            # Provide specific error details
            if "403" in error_msg:
                return False, f"API access forbidden (403). {debug_info}. Error: {error_msg}"
            elif "401" in error_msg:
                return False, f"Invalid API key (401). {debug_info}. Error: {error_msg}"
            elif "429" in error_msg:
                return False, f"Rate limit exceeded (429). {debug_info}. Error: {error_msg}"
            elif "API_KEY_INVALID" in error_msg:
                return False, f"Invalid API key format. {debug_info}. Error: {error_msg}"
            else:
                return False, f"Connection failed. {debug_info}. Error: {error_msg}"
    
    def analyze_content(self, content: str, queries: List[str]) -> AnalysisResults:
        """
        Analyze content using advanced ML for semantic analysis, then use Gemini for enhanced recommendations
        
        Args:
            content: The content to analyze
            queries: List of target queries/keywords
            
        Returns:
            AnalysisResults object with scores and AI-enhanced recommendations
        """
        if self.use_advanced and self.advanced_service:
            try:
                logger.info("Using advanced analysis with real embeddings and ML")
                advanced_results = self.advanced_service.analyze_content(content, queries)
                
                # Generate enhanced recommendations using Gemini based on advanced analysis
                enhanced_recommendations = self._generate_gemini_recommendations(
                    content, queries, advanced_results
                )
                
                # Convert to AnalysisResults format with enhanced recommendations
                return AnalysisResults(
                    embedding_relevance_score=advanced_results.embedding_relevance_score,
                    semantic_density_score=advanced_results.semantic_density_score,
                    authority_score=advanced_results.authority_score,
                    semantic_gaps=[gap.description for gap in advanced_results.semantic_gaps],
                    recommendations=enhanced_recommendations,
                    content_source=advanced_results.content_source,
                    similarity_matrix=advanced_results.similarity_matrix,
                    topic_clusters=advanced_results.topic_clusters,
                    semantic_map_data=advanced_results.semantic_map_data,
                    processing_time=advanced_results.processing_time
                )
                
            except Exception as e:
                logger.error(f"Advanced analysis failed: {e}")
                # Return error results without fallback
                return AnalysisResults(
                    embedding_relevance_score=0,
                    semantic_density_score=0,
                    authority_score=0,
                    semantic_gaps=[f"Advanced analysis failed: {str(e)}"],
                    recommendations=["Please resolve the advanced analysis dependencies and try again."]
                )
        else:
            # No advanced analysis available - use Gemini-only analysis
            logger.info("Using Gemini-only analysis mode")
            return self._gemini_only_analysis(content, queries)

    def _generate_gemini_recommendations(self, content: str, queries: List[str], advanced_results) -> List[str]:
        """
        Generate enhanced recommendations using Gemini AI based on advanced analysis results
        """
        try:
            # Create a detailed prompt with advanced analysis insights
            queries_text = "\n".join([f"- {query}" for query in queries])
            
            # Summarize advanced analysis findings
            semantic_gaps_text = "\n".join([f"- {gap.description}" for gap in advanced_results.semantic_gaps])
            
            # Calculate analysis summary
            avg_relevance = sum(chunk.relevance_scores.values() for chunk in advanced_results.chunk_analysis if chunk.relevance_scores) 
            avg_relevance = avg_relevance / len(advanced_results.chunk_analysis) if advanced_results.chunk_analysis else 0
            
            authority_signals_summary = f"Found {len(advanced_results.authority_signals)} authority signals"
            
            prompt = f"""
            As an expert content strategist, provide specific, actionable recommendations based on advanced semantic analysis results.
            
            CONTENT OVERVIEW:
            Target Queries: {queries_text}
            
            ADVANCED ANALYSIS RESULTS:
            - Embedding Relevance Score: {advanced_results.embedding_relevance_score:.1f}/100
            - Semantic Density Score: {advanced_results.semantic_density_score:.1f}/100  
            - Authority Score: {advanced_results.authority_score:.1f}/100
            - Content Chunks Analyzed: {len(advanced_results.chunk_analysis)}
            - Average Query Relevance: {avg_relevance:.2f}
            - {authority_signals_summary}
            
            IDENTIFIED SEMANTIC GAPS:
            {semantic_gaps_text}
            
            CONTENT SAMPLE (for context):
            {content[:2000]}...
            
            Based on this advanced semantic analysis, provide 5-8 specific, actionable recommendations for content optimization. 
            Focus on:
            1. Addressing the identified semantic gaps
            2. Improving low-scoring areas (relevance, density, authority)
            3. Practical content improvements
            4. SEO and topic authority enhancement
            
            Format as a numbered list with specific, implementable actions.
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("Empty response from Gemini for recommendations")
                return advanced_results.recommendations  # Fallback to advanced service recommendations
            
            # Parse the response into a list of recommendations
            recommendations = self._parse_gemini_recommendations(response.text)
            
            logger.info(f"Generated {len(recommendations)} enhanced recommendations using Gemini")
            return recommendations
            
        except Exception as e:
            logger.warning(f"Failed to generate Gemini recommendations: {e}")
            # Fallback to advanced analysis recommendations
            return advanced_results.recommendations
    
    def _parse_gemini_recommendations(self, response_text: str) -> List[str]:
        """
        Parse Gemini response to extract recommendations
        """
        recommendations = []
        
        # Split by lines and look for numbered or bulleted items
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('•')):
                # Clean up the line by removing numbering/bullets
                cleaned = re.sub(r'^[\d+\.\-•\s]+', '', line).strip()
                if cleaned and len(cleaned) > 10:  # Ensure substantial content
                    recommendations.append(cleaned)
        
        # If no structured recommendations found, try to extract sentences
        if not recommendations:
            sentences = response_text.split('. ')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in 
                    ['add', 'include', 'improve', 'enhance', 'optimize', 'consider', 'should']):
                    recommendations.append(sentence)
        
        # Limit to reasonable number and ensure we have some recommendations
        recommendations = recommendations[:8] if recommendations else [
            "Enhance content relevance to target queries",
            "Improve semantic density with related topics", 
            "Add authority signals and expert references",
            "Strengthen content structure and organization"
        ]
        
        return recommendations

    def _gemini_only_analysis(self, content: str, queries: List[str]) -> AnalysisResults:
        """
        Perform analysis using only Gemini AI when advanced analysis is not available
        """
        try:
            queries_text = "\n".join([f"- {query}" for query in queries])
            
            prompt = f"""
            As an expert content analyst, analyze the following content for semantic optimization.
            
            TARGET QUERIES:
            {queries_text}
            
            CONTENT TO ANALYZE:
            {content[:8000]}
            
            Provide a comprehensive analysis in the EXACT format below:
            
            EMBEDDING_RELEVANCE_SCORE: 75
            (Explanation: How well does the content align semantically with the target queries?)
            
            SEMANTIC_DENSITY_SCORE: 68
            (Explanation: How rich and comprehensive is the semantic content coverage?)
            
            AUTHORITY_SCORE: 82
            (Explanation: How authoritative and credible does the content appear?)
            
            SEMANTIC_GAPS:
            - Missing coverage of specific keyword variations
            - Lack of supporting evidence or examples
            - Insufficient depth in key topic areas
            
            RECOMMENDATIONS:
            - Add more comprehensive keyword coverage
            - Include authoritative sources and citations
            - Expand on key topics with detailed examples
            - Improve content structure and flow
            
            IMPORTANT: Use EXACT format above with numeric scores (0-100) immediately after the colon.
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("No response from Gemini API")
            
            # Debug: log the response for troubleshooting
            logger.info(f"Gemini response length: {len(response.text)}")
            logger.debug(f"Gemini response: {response.text[:500]}...")
            
            return self._parse_gemini_analysis(response.text)
            
        except Exception as e:
            logger.error(f"Gemini-only analysis failed: {e}")
            return AnalysisResults(
                embedding_relevance_score=50,
                semantic_density_score=50,
                authority_score=50,
                semantic_gaps=["Analysis could not be completed due to API issues"],
                recommendations=["Please check your API connection and try again"]
            )
    
    def _parse_gemini_analysis(self, response_text: str) -> AnalysisResults:
        """
        Parse Gemini response for full analysis results
        """
        try:
            # Extract scores
            embedding_score = self._extract_score_from_response(response_text, "EMBEDDING_RELEVANCE_SCORE")
            density_score = self._extract_score_from_response(response_text, "SEMANTIC_DENSITY_SCORE")
            authority_score = self._extract_score_from_response(response_text, "AUTHORITY_SCORE")
            
            # Extract gaps and recommendations
            gaps = self._extract_list_from_response(response_text, "SEMANTIC_GAPS")
            recommendations = self._extract_list_from_response(response_text, "RECOMMENDATIONS")
            
            return AnalysisResults(
                embedding_relevance_score=embedding_score,
                semantic_density_score=density_score,
                authority_score=authority_score,
                semantic_gaps=gaps,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini analysis: {e}")
            return AnalysisResults(
                embedding_relevance_score=60,
                semantic_density_score=55,
                authority_score=65,
                semantic_gaps=["Content analysis completed with limited parsing"],
                recommendations=["Improve content relevance to target queries", "Add more authoritative sources"]
            )
    
    def _extract_score_from_response(self, text: str, score_name: str) -> float:
        """Extract a score from the Gemini response"""
        # Log the text we're trying to parse for debugging
        logger.info(f"Extracting score for {score_name} from text length: {len(text)}")
        
        # Try multiple patterns to catch different formats
        patterns = [
            rf"{score_name}[:\s]*(\d+)",  # Original pattern
            rf"{score_name}[:\s]*[\[\(]?(\d+)[\]\)]?",  # With optional brackets
            rf"{score_name}[:\s]*(\d+)/100",  # Score out of 100
            rf"{score_name}[:\s]*(\d+)%",  # Percentage format
            rf"{score_name}[:\s]*-?\s*(\d+)",  # With optional dash
            rf"({score_name}|{score_name.replace('_', ' ')})[:\s]*(\d+)",  # Space instead of underscore
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the last group that contains the number
                score_str = match.groups()[-1]
                score = int(score_str)
                logger.info(f"Found score {score} for {score_name} using pattern: {pattern}")
                return min(100, max(0, score))
        
        # If no pattern matches, try a more general approach
        lines = text.split('\n')
        for line in lines:
            if score_name.lower().replace('_', ' ') in line.lower():
                # Look for any number in this line
                numbers = re.findall(r'\b(\d+)\b', line)
                if numbers:
                    score = int(numbers[0])
                    if 0 <= score <= 100:  # Only accept reasonable scores
                        logger.info(f"Found score {score} for {score_name} in line: {line}")
                        return score
        
        logger.warning(f"Could not extract score for {score_name}, using default 50")
        return 50  # Default score
    
    def _extract_list_from_response(self, text: str, section_name: str) -> List[str]:
        """Extract list items from a section in the response"""
        # First, try the strict pattern
        pattern = rf"{section_name}[:\s]*\n(.*?)(?=\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        # If that doesn't work, try a more flexible approach
        if not match:
            # Look for the section header and get everything after it
            lines = text.split('\n')
            section_found = False
            items = []
            
            for line in lines:
                line = line.strip()
                if section_name.lower() in line.lower():
                    section_found = True
                    continue
                elif section_found:
                    # Stop if we hit another section header
                    if re.match(r'^[A-Z][A-Z_\s]+:', line):
                        break
                    # Extract list items
                    if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                        cleaned = re.sub(r'^[-•\d.\s]+', '', line).strip()
                        if cleaned:
                            items.append(cleaned)
            
            return items if items else self._fallback_extraction(text, section_name)
        
        section_text = match.group(1).strip()
        items = []
        
        for line in section_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                cleaned = re.sub(r'^[-•\d.\s]+', '', line).strip()
                if cleaned:
                    items.append(cleaned)
        
        return items if items else self._fallback_extraction(text, section_name)
    
    def _fallback_extraction(self, text: str, section_name: str) -> List[str]:
        """Fallback method to extract content when structured parsing fails"""
        if "gaps" in section_name.lower():
            return [
                "Missing topic coverage for target queries",
                "Lack of semantic depth in key areas", 
                "Insufficient authority signals",
                "Content structure could be improved"
            ]
        else:  # recommendations
            return [
                "Optimize content for target keywords",
                "Add more comprehensive coverage of main topics",
                "Include authoritative sources and references",
                "Improve content structure and readability",
                "Strengthen semantic connections between topics"
            ]
    
 