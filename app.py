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

# Custom CSS for modern, beautiful styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #313856 0%, #2c3e50 50%, #34495e 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #313856 0%, #2c3e50 50%, #34495e 100%);
    }
    
    /* Ensure all text has high contrast */
    * {
        color: #ffffff !important;
    }
    
    /* Override Streamlit default text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #ffffff !important;
    }
    
    /* Ensure all form labels are visible */
    label, .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Ensure help text is visible */
    .stTextInput .help, .stTextArea .help, .stSelectbox .help {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Generic text elements */
    p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Streamlit widgets text */
    .stSelectbox > div > div {
        color: #ffffff !important;
    }
    
    /* Main container with glassmorphism effect */
    .main-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Typography */
    .title {
        background: linear-gradient(45deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
    }
    
    .subtitle {
        color: #e0e7ff;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 3rem;
        opacity: 0.9;
    }
    
    /* Section Headers */
    .section-header {
        color: #ffffff !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 2rem;
        margin: 1.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        border-radius: 20px 20px 0 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px 0 rgba(31, 38, 135, 0.4);
    }
    
    .metric-header {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    
    .metric-description {
        color: #e0e7ff;
        font-size: 0.95rem;
        line-height: 1.6;
        opacity: 0.9;
    }
    
    /* Input Mode Buttons */
    .stButton > button {
        background: linear-gradient(145deg, #ff6b6b, #ff8e42) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px 0 rgba(255, 107, 107, 0.4) !important;
        text-transform: none !important;
        letter-spacing: 0.5px !important;
        min-width: 180px !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #ff5252, #ff7a28) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px 0 rgba(255, 107, 107, 0.6) !important;
        border: 2px solid rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Specific styling for mode selection buttons */
    .mode-button {
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Center the button containers */
    .stButton {
        text-align: center !important;
        margin: 1rem 0 !important;
    }
    
    /* Add some spacing between mode selection buttons */
    .stButton > button {
        margin: 0.5rem !important;
    }
    
    /* Mode selection buttons specific styling */
    .stButton > button[key="manual_mode"],
    .stButton > button[key="scrape_mode"] {
        background: linear-gradient(145deg, #ff6b6b, #ff8e42) !important;
        box-shadow: 0 6px 20px 0 rgba(255, 107, 107, 0.4) !important;
    }
    
    .stButton > button[key="manual_mode"]:hover,
    .stButton > button[key="scrape_mode"]:hover {
        background: linear-gradient(145deg, #ff5252, #ff7a28) !important;
        box-shadow: 0 10px 30px 0 rgba(255, 107, 107, 0.6) !important;
    }
    
    /* Scrape Page button - yellow/orange theme */
    .stButton > button:not([kind="primary"]):not([key="manual_mode"]):not([key="scrape_mode"]) {
        background: linear-gradient(145deg, #fbbf24, #f59e0b) !important;
        box-shadow: 0 6px 20px 0 rgba(251, 191, 36, 0.4) !important;
        color: #1f2937 !important;
        font-weight: 700 !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton > button:not([kind="primary"]):not([key="manual_mode"]):not([key="scrape_mode"]):hover {
        background: linear-gradient(145deg, #f59e0b, #d97706) !important;
        box-shadow: 0 10px 30px 0 rgba(251, 191, 36, 0.6) !important;
        color: #111827 !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Primary Action Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(145deg, #4ecdc4, #44a08d) !important;
        box-shadow: 0 6px 20px 0 rgba(78, 205, 196, 0.4) !important;
        font-size: 1.2rem !important;
        padding: 1.2rem 2.5rem !important;
        font-weight: 700 !important;
        border-radius: 20px !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(145deg, #26d0ce, #3b9f8a) !important;
        box-shadow: 0 10px 30px 0 rgba(78, 205, 196, 0.6) !important;
        transform: translateY(-3px) !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Text Areas and Inputs */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #1f2937 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(31, 41, 55, 0.6) !important;
        font-weight: 400 !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #1f2937 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(31, 41, 55, 0.6) !important;
        font-weight: 400 !important;
    }
    
    /* Input Labels */
    .stTextArea > label, .stTextInput > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Info boxes */
    .crawl-info {
        background: linear-gradient(145deg, rgba(74, 222, 128, 0.2), rgba(34, 197, 94, 0.1));
        border: 1px solid rgba(74, 222, 128, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        color: #dcfce7;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px 0 rgba(74, 222, 128, 0.1);
    }
    
    /* API Configuration Section */
    .api-key-section {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 3rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.3);
    }
    
    .api-key-section h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .api-key-section p {
        color: #e0e7ff !important;
        margin-bottom: 1.5rem !important;
        opacity: 0.9;
    }
    
    /* Success/Error Messages */
    .stSuccess > div {
        background: linear-gradient(145deg, rgba(74, 222, 128, 0.2), rgba(34, 197, 94, 0.1)) !important;
        border: 1px solid rgba(74, 222, 128, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        color: #dcfce7 !important;
    }
    
    .stError > div {
        background: linear-gradient(145deg, rgba(248, 113, 113, 0.2), rgba(239, 68, 68, 0.1)) !important;
        border: 1px solid rgba(248, 113, 113, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        color: #fecaca !important;
    }
    
    .stInfo > div {
        background: linear-gradient(145deg, rgba(96, 165, 250, 0.2), rgba(59, 130, 246, 0.1)) !important;
        border: 1px solid rgba(96, 165, 250, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        color: #dbeafe !important;
    }
    
    /* Divider */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent) !important;
        margin: 2rem 0 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #e0e7ff;
        font-size: 0.9rem;
        margin-top: 4rem;
        padding: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        opacity: 0.8;
    }
    
    .footer a {
        color: #fbbf24 !important;
        text-decoration: none !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .footer a:hover {
        color: #f59e0b !important;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main-container {
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(145deg, #313856, #2c3e50);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(145deg, #2c3e50, #34495e);
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
    # Header with improved design
    st.markdown('<h1 class="title">AI-Powered Topic Optimiser</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Elevate your content\'s AI readiness with advanced semantic analysis</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'content' not in st.session_state:
        st.session_state.content = ""
    if 'content_source' not in st.session_state:
        st.session_state.content_source = ""
    
    # Main container
    with st.container():
        # Input mode selection - centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Create two sub-columns for the buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("📝 Manual Input", key="manual_mode"):
                    st.session_state.input_mode = "manual"
            with btn_col2:
                if st.button("🌐 Web Scraping", key="scrape_mode"):
                    st.session_state.input_mode = "scrape"
        
        # Initialize input mode if not set
        if 'input_mode' not in st.session_state:
            st.session_state.input_mode = "manual"
        
        st.markdown("---")
        
        # Content input section
        if st.session_state.input_mode == "manual":
            st.markdown('<div class="section-header">📝 Content Input</div>', unsafe_allow_html=True)
            content = st.text_area(
                "Enter your content to analyse:",
                height=200,
                value=st.session_state.content,
                placeholder="Paste your article, blog post, or any text content here..."
            )
            st.session_state.content = content
            
        else:  # scrape mode
            st.markdown('<div class="section-header">🌐 Web Scraping</div>', unsafe_allow_html=True)
            
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
        st.markdown('<div class="section-header">🎯 Target Queries</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="section-header">⚡ Analysis Results</div>', unsafe_allow_html=True)
        
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
            st.markdown('<div class="section-header">🔬 Advanced Analysis Visualizations</div>', unsafe_allow_html=True)
            
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