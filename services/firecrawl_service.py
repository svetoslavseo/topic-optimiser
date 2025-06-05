from firecrawl import FirecrawlApp
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FirecrawlService:
    """Service for web scraping using Firecrawl API"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Firecrawl API key is required")
        self.app = FirecrawlApp(api_key=api_key)
    
    def _extract_dict_data(self, obj: Any) -> Dict[str, Any]:
        """
        Helper method to extract dictionary data from various object types
        including Pydantic models (v1 and v2)
        """
        if isinstance(obj, dict):
            return obj
        elif hasattr(obj, 'model_dump'):  # Pydantic v2
            return obj.model_dump()
        elif hasattr(obj, 'dict'):  # Pydantic v1
            return obj.dict()
        elif hasattr(obj, '__dict__'):  # Regular object
            return obj.__dict__
        else:
            return {}
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single URL and return the content
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dict containing url, markdown, title, and description
        """
        try:
            result = self.app.scrape_url(
                url,
                formats=['markdown'],
                only_main_content=True
            )
            
            if not result:
                raise Exception('Failed to scrape content from the URL')
            
            # Convert result to dictionary safely
            result_dict = self._extract_dict_data(result)
            
            markdown = result_dict.get('markdown', '')
            metadata = result_dict.get('metadata', {})
            
            if not markdown:
                raise Exception('No markdown content returned from the URL')
            
            # Convert metadata to dictionary safely
            metadata_dict = self._extract_dict_data(metadata)
            
            return {
                'url': metadata_dict.get('sourceURL', url),
                'markdown': markdown,
                'title': metadata_dict.get('title'),
                'description': metadata_dict.get('description')
            }
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise Exception(f"Failed to scrape URL: {str(e)}") 