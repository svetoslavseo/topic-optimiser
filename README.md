# AI-Powered Topic Optimiser

An AI-powered Streamlit application that helps optimise content for better semantic understanding and machine readability. Features web crawling capabilities powered by Firecrawl and advanced content analysis using Google Gemini AI.

## Features

- **🔍 Content Analysis**: Analyse text content for semantic density, relevance, and authority scores
- **🌐 Web Crawling**: Crawl web pages or entire websites using Firecrawl API
- **🤖 AI-Powered Insights**: Get recommendations for improving content optimisation using Gemini AI
- **📊 Interactive Visualisations**: Beautiful charts and metrics using Plotly
- **⚡ Real-time Processing**: Instant analysis and feedback with Streamlit
- **🔑 User-friendly API Configuration**: Enter API keys directly in the interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-powered-topic-optimizer.git
   cd ai-powered-topic-optimizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your API keys (required for functionality):**
   - **Gemini API**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to get your free Gemini API key
   - **Firecrawl API**: Visit [Firecrawl.dev](https://www.firecrawl.dev/) to get your Firecrawl API key (free tier available)
   
   ℹ️ **Note**: You'll enter these API keys directly in the application interface - no environment file setup required!

## Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

1. **🔑 API Setup**: Enter your Gemini and Firecrawl API keys in the configuration section at the top
2. **📝 Manual Input**: Enter your content directly in the text area
3. **🌐 Web Crawling**: Switch to "Crawl URL" mode and enter a website URL to automatically extract content
4. **🎯 Query Analysis**: Add search queries to analyse how well your content matches specific search terms
5. **⚡ Get Insights**: Click "Analyse Content" to receive AI-powered optimisation recommendations

## Project Structure

```
ai-powered-topic-optimiser/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration and environment variables
├── services/
│   ├── firecrawl_service.py    # Web crawling functionality
│   └── analysis_service.py     # AI content analysis
├── components/
│   └── metrics_charts.py       # Plotly visualisations
├── utils/
│   └── helpers.py             # Utility functions
└── README.md
```
