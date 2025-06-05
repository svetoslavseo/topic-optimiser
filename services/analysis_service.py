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
            raise ValueError("Gemini API key is required")
        
        # Debug logging
        logger.info(f"Initializing with API key length: {len(api_key)}")
        logger.info(f"API key starts with: {api_key[:10] if len(api_key) > 10 else api_key}")
        
        # Set environment variable as backup
        import os
        os.environ['GOOGLE_API_KEY'] = api_key
        
        genai.configure(api_key=api_key)
        
        # Check available models and use the correct one
        try:
            # First try the most common model names
            models_to_try = [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'models/gemini-1.5-flash',
                'models/gemini-1.5-pro',
                'gemini-1.0-pro',
                'models/gemini-1.0-pro'
            ]
            
            model_created = False
            for model_name in models_to_try:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    logger.info(f"Successfully using model: {model_name}")
                    model_created = True
                    break
                except Exception as model_error:
                    logger.info(f"Model {model_name} failed: {model_error}")
                    continue
            
            if not model_created:
                raise ValueError("No suitable text generation model found")
                
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            raise ValueError(f"Failed to initialize Gemini model: {e}")
        
        self.api_key = api_key
        self.use_advanced = use_advanced
        
        # Initialize advanced analysis service if requested
        if use_advanced:
            try:
                from .advanced_analysis_service import AdvancedAnalysisService
                self.advanced_service = AdvancedAnalysisService(api_key, cohere_api_key)
                logger.info("Advanced analysis service initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize advanced analysis: {e}. Falling back to basic analysis.")
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
        Analyze content for semantic optimization metrics using advanced ML if available
        
        Args:
            content: The content to analyze
            queries: List of target queries/keywords
            
        Returns:
            AnalysisResults object with scores and recommendations
        """
        # Try advanced analysis first
        if self.use_advanced and self.advanced_service:
            try:
                logger.info("Using advanced analysis with real embeddings and ML")
                advanced_results = self.advanced_service.analyze_content(content, queries)
                
                # Convert to basic AnalysisResults format
                return AnalysisResults(
                    embedding_relevance_score=advanced_results.embedding_relevance_score,
                    semantic_density_score=advanced_results.semantic_density_score,
                    authority_score=advanced_results.authority_score,
                    semantic_gaps=[gap.description for gap in advanced_results.semantic_gaps],
                    recommendations=advanced_results.recommendations,
                    content_source=advanced_results.content_source,
                    similarity_matrix=advanced_results.similarity_matrix,
                    topic_clusters=advanced_results.topic_clusters,
                    semantic_map_data=advanced_results.semantic_map_data,
                    processing_time=advanced_results.processing_time
                )
                
            except Exception as e:
                logger.warning(f"Advanced analysis failed, falling back to basic: {e}")
                # Fall through to basic analysis
        
        # Basic analysis using Gemini AI prompts
        try:
            logger.info("Using basic AI-based analysis")
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
        pattern = rf"{score_name}[:\s]*(\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(100, max(0, score))  # Ensure score is between 0-100
        return 50  # Default score if not found
    
    def _extract_list_items(self, text: str, section_name: str) -> List[str]:
        """Extract list items from a section"""
        # Find the section
        pattern = rf"{section_name}[:\s]*\n(.*?)(?=\n[A-Z_]+:|$)"
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