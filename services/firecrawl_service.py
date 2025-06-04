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
            
            if not result:
                raise Exception('Failed to scrape content from the URL')
            
            # Handle both response object and dict formats
            if hasattr(result, 'markdown'):
                # Response object format
                markdown = result.markdown
                metadata = result.metadata if hasattr(result, 'metadata') else {}
            else:
                # Dictionary format
                markdown = result.get('markdown')
                metadata = result.get('metadata', {})
            
            if not markdown:
                raise Exception('No markdown content returned from the URL')
            
            # Extract metadata safely
            if isinstance(metadata, dict):
                source_url = metadata.get('sourceURL', url)
                title = metadata.get('title')
                description = metadata.get('description')
            else:
                source_url = getattr(metadata, 'sourceURL', url) if metadata else url
                title = getattr(metadata, 'title', None) if metadata else None
                description = getattr(metadata, 'description', None) if metadata else None
            
            return {
                'url': source_url,
                'markdown': markdown,
                'title': title,
                'description': description
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
            
            if not crawl_result:
                raise Exception('Failed to crawl website')
            
            # Handle both response object and dict formats
            if hasattr(crawl_result, 'data'):
                data = crawl_result.data
            else:
                data = crawl_result.get('data', [])
            
            if not data:
                raise Exception('No pages were crawled')
            
            results = []
            for item in data:
                # Handle both response object and dict formats for each item
                if hasattr(item, 'markdown'):
                    # Response object format
                    markdown = item.markdown
                    metadata = item.metadata if hasattr(item, 'metadata') else {}
                else:
                    # Dictionary format
                    markdown = item.get('markdown', '')
                    metadata = item.get('metadata', {})
                
                # Extract metadata safely
                if isinstance(metadata, dict):
                    source_url = metadata.get('sourceURL', '')
                    title = metadata.get('title')
                    description = metadata.get('description')
                else:
                    source_url = getattr(metadata, 'sourceURL', '') if metadata else ''
                    title = getattr(metadata, 'title', None) if metadata else None
                    description = getattr(metadata, 'description', None) if metadata else None
                
                results.append({
                    'url': source_url,
                    'markdown': markdown,
                    'title': title,
                    'description': description
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error crawling website {url}: {str(e)}")
            raise Exception(f"Failed to crawl website: {str(e)}") 