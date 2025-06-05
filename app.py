import streamlit as st
import os
from typing import Dict, List, Any
import asyncio
from dataclasses import dataclass
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import custom modules
from services.firecrawl_service import FirecrawlService
from services.analysis_service import AnalysisService
from components.metrics_charts import create_metrics_chart
from components.advanced_charts import (
    create_similarity_heatmap, create_semantic_map, create_topic_cluster_chart,
    create_authority_signals_chart, create_semantic_gaps_chart, create_processing_metrics_chart
)
from utils.helpers import validate_url

# Configure Streamlit page
st.set_page_config(
    page_title="AI-Powered Topic Optimiser",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: white;
        color: black;
    }
    
    .stApp {
        background-color: white;
    }
    
    .title {
        color: #2c3e50;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        color: #7f8c8d;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: black;
    }
    
    .metric-header {
        color: #2c3e50;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-description {
        color: #495057;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    .footer {
        text-align: center;
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #dee2e6;
    }
    
    .crawl-info {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1565c0;
    }
    
    .api-key-section {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

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

def main():
    # Header
    st.markdown('<h1 class="title">AI-Powered Topic Optimiser</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'content' not in st.session_state:
        st.session_state.content = ""
    if 'content_source' not in st.session_state:
        st.session_state.content_source = ""
    
    # Main container
    with st.container():
        # Input mode selection
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Manual Input", key="manual_mode"):
                st.session_state.input_mode = "manual"
        with col2:
            if st.button("🌐 Web Scraping", key="scrape_mode"):
                st.session_state.input_mode = "scrape"
        
        # Initialize input mode if not set
        if 'input_mode' not in st.session_state:
            st.session_state.input_mode = "manual"
        
        st.markdown("---")
        
        # Content input section
        if st.session_state.input_mode == "manual":
            st.markdown("### 📝 Content Input")
            content = st.text_area(
                "Enter your content to analyse:",
                height=200,
                value=st.session_state.content,
                placeholder="Paste your article, blog post, or any text content here..."
            )
            st.session_state.content = content
            
        else:  # scrape mode
            st.markdown("### 🌐 Web Scraping")
            
            # URL input
            url = st.text_input(
                "URL to scrape:",
                placeholder="https://example.com"
            )
            
            # Scrape button
            if st.button("🔍 Scrape Page"):
                if not url:
                    st.error("Please enter a URL")
                elif not validate_url(url):
                    st.error("Please enter a valid URL (include http:// or https://)")
                elif 'firecrawl_api_key' not in st.session_state or not st.session_state.get('firecrawl_api_key'):
                    st.error("Firecrawl API key is required for web scraping. Please enter your API key in the configuration section below.")
                else:
                    with st.spinner("Scraping content..."):
                        try:
                            firecrawl_service = FirecrawlService(st.session_state.firecrawl_api_key)
                            
                            result = firecrawl_service.scrape_url(url)
                            st.session_state.content = result['markdown']
                            st.session_state.content_source = f"Scraped from: {result['url']}"
                            if result.get('title'):
                                st.session_state.content_source += f" ({result['title']})"
                                    
                            st.success("Content scraped successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error scraping URL: {str(e)}")
        
        # Show scraped content source
        if st.session_state.content_source:
            st.markdown(f'<div class="crawl-info">📄 {st.session_state.content_source}</div>', unsafe_allow_html=True)
        
        # Target queries input
        st.markdown("### 🎯 Target Queries")
        queries = st.text_area(
            "List keywords or questions your content should rank for:",
            height=100,
            placeholder="google top stories tracker\nsemantic search optimisation\nAI content analysis"
        )
        
        # Analyse button
        if st.button("⚡ Analyse Content", key="analyze_btn", type="primary"):
            if not st.session_state.content.strip():
                st.error("Please provide content to analyse")
            elif not queries.strip():
                st.error("Please provide target queries")
            else:
                # Check if API keys are set (they are now at the bottom)
                if 'gemini_api_key' not in st.session_state or not st.session_state.get('gemini_api_key'):
                    st.error("Gemini API key is required for content analysis. Please enter your API key in the configuration section below.")
                else:
                    query_list = [q.strip() for q in queries.split('\n') if q.strip()]
                    
                    with st.spinner("Testing API connection..."):
                        try:
                            gemini_api_key = st.session_state.gemini_api_key
                            if not gemini_api_key.strip():
                                st.error("Please enter a valid Gemini API key")
                                return
                            
                            # First test the API connection
                            analysis_service = AnalysisService(gemini_api_key.strip())
                            
                            # Test connection
                            connection_success, connection_message = analysis_service.test_api_connection()
                            if not connection_success:
                                st.error(f"❌ API connection failed: {connection_message}")
                                st.info("💡 This API key works in React but fails in Python. This might be a library or configuration issue.")
                                return
                            
                            # If connection works, proceed with analysis
                            with st.spinner("Generating insights..."):
                                results = analysis_service.analyze_content(st.session_state.content, query_list)
                                
                                # Check if analysis actually succeeded
                                if "Analysis failed" in str(results.semantic_gaps):
                                    # Extract the specific error message
                                    error_msg = results.semantic_gaps[0] if results.semantic_gaps else "Unknown error"
                                    st.error(f"❌ {error_msg}")
                                    st.info("💡 Please resolve the issue and try again.")
                                else:
                                    st.session_state.analysis_results = results
                                    st.success("✅ Analysis complete!")
                                    st.rerun()
                                    
                        except ValueError as e:
                            st.error(f"❌ API Key Error: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
                            st.info("💡 Please check your API key and internet connection.")
    
    # Analysis Results Section
    if st.session_state.analysis_results:
        st.markdown("---")
        st.markdown("### ⚡ Analysis Results")
        
        results = st.session_state.analysis_results
        
        # Check if advanced analysis data is available
        has_advanced_data = (
            hasattr(results, 'similarity_matrix') and results.similarity_matrix and
            hasattr(results, 'processing_time') and results.processing_time > 0
        )
        
        if has_advanced_data:
            st.info("🚀 **Advanced ML Analysis Active** - Real embeddings, semantic clustering, and authority scoring")
        else:
            st.info("📝 **Basic AI Analysis** - Using Gemini AI prompts for scoring")
        
        # Core metrics visualization
        fig = create_metrics_chart(
            results.embedding_relevance_score,
            results.semantic_density_score,
            results.authority_score
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Advanced visualizations (if available)
        if has_advanced_data:
            st.markdown("#### 🔬 Advanced Analysis Visualizations")
            
            # Create tabs for different visualizations
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Processing Summary", 
                "🔥 Similarity Matrix", 
                "🗺️ Semantic Map", 
                "🎯 Topic Clusters",
                "📈 Authority Signals"
            ])
            
            with tab1:
                # Processing metrics
                processing_fig = create_processing_metrics_chart(
                    results.processing_time,
                    len(results.similarity_matrix) if results.similarity_matrix else 0,
                    len(results.similarity_matrix[0]) if results.similarity_matrix and results.similarity_matrix[0] else 0,
                    results.embedding_relevance_score,
                    results.semantic_density_score,
                    results.authority_score
                )
                st.plotly_chart(processing_fig, use_container_width=True)
            
            with tab2:
                # Similarity heatmap
                if results.similarity_matrix:
                    # Extract chunks and queries from the analysis (this is a simplified version)
                    # In a real implementation, you'd pass the actual chunks and queries
                    chunks = [f"Content chunk {i+1}" for i in range(len(results.similarity_matrix))]
                    queries = [f"Query {i+1}" for i in range(len(results.similarity_matrix[0]))] if results.similarity_matrix[0] else []
                    
                    similarity_fig = create_similarity_heatmap(results.similarity_matrix, chunks, queries)
                    st.plotly_chart(similarity_fig, use_container_width=True)
                else:
                    st.info("No similarity matrix data available")
            
            with tab3:
                # Semantic map
                if results.semantic_map_data:
                    semantic_fig = create_semantic_map(results.semantic_map_data)
                    st.plotly_chart(semantic_fig, use_container_width=True)
                else:
                    st.info("No semantic map data available")
            
            with tab4:
                # Topic clusters
                if results.topic_clusters:
                    cluster_fig = create_topic_cluster_chart(results.topic_clusters)
                    st.plotly_chart(cluster_fig, use_container_width=True)
                else:
                    st.info("No topic clustering data available")
            
            with tab5:
                # Authority signals (convert semantic_gaps to authority signals format for demo)
                authority_signals = [
                    {
                        'signal_type': 'content_quality',
                        'impact_score': results.authority_score,
                        'confidence': 0.8,
                        'description': 'Overall content authority assessment'
                    }
                ]
                authority_fig = create_authority_signals_chart(authority_signals)
                st.plotly_chart(authority_fig, use_container_width=True)
        
        # Detailed results in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Semantic Gaps")
            if results.semantic_gaps:
                for gap in results.semantic_gaps:
                    st.markdown(f"• {gap}")
            else:
                st.info("No significant semantic gaps identified.")
        
        with col2:
            st.markdown("#### 💡 Recommendations")
            if results.recommendations:
                for rec in results.recommendations:
                    st.markdown(f"• {rec}")
            else:
                st.info("Content is well-optimised!")
    
    # Metrics explanation section
    st.markdown("---")
    st.markdown('<h2 class="title" style="font-size: 2rem; margin-top: 2rem;">Algorithm Implementation Details</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Detailed computational methods and mathematical formulations used in our scoring algorithms</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="width: 64px; height: 64px; margin: 0 auto; background-color: rgba(255, 140, 66, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    ⚡
                </div>
            </div>
            <h3 class="metric-header">Embedding Relevance</h3>
            <p class="metric-description">
                <strong>Calculation Method:</strong> Uses sentence-transformers (all-MiniLM-L6-v2) for generating embeddings, implements cosine similarity between content and query embeddings, and applies TF-IDF weighting through TfidfVectorizer for importance-based scoring. Final score is normalized to 0-100 scale based on weighted similarity calculations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="width: 64px; height: 64px; margin: 0 auto; background-color: rgba(139, 157, 195, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    🌐
                </div>
            </div>
            <h3 class="metric-header">Semantic Density</h3>
            <p class="metric-description">
                <strong>Calculation Method:</strong> Uses topic clustering with HDBSCAN, performs entity parsing with spaCy, calculates silhouette scores for cluster quality assessment, and analyzes term diversity using TF-IDF. Entity density and cluster cohesion metrics are combined for the final semantic density score.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="width: 64px; height: 64px; margin: 0 auto; background-color: rgba(49, 56, 86, 0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    📄
                </div>
            </div>
            <h3 class="metric-header">Authority Score</h3>
            <p class="metric-description">
                <strong>Calculation Method:</strong> Implements Flesch-Kincaid readability analysis, detects citation patterns with regex matching, analyzes technical terminology frequency, and uses authority embeddings for comparison. Combines linguistic complexity indicators, citation density, and terminology metrics for final authority assessment.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # API Key Configuration Section (moved to bottom)
    st.markdown("---")
    st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #2c3e50; margin-top: 0;">🔑 API Configuration</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #495057; margin-bottom: 1rem;">Please provide your API keys to enable content analysis and web scraping features.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Google Gemini API Key** (Required for analysis)")
        gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Get your free API key from https://aistudio.google.com/app/apikey",
            label_visibility="collapsed",
            key="gemini_api_input"
        )
        if gemini_api_key:
            st.session_state.gemini_api_key = gemini_api_key
            st.success("✅ Gemini API key provided")
        else:
            st.info("ℹ️ Required for content analysis")

    with col2:
        st.markdown("**Firecrawl API Key** (Required for web scraping)")
        firecrawl_api_key = st.text_input(
            "Firecrawl API Key", 
            type="password",
            placeholder="fc-...",
            help="Get your API key from https://www.firecrawl.dev/",
            label_visibility="collapsed",
            key="firecrawl_api_input"
        )
        if firecrawl_api_key:
            st.session_state.firecrawl_api_key = firecrawl_api_key
            st.success("✅ Firecrawl API key provided")
        else:
            st.info("ℹ️ Required for web scraping")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>&copy; 2024 AI-Powered Topic Optimiser. Powered by <a href="https://svetoslav.co.uk/" target="_blank" style="color: #007bff; text-decoration: none;">Svet Petkov</a>.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 