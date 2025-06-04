import React, { useState } from 'react';
import { Globe, Download, AlertCircle } from 'lucide-react';
import { FirecrawlService, CrawlResult } from '../services/firecrawlService';

interface UrlInputProps {
  onContentCrawled: (content: string, title?: string, url?: string) => void;
  firecrawlApiKey?: string;
}

export const UrlInput: React.FC<UrlInputProps> = ({ onContentCrawled, firecrawlApiKey }) => {
  const [url, setUrl] = useState<string>('');
  const [isCrawling, setIsCrawling] = useState<boolean>(false);
  const [crawlError, setCrawlError] = useState<string | null>(null);
  const [crawlMode, setCrawlMode] = useState<'single' | 'crawl'>('single');
  const [maxPages, setMaxPages] = useState<number>(5);

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleCrawl = async () => {
    if (!url.trim()) {
      setCrawlError('Please enter a URL');
      return;
    }

    if (!validateUrl(url)) {
      setCrawlError('Please enter a valid URL (include http:// or https://)');
      return;
    }

    if (!firecrawlApiKey) {
      setCrawlError('Firecrawl API key is required. Please set your API key in the environment variables.');
      return;
    }

    setIsCrawling(true);
    setCrawlError(null);

    try {
      const firecrawlService = new FirecrawlService(firecrawlApiKey);
      
      if (crawlMode === 'single') {
        const result = await firecrawlService.scrapeUrl(url);
        onContentCrawled(result.markdown, result.title, result.url);
      } else {
        const results = await firecrawlService.crawlWebsite(url, maxPages);
        if (results.length === 0) {
          throw new Error('No pages were crawled');
        }
        
        // Combine all crawled content
        const combinedContent = results.map((result, index) => 
          `## Page ${index + 1}: ${result.title || result.url}\n\n${result.markdown}`
        ).join('\n\n---\n\n');
        
        onContentCrawled(combinedContent, `Crawled ${results.length} pages from ${url}`, url);
      }
    } catch (error: any) {
      console.error('Crawling error:', error);
      setCrawlError(error.message || 'Failed to crawl the URL');
    } finally {
      setIsCrawling(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-3">
        <Globe size={20} style={{color: '#8b9dc3'}} />
        <h2 className="text-xl font-semibold text-slate-200">Web Crawling</h2>
      </div>
      
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            URL to crawl
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent"
            style={{'--focus-ring-color': '#313856'} as React.CSSProperties}
            onFocus={(e) => (e.target as HTMLInputElement).style.boxShadow = '0 0 0 2px rgba(49, 56, 86, 0.5)'}
            onBlur={(e) => (e.target as HTMLInputElement).style.boxShadow = 'none'}
          />
        </div>

        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="radio"
              name="crawlMode"
              value="single"
              checked={crawlMode === 'single'}
              onChange={(e) => setCrawlMode(e.target.value as 'single')}
              style={{accentColor: '#313856'}}
            />
            Single page
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="radio"
              name="crawlMode"
              value="crawl"
              checked={crawlMode === 'crawl'}
              onChange={(e) => setCrawlMode(e.target.value as 'crawl')}
              style={{accentColor: '#313856'}}
            />
            Crawl website
          </label>
        </div>

        {crawlMode === 'crawl' && (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Max pages to crawl
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={maxPages}
              onChange={(e) => setMaxPages(parseInt(e.target.value) || 5)}
              className="w-20 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:border-transparent"
              onFocus={(e) => (e.target as HTMLInputElement).style.boxShadow = '0 0 0 2px rgba(49, 56, 86, 0.5)'}
              onBlur={(e) => (e.target as HTMLInputElement).style.boxShadow = 'none'}
            />
          </div>
        )}

        <button
          onClick={handleCrawl}
          disabled={isCrawling || !url.trim()}
          className="w-full flex items-center justify-center gap-2 disabled:bg-slate-600 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-opacity-75"
          style={{
            backgroundColor: isCrawling || !url.trim() ? '#475569' : '#ff8c42',
            boxShadow: `0 0 0 2px rgba(255, 140, 66, 0.4)`
          }}
          onMouseEnter={(e) => {
            if (!isCrawling && url.trim()) {
              (e.target as HTMLButtonElement).style.backgroundColor = '#ff7a28';
            }
          }}
          onMouseLeave={(e) => {
            if (!isCrawling && url.trim()) {
              (e.target as HTMLButtonElement).style.backgroundColor = '#ff8c42';
            }
          }}
        >
          {isCrawling ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Crawling...
            </>
          ) : (
            <>
              <Download size={16} />
              {crawlMode === 'single' ? 'Scrape Page' : `Crawl ${maxPages} Pages`}
            </>
          )}
        </button>

        {crawlError && (
          <div className="mt-2 p-3 bg-red-700 bg-opacity-50 text-red-300 border border-red-600 rounded-lg flex items-center gap-2">
            <AlertCircle size={16} />
            <p className="text-sm">{crawlError}</p>
          </div>
        )}
      </div>
    </div>
  );
}; 