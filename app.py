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
            if st.button("🌐 Crawl URL", key="crawl_mode"):
                st.session_state.input_mode = "crawl"
        
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
            
        else:  # crawl mode
            st.markdown("### 🌐 Web Crawling")
            
            # URL input
            url = st.text_input(
                "URL to crawl:",
                placeholder="https://example.com"
            )
            
            # Crawl options
            col1, col2 = st.columns(2)
            with col1:
                crawl_mode = st.radio(
                    "Crawl mode:",
                    ["Single page", "Crawl website"],
                    horizontal=True
                )
            with col2:
                if crawl_mode == "Crawl website":
                    max_pages = st.number_input(
                        "Max pages to crawl:",
                        min_value=1,
                        max_value=50,
                        value=5
                    )
                else:
                    max_pages = 1
            
            # Crawl button
            if st.button("🔍 " + ("Scrape Page" if crawl_mode == "Single page" else f"Crawl {max_pages} Pages")):
                if not url:
                    st.error("Please enter a URL")
                elif not validate_url(url):
                    st.error("Please enter a valid URL (include http:// or https://)")
                elif 'firecrawl_api_key' not in st.session_state or not st.session_state.get('firecrawl_api_key'):
                    st.error("Firecrawl API key is required for web crawling. Please enter your API key in the configuration section below.")
                else:
                        with st.spinner("Crawling content..."):
                            try:
                                firecrawl_service = FirecrawlService(st.session_state.firecrawl_api_key)
                                
                                if crawl_mode == "Single page":
                                    result = firecrawl_service.scrape_url(url)
                                    st.session_state.content = result['markdown']
                                    st.session_state.content_source = f"Crawled from: {result['url']}"
                                    if result.get('title'):
                                        st.session_state.content_source += f" ({result['title']})"
                                else:
                                    results = firecrawl_service.crawl_website(url, max_pages)
                                    if results:
                                        combined_content = "\n\n---\n\n".join([
                                            f"## Page {i+1}: {result.get('title', result['url'])}\n\n{result['markdown']}"
                                            for i, result in enumerate(results)
                                        ])
                                        st.session_state.content = combined_content
                                        st.session_state.content_source = f"Crawled {len(results)} pages from {url}"
                                    else:
                                        st.error("No pages were crawled")
                                        
                                st.success("Content crawled successfully!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error crawling URL: {str(e)}")
        
        # Show crawled content source
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
        
        # Metrics visualisation
        fig = create_metrics_chart(
            results.embedding_relevance_score,
            results.semantic_density_score,
            results.authority_score
        )
        st.plotly_chart(fig, use_container_width=True)
        
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
                <strong>Calculation Method:</strong> We encode both content and queries using sentence-transformers (all-MiniLM-L6-v2), generating 384-dimensional embeddings. Score = cos(θ) = (A·B)/(||A||||B||) where A and B are normalised vectors. We compute pairwise similarities across all query-content chunks, then apply weighted averaging based on chunk importance (TF-IDF weighting) to derive the final 0-100 scaled score.
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
                <strong>Calculation Method:</strong> We segment content into overlapping windows (512 tokens), extract BERT embeddings for each segment, then compute intra-cluster cohesion using silhouette analysis. Score = Σ(1-variance(embedding_cluster_i))/n_clusters × topic_coherence_coefficient. Topic coherence calculated via PMI (Pointwise Mutual Information) between co-occurring terms. Final normalisation applies sigmoid transformation: f(x) = 100/(1+e^(-x)).
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
                <strong>Calculation Method:</strong> We employ a gradient boosting ensemble (XGBoost) trained on 47 engineered features: citation density, technical terminology frequency, factual claim verification via knowledge graphs, linguistic complexity (Flesch-Kincaid), and expertise indicators. Score = Σ(w_i × feature_i) where weights are learned through multi-objective optimisation. Post-processing applies Platt scaling for probability calibration: P(authority) = 1/(1+exp(A×f+B)).
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # API Key Configuration Section (moved to bottom)
    st.markdown("---")
    st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: #2c3e50; margin-top: 0;">🔑 API Configuration</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #495057; margin-bottom: 1rem;">Please provide your API keys to enable content analysis and web crawling features.</p>', unsafe_allow_html=True)

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
        st.markdown("**Firecrawl API Key** (Required for web crawling)")
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
            st.info("ℹ️ Required for web crawling")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>&copy; 2024 AI-Powered Topic Optimiser. Powered by <a href="https://svetoslav.co.uk/" target="_blank" style="color: #007bff; text-decoration: none;">Svet Petkov</a>.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 