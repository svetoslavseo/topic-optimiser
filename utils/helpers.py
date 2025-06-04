import re
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted
    
    Args:
        url: The URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: The text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    return text

def truncate_text(text: str, max_length: int = 150) -> str:
    """
    Truncate text to a maximum length with ellipsis
    
    Args:
        text: The text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length].rstrip() + "..."

def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: The URL to extract domain from
        
    Returns:
        str: Domain name or original URL if extraction fails
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return url

def format_score(score: float) -> str:
    """
    Format score for display
    
    Args:
        score: The score to format
        
    Returns:
        str: Formatted score string
    """
    return f"{score:.1f}%"

def get_score_color(score: float) -> str:
    """
    Get color based on score value
    
    Args:
        score: The score value (0-100)
        
    Returns:
        str: Color code
    """
    if score >= 80:
        return "#22c55e"  # Green
    elif score >= 60:
        return "#ff8c42"  # Orange
    elif score >= 40:
        return "#f59e0b"  # Yellow
    else:
        return "#ef4444"  # Red

def parse_queries(query_text: str) -> List[str]:
    """
    Parse query text into list of individual queries
    
    Args:
        query_text: Multi-line string with queries
        
    Returns:
        List[str]: List of cleaned queries
    """
    if not query_text:
        return []
    
    queries = []
    for line in query_text.split('\n'):
        line = line.strip()
        if line:
            queries.append(line)
    
    return queries

def create_summary_stats(results: Any) -> Dict[str, Any]:
    """
    Create summary statistics from analysis results
    
    Args:
        results: AnalysisResults object
        
    Returns:
        Dict with summary statistics
    """
    if not results:
        return {}
    
    scores = [
        results.embedding_relevance_score,
        results.semantic_density_score,
        results.authority_score
    ]
    
    return {
        'average_score': sum(scores) / len(scores),
        'highest_score': max(scores),
        'lowest_score': min(scores),
        'total_gaps': len(results.semantic_gaps),
        'total_recommendations': len(results.recommendations)
    } 