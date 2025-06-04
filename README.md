# Semantic Optimization Assistant

An AI-powered tool that helps optimize content for better semantic understanding and machine readability. Now with web crawling capabilities powered by Firecrawl!

## Features

- **Content Analysis**: Analyze text content for semantic density, relevance, and authority
- **Web Crawling**: Crawl web pages or entire websites using Firecrawl
- **AI-Powered Insights**: Get recommendations for improving content optimization
- **Real-time Processing**: Instant analysis and feedback

## Run Locally

**Prerequisites:** Node.js

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up your API keys:
   - Create a `.env.local` file in the root directory
   - Add your API keys:
   ```
   VITE_GEMINI_API_KEY=your_gemini_api_key_here
   VITE_FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

3. Get your API keys:
   - **Gemini API**: Visit [Google AI Studio](https://aistudio.google.com/) to get your Gemini API key
   - **Firecrawl API**: Visit [Firecrawl.dev](https://www.firecrawl.dev/) to get your Firecrawl API key (free tier available)

4. Run the app:
   ```bash
   npm run dev
   ```

## Usage

1. **Manual Input**: Enter your content directly in the text area
2. **Web Crawling**: Switch to "Crawl URL" mode and enter a website URL to automatically extract content
3. **Query Analysis**: Add search queries to analyze how well your content matches specific search terms
4. **Get Insights**: Click "Analyze Content" to receive AI-powered optimization recommendations
