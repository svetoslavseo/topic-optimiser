# AI-Powered Topic Optimizer

An AI-powered Streamlit application that helps optimize content for better semantic understanding and machine readability. Features web crawling capabilities powered by Firecrawl and advanced content analysis using Google Gemini AI.

## Features

- **🔍 Content Analysis**: Analyze text content for semantic density, relevance, and authority scores
- **🌐 Web Crawling**: Crawl web pages or entire websites using Firecrawl API
- **🤖 AI-Powered Insights**: Get recommendations for improving content optimization using Gemini AI
- **📊 Interactive Visualizations**: Beautiful charts and metrics using Plotly
- **⚡ Real-time Processing**: Instant analysis and feedback with Streamlit

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

3. **Set up your API keys:**
   - Create a `.env` file in the root directory
   - Add your API keys:
   ```env
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Get your API keys:**
   - **Gemini API**: Visit [Google AI Studio](https://aistudio.google.com/) to get your Gemini API key
   - **Firecrawl API**: Visit [Firecrawl.dev](https://www.firecrawl.dev/) to get your Firecrawl API key (free tier available)

## Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

1. **📝 Manual Input**: Enter your content directly in the text area
2. **🌐 Web Crawling**: Switch to "Crawl URL" mode and enter a website URL to automatically extract content
3. **🎯 Query Analysis**: Add search queries to analyze how well your content matches specific search terms
4. **⚡ Get Insights**: Click "Analyze Content" to receive AI-powered optimization recommendations

## Project Structure

```
ai-powered-topic-optimizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration and environment variables
├── services/
│   ├── firecrawl_service.py    # Web crawling functionality
│   └── analysis_service.py     # AI content analysis
├── components/
│   └── metrics_charts.py       # Plotly visualizations
├── utils/
│   └── helpers.py             # Utility functions
└── README.md
```
