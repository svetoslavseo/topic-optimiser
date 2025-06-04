from firecrawl import FirecrawlApp
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FirecrawlService:
    """Service for web crawling using Firecrawl API"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Firecrawl API key is required")
        self.app = FirecrawlApp(api_key=api_key)
    
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
            
            if not result or not result.get('markdown'):
                raise Exception('Failed to scrape content from the URL')
            
            return {
                'url': result.get('metadata', {}).get('sourceURL', url),
                'markdown': result['markdown'],
                'title': result.get('metadata', {}).get('title'),
                'description': result.get('metadata', {}).get('description')
            }
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise Exception(f"Failed to crawl URL: {str(e)}")
    
    def crawl_website(self, url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Crawl multiple pages from a website
        
        Args:
            url: The base URL to crawl
            max_pages: Maximum number of pages to crawl
            
        Returns:
            List of dicts containing crawled page data
        """
        try:
            crawl_result = self.app.crawl_url(
                url,
                limit=max_pages,
                scrape_options={
                    'formats': ['markdown'],
                    'only_main_content': True
                }
            )
            
            if not crawl_result or not crawl_result.get('data'):
                raise Exception('Failed to crawl website')
            
            results = []
            for item in crawl_result['data']:
                results.append({
                    'url': item.get('metadata', {}).get('sourceURL', ''),
                    'markdown': item.get('markdown', ''),
                    'title': item.get('metadata', {}).get('title'),
                    'description': item.get('metadata', {}).get('description')
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error crawling website {url}: {str(e)}")
            raise Exception(f"Failed to crawl website: {str(e)}") 